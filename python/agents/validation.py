"""
Validação de dados recebidos do C++.

Os dicts vindos do gerenciador C++ não têm tipos garantidos. Este módulo
centraliza a checagem de presença, tipo e faixa, com mensagens de erro que
indicam o caminho do campo (ex.: "profile.max_lot").

Classes:
- Side: lado de uma ordem (BUY ou SELL).
- FieldReader: lê e valida campos de um dict.
"""

from enum import Enum
from typing import Optional


class Side(str, Enum):
    """Lado de uma ordem no livro."""

    BUY = "BUY"
    SELL = "SELL"


class FieldReader:
    """Lê campos de um dict recebido do C++, validando tipo, faixa e presença."""

    def __init__(self, data: dict, where: str):
        """
        Args:
            data: dict a ser lido.
            where: caminho do dict, usado nas mensagens de erro.
        Raises:
            TypeError: se `data` não for dict.
        """
        if not isinstance(data, dict):
            raise TypeError(f"'{where}' deve ser dict, recebeu {type(data).__name__}")
        self._data = data
        self._where = where

    @staticmethod
    def require_int(value, name: str) -> int:
        """
        Garante que o valor é int (bool é rejeitado).
        Args:
            value: valor a checar.
            name: nome do campo, usado na mensagem de erro.
        Returns:
            int: o próprio valor.
        Raises:
            TypeError: se não for int.
        """
        # bool é subclasse de int: precisa ser rejeitado antes.
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"'{name}' deve ser int, recebeu {type(value).__name__}")
        return value

    def path(self, key: str) -> str:
        """Retorna o caminho completo da chave (ex.: "profile.max_lot")."""
        return f"{self._where}.{key}"

    def _get(self, key: str):
        """Retorna o valor da chave. Levanta ValueError se ela não existir."""
        if key not in self._data:
            raise ValueError(f"chave obrigatória ausente em {self._where}: '{key}'")
        return self._data[key]

    def _int_at_least(self, key: str, minimum: int) -> int:
        """Lê um int >= `minimum`. Levanta TypeError ou ValueError se inválido."""
        value = self.require_int(self._get(key), self.path(key))
        if value < minimum:
            raise ValueError(f"'{self.path(key)}' deve ser >= {minimum}: {value}")
        return value

    def int_in(self, key: str, low: int, high: int) -> int:
        """
        Lê um int dentro de uma faixa.
        Args:
            key: chave do campo.
            low: mínimo, inclusivo.
            high: máximo, inclusivo.
        Returns:
            int: valor validado.
        Raises:
            TypeError: se não for int.
            ValueError: se a chave faltar ou o valor estiver fora da faixa.
        """
        value = self.require_int(self._get(key), self.path(key))
        if not low <= value <= high:
            raise ValueError(f"'{self.path(key)}' fora da faixa [{low}, {high}]: {value}")
        return value

    def positive(self, key: str) -> int:
        """Lê um int >= 1."""
        return self._int_at_least(key, 1)

    def non_negative(self, key: str) -> int:
        """Lê um int >= 0."""
        return self._int_at_least(key, 0)

    def optional_positive(self, key: str) -> Optional[int]:
        """Lê um int >= 1, ou None se o valor for None (a chave ainda é obrigatória)."""
        if self._get(key) is None:
            return None
        return self.positive(key)

    def non_empty_str(self, key: str) -> str:
        """Lê uma str que não seja vazia nem só espaços."""
        value = self._get(key)
        if not isinstance(value, str):
            raise TypeError(f"'{self.path(key)}' deve ser str, recebeu {type(value).__name__}")
        if not value.strip():
            raise ValueError(f"'{self.path(key)}' não pode ser vazia")
        return value

    def dict_(self, key: str) -> dict:
        """Lê um valor que seja dict (útil para estruturas aninhadas)."""
        value = self._get(key)
        if not isinstance(value, dict):
            raise TypeError(f"'{self.path(key)}' deve ser dict, recebeu {type(value).__name__}")
        return value