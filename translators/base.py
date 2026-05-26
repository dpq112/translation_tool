from abc import ABC, abstractmethod


class BaseTranslator(ABC):
    name = ""

    @abstractmethod
    def translate(self, text: str, from_lang: str = "auto", to_lang: str = "zh") -> str:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass
