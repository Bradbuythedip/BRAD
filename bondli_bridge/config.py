"""
config.py — Configuration for the Brain cognitive trading bridge.

Defines all thresholds, risk limits, strategy parameters, and cognitive
tuning constants. Values are overridable via environment variables
(prefix: BRAIN_) or the /config API endpoint at runtime.
"""

import os
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class RiskConfig:
    """Risk management parameters."""
    max_position_size_sol: float = 1.0
    max_concurrent_positions: int = 5
    max_portfolio_exposure_sol: float = 5.0
    max_drawdown_pct: float = 0.15           # 15% max drawdown before meta-cognitive intervenes
    stop_loss_pct: float = 0.20              # 20% default stop loss
    take_profit_levels: list = field(default_factory=lambda: [0.5, 1.0, 2.0])  # 50%, 100%, 200%
    cooldown_after_loss_seconds: int = 60    # Wait after a loss before next ape
    max_losses_before_pause: int = 3         # Consecutive losses trigger meta-cognitive pause
    min_liquidity_sol: float = 5.0           # Minimum liquidity to consider


@dataclass
class ScoringConfig:
    """Thresholds for token evaluation."""
    min_score_to_ape: float = 0.65           # Minimum ML score to consider aping
    min_score_to_hold: float = 0.40          # Below this, exit
    score_velocity_threshold: float = -0.05  # Negative velocity = deteriorating
    score_accel_threshold: float = -0.02     # Negative acceleration = accelerating decline
    rug_signal_max: int = 2                  # Max rug signals before auto-reject
    confidence_decay_rate: float = 0.01      # How fast old scores lose weight
    recency_weight: float = 0.7              # Weight of recent vs historical scores


@dataclass
class StrategyConfig:
    """Trading strategy parameters."""
    strategies: list = field(default_factory=lambda: [
        "momentum",      # Ride sustained buying pressure
        "snipe",         # Early entry on fresh launches
        "smart_follow",  # Copy smart money entries
        "fade",          # Counter-trade overextended moves
        "survivor",      # Only ape tokens matching survivor archetype
    ])
    default_strategy: str = "momentum"
    strategy_eval_window: int = 20           # Trades to evaluate strategy over
    min_strategy_effectiveness: float = 0.4  # Below this, meta-cognitive forces switch
    regime_lookback_cycles: int = 50         # Cycles to determine market regime


@dataclass
class CognitiveConfig:
    """Cognitive engine tuning parameters."""
    meta_eval_frequency: int = 3             # Meta-cognitive evaluates every N cycles
    attention_capacity: int = 10             # Max tokens to track simultaneously
    self_referential_boost: float = 0.15     # Salience boost for self-referential events
    strange_loop_threshold: int = 5          # Min strange loops for "self-aware" status
    blind_spot_check_frequency: int = 10     # Check for trading blind spots every N cycles
    max_cognitive_trace: int = 500           # Keep last N cycle traces


@dataclass
class BridgeConfig:
    """Top-level configuration."""
    risk: RiskConfig = field(default_factory=RiskConfig)
    scoring: ScoringConfig = field(default_factory=ScoringConfig)
    strategy: StrategyConfig = field(default_factory=StrategyConfig)
    cognitive: CognitiveConfig = field(default_factory=CognitiveConfig)

    # Server config
    host: str = "127.0.0.1"
    port: int = 8421
    debug: bool = False

    @classmethod
    def from_env(cls) -> "BridgeConfig":
        """Build config from environment variables (Bondli's .env)."""
        config = cls()

        # Server
        config.host = os.getenv("BRAIN_HOST", config.host)
        config.port = int(os.getenv("BRAIN_PORT", config.port))
        config.debug = os.getenv("BRAIN_DEBUG", "false").lower() == "true"

        # Risk overrides
        config.risk.max_position_size_sol = float(
            os.getenv("BRAIN_MAX_POSITION_SOL", config.risk.max_position_size_sol))
        config.risk.max_concurrent_positions = int(
            os.getenv("BRAIN_MAX_POSITIONS", config.risk.max_concurrent_positions))
        config.risk.max_portfolio_exposure_sol = float(
            os.getenv("BRAIN_MAX_EXPOSURE_SOL", config.risk.max_portfolio_exposure_sol))
        config.risk.max_drawdown_pct = float(
            os.getenv("BRAIN_MAX_DRAWDOWN", config.risk.max_drawdown_pct))

        # Scoring overrides
        config.scoring.min_score_to_ape = float(
            os.getenv("BRAIN_MIN_SCORE_APE", config.scoring.min_score_to_ape))
        config.scoring.rug_signal_max = int(
            os.getenv("BRAIN_RUG_SIGNAL_MAX", config.scoring.rug_signal_max))

        return config

    def to_dict(self) -> Dict:
        """Serialize for API responses."""
        return {
            "risk": {
                "max_position_size_sol": self.risk.max_position_size_sol,
                "max_concurrent_positions": self.risk.max_concurrent_positions,
                "max_portfolio_exposure_sol": self.risk.max_portfolio_exposure_sol,
                "max_drawdown_pct": self.risk.max_drawdown_pct,
                "stop_loss_pct": self.risk.stop_loss_pct,
                "take_profit_levels": self.risk.take_profit_levels,
                "cooldown_after_loss_seconds": self.risk.cooldown_after_loss_seconds,
                "max_losses_before_pause": self.risk.max_losses_before_pause,
                "min_liquidity_sol": self.risk.min_liquidity_sol,
            },
            "scoring": {
                "min_score_to_ape": self.scoring.min_score_to_ape,
                "min_score_to_hold": self.scoring.min_score_to_hold,
                "score_velocity_threshold": self.scoring.score_velocity_threshold,
                "score_accel_threshold": self.scoring.score_accel_threshold,
                "rug_signal_max": self.scoring.rug_signal_max,
            },
            "strategy": {
                "strategies": self.strategy.strategies,
                "default_strategy": self.strategy.default_strategy,
                "strategy_eval_window": self.strategy.strategy_eval_window,
                "min_strategy_effectiveness": self.strategy.min_strategy_effectiveness,
            },
            "cognitive": {
                "meta_eval_frequency": self.cognitive.meta_eval_frequency,
                "attention_capacity": self.cognitive.attention_capacity,
                "strange_loop_threshold": self.cognitive.strange_loop_threshold,
            },
            "server": {
                "host": self.host,
                "port": self.port,
            },
        }
