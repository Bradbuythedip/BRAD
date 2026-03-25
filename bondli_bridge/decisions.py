"""
decisions.py — Decision output layer for Bondli.

Clean interface that wraps the cognitive hierarchy's output into
structured decisions that Bondli's auto-ape pipeline can consume.

Every decision includes:
- The action (APE/SKIP/EXIT/HOLD/WATCH/PARTIAL_EXIT)
- Confidence score
- Full reasoning chain (why this decision was made)
- Risk check results
- Which cognitive level contributed what
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
import time


class Action(Enum):
    APE = "APE"
    SKIP = "SKIP"
    WATCH = "WATCH"
    HOLD = "HOLD"
    EXIT = "EXIT"
    PARTIAL_EXIT = "PARTIAL_EXIT"


@dataclass
class Decision:
    """A structured trading decision from the cognitive engine."""
    action: Action
    mint: str
    confidence: float
    reasoning: List[str]
    risk_factors: List[str] = field(default_factory=list)
    risk_violations: List[Dict] = field(default_factory=list)
    strategy: str = ""
    position_size_sol: float = 0.0
    exit_pct: float = 0.0
    pnl_pct: float = 0.0
    pnl_sol: float = 0.0
    cognitive_state: Dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict:
        """Serialize for HTTP response to Bondli."""
        result = {
            "action": self.action.value,
            "mint": self.mint,
            "confidence": round(self.confidence, 4),
            "reasoning": self.reasoning,
            "risk_factors": self.risk_factors,
            "risk_violations": self.risk_violations,
            "strategy": self.strategy,
            "timestamp": self.timestamp,
        }

        if self.action == Action.APE:
            result["position_size_sol"] = round(self.position_size_sol, 6)

        if self.action in (Action.EXIT, Action.HOLD, Action.PARTIAL_EXIT):
            result["pnl_pct"] = round(self.pnl_pct, 4)
            result["pnl_sol"] = round(self.pnl_sol, 6)

        if self.action == Action.PARTIAL_EXIT:
            result["exit_pct"] = round(self.exit_pct, 4)

        if self.cognitive_state:
            result["cognitive"] = self.cognitive_state

        return result

    @property
    def is_entry(self) -> bool:
        return self.action == Action.APE

    @property
    def is_exit(self) -> bool:
        return self.action in (Action.EXIT, Action.PARTIAL_EXIT)

    @property
    def is_pass(self) -> bool:
        return self.action in (Action.SKIP, Action.WATCH)


class DecisionLog:
    """Maintains a log of all decisions for analysis and replay."""

    def __init__(self, max_size: int = 1000):
        self.decisions: List[Decision] = []
        self.max_size = max_size
        self._entry_count = 0
        self._exit_count = 0
        self._skip_count = 0

    def record(self, decision: Decision):
        self.decisions.append(decision)
        if len(self.decisions) > self.max_size:
            self.decisions = self.decisions[-self.max_size:]

        if decision.is_entry:
            self._entry_count += 1
        elif decision.is_exit:
            self._exit_count += 1
        elif decision.is_pass:
            self._skip_count += 1

    def get_recent(self, n: int = 20) -> List[Dict]:
        return [d.to_dict() for d in self.decisions[-n:]]

    def get_stats(self) -> Dict:
        return {
            "total_decisions": len(self.decisions),
            "entries": self._entry_count,
            "exits": self._exit_count,
            "skips": self._skip_count,
            "entry_rate": (
                self._entry_count / len(self.decisions)
                if self.decisions else 0.0
            ),
        }

    def get_decisions_for_mint(self, mint: str) -> List[Dict]:
        return [
            d.to_dict() for d in self.decisions
            if d.mint == mint
        ]
