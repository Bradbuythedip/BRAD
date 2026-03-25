"""
positions.py — Position tracking for the cognitive trading layer.

Tracks open positions, P&L, and trade history. Feeds data into the
self-model so BRAD can reason about its own trading performance.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
import time


class PositionStatus(Enum):
    OPEN = "open"
    CLOSED = "closed"
    PARTIAL_EXIT = "partial_exit"


class TradeOutcome(Enum):
    WIN = "win"
    LOSS = "loss"
    BREAKEVEN = "breakeven"
    PENDING = "pending"


@dataclass
class Position:
    """A single trading position."""
    mint: str
    symbol: str
    entry_price_sol: float
    size_sol: float
    entry_time: float = field(default_factory=time.time)
    strategy: str = "momentum"
    entry_score: float = 0.0
    entry_reasoning: List[str] = field(default_factory=list)

    # Live state
    current_price_sol: float = 0.0
    current_score: float = 0.0
    status: PositionStatus = PositionStatus.OPEN
    partial_exits: List[Dict] = field(default_factory=list)

    # Exit
    exit_price_sol: float = 0.0
    exit_time: float = 0.0
    exit_reason: str = ""
    exit_reasoning: List[str] = field(default_factory=list)

    @property
    def pnl_sol(self) -> float:
        if self.status == PositionStatus.CLOSED:
            return (self.exit_price_sol - self.entry_price_sol) * self._effective_size()
        price = self.current_price_sol or self.entry_price_sol
        return (price - self.entry_price_sol) * self._effective_size()

    @property
    def pnl_pct(self) -> float:
        if self.entry_price_sol == 0:
            return 0.0
        if self.status == PositionStatus.CLOSED:
            return (self.exit_price_sol - self.entry_price_sol) / self.entry_price_sol
        price = self.current_price_sol or self.entry_price_sol
        return (price - self.entry_price_sol) / self.entry_price_sol

    @property
    def hold_time_seconds(self) -> float:
        end = self.exit_time if self.status == PositionStatus.CLOSED else time.time()
        return end - self.entry_time

    @property
    def outcome(self) -> TradeOutcome:
        if self.status != PositionStatus.CLOSED:
            return TradeOutcome.PENDING
        pct = self.pnl_pct
        if pct > 0.01:
            return TradeOutcome.WIN
        elif pct < -0.01:
            return TradeOutcome.LOSS
        return TradeOutcome.BREAKEVEN

    def _effective_size(self) -> float:
        """Size after partial exits."""
        exited = sum(p.get("size_sol", 0) for p in self.partial_exits)
        return max(0, self.size_sol - exited)

    def partial_exit(self, size_sol: float, price_sol: float, reason: str):
        self.partial_exits.append({
            "size_sol": size_sol,
            "price_sol": price_sol,
            "reason": reason,
            "time": time.time(),
        })
        if self._effective_size() <= 0:
            self.close(price_sol, reason)
        else:
            self.status = PositionStatus.PARTIAL_EXIT

    def close(self, exit_price_sol: float, reason: str):
        self.exit_price_sol = exit_price_sol
        self.exit_time = time.time()
        self.exit_reason = reason
        self.status = PositionStatus.CLOSED

    def to_dict(self) -> Dict:
        return {
            "mint": self.mint,
            "symbol": self.symbol,
            "entry_price_sol": self.entry_price_sol,
            "size_sol": self.size_sol,
            "effective_size_sol": self._effective_size(),
            "entry_time": self.entry_time,
            "strategy": self.strategy,
            "entry_score": self.entry_score,
            "entry_reasoning": self.entry_reasoning,
            "current_price_sol": self.current_price_sol,
            "current_score": self.current_score,
            "status": self.status.value,
            "pnl_sol": self.pnl_sol,
            "pnl_pct": self.pnl_pct,
            "hold_time_seconds": self.hold_time_seconds,
            "outcome": self.outcome.value,
            "exit_price_sol": self.exit_price_sol,
            "exit_reason": self.exit_reason,
            "partial_exits": self.partial_exits,
        }


class PositionTracker:
    """
    Tracks all positions and computes aggregate statistics.
    Feeds into the self-model for performance awareness.
    """

    def __init__(self):
        self.open_positions: Dict[str, Position] = {}  # mint -> Position
        self.closed_positions: List[Position] = []
        self.total_pnl_sol: float = 0.0

    def open_position(self, mint: str, symbol: str, price_sol: float,
                      size_sol: float, strategy: str, score: float,
                      reasoning: List[str]) -> Position:
        pos = Position(
            mint=mint,
            symbol=symbol,
            entry_price_sol=price_sol,
            size_sol=size_sol,
            current_price_sol=price_sol,
            strategy=strategy,
            entry_score=score,
            entry_reasoning=reasoning,
        )
        self.open_positions[mint] = pos
        return pos

    def update_position(self, mint: str, price_sol: float = None,
                        score: float = None) -> Optional[Position]:
        pos = self.open_positions.get(mint)
        if not pos:
            return None
        if price_sol is not None:
            pos.current_price_sol = price_sol
        if score is not None:
            pos.current_score = score
        return pos

    def close_position(self, mint: str, exit_price_sol: float,
                       reason: str) -> Optional[Position]:
        pos = self.open_positions.pop(mint, None)
        if not pos:
            return None
        pos.close(exit_price_sol, reason)
        self.closed_positions.append(pos)
        self.total_pnl_sol += pos.pnl_sol
        return pos

    def partial_exit(self, mint: str, size_sol: float, price_sol: float,
                     reason: str) -> Optional[Position]:
        pos = self.open_positions.get(mint)
        if not pos:
            return None
        pos.partial_exit(size_sol, price_sol, reason)
        if pos.status == PositionStatus.CLOSED:
            self.open_positions.pop(mint, None)
            self.closed_positions.append(pos)
            self.total_pnl_sol += pos.pnl_sol
        return pos

    def get_position(self, mint: str) -> Optional[Position]:
        return self.open_positions.get(mint)

    def has_position(self, mint: str) -> bool:
        return mint in self.open_positions

    @property
    def open_count(self) -> int:
        return len(self.open_positions)

    @property
    def total_exposure_sol(self) -> float:
        return sum(p.size_sol for p in self.open_positions.values())

    @property
    def unrealized_pnl_sol(self) -> float:
        return sum(p.pnl_sol for p in self.open_positions.values())

    def get_stats(self, window: int = 0) -> Dict:
        """Aggregate trading statistics. window=0 means all time."""
        closed = self.closed_positions
        if window > 0:
            closed = closed[-window:]

        if not closed:
            return {
                "total_trades": 0,
                "wins": 0,
                "losses": 0,
                "win_rate": 0.0,
                "total_pnl_sol": 0.0,
                "avg_pnl_pct": 0.0,
                "avg_hold_time": 0.0,
                "best_trade_pct": 0.0,
                "worst_trade_pct": 0.0,
                "consecutive_losses": 0,
                "open_positions": self.open_count,
                "total_exposure_sol": self.total_exposure_sol,
                "unrealized_pnl_sol": self.unrealized_pnl_sol,
            }

        wins = [p for p in closed if p.outcome == TradeOutcome.WIN]
        losses = [p for p in closed if p.outcome == TradeOutcome.LOSS]
        pnls = [p.pnl_pct for p in closed]

        # Count consecutive losses from the end
        consecutive_losses = 0
        for p in reversed(closed):
            if p.outcome == TradeOutcome.LOSS:
                consecutive_losses += 1
            else:
                break

        return {
            "total_trades": len(closed),
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": len(wins) / len(closed) if closed else 0.0,
            "total_pnl_sol": sum(p.pnl_sol for p in closed),
            "avg_pnl_pct": sum(pnls) / len(pnls) if pnls else 0.0,
            "avg_hold_time": sum(p.hold_time_seconds for p in closed) / len(closed),
            "best_trade_pct": max(pnls) if pnls else 0.0,
            "worst_trade_pct": min(pnls) if pnls else 0.0,
            "consecutive_losses": consecutive_losses,
            "open_positions": self.open_count,
            "total_exposure_sol": self.total_exposure_sol,
            "unrealized_pnl_sol": self.unrealized_pnl_sol,
        }

    def get_strategy_stats(self) -> Dict[str, Dict]:
        """Performance broken down by strategy."""
        by_strategy: Dict[str, List[Position]] = {}
        for p in self.closed_positions:
            by_strategy.setdefault(p.strategy, []).append(p)

        result = {}
        for strategy, positions in by_strategy.items():
            wins = [p for p in positions if p.outcome == TradeOutcome.WIN]
            losses = [p for p in positions if p.outcome == TradeOutcome.LOSS]
            result[strategy] = {
                "trades": len(positions),
                "wins": len(wins),
                "losses": len(losses),
                "win_rate": len(wins) / len(positions) if positions else 0.0,
                "total_pnl_sol": sum(p.pnl_sol for p in positions),
                "avg_pnl_pct": sum(p.pnl_pct for p in positions) / len(positions),
            }
        return result

    def to_dict(self) -> Dict:
        return {
            "open": {mint: p.to_dict() for mint, p in self.open_positions.items()},
            "stats": self.get_stats(),
            "strategy_stats": self.get_strategy_stats(),
        }
