from .base import BaseTranslator


# Google 翻译使用 deep_translator 库，语言代码与简化代码不同
_GOOGLE_LANG_MAP = {
    "zh": "zh-CN",
    "auto": "auto",
    "en": "en",
    "ja": "ja",
    "ko": "ko",
    "fr": "fr",
    "de": "de",
    "es": "es",
    "ru": "ru",
    "pt": "pt",
    "it": "it",
    "th": "th",
    "vi": "vi",
    "ar": "ar",
}


class GoogleTranslate(BaseTranslator):
    name = "Google 翻译"

    def translate(self, text, from_lang="auto", to_lang="zh"):
        if not text.strip():
            return ""
        try:
            from deep_translator import GoogleTranslator

            src = _GOOGLE_LANG_MAP.get(from_lang, from_lang)
            tgt = _GOOGLE_LANG_MAP.get(to_lang, to_lang)
            translator = GoogleTranslator(source=src, target=tgt)
            return translator.translate(text)
        except Exception as e:
            return f"[翻译失败] {str(e)}"

    def is_available(self):
        return True
