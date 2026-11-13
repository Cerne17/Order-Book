import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "python"))

from agents import AgentView, MarketContext, Side, Suggestion

PROFILE = {"buy_bias_bps": 5000, "max_lot": 10, "interval_rounds": 2, "price_margin_bps": 100}
CONTEXT = {"round": 4, "ticker": "PETR4", "reference_price_minor": 3000, "last_price_minor": None,
           "tick_size_minor": 1, "best_bid_minor": None, "best_ask_minor": 3010}


def view_dict(agent_id=2, cash=10000, shares=1):
    return {"agent_id": agent_id, "profile": PROFILE, "cash_free_minor": cash, "shares_free": shares}


class MarketContextTest(unittest.TestCase):
    def test_anchor_uses_reference_without_trades(self):
        self.assertEqual(MarketContext.from_dict(CONTEXT).anchor_minor, 3000)

    def test_anchor_uses_last_price(self):
        ctx = MarketContext.from_dict({**CONTEXT, "last_price_minor": 3050})
        self.assertEqual(ctx.anchor_minor, 3050)


class AgentViewTest(unittest.TestCase):
    def setUp(self):
        self.view = AgentView.parse_list([view_dict()])[0]

    def test_acts_on(self):
        self.assertTrue(self.view.acts_on(4))
        self.assertFalse(self.view.acts_on(5))

    def test_max_qty(self):
        self.assertEqual(self.view.max_qty(Side.BUY, 3010), 3)
        self.assertEqual(self.view.max_qty(Side.SELL, 3010), 1)

    def test_empty_balance_accepted(self):
        view = AgentView.from_dict(view_dict(cash=0, shares=0))
        self.assertEqual(view.max_qty(Side.BUY, 3010), 0)

    def test_duplicate_agent_id_rejected(self):
        with self.assertRaises(ValueError):
            AgentView.parse_list([view_dict(cash=0, shares=0)] * 2)

    def test_non_list_rejected(self):
        with self.assertRaises(TypeError):
            AgentView.parse_list({})


class SuggestionTest(unittest.TestCase):
    def test_to_dict(self):
        self.assertEqual(Suggestion(2, Side.SELL, 1, 3010).to_dict(),
                         {"agent_id": 2, "side": "SELL", "qty": 1, "price_minor": 3010})


if __name__ == "__main__":
    unittest.main()
