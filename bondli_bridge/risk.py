"""
risk.py — Risk management layer for the cognitive trading bridge.

Sits between the decision engine and trade execution.
Enforces hard limits that even the meta-cognitive layer can't override.
This is the "circuit breaker" — the last line of defense.
"""

from typing import Dict, List, Optional, Tuple
from .config import BridgeConfig
from .positions import PositionTracker
import time


class RiskViolation:
    """A risk rule that was violated."""

    def __init__(self, rule: str, severity: str, details: str):
        self.rule = rule
        self.severity = severity  # "hard" (block trade) or "soft" (warn)
        self.details = details
        self.timestamp = time.time()

    def to_dict(self) -> Dict:
        return {
            "rule": self.rule,
            "severity": self.severity,
            "details": self.details,
        }


class RiskManager:
    """
    Hard risk limits enforced on every trade decision.

    The cognitive layer (Levels 0-2) can be wrong. The risk manager
    catches the cases the strange loop misses.

    Rules are simple and absolute — no ML, no confidence scores,
    just hard math on exposure, drawdown, and position limits.
    """

    def __init__(self, config: BridgeConfig, positions: PositionTracker):
        self.config = config
        self.positions = positions
        self._daily_trades: List[float] = []  # timestamps
        self._daily_pnl: float = 0.0
        self._peak_equity: float = 0.0
        self._current_equity: float = 0.0
        self._violations: List[RiskViolation] = []
        self._circuit_breaker_active: bool = False
        self._circuit_breaker_reason: str = ""
        self._circuit_breaker_until: float = 0.0

    def check_entry(self, mint: str, size_sol: float,
                    token_data: Dict) -> Tuple[bool, List[RiskViolation]]:
        """
        Check if a new entry is allowed by risk rules.

        Returns (allowed, violations).
        Hard violations block the trade. Soft violations are warnings.
        """
        violations = []

        # Circuit breaker
        if self._circuit_breaker_active:
            if time.time() < self._circuit_breaker_until:
                violations.append(RiskViolation(
                    "circuit_breaker",
                    "hard",
                    f"Circuit breaker active: {self._circuit_breaker_reason}",
                ))
                return False, violations
            else:
                self._circuit_breaker_active = False

        # Max concurrent positions
        if self.positions.open_count >= self.config.risk.max_concurrent_positions:
            violations.append(RiskViolation(
                "max_positions",
                "hard",
                f"Max positions ({self.config.risk.max_concurrent_positions}) reached",
            ))

        # Max exposure
        new_exposure = self.positions.total_exposure_sol + size_sol
        if new_exposure > self.config.risk.max_portfolio_exposure_sol:
            violations.append(RiskViolation(
                "max_exposure",
                "hard",
                f"Exposure would be {new_exposure:.2f} SOL > "
                f"{self.config.risk.max_portfolio_exposure_sol} SOL limit",
            ))

        # Max position size
        if size_sol > self.config.risk.max_position_size_sol:
            violations.append(RiskViolation(
                "max_position_size",
                "hard",
                f"Size {size_sol:.4f} SOL > {self.config.risk.max_position_size_sol} SOL limit",
            ))

        # Minimum liquidity
        liquidity = token_data.get("liquidity_sol", 0.0)
        if liquidity < self.config.risk.min_liquidity_sol:
            violations.append(RiskViolation(
                "min_liquidity",
                "hard",
                f"Liquidity {liquidity:.1f} SOL < {self.config.risk.min_liquidity_sol} SOL minimum",
            ))

        # Position size vs liquidity (don't be >2% of pool)
        if liquidity > 0 and size_sol / liquidity > 0.02:
            violations.append(RiskViolation(
                "size_vs_liquidity",
                "soft",
                f"Position is {size_sol / liquidity:.1%} of liquidity pool",
            ))

        # Duplicate position
        if self.positions.has_position(mint):
            violations.append(RiskViolation(
                "duplicate_position",
                "hard",
                "Already have position in this token",
            ))

        # Rug signal hard reject
        rug_signals = token_data.get("rug_signals", 0)
        if rug_signals >= self.config.scoring.rug_signal_max + 1:
            violations.append(RiskViolation(
                "rug_detected",
                "hard",
                f"Token has {rug_signals} rug signals",
            ))

        # Drawdown check
        if self._peak_equity > 0:
            current_dd = (self._peak_equity - self._current_equity) / self._peak_equity
            if current_dd > self.config.risk.max_drawdown_pct:
                violations.append(RiskViolation(
                    "max_drawdown",
                    "hard",
                    f"Portfolio drawdown {current_dd:.1%} exceeds "
                    f"{self.config.risk.max_drawdown_pct:.1%} limit",
                ))

        # Record
        self._violations.extend(violations)

        has_hard = any(v.severity == "hard" for v in violations)
        return not has_hard, violations

    def check_exit(self, mint: str, reason: str) -> Tuple[bool, List[RiskViolation]]:
        """
        Exits are almost always allowed. Only check sanity.
        """
        violations = []

        if not self.positions.has_position(mint):
            violations.append(RiskViolation(
                "no_position",
                "hard",
                "No open position to exit",
            ))
            return False, violations

        return True, violations

    def update_equity(self, total_equity_sol: float):
        """Update equity tracking for drawdown calculation."""
        self._current_equity = total_equity_sol
        if total_equity_sol > self._peak_equity:
            self._peak_equity = total_equity_sol

    def record_daily_trade(self, pnl_sol: float = 0.0):
        """Track daily trading activity."""
        now = time.time()
        self._daily_trades.append(now)
        self._daily_pnl += pnl_sol

        # Prune trades older than 24h
        cutoff = now - 86400
        self._daily_trades = [t for t in self._daily_trades if t > cutoff]

    def trigger_circuit_breaker(self, reason: str, duration_seconds: int = 300):
        """Emergency stop. Blocks all new entries for duration."""
        self._circuit_breaker_active = True
        self._circuit_breaker_reason = reason
        self._circuit_breaker_until = time.time() + duration_seconds

    def get_risk_state(self) -> Dict:
        """Current risk state for API responses."""
        drawdown = 0.0
        if self._peak_equity > 0:
            drawdown = (self._peak_equity - self._current_equity) / self._peak_equity

        return {
            "circuit_breaker": {
                "active": self._circuit_breaker_active,
                "reason": self._circuit_breaker_reason,
                "remaining_seconds": max(0, self._circuit_breaker_until - time.time()),
            },
            "exposure": {
                "current_sol": self.positions.total_exposure_sol,
                "max_sol": self.config.risk.max_portfolio_exposure_sol,
                "utilization": (
                    self.positions.total_exposure_sol /
                    self.config.risk.max_portfolio_exposure_sol
                    if self.config.risk.max_portfolio_exposure_sol > 0 else 0
                ),
            },
            "positions": {
                "open": self.positions.open_count,
                "max": self.config.risk.max_concurrent_positions,
            },
            "drawdown": {
                "current": drawdown,
                "max_allowed": self.config.risk.max_drawdown_pct,
                "peak_equity": self._peak_equity,
            },
            "daily": {
                "trades": len(self._daily_trades),
                "pnl_sol": self._daily_pnl,
            },
            "recent_violations": [
                v.to_dict() for v in self._violations[-10:]
            ],
        }
