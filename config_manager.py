import json
import os
from pathlib import Path


class ConfigManager:
    def __init__(self):
        self.config_dir = Path(os.environ["APPDATA"]) / "TranslationTool"
        self.config_file = self.config_dir / "config.json"
        self.config = self._load()

    def _default_config(self):
        return {
            "data_dir": str(Path(os.environ["APPDATA"]) / "TranslationTool"),
            "translators": {
                "baidu": {"app_id": "", "secret_key": "", "enabled": False},
                "google": {"enabled": True},
            },
            "default_engine": "google",
            "source_lang": "auto",
            "target_lang": "en",
            "hotkeys": {
                "mini_window": "ctrl+shift+q",
                "main_window": "ctrl+shift+w",
                "screenshot": "ctrl+shift+e",
            },
        }

    def _load(self):
        self.config_dir.mkdir(parents=True, exist_ok=True)
        if self.config_file.exists():
            with open(self.config_file, "r", encoding="utf-8") as f:
                saved = json.load(f)
                defaults = self._default_config()
                for key, value in defaults.items():
                    if key not in saved:
                        saved[key] = value
                return saved
        config = self._default_config()
        self._save(config)
        return config

    def _save(self, config=None):
        if config is None:
            config = self.config
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def get(self, key, default=None):
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

    def set(self, key, value):
        keys = key.split(".")
        target = self.config
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        target[keys[-1]] = value
        self._save()

    def save(self):
        self._save()
