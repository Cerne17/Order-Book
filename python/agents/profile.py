from copy import replace
from dataclasses import dataclass
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
        for name, (low, high) in self.LIMITS.items():
            value = FieldReader.require_int(getattr(self, name), name)
            if not low <= value <= high:
                raise ValueError(f"'{name}' fora da faixa [{low}, {high}]: {value}")

    @classmethod
    def from_dict(cls, data: dict, where: str = "profile") -> "Profile":
        reader = FieldReader(data, where)
        return cls(**{name: reader.int_in(name, low, high) for name, (low, high) in cls.LIMITS.items()})

    def with_overrides(self, overrides: dict) -> "Profile":
        if not isinstance(overrides, dict):
            raise TypeError(f"'overrides' deve ser dict, recebeu {type(overrides).__name__}")
        
        unknown = [key for key in overrides if key not in self.LIMITS]
        if unknown:
            valid = ", ".join(self.LIMITS)
            raise ValueError(f"ajuste desconhecido: {unknown} (válidos: {valid})")    
        return replace(self, **overrides)

    def to_dict(self) -> dict:
        return {name: getattr(self, name) for name in self.LIMITS}