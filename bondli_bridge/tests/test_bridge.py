"""
test_bridge.py — Integration tests for the Bondli cognitive bridge.

Tests the full cognitive cycle: perceive → decide → risk check →
meta-evaluate → intervene → output.

Run with:
    python -m pytest bondli_bridge/tests/test_bridge.py -v
    # or without pytest:
    python bondli_bridge/tests/test_bridge.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))

import unittest
import time

from bondli_bridge.config import BridgeConfig
from bondli_bridge.engine import TradingEngine
from bondli_bridge.market_world import MarketWorldModel, TokenEntity
from bondli_bridge.trading_self import TradingSelfModel
from bondli_bridge.trading_meta import TradingMetaCognitive
from bondli_bridge.positions import PositionTracker, Position, TradeOutcome
from bondli_bridge.risk import RiskManager
from bondli_bridge.decisions import Decision, Action, DecisionLog


def make_token(mint="mint123", score=0.75, **kwargs):
    """Helper to create test token data."""
    defaults = {
        "mint": mint,
        "name": "TestToken",
        "symbol": "TEST",
        "source": "pump",
        "score": score,
        "velocity": 0.03,
        "acceleration": 0.01,
        "rug_signals": 0,
        "rug_details": [],
        "holder_count": 50,
        "top_holder_pct": 0.15,
        "liquidity_sol": 20.0,
        "mcap_sol": 100.0,
        "volume_5m": 5.0,
        "buy_pressure": 0.65,
        "smart_money_in": False,
        "dev_wallet": "devwallet123",
        "is_graduated": False,
        "price_sol": 0.001,
    }
    defaults.update(kwargs)
    return defaults


class TestConfig(unittest.TestCase):
    """Test configuration."""

    def test_default_config(self):
        config = BridgeConfig()
        self.assertEqual(config.risk.max_concurrent_positions, 5)
        self.assertEqual(config.scoring.min_score_to_ape, 0.65)
        self.assertIn("momentum", config.strategy.strategies)

    def test_config_to_dict(self):
        config = BridgeConfig()
        d = config.to_dict()
        self.assertIn("risk", d)
        self.assertIn("scoring", d)
        self.assertIn("strategy", d)


class TestMarketWorldModel(unittest.TestCase):
    """Test Level 0: Market perception."""

    def setUp(self):
        self.world = MarketWorldModel()

    def test_ingest_token(self):
        token_data = make_token()
        event = self.world.ingest_token("mint123", token_data)
        self.assertEqual(event.event_type.value, "perception")
        self.assertIn("mint123", self.world.tokens)

    def test_token_update(self):
        self.world.ingest_token("mint123", make_token(score=0.5))
        self.world.ingest_token("mint123", make_token(score=0.8))
        token = self.world.get_token("mint123")
        self.assertEqual(token.score, 0.8)
        self.assertEqual(len(token.score_history), 1)

    def test_token_salience(self):
        # High score + smart money should have high salience
        event = self.world.ingest_token("good", make_token(
            mint="good", score=0.9, smart_money_in=True))
        self.assertGreater(event.salience, 0.8)

        # Low score + rug signals should have low salience
        event = self.world.ingest_token("bad", make_token(
            mint="bad", score=0.2, rug_signals=3))
        self.assertLess(event.salience, 0.3)

    def test_regime_update(self):
        self.world.update_regime({
            "regime": "bull",
            "confidence": 0.8,
            "bull_score": 0.8,
        })
        self.assertEqual(self.world.get_regime(), "bull")

    def test_auto_beliefs_rug(self):
        self.world.ingest_token("rug", make_token(
            mint="rug", rug_signals=4,
            rug_details=["dev_dump", "wash_trading", "sybil", "staircase"]))
        beliefs = list(self.world.beliefs.values())
        rug_beliefs = [b for b in beliefs if "rug" in b.content.lower()]
        self.assertGreater(len(rug_beliefs), 0)

    def test_smart_wallet_ingest(self):
        event = self.world.ingest_smart_wallet("wallet123", {
            "win_rate": 0.8,
            "avg_profit": 2.5,
            "total_trades": 50,
            "active_tokens": [],
        })
        self.assertIn("wallet123", self.world.smart_wallets)

    def test_prune_stale(self):
        self.world.ingest_token("old", make_token(mint="old"))
        # Manually age it
        self.world.tokens["old"].last_updated = time.time() - 700
        self.world.prune_stale_tokens(max_age_seconds=600)
        self.assertNotIn("old", self.world.tokens)

    def test_self_entity_exists(self):
        self_entity = self.world.get_self()
        self.assertEqual(self_entity.properties["type"], "trading_agent")

    def test_market_summary(self):
        self.world.ingest_token("a", make_token(mint="a", score=0.7))
        self.world.ingest_token("b", make_token(mint="b", score=0.3))
        summary = self.world.get_market_summary()
        self.assertEqual(summary["token_count"], 2)
        self.assertAlmostEqual(summary["avg_score"], 0.5, places=1)


class TestPositionTracker(unittest.TestCase):
    """Test position management."""

    def setUp(self):
        self.tracker = PositionTracker()

    def test_open_close(self):
        pos = self.tracker.open_position(
            "mint1", "TEST", 0.001, 0.5, "momentum", 0.8, [])
        self.assertEqual(self.tracker.open_count, 1)
        self.tracker.close_position("mint1", 0.002, "take_profit")
        self.assertEqual(self.tracker.open_count, 0)
        self.assertEqual(len(self.tracker.closed_positions), 1)

    def test_pnl_calculation(self):
        pos = self.tracker.open_position(
            "mint1", "TEST", 0.001, 1.0, "momentum", 0.8, [])
        self.tracker.close_position("mint1", 0.002, "tp")
        closed = self.tracker.closed_positions[0]
        self.assertGreater(closed.pnl_sol, 0)
        self.assertEqual(closed.outcome, TradeOutcome.WIN)

    def test_loss_tracking(self):
        self.tracker.open_position(
            "mint1", "TEST", 0.002, 1.0, "momentum", 0.8, [])
        self.tracker.close_position("mint1", 0.001, "stop_loss")
        closed = self.tracker.closed_positions[0]
        self.assertLess(closed.pnl_sol, 0)
        self.assertEqual(closed.outcome, TradeOutcome.LOSS)

    def test_stats(self):
        # 2 wins, 1 loss
        for i, (entry, exit) in enumerate([(0.001, 0.002), (0.001, 0.003), (0.003, 0.001)]):
            self.tracker.open_position(
                f"m{i}", "T", entry, 1.0, "momentum", 0.8, [])
            self.tracker.close_position(f"m{i}", exit, "test")
        stats = self.tracker.get_stats()
        self.assertEqual(stats["total_trades"], 3)
        self.assertEqual(stats["wins"], 2)
        self.assertEqual(stats["losses"], 1)

    def test_partial_exit(self):
        self.tracker.open_position(
            "mint1", "TEST", 0.001, 1.0, "momentum", 0.8, [])
        self.tracker.partial_exit("mint1", 0.33, 0.002, "tp1")
        pos = self.tracker.get_position("mint1")
        self.assertEqual(pos.status.value, "partial_exit")
        self.assertEqual(len(pos.partial_exits), 1)

    def test_exposure(self):
        self.tracker.open_position("m1", "T", 0.001, 0.5, "m", 0.8, [])
        self.tracker.open_position("m2", "T", 0.001, 0.3, "m", 0.8, [])
        self.assertAlmostEqual(self.tracker.total_exposure_sol, 0.8)

    def test_strategy_stats(self):
        self.tracker.open_position("m1", "T", 0.001, 1.0, "momentum", 0.8, [])
        self.tracker.close_position("m1", 0.002, "tp")
        self.tracker.open_position("m2", "T", 0.001, 1.0, "snipe", 0.8, [])
        self.tracker.close_position("m2", 0.0005, "sl")
        stats = self.tracker.get_strategy_stats()
        self.assertIn("momentum", stats)
        self.assertIn("snipe", stats)
        self.assertEqual(stats["momentum"]["wins"], 1)
        self.assertEqual(stats["snipe"]["losses"], 1)


class TestTradingSelfModel(unittest.TestCase):
    """Test Level 1: Trading decisions."""

    def setUp(self):
        self.config = BridgeConfig()
        self.self_model = TradingSelfModel(self.config)

    def test_ape_good_token(self):
        token = make_token(score=0.8, velocity=0.05, liquidity_sol=50)
        market = {"regime": "bull"}
        result = self.self_model.evaluate_token(token, market)
        self.assertEqual(result["action"], "APE")
        self.assertGreater(result["confidence"], 0.5)
        self.assertIn("position_size_sol", result)

    def test_skip_bad_score(self):
        token = make_token(score=0.3)
        result = self.self_model.evaluate_token(token, {"regime": "unknown"})
        self.assertIn(result["action"], ("SKIP", "WATCH"))

    def test_skip_rug(self):
        token = make_token(rug_signals=4)
        result = self.self_model.evaluate_token(token, {"regime": "unknown"})
        self.assertEqual(result["action"], "SKIP")
        self.assertIn("rug_detected", result["risk_factors"])

    def test_skip_low_liquidity(self):
        token = make_token(score=0.9, liquidity_sol=1.0)
        result = self.self_model.evaluate_token(token, {"regime": "unknown"})
        self.assertEqual(result["action"], "SKIP")

    def test_skip_max_positions(self):
        for i in range(5):
            self.self_model.positions.open_position(
                f"m{i}", "T", 0.001, 0.5, "m", 0.8, [])
        token = make_token(score=0.9)
        result = self.self_model.evaluate_token(token, {"regime": "unknown"})
        self.assertEqual(result["action"], "SKIP")

    def test_exit_on_score_drop(self):
        self.self_model.positions.open_position(
            "mint1", "TEST", 0.001, 0.5, "momentum", 0.8, [])
        token = make_token(score=0.2, velocity=-0.1, acceleration=-0.05)
        result = self.self_model.evaluate_position(
            "mint1", token, {"regime": "unknown"})
        self.assertEqual(result["action"], "EXIT")

    def test_hold_good_position(self):
        self.self_model.positions.open_position(
            "mint1", "TEST", 0.001, 0.5, "momentum", 0.8, [])
        self.self_model.positions.update_position("mint1", price_sol=0.0015)
        token = make_token(score=0.75, velocity=0.02)
        result = self.self_model.evaluate_position(
            "mint1", token, {"regime": "unknown"})
        self.assertEqual(result["action"], "HOLD")

    def test_strategy_switch(self):
        self.self_model.switch_strategy("snipe", "test")
        self.assertEqual(self.self_model.active_strategy, "snipe")

    def test_pause_after_losses(self):
        # Need actual closed positions for consecutive loss tracking
        for i in range(4):
            self.self_model.positions.open_position(
                f"m{i}", "T", 0.002, 0.5, "momentum", 0.8, [])
            self.self_model.positions.close_position(f"m{i}", 0.001, "sl")
            self.self_model.record_trade_outcome(
                f"m{i}", -0.1, False, "unknown")
        self.assertTrue(self.self_model._paused)

    def test_smart_money_boost(self):
        # Marginal score without smart money
        token1 = make_token(score=0.6, smart_money_in=False, liquidity_sol=50)
        r1 = self.self_model.evaluate_token(token1, {"regime": "unknown"})

        # Reset
        self.self_model = TradingSelfModel(self.config)

        # Same score with smart money
        token2 = make_token(score=0.6, smart_money_in=True, liquidity_sol=50)
        r2 = self.self_model.evaluate_token(token2, {"regime": "unknown"})

        self.assertGreaterEqual(r2["confidence"], r1["confidence"])


class TestTradingMetaCognitive(unittest.TestCase):
    """Test Level 2: Meta-cognitive oversight."""

    def setUp(self):
        self.config = BridgeConfig()
        self.self_model = TradingSelfModel(self.config)
        self.world = MarketWorldModel(self.config)
        self.meta = TradingMetaCognitive(self.config)

    def test_overconfidence_detection(self):
        # Inflate confidence without supporting win rate
        self.self_model.confidence_states["strategy"] = 0.9
        # Record some losses
        for i in range(6):
            self.self_model.positions.open_position(
                f"m{i}", "T", 0.001, 0.5, "momentum", 0.8, [])
            self.self_model.positions.close_position(f"m{i}", 0.0005, "sl")

        eval_result = self.meta.evaluate_trading(self.self_model, self.world)
        blind_spots = eval_result.get("blind_spots_triggered", [])
        overconf = [b for b in blind_spots if b.get("blind_spot") == "overconfidence"]
        self.assertGreater(len(overconf), 0)

    def test_strategy_switch_intervention(self):
        # Make momentum strategy very ineffective
        strat = self.self_model.strategies["momentum"]
        for _ in range(25):
            strat.record_trade(False, -0.1, "unknown")

        eval_result = self.meta.evaluate_trading(self.self_model, self.world)
        interventions = eval_result.get("recommended_interventions", [])
        switches = [i for i in interventions if i.get("type") == "switch_strategy"]
        self.assertGreater(len(switches), 0)

    def test_restructure_strategy_switch(self):
        self.assertEqual(self.self_model.active_strategy, "momentum")
        crossing = self.meta.restructure_trading(self.self_model, {
            "type": "switch_strategy",
            "to_strategy": "snipe",
            "reason": "test",
        })
        self.assertEqual(self.self_model.active_strategy, "snipe")
        self.assertTrue(crossing.is_strange)

    def test_restructure_pause(self):
        crossing = self.meta.restructure_trading(self.self_model, {
            "type": "pause_trading",
            "reason": "test pause",
        })
        self.assertTrue(self.self_model._paused)
        self.assertTrue(crossing.is_strange)

    def test_restructure_confidence(self):
        old = self.self_model.confidence_states["strategy"]
        self.meta.restructure_trading(self.self_model, {
            "type": "reduce_confidence",
            "domain": "strategy",
            "magnitude": 0.2,
        })
        self.assertLess(
            self.self_model.confidence_states["strategy"], old)


class TestRiskManager(unittest.TestCase):
    """Test risk management."""

    def setUp(self):
        self.config = BridgeConfig()
        self.positions = PositionTracker()
        self.risk = RiskManager(self.config, self.positions)

    def test_allow_good_entry(self):
        token = make_token(liquidity_sol=50)
        allowed, violations = self.risk.check_entry("mint1", 0.5, token)
        self.assertTrue(allowed)
        self.assertEqual(len([v for v in violations if v.severity == "hard"]), 0)

    def test_block_max_positions(self):
        for i in range(5):
            self.positions.open_position(
                f"m{i}", "T", 0.001, 0.5, "m", 0.8, [])
        token = make_token()
        allowed, violations = self.risk.check_entry("new", 0.5, token)
        self.assertFalse(allowed)

    def test_block_max_exposure(self):
        self.positions.open_position("m1", "T", 0.001, 4.5, "m", 0.8, [])
        token = make_token()
        allowed, violations = self.risk.check_entry("new", 1.0, token)
        self.assertFalse(allowed)

    def test_block_rug(self):
        token = make_token(rug_signals=4)
        allowed, violations = self.risk.check_entry("rug", 0.5, token)
        self.assertFalse(allowed)

    def test_block_low_liquidity(self):
        token = make_token(liquidity_sol=2.0)
        allowed, violations = self.risk.check_entry("low", 0.5, token)
        self.assertFalse(allowed)

    def test_circuit_breaker(self):
        self.risk.trigger_circuit_breaker("test", 60)
        token = make_token()
        allowed, violations = self.risk.check_entry("any", 0.5, token)
        self.assertFalse(allowed)

    def test_duplicate_position(self):
        self.positions.open_position("m1", "T", 0.001, 0.5, "m", 0.8, [])
        token = make_token()
        allowed, violations = self.risk.check_entry("m1", 0.5, token)
        self.assertFalse(allowed)

    def test_exit_allowed(self):
        self.positions.open_position("m1", "T", 0.001, 0.5, "m", 0.8, [])
        allowed, violations = self.risk.check_exit("m1", "test")
        self.assertTrue(allowed)

    def test_exit_no_position(self):
        allowed, violations = self.risk.check_exit("none", "test")
        self.assertFalse(allowed)


class TestTradingEngine(unittest.TestCase):
    """Test the full cognitive cycle."""

    def setUp(self):
        self.config = BridgeConfig()
        self.engine = TradingEngine(self.config)

    def test_evaluate_good_token(self):
        decision = self.engine.evaluate_token(
            make_token(score=0.85, liquidity_sol=50))
        self.assertEqual(decision.action, Action.APE)
        self.assertGreater(decision.position_size_sol, 0)
        self.assertGreater(len(decision.reasoning), 0)

    def test_evaluate_bad_token(self):
        decision = self.engine.evaluate_token(
            make_token(score=0.2, rug_signals=3))
        self.assertIn(decision.action, (Action.SKIP, Action.WATCH))

    def test_full_trade_cycle(self):
        # 1. Evaluate → APE
        decision = self.engine.evaluate_token(
            make_token(mint="cycle1", score=0.85, liquidity_sol=50))
        self.assertEqual(decision.action, Action.APE)

        # 2. Record entry
        self.engine.record_entry(
            "cycle1", "TEST", 0.001, 0.5, 0.85, ["test entry"])
        self.assertTrue(self.engine.self_model.positions.has_position("cycle1"))

        # 3. Evaluate position → HOLD (price up 20%, below first TP at 50%)
        hold_decision = self.engine.evaluate_position(
            "cycle1", make_token(mint="cycle1", score=0.8, price_sol=0.0012))
        self.assertEqual(hold_decision.action, Action.HOLD)

        # 4. Record exit
        result = self.engine.record_exit("cycle1", 0.002, "take_profit")
        self.assertIsNotNone(result)
        self.assertGreater(result["pnl_sol"], 0)

    def test_strange_loop_on_exit(self):
        # Record some losses to trigger meta-cognitive
        for i in range(4):
            self.engine.record_entry(
                f"sl{i}", "T", 0.002, 0.5, 0.7, [])
            self.engine.record_exit(f"sl{i}", 0.001, "stop_loss")

        # Should have strange loops from meta-cognitive interventions
        self.assertGreater(self.engine.total_strange_loops, 0)

    def test_regime_affects_decisions(self):
        self.engine.update_regime({
            "regime": "bear",
            "confidence": 0.8,
            "bear_score": 0.8,
        })
        state = self.engine.get_state()
        self.assertEqual(
            state["world_model"]["market"]["regime"], "bear")

    def test_metrics(self):
        metrics = self.engine.get_metrics()
        self.assertIn("hofstadter_index", metrics)
        self.assertIn("total_trades", metrics)
        self.assertIn("win_rate", metrics)
        self.assertIn("active_strategy", metrics)

    def test_decision_log(self):
        self.engine.evaluate_token(make_token(score=0.85, liquidity_sol=50))
        self.engine.evaluate_token(make_token(mint="m2", score=0.3))
        stats = self.engine.decision_log.get_stats()
        self.assertEqual(stats["total_decisions"], 2)

    def test_config_update(self):
        self.engine.update_config({
            "risk": {"max_position_size_sol": 2.0},
            "scoring": {"min_score_to_ape": 0.5},
        })
        self.assertEqual(self.engine.config.risk.max_position_size_sol, 2.0)
        self.assertEqual(self.engine.config.scoring.min_score_to_ape, 0.5)

    def test_smart_wallet_integration(self):
        self.engine.ingest_smart_wallet("wallet1", {
            "win_rate": 0.9,
            "avg_profit": 3.0,
            "total_trades": 100,
            "active_tokens": [],
        })
        state = self.engine.get_state()
        self.assertGreater(
            state["world_model"]["entity_count"], 2)  # SELF + REGIME + wallet

    def test_multiple_cycles_build_strange_loops(self):
        for i in range(10):
            self.engine.evaluate_token(
                make_token(mint=f"tok{i}", score=0.7 + i * 0.02,
                           liquidity_sol=50))
        self.assertGreater(self.engine.cycle_count, 0)
        state = self.engine.get_state()
        self.assertGreater(state["engine"]["level_crossings"], 0)


class TestDecisions(unittest.TestCase):
    """Test decision output layer."""

    def test_decision_serialization(self):
        d = Decision(
            action=Action.APE,
            mint="mint123",
            confidence=0.85,
            reasoning=["Good score", "Smart money"],
            position_size_sol=0.5,
            strategy="momentum",
        )
        result = d.to_dict()
        self.assertEqual(result["action"], "APE")
        self.assertEqual(result["position_size_sol"], 0.5)
        self.assertIn("reasoning", result)

    def test_decision_log(self):
        log = DecisionLog(max_size=5)
        for i in range(10):
            log.record(Decision(
                action=Action.SKIP,
                mint=f"m{i}",
                confidence=0.3,
                reasoning=["test"],
            ))
        self.assertEqual(len(log.decisions), 5)  # Pruned to max_size

    def test_decision_properties(self):
        ape = Decision(action=Action.APE, mint="m", confidence=0.8, reasoning=[])
        self.assertTrue(ape.is_entry)
        self.assertFalse(ape.is_exit)

        exit_d = Decision(action=Action.EXIT, mint="m", confidence=0.8, reasoning=[])
        self.assertTrue(exit_d.is_exit)

        skip = Decision(action=Action.SKIP, mint="m", confidence=0.8, reasoning=[])
        self.assertTrue(skip.is_pass)


# ================================================================
# RUN
# ================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("BRAD Bondli Bridge — Integration Tests")
    print("=" * 60)

    # Run with verbose output
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print()
    if result.wasSuccessful():
        print(f"ALL {result.testsRun} TESTS PASSED")
    else:
        print(f"FAILURES: {len(result.failures)}")
        print(f"ERRORS: {len(result.errors)}")

    sys.exit(0 if result.wasSuccessful() else 1)
