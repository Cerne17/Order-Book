"""
Contexto de mercado visto pelos agentes (em desenvolvimento).

Classes:
- MarketContext: estado do mercado em uma rodada.
- AgentView: visão do agente sobre si mesmo (saldo, posição).
- Suggestion: ordem sugerida pelo agente.
"""

from dataclasses import dataclass
from typing import Optional

from .validation import FieldReader, require_list, require_unique, Side
from .profile import Profile

@dataclass(frozen=True)
class MarketContext:
    """Estado do mercado no início da rodada, como o C++ enviou."""

    round: int
    ticker: str
    reference_price_minor: int
    last_price_minor: Optional[int]
    tick_size_minor: int
    best_bid_minor: Optional[int]
    best_ask_minor: Optional[int]

    @classmethod
    def from_dict(cls, data, where="context") -> "MarketContext":
        reader = FieldReader(data, where)
        return cls(
            round=reader.positive("round"),
            ticker=reader.non_empty_str("ticker"),
            reference_price_minor=reader.positive("reference_price_minor"),
            last_price_minor=reader.optional_positive("last_price_minor"),
            tick_size_minor=reader.positive("tick_size_minor"),
            best_bid_minor=reader.optional_positive("best_bid_minor"),
            best_ask_minor=reader.optional_positive("best_ask_minor"),
        )

    @property
    def anchor_minor(self) -> int:
        # Âncora de preço: último negócio; sem negócios, a referência.
        if self.last_price_minor is not None:
            return self.last_price_minor
        return self.reference_price_minor

@dataclass(frozen=True)
class AgentView:
    agent_id: int
    profile: Profile
    cash_free_minor: int
    shares_free: int

    @classmethod
    def from_dict(cls, data, where="view") -> "AgentView":
        reader = FieldReader(data, where)
        return cls(
            agent_id=reader.integer("agent_id"),
            profile=Profile.from_dict(reader.dict_("profile"),reader.path("profile")),
            cash_free_minor=reader.non_negative("cash_free_minor"),
            shares_free=reader.non_negative("shares_free"),
        )

    @classmethod
    def parse_list(cls, items: list) -> list["AgentView"]:
        require_list(items, "items")
        views = [cls.from_dict(item, f"agents[{index}]") for index, item in enumerate(items)]
        require_unique([view.agent_id for view in views], "agent_id")
        return views

    def acts_on(self, round_number: int) -> bool:
        return (round_number + self.agent_id) % self.profile.interval_rounds == 0

    def max_qty(self, side: Side, price_minor: int) -> int:
        if side == Side.BUY:
            return min(self.profile.max_lot, self.cash_free_minor // price_minor)
        if side == Side.SELL:
            return min(self.profile.max_lot, self.shares_free)


@dataclass(frozen=True)
class Suggestion:
    agent_id: int
    side: Side
    qty: int
    price_minor: int

    def to_dict(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "side": self.side.value,
            "qty": self.qty,
            "price_minor": self.price_minor,
        }