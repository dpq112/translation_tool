import hashlib
import random
import requests
from .base import BaseTranslator

# 百度翻译 API 语言代码映射
# https://fanyi-api.baidu.com/doc/21
_BAIDU_LANG_MAP = {
    "auto": "auto",
    "zh": "zh",
    "en": "en",
    "ja": "jp",
    "ko": "kor",
    "fr": "fra",
    "de": "de",
    "es": "spa",
    "ru": "ru",
    "pt": "pt",
    "it": "it",
    "th": "th",
    "vi": "vie",
    "ar": "ara",
}


class BaiduTranslate(BaseTranslator):
    name = "百度翻译"

    def __init__(self, app_id="", secret_key=""):
        self.app_id = app_id
        self.secret_key = secret_key

    def translate(self, text, from_lang="auto", to_lang="zh"):
        if not self.is_available():
            return "[翻译失败] 请先配置百度翻译 APP ID 和密钥"
        if not text.strip():
            return ""

        url = "https://fanyi-api.baidu.com/api/trans/vip/translate"
        salt = str(random.randint(32768, 65536))
        src = _BAIDU_LANG_MAP.get(from_lang, from_lang)
        tgt = _BAIDU_LANG_MAP.get(to_lang, to_lang)
        sign_str = self.app_id + text + salt + self.secret_key
        sign = hashlib.md5(sign_str.encode()).hexdigest()

        params = {
            "q": text,
            "from": src,
            "to": tgt,
            "appid": self.app_id,
            "salt": salt,
            "sign": sign,
        }

        try:
            resp = requests.get(url, params=params, timeout=5)
            data = resp.json()
            if "trans_result" in data:
                return data["trans_result"][0]["dst"]
            return f"[翻译失败] {data.get('error_msg', '未知错误')} (错误码: {data.get('error_code', '')})"
        except Exception as e:
            return f"[翻译失败] 网络错误: {str(e)}"

    def is_available(self):
        return bool(self.app_id and self.secret_key)
