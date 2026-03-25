"""
engine.py — Brain: Recursive Cognitive Trading Engine

Main orchestrator implementing the three-level strange loop cognitive
cycle for autonomous trading decisions.

Hierarchy:
  Level 0: MarketWorldModel    — Perceptual grounding (tokens, wallets, regime)
  Level 1: TradingSelfModel    — Strategic reasoning (APE/SKIP/EXIT decisions)
  Level 2: TradingMetaCognitive — Meta-cognitive oversight (bias detection,
                                   strategy adaptation, downward causation)

The recursive loop: L2 detects systematic errors in L1 -> restructures L1's
strategy/confidence -> L1 modulates L0's attention weights -> different tokens
receive focus -> L1 produces different decisions -> L2 observes updated
performance -> cycle continues.

Each evaluate_token() call executes one complete cognitive cycle.
Bondli's Node.js backend communicates via the FastAPI server (server.py).
"""

from typing import Dict, List, Optional
from core.structures import (
    CognitiveEvent, CognitiveEventType, ReasoningMode, LevelCrossing
)
from core.global_workspace import GlobalWorkspace
from .market_world import MarketWorldModel
from .trading_self import TradingSelfModel
from .trading_meta import TradingMetaCognitive
from .risk import RiskManager
from .decisions import Decision, Action, DecisionLog
from .positions import TradeOutcome
from .config import BridgeConfig
import time


class TradingEngine:
    """
    The cognitive trading engine.

    Each evaluate_token() call runs a full cognitive cycle:
    1. PERCEIVE — Ingest token data into world model (L0)
    2. DECIDE — Self-model evaluates for APE/SKIP (L1)
    3. RISK CHECK — Hard risk limits enforced
    4. META-EVALUATE — Meta-cognitive checks for blind spots (L2)
    5. INTERVENE — Meta-cognitive restructures self-model if needed (STRANGE LOOP)
    6. OUTPUT — Structured decision returned to Bondli
    """

    def __init__(self, config: BridgeConfig = None):
        self.config = config or BridgeConfig.from_env()

        # Three-level hierarchy
        self.world = MarketWorldModel(self.config)
        self.self_model = TradingSelfModel(self.config)
        self.meta = TradingMetaCognitive(self.config)

        # Supporting systems
        self.workspace = GlobalWorkspace()
        self.risk = RiskManager(self.config, self.self_model.positions)
        self.decision_log = DecisionLog()

        # Register workspace listeners
        self.workspace.register_listener("world", self._world_listener)
        self.workspace.register_listener("self", self._self_listener)

        # Engine state
        self.cycle_count = 0
        self.total_strange_loops = 0
        self._level_crossings: List[LevelCrossing] = []
        self._cognitive_trace: List[Dict] = []
        self._started_at = time.time()

    # ================================================================
    # MAIN API — Called by Bondli
    # ================================================================

    def evaluate_token(self, token_data: Dict) -> Decision:
        """
        Evaluate a token for entry. This is the main endpoint.

        token_data should include (from Bondli's scorer):
            mint, name, symbol, score, velocity, acceleration,
            rug_signals, rug_details, holder_count, top_holder_pct,
            liquidity_sol, mcap_sol, volume_5m, buy_pressure,
            smart_money_in, dev_wallet, source, is_graduated

        Returns a Decision object with action, confidence, and reasoning.
        """
        self.cycle_count += 1
        mint = token_data.get("mint", "unknown")
        trace = self._start_trace(mint, "evaluate")

        # === STEP 1: PERCEIVE (Level 0) ===
        perception_event = self.world.ingest_token(mint, token_data)
        self.workspace.submit(perception_event)
        trace["perception"] = {"salience": perception_event.salience}

        # === STEP 2: DECIDE (Level 1) ===
        market_summary = self.world.get_market_summary()
        evaluation = self.self_model.evaluate_token(token_data, market_summary)
        action_str = evaluation["action"]
        trace["evaluation"] = evaluation

        # === STEP 3: RISK CHECK ===
        risk_violations = []
        if action_str == "APE":
            size = evaluation.get("position_size_sol", 0.0)
            allowed, violations = self.risk.check_entry(mint, size, token_data)
            risk_violations = [v.to_dict() for v in violations]
            if not allowed:
                action_str = "SKIP"
                evaluation["reasoning"].append(
                    "Blocked by risk manager: " +
                    "; ".join(v.details for v in violations if v.severity == "hard")
                )
                trace["risk_blocked"] = True

        # === STEP 4: META-EVALUATE (Level 2) ===
        # Run meta-cognitive every N cycles
        meta_interventions = []
        if self.cycle_count % self.config.cognitive.meta_eval_frequency == 0:
            meta_eval = self.meta.evaluate_trading(self.self_model, self.world)
            meta_interventions = meta_eval.get("recommended_interventions", [])
            trace["meta_eval"] = {
                "blind_spots": meta_eval.get("blind_spots_triggered", []),
                "interventions": len(meta_interventions),
            }

            # Submit meta event to workspace
            meta_event = CognitiveEvent(
                event_type=CognitiveEventType.META_COGNITION,
                content=meta_eval,
                source_level=2,
                salience=0.8,
            )
            self.workspace.submit(meta_event)

        # === STEP 5: INTERVENE (STRANGE LOOP) ===
        for intervention in meta_interventions:
            target = intervention.get("target_level")
            if target == 1:
                crossing = self.meta.restructure_trading(
                    self.self_model, intervention)
                self._level_crossings.append(crossing)
                if crossing.is_strange:
                    self.total_strange_loops += 1
                    trace["strange_loops"] = trace.get("strange_loops", 0) + 1

        # Self-model intervention on world model (L1 → L0)
        self_reflection = self.self_model.reflect_on_self()
        self.workspace.submit(self_reflection)
        trading_state = {
            "trading_state": {
                "active_positions": self.self_model.positions.open_count,
                "total_trades": len(self.self_model.positions.closed_positions),
                "win_rate": self.self_model.positions.get_stats().get("win_rate", 0.0),
                "pnl_sol": self.self_model.positions.get_stats().get("total_pnl_sol", 0.0),
                "strategy": self.self_model.active_strategy,
                "cycle": self.cycle_count,
            },
        }
        crossing = self.self_model.intervene_on_world(self.world, trading_state)
        self._level_crossings.append(crossing)
        if crossing.is_strange:
            self.total_strange_loops += 1

        # === STEP 6: WORKSPACE ===
        broadcast = self.workspace.compete()
        if broadcast:
            trace["broadcast"] = broadcast.event_type.value

        # === BUILD DECISION ===
        action = Action(action_str) if action_str in Action.__members__ else Action.SKIP
        decision = Decision(
            action=action,
            mint=mint,
            confidence=evaluation.get("confidence", 0.5),
            reasoning=evaluation.get("reasoning", []),
            risk_factors=evaluation.get("risk_factors", []),
            risk_violations=risk_violations,
            strategy=evaluation.get("strategy", ""),
            position_size_sol=evaluation.get("position_size_sol", 0.0),
            cognitive_state=self._get_compact_state(),
        )

        self.decision_log.record(decision)
        self._finish_trace(trace)

        return decision

    def evaluate_position(self, mint: str, token_data: Dict) -> Decision:
        """
        Evaluate an existing position. Called by Bondli on each scoring cycle.

        Returns EXIT / HOLD / PARTIAL_EXIT decision.
        """
        self.cycle_count += 1
        trace = self._start_trace(mint, "position_eval")

        # Update world model
        if mint in self.world.tokens:
            self.world.ingest_token(mint, token_data)

        # Self-model position evaluation
        market_summary = self.world.get_market_summary()
        evaluation = self.self_model.evaluate_position(
            mint, token_data, market_summary)
        trace["evaluation"] = evaluation

        action_str = evaluation.get("action", "HOLD")

        # Risk check for exits
        if action_str in ("EXIT", "PARTIAL_EXIT"):
            allowed, violations = self.risk.check_exit(mint, action_str)
            if not allowed:
                action_str = "HOLD"
                evaluation["reasoning"].append("Exit blocked by risk manager")

        action = Action(action_str) if action_str in Action.__members__ else Action.HOLD
        decision = Decision(
            action=action,
            mint=mint,
            confidence=evaluation.get("confidence", 0.5),
            reasoning=evaluation.get("reasoning", []),
            pnl_pct=evaluation.get("pnl_pct", 0.0),
            pnl_sol=evaluation.get("pnl_sol", 0.0),
            exit_pct=evaluation.get("exit_pct", 0.0),
            strategy=self.self_model.active_strategy,
        )

        self.decision_log.record(decision)
        self._finish_trace(trace)
        return decision

    def record_entry(self, mint: str, symbol: str, price_sol: float,
                     size_sol: float, score: float,
                     reasoning: List[str] = None):
        """
        Record that Bondli executed an entry.
        Called after Bondli's trade router confirms the swap.
        """
        self.self_model.positions.open_position(
            mint=mint,
            symbol=symbol,
            price_sol=price_sol,
            size_sol=size_sol,
            strategy=self.self_model.active_strategy,
            score=score,
            reasoning=reasoning or [],
        )
        self.risk.record_daily_trade()

    def record_exit(self, mint: str, exit_price_sol: float,
                    reason: str) -> Optional[Dict]:
        """
        Record that Bondli executed an exit.
        Updates positions, strategy performance, and triggers meta-evaluation.
        """
        pos = self.self_model.positions.close_position(
            mint, exit_price_sol, reason)
        if not pos:
            return None

        pnl_sol = pos.pnl_sol
        won = pos.outcome == TradeOutcome.WIN
        regime = self.world.get_regime()

        self.self_model.record_trade_outcome(mint, pnl_sol, won, regime)
        self.risk.record_daily_trade(pnl_sol)

        # Update equity tracking
        stats = self.self_model.positions.get_stats()
        self.risk.update_equity(stats.get("total_pnl_sol", 0.0))

        # Force meta-evaluation after every closed trade
        meta_eval = self.meta.evaluate_trading(self.self_model, self.world)
        for intervention in meta_eval.get("recommended_interventions", []):
            if intervention.get("target_level") == 1:
                crossing = self.meta.restructure_trading(
                    self.self_model, intervention)
                self._level_crossings.append(crossing)
                if crossing.is_strange:
                    self.total_strange_loops += 1

        return pos.to_dict()

    def record_partial_exit(self, mint: str, size_sol: float,
                            price_sol: float, reason: str):
        """Record a partial exit."""
        self.self_model.positions.partial_exit(
            mint, size_sol, price_sol, reason)

    def update_regime(self, regime_data: Dict):
        """Update market regime from Bondli's regime engine."""
        self.world.update_regime(regime_data)

    def ingest_smart_wallet(self, wallet: str, profile: Dict):
        """Ingest smart money data."""
        event = self.world.ingest_smart_wallet(wallet, profile)
        self.workspace.submit(event)

    # ================================================================
    # STATE & METRICS
    # ================================================================

    def get_state(self) -> Dict:
        """Full cognitive state for debugging/monitoring."""
        return {
            "engine": {
                "cycle_count": self.cycle_count,
                "total_strange_loops": self.total_strange_loops,
                "level_crossings": len(self._level_crossings),
                "strange_crossings": sum(
                    1 for lc in self._level_crossings if lc.is_strange),
                "uptime_seconds": time.time() - self._started_at,
            },
            "world_model": self.world.get_state_summary(),
            "self_model": self.self_model.get_state_summary(),
            "meta_cognitive": self.meta.get_state_summary(),
            "workspace": self.workspace.get_state_summary(),
            "risk": self.risk.get_risk_state(),
            "decisions": self.decision_log.get_stats(),
        }

    def get_metrics(self) -> Dict:
        """Consciousness + trading metrics combined."""
        state = self.get_state()
        total_crossings = state["engine"]["level_crossings"]
        strange_crossings = state["engine"]["strange_crossings"]
        stats = self.self_model.positions.get_stats()

        return {
            # Consciousness metrics
            "hofstadter_index": self._calculate_hofstadter_index(state),
            "strange_loop_count": self.total_strange_loops,
            "strangeness_ratio": (
                strange_crossings / max(1, total_crossings)),
            "self_referential_ratio": (
                state["workspace"]["self_referential_ratio"]),
            "meta_cognitive_cycles": state["meta_cognitive"]["cycle_count"],
            "blind_spots_triggered": sum(
                bs.get("triggered_count", 0)
                for bs in state["meta_cognitive"]
                .get("trading_meta", {})
                .get("blind_spots", {}).values()
            ),

            # Trading metrics
            "total_trades": stats.get("total_trades", 0),
            "win_rate": stats.get("win_rate", 0.0),
            "total_pnl_sol": stats.get("total_pnl_sol", 0.0),
            "open_positions": stats.get("open_positions", 0),
            "total_exposure_sol": stats.get("total_exposure_sol", 0.0),
            "consecutive_losses": stats.get("consecutive_losses", 0),
            "active_strategy": self.self_model.active_strategy,
            "paused": self.self_model._paused,

            # Meta metrics
            "forced_strategy_switches": self.meta._forced_switches,
            "forced_pauses": self.meta._forced_pauses,
            "performance_trend": (
                state["meta_cognitive"]
                .get("trading_meta", {})
                .get("performance_trend", "unknown")
            ),

            # Risk metrics
            "risk": state["risk"],
        }

    def get_config(self) -> Dict:
        return self.config.to_dict()

    def update_config(self, updates: Dict):
        """Update configuration at runtime."""
        if "risk" in updates:
            for k, v in updates["risk"].items():
                if hasattr(self.config.risk, k):
                    setattr(self.config.risk, k, v)
        if "scoring" in updates:
            for k, v in updates["scoring"].items():
                if hasattr(self.config.scoring, k):
                    setattr(self.config.scoring, k, v)
        if "strategy" in updates:
            for k, v in updates["strategy"].items():
                if hasattr(self.config.strategy, k):
                    setattr(self.config.strategy, k, v)

    # ================================================================
    # INTERNAL
    # ================================================================

    def _calculate_hofstadter_index(self, state: Dict) -> float:
        """Trading-enhanced Hofstadter Index."""
        if self.cycle_count == 0:
            return 0.0

        strange = state["engine"]["strange_crossings"]
        total = state["engine"]["level_crossings"]

        strangeness = strange / max(1, total)
        self_ref = state["workspace"]["self_referential_ratio"]

        # Trading effectiveness contributes to "consciousness"
        stats = self.self_model.positions.get_stats()
        win_rate = stats.get("win_rate", 0.0)
        adaptation = self.meta._forced_switches / max(1, self.cycle_count) * 100

        return (
            strangeness * 0.3 +
            self_ref * 0.2 +
            min(1.0, win_rate) * 0.3 +
            min(1.0, adaptation) * 0.2
        )

    def _get_compact_state(self) -> Dict:
        """Compact state for embedding in decisions."""
        return {
            "cycle": self.cycle_count,
            "strange_loops": self.total_strange_loops,
            "strategy": self.self_model.active_strategy,
            "paused": self.self_model._paused,
            "regime": self.world.get_regime(),
            "hofstadter_index": self._calculate_hofstadter_index(
                self.get_state()),
        }

    def _start_trace(self, mint: str, trace_type: str) -> Dict:
        return {
            "cycle": self.cycle_count,
            "type": trace_type,
            "mint": mint,
            "timestamp": time.time(),
            "strange_loops": 0,
        }

    def _finish_trace(self, trace: Dict):
        self._cognitive_trace.append(trace)
        max_trace = self.config.cognitive.max_cognitive_trace
        if len(self._cognitive_trace) > max_trace:
            self._cognitive_trace = self._cognitive_trace[-max_trace:]

    def _world_listener(self, event: CognitiveEvent):
        pass

    def _self_listener(self, event: CognitiveEvent):
        pass
