"""
trading_self.py — Level 1: Strategic Reasoning Layer

Extends the base SelfModel with trading-specific decision logic.
Implements strategy selection, goal-driven evaluation, and downward
causation on the market world model (Level 0) via attention modulation.

Primary responsibility: Given scored token data and market context,
produce a structured decision (APE / SKIP / EXIT / HOLD) with an
auditable reasoning chain. Position sizing follows a half-Kelly
criterion adapted for regime-dependent risk adjustment.

The meta-cognitive layer (Level 2) monitors these decisions and
applies corrective interventions when systematic errors are detected.
"""

from typing import Dict, List, Optional, Tuple
from core.structures import (
    Goal, GoalPriority, FailureRecord, Belief, ReasoningMode,
    CognitiveEvent, CognitiveEventType, LevelCrossing
)
from core.self_model import SelfModel, ReasoningPattern
from .positions import PositionTracker, Position, TradeOutcome
from .config import BridgeConfig
import time
import math


class TradingStrategy:
    """A trading strategy with performance tracking."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.trades: int = 0
        self.wins: int = 0
        self.losses: int = 0
        self.total_pnl_sol: float = 0.0
        self.active: bool = True
        self.activated_at: float = time.time()
        self.deactivated_at: float = 0.0
        self.regime_affinity: Dict[str, float] = {}  # regime -> effectiveness

    @property
    def effectiveness(self) -> float:
        if self.trades == 0:
            return 0.5  # No data, neutral
        return self.wins / self.trades

    @property
    def avg_pnl(self) -> float:
        return self.total_pnl_sol / self.trades if self.trades > 0 else 0.0

    def record_trade(self, won: bool, pnl_sol: float, regime: str = "unknown"):
        self.trades += 1
        if won:
            self.wins += 1
        else:
            self.losses += 1
        self.total_pnl_sol += pnl_sol

        # Track regime affinity
        if regime not in self.regime_affinity:
            self.regime_affinity[regime] = 0.5
        current = self.regime_affinity[regime]
        # Exponential moving average
        alpha = 0.3
        outcome_val = 1.0 if won else 0.0
        self.regime_affinity[regime] = current * (1 - alpha) + outcome_val * alpha

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "trades": self.trades,
            "wins": self.wins,
            "losses": self.losses,
            "effectiveness": self.effectiveness,
            "total_pnl_sol": self.total_pnl_sol,
            "avg_pnl": self.avg_pnl,
            "active": self.active,
            "regime_affinity": self.regime_affinity,
        }


class TradingSelfModel(SelfModel):
    """
    Level 1 of the trading cognitive hierarchy.

    Extends the base self-model with:
    - Multi-strategy management with regime-conditional selection
    - Position-aware gating (exposure, liquidity, rug detection)
    - Performance self-assessment via confidence state tracking
    - Downward causation on Level 0 attention weights
    """

    def __init__(self, config: BridgeConfig = None):
        super().__init__()
        self.config = config or BridgeConfig()
        self.positions = PositionTracker()
        self.strategies: Dict[str, TradingStrategy] = {}
        self.active_strategy: str = self.config.strategy.default_strategy
        self._last_loss_time: float = 0.0
        self._paused: bool = False
        self._pause_reason: str = ""
        self._decision_history: List[Dict] = []

        # Override confidence states for trading
        self.confidence_states = {
            "scoring": 0.5,       # Confidence in ML scores
            "timing": 0.5,        # Confidence in entry/exit timing
            "rug_detection": 0.7, # Confidence in rug scanner
            "regime_read": 0.4,   # Confidence in regime classification
            "strategy": 0.5,      # Confidence in current strategy
            "risk_mgmt": 0.6,     # Confidence in position sizing
            "self_knowledge": 0.3, # Phase 1: how well we predict our own decisions
        }

        # Initialize strategies
        self._init_trading_strategies()
        self._init_trading_goals()
        self._init_trading_patterns()

    def _init_trading_strategies(self):
        strats = {
            "momentum": ("Ride sustained buying pressure",),
            "snipe": ("Early entry on fresh launches",),
            "smart_follow": ("Copy smart money wallet entries",),
            "fade": ("Counter-trade overextended moves",),
            "survivor": ("Only ape tokens matching survivor archetype",),
        }
        for name, (desc,) in strats.items():
            self.strategies[name] = TradingStrategy(name, desc)

    def _init_trading_goals(self):
        goals = [
            ("goal_profitable", "Maintain positive P&L", GoalPriority.HIGH),
            ("goal_avoid_rugs", "Detect and avoid rug pulls", GoalPriority.CRITICAL),
            ("goal_adapt_regime", "Adapt strategy to market regime", GoalPriority.MEDIUM),
            ("goal_risk_mgmt", "Keep exposure within limits", GoalPriority.HIGH),
        ]
        for gid, desc, priority in goals:
            self.goals[gid] = Goal(id=gid, description=desc, priority=priority)

    def _init_trading_patterns(self):
        patterns = [
            ("momentum_read", "Detecting sustained buying momentum"),
            ("rug_pattern", "Recognizing rug pull patterns"),
            ("regime_shift", "Detecting market regime changes"),
            ("smart_money_follow", "Following profitable wallet patterns"),
            ("overconfidence", "Tendency to oversize after wins"),
            ("revenge_trade", "Tendency to ape after losses"),
        ]
        for name, desc in patterns:
            self.reasoning_patterns[name] = ReasoningPattern(name, desc)

    # ═══════════════════════════════════════
    # SELF-PREDICTION (Phase 1 Consciousness)
    # ═══════════════════════════════════════

    def predict_own_decision(self, token_data: Dict, market_summary: Dict) -> Dict:
        """
        Before deciding, predict what we WILL decide.

        This is the core of the self-prediction loop. The self-model
        uses its knowledge of its own gates, thresholds, and recent
        behavior to predict its own output. The prediction is compared
        against the actual decision after evaluate_token() runs.

        Uses fast heuristics (System 1 self-model) — NOT the full
        evaluation logic. The whole point is that this is an imperfect
        model of ourselves, and the error signal drives learning.
        """
        mint = token_data.get("mint", "")
        score = token_data.get("score", 0.0)
        velocity = token_data.get("velocity", 0.0)
        rug_signals = token_data.get("rug_signals", 0)
        smart_money = token_data.get("smart_money_in", False)
        liquidity = token_data.get("liquidity_sol", 0.0)

        # Quick gate predictions (these are deterministic, easy to predict)
        if self._paused:
            return {"action": "SKIP", "confidence": 0.9, "reasoning": "paused"}
        if self._in_cooldown():
            return {"action": "SKIP", "confidence": 0.8, "reasoning": "cooldown"}
        if self.positions.has_position(mint):
            return {"action": "SKIP", "confidence": 1.0, "reasoning": "has_position"}
        if rug_signals >= self.config.scoring.rug_signal_max + 1:
            return {"action": "SKIP", "confidence": 0.95, "reasoning": "rug"}
        if liquidity < self.config.risk.min_liquidity_sol:
            return {"action": "SKIP", "confidence": 0.8, "reasoning": "low_liquidity"}
        if self.positions.open_count >= self.config.risk.max_concurrent_positions:
            return {"action": "SKIP", "confidence": 0.9, "reasoning": "max_positions"}
        if self.positions.total_exposure_sol >= self.config.risk.max_portfolio_exposure_sol:
            return {"action": "SKIP", "confidence": 0.9, "reasoning": "max_exposure"}

        # Scoring prediction — this is where self-knowledge matters.
        # We use our confidence states and recent history to estimate
        # what we think we'll do, rather than running the full logic.
        predicted_action = "SKIP"
        predicted_confidence = 0.5

        if score >= self.config.scoring.min_score_to_ape:
            predicted_action = "APE"
            predicted_confidence = score

            # Predict our own adjustments using self-knowledge
            if velocity < self.config.scoring.score_velocity_threshold:
                predicted_action = "WATCH"
                predicted_confidence -= 0.15

            if smart_money and score > 0.55:
                predicted_action = "APE"
                predicted_confidence += 0.15

            # Self-knowledge adjustment: if we've been wrong a lot recently,
            # we know we tend to be more cautious (System 2 active)
            if self._prediction_error_ema > 0.5:
                # We're in System 2 / uncertain — predict more caution
                predicted_confidence -= 0.1
                if predicted_action == "APE" and predicted_confidence < 0.55:
                    predicted_action = "WATCH"
        elif score > 0.5:
            predicted_action = "WATCH"
            predicted_confidence = 0.6
        else:
            predicted_action = "SKIP"
            predicted_confidence = 0.6

        # Factor in regime knowledge
        regime = market_summary.get("regime", "unknown")
        strategy = self.strategies.get(self.active_strategy)
        if strategy and regime in strategy.regime_affinity:
            if strategy.regime_affinity[regime] < 0.3:
                predicted_confidence -= 0.1

        predicted_confidence = max(0.0, min(1.0, predicted_confidence))

        # Final gate: we know we reject low-confidence APEs
        if predicted_action == "APE" and predicted_confidence < 0.5:
            predicted_action = "WATCH"

        return {
            "action": predicted_action,
            "confidence": round(predicted_confidence, 4),
            "reasoning": "self_prediction",
        }

    def compare_prediction(self, prediction: Dict, actual: Dict) -> Dict:
        """
        Compare self-prediction against actual decision.
        Delegates to base SelfModel's prediction tracking,
        then applies trading-specific feedback.
        """
        record = self.record_prediction_outcome(prediction, actual)

        # Trading-specific feedback: prediction error modulates
        # trading confidence states
        error = record["combined_error"]

        # High self-prediction error → reduce confidence in scoring
        if error > 0.5:
            self.confidence_states["scoring"] = max(
                0.2, self.confidence_states["scoring"] - 0.03)
            self.confidence_states["strategy"] = max(
                0.2, self.confidence_states["strategy"] - 0.02)
        elif error < 0.2:
            # Good self-knowledge → boost confidence slightly
            self.confidence_states["scoring"] = min(
                0.9, self.confidence_states["scoring"] + 0.01)
            self.confidence_states["strategy"] = min(
                0.9, self.confidence_states["strategy"] + 0.01)

        # Track self-prediction pattern effectiveness
        if "self_referential" in self.reasoning_patterns:
            self.reasoning_patterns["self_referential"].record_use(
                succeeded=record["action_match"],
                context=f"pred={prediction.get('action')} actual={actual.get('action')}"
            )

        return record

    def evaluate_token(self, token_data: Dict, market_summary: Dict) -> Dict:
        """
        Core decision function. Evaluates a token and returns a decision.

        Returns:
            {
                "action": "APE" | "SKIP" | "WATCH",
                "confidence": float,
                "reasoning": [str],
                "strategy": str,
                "position_size_sol": float,  (only if APE)
                "risk_factors": [str],
            }
        """
        mint = token_data.get("mint", "")
        score = token_data.get("score", 0.0)
        velocity = token_data.get("velocity", 0.0)
        acceleration = token_data.get("acceleration", 0.0)
        rug_signals = token_data.get("rug_signals", 0)
        smart_money = token_data.get("smart_money_in", False)
        liquidity = token_data.get("liquidity_sol", 0.0)

        reasoning = []
        risk_factors = []
        action = "SKIP"
        confidence = 0.5

        # === GATE 1: Pause check ===
        if self._paused:
            return {
                "action": "SKIP",
                "confidence": 0.9,
                "reasoning": [f"Trading paused: {self._pause_reason}"],
                "strategy": self.active_strategy,
                "risk_factors": ["system_paused"],
            }

        # === GATE 2: Cooldown check ===
        if self._in_cooldown():
            remaining = self._cooldown_remaining()
            return {
                "action": "SKIP",
                "confidence": 0.8,
                "reasoning": [f"In cooldown after loss ({remaining:.0f}s remaining)"],
                "strategy": self.active_strategy,
                "risk_factors": ["cooldown_active"],
            }

        # === GATE 3: Already have position ===
        if self.positions.has_position(mint):
            return {
                "action": "SKIP",
                "confidence": 1.0,
                "reasoning": ["Already have position in this token"],
                "strategy": self.active_strategy,
                "risk_factors": [],
            }

        # === GATE 4: Rug check (hard reject) ===
        if rug_signals >= self.config.scoring.rug_signal_max + 1:
            rug_details = token_data.get("rug_details", [])
            self.reasoning_patterns["rug_pattern"].record_use(True, f"Rejected {mint[:8]}")
            return {
                "action": "SKIP",
                "confidence": 0.95,
                "reasoning": [f"Rug detected: {rug_signals} signals"] + rug_details[:3],
                "strategy": self.active_strategy,
                "risk_factors": ["rug_detected"],
            }

        # === GATE 5: Liquidity check ===
        if liquidity < self.config.risk.min_liquidity_sol:
            return {
                "action": "SKIP",
                "confidence": 0.8,
                "reasoning": [f"Insufficient liquidity: {liquidity:.1f} SOL < {self.config.risk.min_liquidity_sol} SOL"],
                "strategy": self.active_strategy,
                "risk_factors": ["low_liquidity"],
            }

        # === GATE 6: Exposure check ===
        if self.positions.open_count >= self.config.risk.max_concurrent_positions:
            return {
                "action": "SKIP",
                "confidence": 0.9,
                "reasoning": [f"Max positions reached ({self.positions.open_count})"],
                "strategy": self.active_strategy,
                "risk_factors": ["max_positions"],
            }

        if self.positions.total_exposure_sol >= self.config.risk.max_portfolio_exposure_sol:
            return {
                "action": "SKIP",
                "confidence": 0.9,
                "reasoning": [f"Max exposure reached ({self.positions.total_exposure_sol:.2f} SOL)"],
                "strategy": self.active_strategy,
                "risk_factors": ["max_exposure"],
            }

        # === SCORING EVALUATION ===
        reasoning.append(f"ML score: {score:.3f}")

        # Score threshold
        if score < self.config.scoring.min_score_to_ape:
            reasoning.append(f"Score below threshold ({self.config.scoring.min_score_to_ape})")
            action = "WATCH" if score > 0.5 else "SKIP"
            confidence = 0.6
        else:
            reasoning.append("Score above ape threshold")
            action = "APE"
            confidence = score  # Base confidence = score

        # Score derivatives (Bondli's edge)
        if velocity < self.config.scoring.score_velocity_threshold:
            reasoning.append(f"Score velocity negative ({velocity:.4f}) - deteriorating")
            risk_factors.append("negative_velocity")
            confidence -= 0.15
            if action == "APE":
                action = "WATCH"
        elif velocity > 0.05:
            reasoning.append(f"Score velocity positive ({velocity:.4f}) - improving")
            confidence += 0.1

        if acceleration < self.config.scoring.score_accel_threshold:
            reasoning.append(f"Score accelerating down ({acceleration:.4f})")
            risk_factors.append("negative_acceleration")
            confidence -= 0.1
            if action == "APE":
                action = "WATCH"

        # Smart money signal
        if smart_money:
            reasoning.append("Smart money detected in token")
            confidence += 0.15
            if action == "WATCH" and score > 0.55:
                action = "APE"
                reasoning.append("Smart money overrides marginal score")

        # Rug signals (soft penalty for 1-2 signals)
        if rug_signals > 0:
            reasoning.append(f"Rug signals present: {rug_signals}")
            risk_factors.append(f"rug_signals_{rug_signals}")
            confidence -= rug_signals * 0.1

        # Regime adjustment
        regime = market_summary.get("regime", "unknown")
        strategy = self.strategies.get(self.active_strategy)
        if strategy and regime in strategy.regime_affinity:
            affinity = strategy.regime_affinity[regime]
            if affinity < 0.3:
                reasoning.append(f"Strategy '{self.active_strategy}' poor fit for '{regime}' regime")
                risk_factors.append("regime_mismatch")
                confidence -= 0.1

        # Clamp confidence
        confidence = max(0.0, min(1.0, confidence))

        # Final decision
        if action == "APE" and confidence < 0.5:
            action = "WATCH"
            reasoning.append("Confidence too low after risk adjustments")

        result = {
            "action": action,
            "confidence": confidence,
            "reasoning": reasoning,
            "strategy": self.active_strategy,
            "risk_factors": risk_factors,
        }

        # Calculate position size if aping
        if action == "APE":
            size = self._calculate_position_size(confidence, score, market_summary)
            result["position_size_sol"] = size
            reasoning.append(f"Position size: {size:.4f} SOL")

        # Record decision
        self._decision_history.append({
            "mint": mint,
            "action": action,
            "confidence": confidence,
            "strategy": self.active_strategy,
            "timestamp": time.time(),
        })
        if len(self._decision_history) > 200:
            self._decision_history = self._decision_history[-200:]

        return result

    def evaluate_position(self, mint: str, token_data: Dict,
                          market_summary: Dict) -> Dict:
        """
        Evaluate an existing position. Returns EXIT / HOLD / PARTIAL_EXIT.

        This is called on each cycle for open positions.
        """
        pos = self.positions.get_position(mint)
        if not pos:
            return {"action": "SKIP", "reasoning": ["No position found"]}

        score = token_data.get("score", pos.current_score)
        velocity = token_data.get("velocity", 0.0)
        acceleration = token_data.get("acceleration", 0.0)
        rug_signals = token_data.get("rug_signals", 0)
        price = token_data.get("price_sol", pos.current_price_sol)

        # Update position
        pos.current_price_sol = price
        pos.current_score = score

        reasoning = []
        action = "HOLD"
        confidence = 0.5
        exit_pct = 0.0  # For partial exits

        # === EXIT LAYER 1: Score derivatives (fastest signal) ===
        if (velocity < self.config.scoring.score_velocity_threshold and
                acceleration < self.config.scoring.score_accel_threshold):
            action = "EXIT"
            confidence = 0.85
            reasoning.append(
                f"Score derivatives signal exit: v={velocity:.4f}, a={acceleration:.4f}")
            reasoning.append("Deterioration detected 2 cycles before price drop")

        # === EXIT LAYER 2: Absolute thresholds ===
        if score < self.config.scoring.min_score_to_hold:
            action = "EXIT"
            confidence = max(confidence, 0.8)
            reasoning.append(f"Score below hold threshold: {score:.3f} < {self.config.scoring.min_score_to_hold}")

        # === EXIT LAYER 3: Rug detection ===
        if rug_signals >= self.config.scoring.rug_signal_max + 1:
            action = "EXIT"
            confidence = 0.95
            reasoning.append(f"Rug signals detected: {rug_signals}")

        # === EXIT LAYER 4: Stop loss ===
        if pos.pnl_pct < -self.config.risk.stop_loss_pct:
            action = "EXIT"
            confidence = 0.9
            reasoning.append(f"Stop loss hit: {pos.pnl_pct:.1%} < -{self.config.risk.stop_loss_pct:.1%}")

        # === TAKE PROFIT (partial exits) ===
        if action == "HOLD":
            for level in self.config.risk.take_profit_levels:
                if pos.pnl_pct >= level and not self._took_profit_at(pos, level):
                    action = "PARTIAL_EXIT"
                    exit_pct = 0.33  # Take 1/3 at each level
                    confidence = 0.75
                    reasoning.append(f"Take profit at {level:.0%}: P&L = {pos.pnl_pct:.1%}")
                    break

        # === HOLD reasoning ===
        if action == "HOLD":
            reasoning.append(f"Holding: score={score:.3f}, P&L={pos.pnl_pct:.1%}")
            if velocity > 0:
                reasoning.append("Score improving")
            confidence = min(0.8, score)

        result = {
            "action": action,
            "confidence": confidence,
            "reasoning": reasoning,
            "pnl_pct": pos.pnl_pct,
            "pnl_sol": pos.pnl_sol,
            "hold_time": pos.hold_time_seconds,
        }
        if action == "PARTIAL_EXIT":
            result["exit_pct"] = exit_pct
            result["exit_size_sol"] = pos.size_sol * exit_pct

        return result

    def record_trade_outcome(self, mint: str, pnl_sol: float, won: bool,
                             regime: str = "unknown"):
        """Record a completed trade for self-assessment."""
        strategy = self.strategies.get(self.active_strategy)
        if strategy:
            strategy.record_trade(won, pnl_sol, regime)

        if not won:
            self._last_loss_time = time.time()
            self.record_failure(FailureRecord(
                description=f"Loss on {mint[:8]}: {pnl_sol:.4f} SOL",
                failure_type="trading",
                context={"mint": mint, "pnl_sol": pnl_sol, "strategy": self.active_strategy},
                severity=min(1.0, abs(pnl_sol) / self.config.risk.max_position_size_sol),
            ))

            # Check consecutive losses
            stats = self.positions.get_stats(window=10)
            if stats["consecutive_losses"] >= self.config.risk.max_losses_before_pause:
                self._paused = True
                self._pause_reason = (
                    f"{stats['consecutive_losses']} consecutive losses - "
                    "meta-cognitive review required"
                )

        # Update goal progress
        stats = self.positions.get_stats()
        if "goal_profitable" in self.goals:
            self.goals["goal_profitable"].progress = max(0.0, min(1.0,
                0.5 + stats.get("win_rate", 0.0) * 0.5))
        if "goal_avoid_rugs" in self.goals:
            rug_pattern = self.reasoning_patterns.get("rug_pattern")
            if rug_pattern:
                self.goals["goal_avoid_rugs"].progress = rug_pattern.effectiveness

    def switch_strategy(self, strategy_name: str, reason: str = ""):
        """Switch active trading strategy (can be called by meta-cognitive)."""
        if strategy_name in self.strategies:
            old = self.active_strategy
            self.active_strategy = strategy_name
            self.current_strategy = strategy_name  # Parent class field

            # Record the switch as a level crossing when called by meta
            self._decision_history.append({
                "type": "strategy_switch",
                "from": old,
                "to": strategy_name,
                "reason": reason,
                "timestamp": time.time(),
            })

    def unpause(self, reason: str = "meta_cognitive_review"):
        """Resume trading after pause."""
        self._paused = False
        self._pause_reason = ""

    def intervene_on_world(self, world_model, intervention: Dict) -> LevelCrossing:
        """
        STRANGE LOOP: Self-model modifies the market world model.

        Trading-specific interventions:
        - Boost attention on tokens matching current strategy
        - Suppress attention on tokens with rug signals
        - Update self-entity with trading performance
        """
        crossing = super().intervene_on_world(world_model, intervention)

        # Trading-specific interventions
        if "boost_tokens" in intervention:
            for mint, boost in intervention["boost_tokens"].items():
                token = world_model.get_token(mint) if hasattr(world_model, 'get_token') else None
                if token and token.entity_id:
                    current = world_model.attention_weights.get(token.entity_id, 0.5)
                    world_model.set_attention(token.entity_id, min(1.0, current + boost))
                    crossing.causal_chain.append(f"boost({mint[:8]})={boost}")

        if "suppress_tokens" in intervention:
            for mint in intervention["suppress_tokens"]:
                token = world_model.get_token(mint) if hasattr(world_model, 'get_token') else None
                if token and token.entity_id:
                    world_model.set_attention(token.entity_id, 0.0)
                    crossing.causal_chain.append(f"suppress({mint[:8]})")

        # Update SELF with trading state
        if "trading_state" in intervention:
            world_model.update_self(intervention["trading_state"])
            crossing.causal_chain.append("self_trading_update")

        return crossing

    def _calculate_position_size(self, confidence: float, score: float,
                                 market_summary: Dict) -> float:
        """
        Calculate position size based on confidence, score, and risk limits.
        Uses a simplified Kelly criterion approach.
        """
        max_size = self.config.risk.max_position_size_sol
        remaining_exposure = (
            self.config.risk.max_portfolio_exposure_sol -
            self.positions.total_exposure_sol
        )
        max_size = min(max_size, remaining_exposure)

        if max_size <= 0:
            return 0.0

        # Kelly-inspired sizing: f = (p * b - q) / b
        # where p = win probability, q = 1-p, b = avg win/avg loss ratio
        stats = self.positions.get_stats(window=20)
        win_rate = stats.get("win_rate", 0.5)

        # Use confidence as win probability estimate
        p = (confidence + win_rate) / 2
        q = 1 - p
        b = 2.0  # Assume 2:1 reward/risk target

        kelly_fraction = max(0.0, (p * b - q) / b)
        # Use half-Kelly for safety
        kelly_fraction = min(kelly_fraction * 0.5, 0.25)

        # Regime adjustment
        regime = market_summary.get("regime", "unknown")
        if regime == "bear":
            kelly_fraction *= 0.5
        elif regime == "chop":
            kelly_fraction *= 0.7

        size = max_size * kelly_fraction
        # Minimum viable position
        return max(0.01, min(size, max_size))

    def _in_cooldown(self) -> bool:
        if self._last_loss_time == 0:
            return False
        elapsed = time.time() - self._last_loss_time
        return elapsed < self.config.risk.cooldown_after_loss_seconds

    def _cooldown_remaining(self) -> float:
        if self._last_loss_time == 0:
            return 0.0
        elapsed = time.time() - self._last_loss_time
        return max(0, self.config.risk.cooldown_after_loss_seconds - elapsed)

    def _took_profit_at(self, pos: Position, level: float) -> bool:
        """Check if we already took profit at this level."""
        for exit in pos.partial_exits:
            if abs(exit.get("pnl_at_exit", 0) - level) < 0.05:
                return True
        return False

    def reflect_on_self(self) -> CognitiveEvent:
        """Override parent to include trading self-assessment."""
        base = super().reflect_on_self()
        stats = self.positions.get_stats(window=20)
        strategy_stats = self.positions.get_strategy_stats()

        base.content.update({
            "trading": {
                "active_strategy": self.active_strategy,
                "paused": self._paused,
                "pause_reason": self._pause_reason,
                "open_positions": self.positions.open_count,
                "total_exposure_sol": self.positions.total_exposure_sol,
                "recent_stats": stats,
                "strategy_effectiveness": {
                    name: s.effectiveness
                    for name, s in self.strategies.items()
                },
                "consecutive_losses": stats.get("consecutive_losses", 0),
            },
            "self_prediction": self.get_prediction_stats(),
        })
        return base

    def get_state_summary(self) -> Dict:
        base = super().get_state_summary()
        base["trading"] = {
            "active_strategy": self.active_strategy,
            "paused": self._paused,
            "strategies": {n: s.to_dict() for n, s in self.strategies.items()},
            "positions": self.positions.to_dict(),
            "recent_decisions": self._decision_history[-10:],
        }
        return base
