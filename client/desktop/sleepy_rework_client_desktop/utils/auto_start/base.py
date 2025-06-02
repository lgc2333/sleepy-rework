import traceback
from abc import ABC, abstractmethod


class BaseAutoStartManager(ABC):
    @staticmethod
    @abstractmethod
    def _is_enabled() -> bool: ...

    @staticmethod
    @abstractmethod
    def _enable() -> bool: ...

    @staticmethod
    @abstractmethod
    def _disable() -> bool: ...

    @classmethod
    def is_enabled(cls) -> bool:
        try:
            return cls._is_enabled()
        except Exception:
            traceback.print_exc()
            return False

    @classmethod
    def enable(cls) -> bool:
        try:
            return cls._enable()
        except Exception:
            traceback.print_exc()
            return False

    @classmethod
    def disable(cls) -> bool:
        try:
            return cls._disable()
        except Exception:
            traceback.print_exc()
            return False
