import logging
import os
import shutil
import subprocess
import sys
import traceback
import threading
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QIcon

from core.logger import setup_logging
from core.network_manager import disable_proxy_for_launcher, log_proxy_environment


def install_global_exception_hooks():
    def log_unhandled_exception(exc_type, exc_value, exc_traceback):
        logging.getLogger(__name__).critical(
            "Unhandled exception",
            exc_info=(exc_type, exc_value, exc_traceback),
        )

    def log_thread_exception(args):
        logging.getLogger(__name__).critical(
            "Unhandled thread exception in %s",
            getattr(args.thread, "name", "thread"),
            exc_info=(args.exc_type, args.exc_value, args.exc_traceback),
        )

    sys.excepthook = log_unhandled_exception
    threading.excepthook = log_thread_exception


def show_fatal_error(error: BaseException):
    message = QMessageBox()
    message.setIcon(QMessageBox.Critical)
    message.setWindowTitle("Lylos Launcher — ошибка запуска")
    message.setText("Не удалось запустить Lylos Launcher.")
    message.setInformativeText(str(error))
    message.setDetailedText(traceback.format_exc())
    message.exec()


def main():
    setup_logging()
    install_global_exception_hooks()
    logger = logging.getLogger(__name__)

    if "--diagnose" in sys.argv:
        from tools.diagnose_sm import run_diagnostics
        run_diagnostics()
        return

    try:
        try:
            from core.windows_app_id import set_windows_app_id
            set_windows_app_id()
        except Exception:
            logger.debug("Windows AppUserModelID setup skipped", exc_info=True)

        logger.info("Checking proxy environment before cleanup")
        log_proxy_environment()

        disable_proxy_for_launcher()

        logger.info("Checking proxy environment after cleanup")
        log_proxy_environment()

        from core.i18n import set_language
        from storage.paths import DATA_DIR
        import json

        settings_file = DATA_DIR / "launcher_settings.json"
        settings_data = {}
        if settings_file.exists():
            try:
                settings_data = json.loads(settings_file.read_text(encoding="utf-8"))
            except Exception:
                pass

        lang = "ru"
        if settings_data.get("language") != lang:
            try:
                settings_data["language"] = lang
                settings_file.parent.mkdir(parents=True, exist_ok=True)
                settings_file.write_text(json.dumps(settings_data, ensure_ascii=False, indent=2), encoding="utf-8")
            except Exception:
                logger.debug("Could not persist forced launcher language", exc_info=True)
        set_language(lang)
        logger.info("Loaded language: %s", lang)

        from app.window import MainWindow

        logger.info("Creating QApplication")
        app = QApplication(sys.argv)
        try:
            from ui.wheel_guard import install_no_wheel_value_changes
            install_no_wheel_value_changes(app)
        except Exception:
            logger.debug("Wheel guard setup skipped", exc_info=True)
        try:
            app.setApplicationName("Lylos Launcher")
            app.setApplicationDisplayName("Lylos Launcher")
            app.setOrganizationName("Lylos")
        except Exception:
            pass

        try:
            app_icon = Path(__file__).resolve().parent / "assets" / "LL.ico"
            if app_icon.exists():
                app.setWindowIcon(QIcon(str(app_icon)))
        except Exception:
            pass

        from ui.styles import get_app_style
        theme = settings_data.get("theme", "dark")
        if theme == "light":
            theme = "dark"
        try:
            app.setStyleSheet(get_app_style(theme))
            logger.info("Applied theme: %s", theme)
        except Exception:
            logger.exception("Failed to apply saved theme")
            app.setStyleSheet(get_app_style("dark"))

        # ---- Splash screen + startup update check ----------------------
        import core.constants as constants
        from ui.splash import SplashScreen, UpdateCheckWorker

        splash = SplashScreen()
        splash.show()

        flow_state: dict = {}

        def _needs_account_setup() -> bool:
            """Нужно ли показать отдельное окно создания аккаунта.

            Показываем, если аккаунтов нет или есть только автоматический
            LLPlayer (пользователь ещё не создал свой аккаунт).
            """
            try:
                from auth.account_manager import get_account_manager

                accounts = get_account_manager().list_accounts()
                if not accounts:
                    return True
                if len(accounts) == 1:
                    acc = accounts[0]
                    provider = str(acc.get("provider") or "offline").lower()
                    username = str(acc.get("username") or acc.get("display_name") or "").lower()
                    if provider == "offline" and username == "llplayer":
                        return True
            except Exception:
                logger.debug("Account setup check failed", exc_info=True)
            return False

        def _ensure_default_skins() -> None:
            """Назначить случайный Steve/Alex аккаунтам без скина."""
            try:
                from auth.account_manager import get_account_manager
                from core.default_skins import ensure_default_skin

                for account in get_account_manager().list_accounts():
                    ensure_default_skin(account)
            except Exception:
                logger.debug("Default skin assignment failed", exc_info=True)

        def _create_main_window():
            logger.info("Creating main window")
            _ensure_default_skins()
            window = MainWindow()
            window.show()
            QApplication.processEvents()
            try:
                splash.close()
            except Exception:
                pass

            if "--open-updates" in sys.argv:
                from PySide6.QtCore import QTimer
                from app.window import PageIndex

                def open_updates_page():
                    try:
                        window.change_page(PageIndex.SETTINGS)
                        if hasattr(window.settings_page, "check_updates_from_settings"):
                            window.settings_page.check_updates_from_settings()
                    except Exception:
                        logger.exception("Failed to open updates page")

                QTimer.singleShot(500, open_updates_page)

        def _show_account_setup_window():
            """Отдельное окно создания аккаунта (видео-фон) до главного окна."""
            from ui.components.account_setup_window import AccountSetupWindow

            setup_window = AccountSetupWindow()
            flow_state["setup_window"] = setup_window
            setup_window.finished_setup.connect(_create_main_window)
            try:
                splash.close()
            except Exception:
                pass
            setup_window.show()

        def _open_main_window():
            constants.STARTUP_UPDATE_HANDLED = True
            if _needs_account_setup():
                logger.info("No account yet — showing account setup window first")
                _show_account_setup_window()
            else:
                _create_main_window()

        def _loading_then_open():
            """Show „Загрузка...“ on the splash for 3 seconds, then open the launcher."""
            splash.set_status("Загрузка...")
            splash.play_loading(3000, _open_main_window)

        def _ask_update(release):
            from PySide6.QtWidgets import QMessageBox
            from core.app_info import APP_VERSION

            box = QMessageBox(splash)
            box.setIcon(QMessageBox.Icon.Information)
            box.setWindowTitle("Доступно обновление")
            box.setText(f"Ваша версия {APP_VERSION} устарела. Обновить до {release.version}?")
            box.setInformativeText(
                "LylosUpdater.exe скачает архив обновления и заменит файлы лаунчера."
            )
            yes_button = box.addButton("Да", QMessageBox.ButtonRole.AcceptRole)
            no_button = box.addButton("Позже", QMessageBox.ButtonRole.RejectRole)
            box.setDefaultButton(yes_button)
            box.exec()

            if box.clickedButton() is not yes_button:
                _loading_then_open()
                return

            is_frozen = getattr(sys, "frozen", False)
            launcher_dir = (
                Path(sys.executable).resolve().parent
                if is_frozen
                else Path(__file__).resolve().parent
            )
            appdata = Path(os.environ.get("APPDATA") or (Path.home() / "AppData" / "Roaming"))
            install_dir = launcher_dir if is_frozen else appdata / "Lylos Launcher"
            updater_dir = install_dir / "update"
            updater_path = updater_dir / "SMUpdate.exe"
            updater_candidates = [
                launcher_dir / "LylosUpdater.exe",
                launcher_dir / "SMUpdater.exe",
                launcher_dir / "update" / "SMUpdate.exe",
                launcher_dir / "update" / "LylosUpdater.exe",
                launcher_dir / "update" / "SMUpdater.exe",
                install_dir / "LylosUpdater.exe",
                install_dir / "SMUpdater.exe",
                install_dir / "update" / "SMUpdate.exe",
                install_dir / "update" / "LylosUpdater.exe",
                install_dir / "update" / "SMUpdater.exe",
            ]
            if not is_frozen:
                updater_candidates.extend(
                    [
                        launcher_dir / "dist" / "LylosUpdater.exe",
                        launcher_dir / "dist" / "SMUpdater.exe",
                    ]
                )
            updater_source = next(
                (candidate for candidate in updater_candidates if candidate.is_file()),
                None,
            )

            try:
                if updater_source is None:
                    searched = ", ".join(str(path) for path in updater_candidates)
                    raise FileNotFoundError(f"Обновлятор не найден. Проверены пути: {searched}")
                updater_dir.mkdir(parents=True, exist_ok=True)
                if updater_source.resolve() != updater_path.resolve():
                    shutil.copy2(updater_source, updater_path)
                subprocess.Popen(
                    [
                        str(updater_path),
                        "--wait-pid", str(os.getpid()),
                        "--install-dir", str(install_dir),
                    ],
                    cwd=str(install_dir),
                )
            except Exception as error:
                logger.exception("Failed to start updater")
                QMessageBox.critical(splash, "Ошибка обновления", str(error))
                _loading_then_open()
                return

            app.quit()

        def _on_check_done(release):
            if release is not None and release.is_newer:
                _ask_update(release)
            else:
                _loading_then_open()

        check_worker = UpdateCheckWorker(timeout=8)
        flow_state["check_worker"] = check_worker
        check_worker.result_ready.connect(_on_check_done)
        check_worker.start()

        logger.info("Application event loop started")
        exit_code = app.exec()

        logger.info("Application closed with code %s", exit_code)
        sys.exit(exit_code)

    except Exception as error:
        logger.exception("Fatal application error")

        try:
            app = QApplication.instance() or QApplication(sys.argv)
            show_fatal_error(error)
        except Exception:
            pass

        sys.exit(1)


if __name__ == "__main__":
    main()
