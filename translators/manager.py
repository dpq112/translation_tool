from .google import GoogleTranslate
from .baidu import BaiduTranslate


class TranslatorManager:
    def __init__(self, config_manager):
        self.config = config_manager
        self.translators = {}
        self._init_translators()

    def _init_translators(self):
        self.translators["google"] = GoogleTranslate()
        self.translators["baidu"] = BaiduTranslate()
        self.refresh_credentials()

    def refresh_credentials(self):
        baidu = self.config.get("translators.baidu", {})
        self.translators["baidu"].app_id = baidu.get("app_id", "")
        self.translators["baidu"].secret_key = baidu.get("secret_key", "")

    def get_translator(self, engine=None):
        if engine is None:
            engine = self.config.get("default_engine", "google")
        return self.translators.get(engine, self.translators["google"])

    def get_available_engines(self):
        return [
            (key, t) for key, t in self.translators.items() if t.is_available()
        ]

    def translate(self, text, from_lang="auto", to_lang="zh", engine=None):
        translator = self.get_translator(engine)
        return translator.translate(text, from_lang, to_lang)
