"""
Perfil de comportamento de um agente.

O `Profile` é imutável e sempre válido: qualquer instância respeita as faixas
de `Profile.LIMITS`. Pode ser criado a partir de um dict (vindo do C++),
customizado com `with_overrides` e serializado de volta com `to_dict`.

Classes:
- Profile: parâmetros de comportamento (viés de compra, lote, intervalo e margem).
"""

from dataclasses import dataclass, replace
from types import MappingProxyType
from typing import ClassVar

from .validation import FieldReader


@dataclass(frozen=True)
class Profile:
    """Parâmetros de comportamento de um agente. Toda instância é válida."""

    # ClassVar: variavel de classe, não de instância. Não é incluída no __init__ nem na comparação.
    # MappingProxyType: dicionário imutável (readonly), para evitar que LIMITS seja alterado em tempo de execução.
    LIMITS: ClassVar = MappingProxyType({
        # buy_bias_bps: diferença percentual entre preço de compra e preço de venda, em bps (0.01%)
        "buy_bias_bps": (0, 10_000),
        # max_lot: tamanho máximo do lote de ordens
        "max_lot": (1, 100),
        # interval_rounds: número de rodadas entre ordens
        "interval_rounds": (1, 100),
        # price_margin_bps: margem de preço em bps (0.01%)
        "price_margin_bps": (0, 1_000),
    })

    buy_bias_bps: int
    max_lot: int
    interval_rounds: int
    price_margin_bps: int

    def __post_init__(self) -> None:
        """
        Valida tipo e faixa de todos os campos.
        Raises:
            TypeError: se algum campo não for int.
            ValueError: se algum campo estiver fora de `LIMITS`.
        """
        for name, (low, high) in self.LIMITS.items():
            value = FieldReader.require_int(getattr(self, name), name)
            if not low <= value <= high:
                raise ValueError(f"'{name}' fora da faixa [{low}, {high}]: {value}")

    @classmethod
    def from_dict(cls, data: dict, where: str = "profile") -> "Profile":
        """
        Cria um perfil a partir de um dict.
        Args:
            data: dict com todas as chaves de `LIMITS`.
            where: caminho do dict, usado nas mensagens de erro.
        Returns:
            Profile: perfil validado.
        Raises:
            TypeError: se `data` não for dict ou algum valor não for int.
            ValueError: se faltar chave ou valor estiver fora da faixa.
        """
        reader = FieldReader(data, where)
        return cls(**{name: reader.int_in(name, low, high) for name, (low, high) in cls.LIMITS.items()})

    def with_overrides(self, overrides: dict) -> "Profile":
        """
        Cria uma cópia do perfil com alguns campos substituídos.
        Args:
            overrides: nome do campo -> novo valor. Pode ser parcial.
        Returns:
            Profile: novo perfil (o original não é alterado).
        Raises:
            TypeError: se `overrides` não for dict.
            ValueError: se houver campo desconhecido ou valor fora da faixa.
        """
        if not isinstance(overrides, dict):
            raise TypeError(f"'overrides' deve ser dict, recebeu {type(overrides).__name__}")
        
        unknown = [key for key in overrides if key not in self.LIMITS]
        if unknown:
            valid = ", ".join(self.LIMITS)
            raise ValueError(f"ajuste desconhecido: {unknown} (válidos: {valid})")    
        return replace(self, **overrides)

    def to_dict(self) -> dict:
        """
        Serializa o perfil.
        Returns:
            dict: nome do campo -> valor, para devolver ao C++.
        """
        return {name: getattr(self, name) for name in self.LIMITS}