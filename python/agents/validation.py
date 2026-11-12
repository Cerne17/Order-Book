
from enum import Enum
from typing import Optional


class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class FieldReader:
    """Lê campos de um dict recebido do C++, validando tipo, faixa e presença."""

    def __init__(self, data: dict, where: str):
        if not isinstance(data, dict):
            raise TypeError(f"'{where}' deve ser dict, recebeu {type(data).__name__}")
        self._data = data
        self._where = where

    @staticmethod
    def require_int(value, name: str) -> int:
        # bool é subclasse de int: precisa ser rejeitado antes.
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"'{name}' deve ser int, recebeu {type(value).__name__}")
        return value

    def path(self, key: str) -> str:
        return f"{self._where}.{key}"

    def _get(self, key: str):
        if key not in self._data:
            raise ValueError(f"chave obrigatória ausente em {self._where}: '{key}'")
        return self._data[key]

    def _int_at_least(self, key: str, minimum: int) -> int:
        value = self.require_int(self._get(key), self.path(key))
        if value < minimum:
            raise ValueError(f"'{self.path(key)}' deve ser >= {minimum}: {value}")
        return value

    def int_in(self, key: str, low: int, high: int) -> int:
        value = self.require_int(self._get(key), self.path(key))
        if not low <= value <= high:
            raise ValueError(f"'{self.path(key)}' fora da faixa [{low}, {high}]: {value}")
        return value

    def positive(self, key: str) -> int:
        return self._int_at_least(key, 1)

    def non_negative(self, key: str) -> int:
        return self._int_at_least(key, 0)

    def optional_positive(self, key: str) -> Optional[int]:
        if self._get(key) is None:
            return None
        return self.positive(key)

    def non_empty_str(self, key: str) -> str:
        value = self._get(key)
        if not isinstance(value, str):
            raise TypeError(f"'{self.path(key)}' deve ser str, recebeu {type(value).__name__}")
        if not value.strip():
            raise ValueError(f"'{self.path(key)}' não pode ser vazia")
        return value

    def dict_(self, key: str) -> dict:
        value = self._get(key)
        if not isinstance(value, dict):
            raise TypeError(f"'{self.path(key)}' deve ser dict, recebeu {type(value).__name__}")
        return value