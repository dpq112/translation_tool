from abc import ABC, abstractmethod


class BaseOCR(ABC):
    name = ""

    @abstractmethod
    def recognize(self, image_bytes):
        """返回 (ok: bool, text_or_error: str)"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass
