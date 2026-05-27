# -*- coding: utf-8 -*-
"""Windows 系统 OCR — 免费，无需 API Key"""
from winrt.windows.media.ocr import OcrEngine
from winrt.windows.graphics.imaging import BitmapDecoder
from winrt.windows.storage.streams import InMemoryRandomAccessStream, DataWriter
from winrt.windows.globalization import Language

from .base import BaseOCR


class WindowsOCR(BaseOCR):
    name = "Windows 系统 OCR"

    def __init__(self):
        self._engine = None
        self._init_engine()

    def _init_engine(self):
        engine = OcrEngine.try_create_from_user_profile_languages()
        if not engine:
            langs = list(OcrEngine.get_supported_languages())
            if langs:
                engine = OcrEngine.try_create_from_language(langs[0])
        self._engine = engine

    def recognize(self, image_bytes):
        if self._engine is None:
            return False, "Windows OCR 不可用，请确认系统已安装语言包"

        try:
            stream = InMemoryRandomAccessStream()
            writer = DataWriter(stream.get_output_stream_at(0))
            writer.write_bytes(bytes(image_bytes))
            writer.store_async().get()
            writer.flush_async().get()

            decoder = BitmapDecoder.create_async(stream).get()
            bitmap = decoder.get_software_bitmap_async().get()
            result = self._engine.recognize_async(bitmap).get()
            lines = [line.text for line in result.lines]
            return True, "\n".join(lines) if lines else ""
        except Exception as e:
            return False, f"Windows OCR 识别失败: {str(e)}"

    def is_available(self):
        return self._engine is not None
