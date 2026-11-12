"""
Estratégias de estilo dos agentes (padrão Strategy).

Cada estilo define faixas (min, max) para cada parâmetro do `Profile`. Ao criar
um agente, um valor inteiro é sorteado dentro de cada faixa, usando um gerador
de números aleatórios com semente, o que torna a simulação reprodutível.

Classes:
- StyleStrategy: interface das estratégias; implementa `draw_profile`.
- Conservador: lotes pequenos, ordens espaçadas e margens de preço estreitas.
- Moderado: perfil intermediário entre Conservador e Agressivo.
- Agressivo: lotes grandes, ordens frequentes e margens de preço largas.
- StyleRegistry: resolve o nome de um estilo (str) para sua estratégia.

Exemplo:
    strategy = StyleRegistry.resolve("moderado")
    profile = strategy.draw_profile(random.Random(42))
"""

from abc import ABC, abstractmethod
import random
from types import MappingProxyType
from typing import ClassVar

from .profile import Profile


class StyleStrategy(ABC):
    """Interface de um estilo de agente: define as faixas de cada parâmetro do perfil."""

    @property
    @abstractmethod
    def RANGES(self) -> MappingProxyType:
        """
        Faixas de sorteio do estilo.
        Returns:
            MappingProxyType: nome do parâmetro -> (mínimo, máximo), ambos inclusivos.
                Deve ter as mesmas chaves de `Profile.LIMITS`.
        """
        ...

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
    """Estilo cauteloso: lotes pequenos, ordens espaçadas e margens estreitas."""

    RANGES = MappingProxyType({
        "buy_bias_bps": (4_000, 6_000),
        "max_lot": (1, 10),
        "interval_rounds": (5, 10),
        "price_margin_bps": (10, 100),
        })


class Moderado(StyleStrategy):
    """Estilo intermediário entre Conservador e Agressivo."""

    RANGES = MappingProxyType({
        "buy_bias_bps": (3_500, 6_500),
        "max_lot": (5, 30),
        "interval_rounds": (2, 5),
        "price_margin_bps": (50, 300),
    })


class Agressivo(StyleStrategy):
    """Estilo arrojado: lotes grandes, ordens frequentes e margens largas."""

    RANGES = MappingProxyType({
        "buy_bias_bps": (2_000, 8_000),
        "max_lot": (20, 100),
        "interval_rounds": (1, 2),
        "price_margin_bps": (200, 1_000),
    })


class StyleRegistry:
    """Catálogo dos estilos disponíveis, indexados pelo nome em minúsculas."""

    _STRATEGIES: ClassVar = {
        "conservador": Conservador(),
        "moderado": Moderado(),
        "agressivo": Agressivo(),
        }

    @classmethod
    def resolve(cls, name: str) -> StyleStrategy:
        """
        Busca a estratégia correspondente ao nome do estilo.
        Args:
            name: nome do estilo, em minúsculas (ex.: "moderado").
        Returns:
            StyleStrategy: estratégia do estilo.
        Raises:
            ValueError: se o estilo não existir.
        """
        if name not in cls._STRATEGIES:
            valid = ", ".join(cls._STRATEGIES)
            raise ValueError(f"estilo desconhecido: '{name}' (válidos: {valid})")
        return cls._STRATEGIES[name]

    @classmethod
    def names(cls) -> list[str]:
        """
        Lista os estilos disponíveis.
        Returns:
            list[str]: nomes dos estilos registrados.
        """
        return list(cls._STRATEGIES)