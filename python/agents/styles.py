"""
Estratégias de estilo para o agente.

Classes:
- StyleStrategy: interface para estratégias de estilo.
- Conservador, Moderado, Agressivo: estratégias concretas.
"""

from abc import ABC, abstractmethod
import random
from types import MappingProxyType
from typing import ClassVar

from .profile import Profile


class StyleStrategy(ABC):
    @property
    @abstractmethod
    def RANGES(self) -> MappingProxyType: ...

    def draw_profile(self, rng: random.Random) -> Profile:
        """
        Desenha um perfil para este estilo.
        Args:
            rng: gerador de números aleatórios, para permitir reprodutibilidade.
        Returns:
            Profile: perfil de comportamento do agente.
        """
        return Profile(**{name: rng.randint(low, high) for name, (low, high) in self.RANGES.items()})


class Conservador(StyleStrategy):
    RANGES = MappingProxyType({
        "buy_bias_bps": (4_000, 6_000),
        "max_lot": (1, 10),
        "interval_rounds": (5, 10),
        "price_margin_bps": (10, 100),
        })


class Moderado(StyleStrategy):
    RANGES = MappingProxyType({
        "buy_bias_bps": (3_500, 6_500),
        "max_lot": (5, 30),
        "interval_rounds": (2, 5),
        "price_margin_bps": (50, 300),
    })


class Agressivo(StyleStrategy):
    RANGES = MappingProxyType({
        "buy_bias_bps": (2_000, 8_000),
        "max_lot": (20, 100),
        "interval_rounds": (1, 2),
        "price_margin_bps": (200, 1_000),
    })


class StyleRegistry:
    _STRATEGIES: ClassVar = {
        "conservador": Conservador(),
        "moderado": Moderado(),
        "agressivo": Agressivo(),
        }

    @classmethod
    def resolve(cls, name: str) -> StyleStrategy:
        if name not in cls._STRATEGIES:
            valid = ", ".join(cls._STRATEGIES)
            raise ValueError(f"estilo desconhecido: '{name}' (válidos: {valid})")
        return cls._STRATEGIES[name]

    @classmethod
    def names(cls) -> list[str]:
        return list(cls._STRATEGIES)