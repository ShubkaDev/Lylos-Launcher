"""Local skin handoff to the Minecraft client."""

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from core.custom_skin_loader import prepare_custom_skin_loader
from core.launcher import Launcher


class CustomSkinLoaderTests(unittest.TestCase):
    def test_fabric_skin_uses_legacy_profile_and_keeps_other_providers(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            minecraft_dir = root / ".minecraft"
            config_path = minecraft_dir / "CustomSkinLoader" / "CustomSkinLoader.json"
            config_path.parent.mkdir(parents=True)
            config_path.write_text(json.dumps({
                "cacheExpiry": 12,
                "loadlist": [
                    {"name": "LocalSkin", "type": "LocalSkin", "root": "wrong"},
                    {"name": "OtherSite", "type": "CustomSkinAPI", "root": "https://example.org/"},
                ],
            }), encoding="utf-8")
            mod = minecraft_dir / "mods" / "CustomSkinLoader.jar"
            mod.parent.mkdir()
            mod.write_bytes(b"existing mod")
            source = root / "chosen.png"
            source.write_bytes(b"chosen skin")

            result = prepare_custom_skin_loader(
                {"loader": "fabric", "minecraft_version": "1.20.1", "minecraft_dir": str(minecraft_dir)},
                {"username": "Player_1", "skin_model": "slim"},
                {"path": str(source)},
            )

            self.assertTrue(result.prepared)
            self.assertEqual(result.mod_path, mod)
            self.assertEqual(result.skin_path.read_bytes(), b"chosen skin")
            self.assertEqual(result.skin_path.name, "Player_1.png")
            config = json.loads(config_path.read_text(encoding="utf-8"))
            self.assertEqual(config["cacheExpiry"], 12)
            self.assertEqual(config["loadlist"][0], {
                "name": "LocalSkin",
                "type": "Legacy",
                "checkPNG": True,
                "skin": "LocalSkin/skins/{USERNAME}.png",
                "model": "slim",
            })
            self.assertEqual(config["loadlist"][1]["name"], "OtherSite")

    def test_vanilla_does_not_claim_to_apply_local_skin(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "chosen.png"
            source.write_bytes(b"chosen skin")
            result = prepare_custom_skin_loader(
                {"loader": "vanilla", "minecraft_dir": str(root / ".minecraft")},
                {"username": "Player_1"},
                {"path": str(source)},
            )
            self.assertFalse(result.prepared)
            self.assertIn("Vanilla", result.message)
            self.assertFalse((root / ".minecraft").exists())

    def test_vanilla_with_skin_does_not_install_fabric(self):
        """Vanilla + выбранный скин → лаунчер НЕ подменяет сборку на Fabric.

        Локальный PNG-скин работает только в модовых сборках; тихая установка
        Fabric убрана, чтобы старые версии (в т.ч. 1.0, beta/alpha) можно было
        запускать как обычную Vanilla.
        """
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "chosen.png"
            source.write_bytes(b"chosen skin")
            instance = {
                "id": "test", "loader": "vanilla", "minecraft_version": "1.0",
                "minecraft_dir": str(root / ".minecraft"),
            }

            with patch.object(Launcher, "_check_disk_space"), patch.object(
                Launcher, "_check_writable",
            ), patch.object(Launcher, "_check_loader_compatibility"), patch(
                "core.launcher.minecraft_launcher_lib.install.install_minecraft_version",
            ), patch(
                "core.launcher.minecraft_launcher_lib.command.get_minecraft_command",
                return_value=["java", "-jar", "client.jar"],
            ), patch("core.launcher.get_required_java_major", return_value=8), patch(
                "core.launcher.find_java_executable", return_value="java",
            ), patch("core.launcher.ensure_java_is_compatible", return_value=8), patch(
                "core.launcher.AccountManager",
            ) as manager, patch("core.skin_manager.SkinManager") as skins, patch(
                "core.launcher.LoaderManager",
            ) as loader_cls, patch(
                "core.custom_skin_loader.prepare_custom_skin_loader",
            ) as prepare, patch("core.launcher.get_instance_manager"), patch(
                "core.launcher.subprocess.Popen",
            ) as popen:
                manager.return_value.get_active_account.return_value = {
                    "id": "1", "username": "Player_1", "provider": "offline",
                }
                manager.return_value.get_launch_profile.return_value = {
                    "username": "Player_1", "uuid": "1234", "token": "0", "provider": "offline",
                }
                skins.return_value.get_account_skin.return_value = {"path": str(source)}
                skins.return_value.ensure_ely_skin.return_value = None

                Launcher().launch_instance(instance)

                # Fabric не устанавливается по-тихому.
                loader_cls.return_value.install_loader.assert_not_called()
                # Локальный скин не готовится в Vanilla.
                prepare.assert_not_called()
                # Игра всё равно запускается как vanilla.
                popen.assert_called_once()


if __name__ == "__main__":
    unittest.main()
