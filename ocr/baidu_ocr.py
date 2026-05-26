import base64
import requests


class BaiduOCR:
    name = "百度 OCR"

    def __init__(self, api_key="", secret_key=""):
        self.api_key = api_key
        self.secret_key = secret_key
        self.access_token = None

    def _get_access_token(self):
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.secret_key,
        }
        try:
            resp = requests.post(url, params=params, timeout=5)
            data = resp.json()
            return data.get("access_token", "")
        except Exception:
            return ""

    def recognize(self, image_bytes):
        if not self.is_available():
            return False, "请先配置百度 OCR API Key"

        if not self.access_token:
            self.access_token = self._get_access_token()
            if not self.access_token:
                return False, "获取 OCR access token 失败，请检查 API Key"

        url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"
        img_base64 = base64.b64encode(image_bytes).decode()

        for attempt in range(2):
            try:
                resp = requests.post(
                    url,
                    data={"image": img_base64},
                    params={"access_token": self.access_token},
                    timeout=10,
                )
                data = resp.json()

                if "error_code" in data:
                    if attempt == 0:
                        self.access_token = self._get_access_token()
                        continue
                    return (
                        False,
                        f"OCR 识别失败: {data.get('error_msg', '未知错误')}",
                    )

                words = [w["words"] for w in data.get("words_result", [])]
                return True, "\n".join(words)

            except Exception as e:
                return False, f"OCR 请求失败: {str(e)}"

        return False, "OCR 识别失败"

    def is_available(self):
        return bool(self.api_key and self.secret_key)
