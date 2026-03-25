"""
trading_meta.py — Level 2: The Trading Watcher

Extends BRAD's MetaCognitiveLoop for trading.
Monitors the self-model's trading performance, detects pathological
patterns (overconfidence, revenge trading, regime blindness), and
forces strategy switches through downward causation.

This is where BRAD's strange loop architecture earns its keep:
the system watches itself trade, and when it detects it's failing,
it restructures its own decision-making before more money is lost.
"""

from typing import Dict, List, Optional
from core.structures import BlindSpot, CognitiveEvent, CognitiveEventType, LevelCrossing
from core.meta_cognitive import MetaCognitiveLoop, MetaPattern
from .config import BridgeConfig
import time
import math


class TradingBlindSpot:
    """A trading-specific blind spot — a systematic error the system can detect."""

    def __init__(self, name: str, description: str, detection_fn_name: str):
        self.name = name
        self.description = description
        self.detection_fn_name = detection_fn_name
        self.triggered_count: int = 0
        self.last_triggered: float = 0.0
        self.severity: float = 0.0  # 0-1, updated each check
        self.mitigations_applied: int = 0

    def trigger(self, severity: float):
        self.triggered_count += 1
        self.last_triggered = time.time()
        self.severity = severity

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "triggered_count": self.triggered_count,
            "severity": self.severity,
            "last_triggered": self.last_triggered,
            "mitigations_applied": self.mitigations_applied,
        }


class TradingMetaCognitive(MetaCognitiveLoop):
    """
    Level 2 of the trading cognitive hierarchy.

    Monitors Level 1 (TradingSelfModel) and intervenes when:
    - Strategy effectiveness drops below threshold
    - Consecutive losses suggest regime mismatch
    - Overconfidence detected (win rate inflated vs reality)
    - Revenge trading pattern detected
    - Drawdown exceeds limits
    - Regime change detected but strategy hasn't adapted
    """

    def __init__(self, config: BridgeConfig = None):
        super().__init__()
        self.config = config or BridgeConfig()
        self.trading_blind_spots: Dict[str, TradingBlindSpot] = {}
        self._regime_history: List[Dict] = []
        self._performance_snapshots: List[Dict] = []
        self._forced_switches: int = 0
        self._forced_pauses: int = 0

        self._init_trading_blind_spots()
        self._init_trading_patterns()

    def _init_trading_blind_spots(self):
        """Trading-specific systematic errors we can detect."""
        spots = [
            ("overconfidence", "Sizing up after wins, ignoring base rate",
             "detect_overconfidence"),
            ("revenge_trading", "Aping immediately after losses to recover",
             "detect_revenge_trading"),
            ("regime_blindness", "Using wrong strategy for current regime",
             "detect_regime_blindness"),
            ("winner_bias", "Holding winners too long, not taking profit",
             "detect_winner_bias"),
            ("loss_aversion", "Not cutting losers fast enough",
             "detect_loss_aversion"),
            ("recency_bias", "Over-weighting last few trades vs base rate",
             "detect_recency_bias"),
            ("concentration_risk", "Too much exposure in similar tokens",
             "detect_concentration_risk"),
        ]
        for name, desc, fn in spots:
            self.trading_blind_spots[name] = TradingBlindSpot(name, desc, fn)

    def _init_trading_patterns(self):
        """Meta-patterns about trading behavior."""
        patterns = [
            ("hot_streak", "Extended winning period", "behavioral"),
            ("cold_streak", "Extended losing period", "behavioral"),
            ("strategy_decay", "Strategy effectiveness declining over time", "strategic"),
            ("regime_shift", "Market regime is changing", "environmental"),
            ("exposure_creep", "Gradually increasing position sizes", "risk"),
        ]
        for name, desc, ptype in patterns:
            self.detected_patterns[name] = MetaPattern(name, desc, ptype)

    def evaluate_trading(self, self_model, world_model) -> Dict:
        """
        Full meta-cognitive evaluation of trading performance.
        Returns recommended interventions for Level 1.
        """
        self.cycle_count += 1
        self_state = self_model.get_state_summary()
        world_state = world_model.get_state_summary()

        trading = self_state.get("trading", {})
        market = world_state.get("market", {})
        stats = trading.get("positions", {}).get("stats", {})
        strategy_stats = trading.get("positions", {}).get("strategy_stats", {})

        evaluation = {
            "cycle": self.cycle_count,
            "timestamp": time.time(),
            "assessments": [],
            "blind_spots_triggered": [],
            "recommended_interventions": [],
            "strange_loop_metrics": self._measure_strange_loop(self_state),
        }

        # --- BLIND SPOT DETECTION ---

        # 1. Overconfidence: win rate inflated, sizing too large
        overconf = self._detect_overconfidence(self_model, stats)
        if overconf:
            evaluation["blind_spots_triggered"].append(overconf)
            evaluation["recommended_interventions"].append(overconf["intervention"])

        # 2. Revenge trading: rapid entries after losses
        revenge = self._detect_revenge_trading(self_model, trading)
        if revenge:
            evaluation["blind_spots_triggered"].append(revenge)
            evaluation["recommended_interventions"].append(revenge["intervention"])

        # 3. Regime blindness: strategy doesn't match regime
        regime_blind = self._detect_regime_blindness(
            self_model, market, trading, strategy_stats)
        if regime_blind:
            evaluation["blind_spots_triggered"].append(regime_blind)
            evaluation["recommended_interventions"].append(regime_blind["intervention"])

        # 4. Loss aversion: holding losers too long
        loss_aversion = self._detect_loss_aversion(self_model)
        if loss_aversion:
            evaluation["blind_spots_triggered"].append(loss_aversion)
            evaluation["recommended_interventions"].append(loss_aversion["intervention"])

        # --- STRATEGY EFFECTIVENESS ---
        active = trading.get("active_strategy", "momentum")
        active_strat = trading.get("strategies", {}).get(active, {})
        effectiveness = active_strat.get("effectiveness", 0.5)

        if (active_strat.get("trades", 0) >= self.config.strategy.strategy_eval_window and
                effectiveness < self.config.strategy.min_strategy_effectiveness):
            best = self._find_best_strategy(trading.get("strategies", {}), market)
            if best and best != active:
                evaluation["assessments"].append(
                    f"Strategy '{active}' underperforming ({effectiveness:.1%}). "
                    f"Recommending switch to '{best}'."
                )
                evaluation["recommended_interventions"].append({
                    "type": "switch_strategy",
                    "target_level": 1,
                    "from_strategy": active,
                    "to_strategy": best,
                    "reason": f"effectiveness {effectiveness:.1%} below threshold",
                })

        # --- DRAWDOWN CHECK ---
        total_pnl = stats.get("total_pnl_sol", 0.0)
        peak_pnl = max(
            (s.get("total_pnl_sol", 0.0) for s in self._performance_snapshots),
            default=0.0
        )
        if peak_pnl > 0:
            drawdown = (peak_pnl - total_pnl) / peak_pnl
            if drawdown > self.config.risk.max_drawdown_pct:
                evaluation["assessments"].append(
                    f"Drawdown {drawdown:.1%} exceeds max {self.config.risk.max_drawdown_pct:.1%}"
                )
                evaluation["recommended_interventions"].append({
                    "type": "pause_trading",
                    "target_level": 1,
                    "reason": f"drawdown {drawdown:.1%}",
                    "drawdown": drawdown,
                })

        # --- CONSECUTIVE LOSS CHECK ---
        consecutive = stats.get("consecutive_losses", 0)
        if consecutive >= self.config.risk.max_losses_before_pause:
            evaluation["recommended_interventions"].append({
                "type": "pause_trading",
                "target_level": 1,
                "reason": f"{consecutive} consecutive losses",
            })

        # --- CONFIDENCE CALIBRATION (from parent) ---
        base_eval = self.evaluate(self_model, world_model)
        for intervention in base_eval.get("recommended_interventions", []):
            evaluation["recommended_interventions"].append(intervention)

        # Snapshot
        self._performance_snapshots.append({
            "cycle": self.cycle_count,
            "total_pnl_sol": total_pnl,
            "win_rate": stats.get("win_rate", 0.0),
            "open_positions": stats.get("open_positions", 0),
            "timestamp": time.time(),
        })
        if len(self._performance_snapshots) > 200:
            self._performance_snapshots = self._performance_snapshots[-200:]

        self.performance_history.append(evaluation)
        return evaluation

    def restructure_trading(self, self_model, intervention: Dict) -> LevelCrossing:
        """
        STRANGE LOOP: Meta-cognitive restructures the trading self-model.

        This is downward causation — Level 2 modifying Level 1's behavior.
        """
        crossing = LevelCrossing(
            from_level=2, to_level=1, direction="downward",
            content=str(intervention),
        )

        itype = intervention.get("type", "")

        if itype == "switch_strategy":
            to_strategy = intervention.get("to_strategy", "")
            reason = intervention.get("reason", "meta-cognitive override")
            self_model.switch_strategy(to_strategy, reason)
            self._forced_switches += 1
            crossing.causal_chain.append(
                f"strategy_switch → {to_strategy} ({reason})")

        elif itype == "pause_trading":
            reason = intervention.get("reason", "meta-cognitive pause")
            self_model._paused = True
            self_model._pause_reason = f"Meta-cognitive: {reason}"
            self._forced_pauses += 1
            crossing.causal_chain.append(f"forced_pause ({reason})")

        elif itype == "unpause_trading":
            self_model.unpause("meta_cognitive_review_complete")
            crossing.causal_chain.append("forced_unpause")

        elif itype == "reduce_confidence":
            domain = intervention.get("domain", "")
            magnitude = intervention.get("magnitude", 0.1)
            if domain in self_model.confidence_states:
                old = self_model.confidence_states[domain]
                self_model.confidence_states[domain] = max(0.1, old - magnitude)
                crossing.causal_chain.append(
                    f"confidence[{domain}] {old:.2f} → {old - magnitude:.2f}")

        elif itype == "increase_confidence":
            domain = intervention.get("domain", "")
            magnitude = intervention.get("magnitude", 0.1)
            if domain in self_model.confidence_states:
                old = self_model.confidence_states[domain]
                self_model.confidence_states[domain] = min(1.0, old + magnitude)
                crossing.causal_chain.append(
                    f"confidence[{domain}] {old:.2f} → {old + magnitude:.2f}")

        elif itype == "calibrate_confidence":
            # Delegate to parent
            return super().restructure_self(self_model, intervention)

        self.restructure_log.append({
            "cycle": self.cycle_count,
            "intervention": intervention,
            "timestamp": time.time(),
        })

        return crossing

    # ================================================================
    # BLIND SPOT DETECTORS
    # ================================================================

    def _detect_overconfidence(self, self_model, stats: Dict) -> Optional[Dict]:
        """Detect if system is oversizing after wins."""
        win_rate = stats.get("win_rate", 0.5)
        confidence = self_model.confidence_states.get("strategy", 0.5)

        # Overconfident if stated confidence >> actual win rate
        gap = confidence - win_rate
        if gap > 0.2 and stats.get("total_trades", 0) >= 5:
            spot = self.trading_blind_spots["overconfidence"]
            spot.trigger(min(1.0, gap))
            return {
                "blind_spot": "overconfidence",
                "severity": gap,
                "details": f"Confidence {confidence:.1%} vs actual win rate {win_rate:.1%}",
                "intervention": {
                    "type": "reduce_confidence",
                    "target_level": 1,
                    "domain": "strategy",
                    "magnitude": gap * 0.5,
                },
            }
        return None

    def _detect_revenge_trading(self, self_model,
                                trading: Dict) -> Optional[Dict]:
        """Detect rapid entries immediately after losses."""
        decisions = trading.get("recent_decisions", [])
        if len(decisions) < 3:
            return None

        recent = decisions[-5:]
        apes_after_loss = 0
        saw_loss = False

        for d in recent:
            if d.get("type") == "strategy_switch":
                continue
            if saw_loss and d.get("action") == "APE":
                apes_after_loss += 1
            # Check if this was around a loss time
            if d.get("action") == "APE" and self_model._last_loss_time > 0:
                time_since_loss = d.get("timestamp", 0) - self_model._last_loss_time
                if 0 < time_since_loss < 30:  # Ape within 30s of loss
                    apes_after_loss += 1

        if apes_after_loss >= 2:
            spot = self.trading_blind_spots["revenge_trading"]
            spot.trigger(0.7)
            return {
                "blind_spot": "revenge_trading",
                "severity": 0.7,
                "details": f"Detected {apes_after_loss} rapid entries after losses",
                "intervention": {
                    "type": "pause_trading",
                    "target_level": 1,
                    "reason": "revenge trading pattern detected",
                },
            }
        return None

    def _detect_regime_blindness(self, self_model, market: Dict,
                                 trading: Dict,
                                 strategy_stats: Dict) -> Optional[Dict]:
        """Detect using wrong strategy for current market regime."""
        regime = market.get("regime", "unknown")
        if regime == "unknown":
            return None

        active = trading.get("active_strategy", "")
        strat = trading.get("strategies", {}).get(active, {})
        affinity = strat.get("regime_affinity", {}).get(regime, 0.5)

        # Low affinity + declining performance = regime blindness
        if affinity < 0.3 and strat.get("trades", 0) >= 5:
            # Find a better strategy for this regime
            best_strategy = None
            best_affinity = affinity

            for name, s in trading.get("strategies", {}).items():
                s_affinity = s.get("regime_affinity", {}).get(regime, 0.5)
                if s_affinity > best_affinity:
                    best_affinity = s_affinity
                    best_strategy = name

            if best_strategy:
                spot = self.trading_blind_spots["regime_blindness"]
                spot.trigger(0.6)
                return {
                    "blind_spot": "regime_blindness",
                    "severity": 0.6,
                    "details": (
                        f"Strategy '{active}' has {affinity:.1%} affinity for "
                        f"'{regime}' regime. '{best_strategy}' has {best_affinity:.1%}."
                    ),
                    "intervention": {
                        "type": "switch_strategy",
                        "target_level": 1,
                        "from_strategy": active,
                        "to_strategy": best_strategy,
                        "reason": f"regime mismatch: {regime}",
                    },
                }
        return None

    def _detect_loss_aversion(self, self_model) -> Optional[Dict]:
        """Detect holding losers too long."""
        positions = self_model.positions.open_positions
        bad_holds = []

        for mint, pos in positions.items():
            # Holding a loser with deteriorating score
            if (pos.pnl_pct < -0.10 and
                    pos.current_score < 0.4 and
                    pos.hold_time_seconds > 120):
                bad_holds.append(mint)

        if len(bad_holds) >= 2:
            spot = self.trading_blind_spots["loss_aversion"]
            spot.trigger(0.5)
            return {
                "blind_spot": "loss_aversion",
                "severity": 0.5,
                "details": f"Holding {len(bad_holds)} losing positions with low scores",
                "intervention": {
                    "type": "reduce_confidence",
                    "target_level": 1,
                    "domain": "timing",
                    "magnitude": 0.15,
                },
            }
        return None

    def _find_best_strategy(self, strategies: Dict,
                            market: Dict) -> Optional[str]:
        """Find the best strategy for current conditions."""
        regime = market.get("regime", "unknown")
        best_name = None
        best_score = -1.0

        for name, strat in strategies.items():
            effectiveness = strat.get("effectiveness", 0.5)
            affinity = strat.get("regime_affinity", {}).get(regime, 0.5)
            # Weight: 60% effectiveness, 40% regime affinity
            score = effectiveness * 0.6 + affinity * 0.4
            if score > best_score:
                best_score = score
                best_name = name

        return best_name

    def get_state_summary(self) -> Dict:
        base = super().get_state_summary()
        base["trading_meta"] = {
            "blind_spots": {
                name: bs.to_dict()
                for name, bs in self.trading_blind_spots.items()
            },
            "forced_switches": self._forced_switches,
            "forced_pauses": self._forced_pauses,
            "performance_trend": self._get_performance_trend(),
        }
        return base

    def _get_performance_trend(self) -> str:
        """Classify recent performance trajectory."""
        if len(self._performance_snapshots) < 5:
            return "insufficient_data"

        recent = self._performance_snapshots[-5:]
        pnls = [s["total_pnl_sol"] for s in recent]

        # Simple trend: are we making or losing money?
        if all(pnls[i] <= pnls[i + 1] for i in range(len(pnls) - 1)):
            return "improving"
        if all(pnls[i] >= pnls[i + 1] for i in range(len(pnls) - 1)):
            return "declining"
        return "mixed"
