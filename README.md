<div align="center">

# ⛏️ Lylos Launcher

**Современный open-source лаунчер Minecraft для Windows**

<p>
  <img src="assets/LL.png" alt="Lylos Launcher" width="140">
</p>

**Управляй сборками, модами, мирами и аккаунтами — всё в одном красивом окне.**

[🚀 Скачать](https://github.com/ShubkaDev/Lylos-Launcher/releases/latest) •
[🌐 Сайт](https://shubkadev.github.io/Lylos-Launcher/) •
[🐛 Сообщить о баге](https://github.com/ShubkaDev/Lylos-Launcher/issues/new)

![Python](https://img.shields.io/badge/Python-3.12+-3572A5?style=flat&logo=python&logoColor=white)
![PySide6](https://img.shields.io/badge/UI-PySide6%20%2F%20Qt6-41B883?style=flat)
![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-0078D7?style=flat&logo=windows&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)
![PRs](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat)

</div>

---

## ✨ Что это?

**Lylos Launcher** — полностью открытый десктоп-лаунчер Minecraft, написанный на **Python + PySide6 (Qt6)**. Он умеет всё, что нужно современному игроку:

- создавать и запускать **отдельные сборки** с разными версиями Minecraft;
- ставить **моды, шейдеры, ресурспаки и модпаки** прямо из Modrinth;
- добавлять **миры и моды** из ZIP/JAR-архивов в пару кликов;
- управлять **аккаунтами** — Offline и Ely.by (со скинами!);
- автоматически **скачивать Java** и настраивать RAM;
- обновляться **сам** через `realese.json` на сайте проекта (fallback — GitHub Releases).

> 🎨 Красивый тёмный интерфейс, видео-фон при первом запуске и встроенные скины Steve / Alex — из коробки.

---

## ✨ Возможности

| | | |
|---|---|---|
| 🗂️ **Сборки** | Vanilla, Fabric, Forge, NeoForge, Quilt — создание, запуск, экспорт и импорт `.zip` |
| 🧩 **Моды** | Каталог Modrinth, установка модов/шейдеров/ресурспаков, импорт `.mrpack` |
| 🌍 **Миры** | Добавление миров из ZIP с автоматической распаковкой вложенных архивов |
| 👤 **Аккаунты** | Offline-профили и Ely.by OAuth, локальные скины Steve/Alex, CustomSkinLoader |
| ☕ **Java** | Автоскачивание Temurin JRE под нужную версию Minecraft |
| ⚙️ **Настройки** | RAM, разрешение окна, папки данных, 6 тем оформления |
| 🔄 **Обновления** | Проверка `realese.json` на сайте проекта + fallback GitHub Releases |

---

## ✨ Скриншоты

> Скриншоты будут добавлены позже. А пока — просто запусти и посмотри 😉

| Экран входа | Главная | Сборки |
|---|---|---|
| Видео-фон + панель Lylos Launcher | Быстрый запуск активной сборки | Карточки с кнопками «Добавить мод/мир» |

---

## ✨ Быстрый старт

### Готовый бинарник

1. Скачай последний релиз: [releases/latest](https://github.com/ShubkaDev/Lylos-Launcher/releases/latest)
2. Запусти `LylosLauncher.exe` (или установи через `LylosSetup.exe`)
3. Создай аккаунт — Offline или через Ely.by
4. Создай сборку и жми **Играть** 🚀

### Из исходников

```powershell
# 1. Клонируй
git clone https://github.com/ShubkaDev/Lylos-Launcher.git
cd Lylos-Launcher

# 2. Виртуальное окружение
python -m venv .venv
.\.venv\Scripts\activate

# 3. Зависимости
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# 4. Запуск
python main.py
```

> 💡 При запуске из Python данные хранятся в `data/`, `instances/`, `logs/` внутри проекта. Собранный `.exe` использует `%APPDATA%\Lylos Launcher`.

---

## ✨ Разработка

### Структура проекта

```text
Lylos-Launcher/
├─ app/                 # Главное окно, маршрутизация страниц
├─ auth/                # Аккаунты: Offline, Ely.by OAuth
├─ core/                # Запуск Minecraft, Java, updater, настройки
│  ├─ archive_importer.py   # Импорт миров и модов из ZIP/JAR
│  ├─ default_skins.py      # Встроенные скины Steve / Alex
│  └─ ...
├─ mods/                # Modrinth API, установка контента, совместимость
├─ storage/             # Пути и JSON-хранилище
├─ ui/                  # PySide6-компоненты, страницы, стили
│  ├─ components/account_setup_window.py  # Экран входа с видео-фоном
│  └─ ...
├─ updater/             # SMUpdater — отдельное окно обновления
├─ installer/           # Inno Setup installer
├─ scripts/             # Build / release скрипты
├─ tools/               # Диагностика, QA, генерация metadata
├─ tests/               # unittest-проверки
├─ website/             # Продакшен-сайт GitHub Pages
├─ realese.json         # Версия и ссылки для автообновления (публикуется на Pages)
├─ main.py              # Точка входа GUI
└─ requirements.txt     # Python-зависимости
```

### Проверки перед релизом

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
.\.venv\Scripts\python.exe tools\deep_qa.py
.\.venv\Scripts\python.exe tools\full_audit.py
```

### Сборка релиза

Сборка лаунчера идёт через `build_all.bat` — он делает всё автоматически:

```bat
build_all.bat
```

Скрипт по порядку:

1. скачивает видео-фон в `assets\video-panarama\1.mp4` (при неудаче открывает страницу для ручного скачивания);
2. проверяет наличие Python 3.12+ — если его нет, показывает ошибку и ждёт 10 секунд;
3. при необходимости устанавливает зависимости из `requirements.txt`;
4. спрашивает OAuth Client ID / Client Secret и настраивает их локально;
5. последовательно собирает через PyInstaller:
   - `LylosLauncher.exe` — основной лаунчер;
   - `LylosUpdater.exe` — обновлятор;
   - `LylosUninstaller.exe` — удалятор;
   - `LylosSetup.exe` — установщик.

Результаты попадают в `release/`. Публикация GitHub Release — через tag workflow `v*`.

---

## ✨ Технологии

| Слой | Стек |
|---|---|
| **Язык** | Python 3.12+ |
| **GUI** | PySide6 (Qt 6) |
| **Запуск Minecraft** | `minecraft_launcher_lib` |
| **Каталог модов** | Modrinth API |
| **Авторизация** | Ely.by OAuth 2.0 (локальный callback-сервер) |
| **Сборка** | PyInstaller + Inno Setup |
| **Сайт** | Статический HTML/CSS/JS на GitHub Pages |
| **CI** | GitHub Actions (Python 3.12) |

---

## ✨ Частые вопросы

<details>
<summary><b>Сборки не видны в .exe?</b></summary>

Python-запуск и `.exe` используют разные хранилища данных. Проверь `%APPDATA%\Lylos Launcher\data\instances.json`.
</details>

<details>
<summary><b>Моды не устанавливаются?</b></summary>

Проверь выбранную сборку, loader, совместимость версии Minecraft, интернет и `logs/latest.log`.
</details>

<details>
<summary><b>Minecraft не запускается из-за Java?</b></summary>

Проверь `java -version`, путь Java в настройках и `logs/latest.log`. Лаунчер умеет скачивать Java автоматически.
</details>

<details>
<summary><b>Как добавить мир или мод из архива?</b></summary>

В карточке сборки нажми **«+ Добавить мир»** или **«+ Добавить мод»** и выбери ZIP/JAR. Лаунчер сам распакует вложенные архивы и разложит файлы по папкам `saves/` и `mods/`.
</details>

---

## ✨ Участие

Проект полностью открыт — форкай, правь, предлагай!

1. [Fork](https://github.com/ShubkaDev/Lylos-Launcher/fork) репозитория
2. Создай ветку `feature/имя-фичи`
3. Внеси изменения и открой **Pull Request**

---

## ✨ Лицензия

**MIT** — проект можно свободно форкать, изменять и распространять. См. [LICENSE](LICENSE).

> ⚠️ Lylos Launcher — неофициальный open-source проект. Он **не связан** с Mojang, Microsoft, Fabric, Forge, NeoForge, Quilt или Modrinth. Minecraft — товарный знак Mojang/Microsoft.

<div align="center">

**Сделано с 💜 для Minecraft-сообщества**

</div>
