from .windows_ocr import WindowsOCR


class OCRManager:
    def __init__(self, config_manager):
        self.config = config_manager
        self.engines = {}
        self._init_engines()

    def _init_engines(self):
        self.engines["windows"] = WindowsOCR()

    def get_engine(self, name=None):
        return self.engines.get(name or "windows", self.engines["windows"])

    def recognize(self, image_bytes, engine_name=None):
        return self.get_engine(engine_name).recognize(image_bytes)
