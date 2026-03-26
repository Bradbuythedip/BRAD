"""
baselines.py — Baseline Models for Comparison

Provides simple baseline models that implement the same interface
as StrangeLoopEngine but with progressively simpler architectures.
Used for controlled comparison in ablation studies and benchmarks.

Baselines:
    RandomBaseline      — Random decisions (lower bound)
    ThresholdBaseline   — Fixed threshold on salience (no learning)
    EMABaseline         — Exponential moving average (simple adaptive)
    FlatHierarchy       — Single-level processing (no strange loops)
"""

from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from typing import Dict, List, Optional
import random
import math


class BaselineEngine:
    """Interface matching StrangeLoopEngine's public API for benchmarks."""

    def __init__(self):
        self.cycle_count = 0
        self.total_strange_loops = 0
        self.confidence_states = {
            "perception": 0.5,
            "reasoning": 0.5,
            "prediction": 0.5,
            "self_knowledge": 0.5,
            "meta_cognition": 0.5,
        }

    def step(self, perception: Dict = None) -> Dict:
        """Execute one cycle. Returns a trace dict."""
        raise NotImplementedError

    def get_consciousness_metrics(self) -> Dict:
        return {
            "hofstadter_index": 0.0,
            "strange_loop_count": 0,
            "strangeness_ratio": 0.0,
            "self_referential_broadcast_ratio": 0.0,
            "meta_cognitive_cycles": 0,
            "blind_spots_encountered": 0,
            "fundamental_limits_hit": 0,
            "self_modifications": 0,
            "kahneman_mode_distribution": {"fast": 1.0, "slow": 0.0, "loop": 0.0},
        }

    def get_full_state(self) -> Dict:
        return {
            "engine": {
                "cycle_count": self.cycle_count,
                "total_strange_loops": 0,
                "level_crossings": 0,
                "strange_crossings": 0,
            },
            "world_model": {"entity_count": 0, "belief_count": 0},
            "self_model": {"mode": "fast", "confidence": dict(self.confidence_states)},
            "meta_cognitive": {"cycle_count": 0, "blind_spots": {}},
            "workspace": {"total_broadcasts": 0, "self_referential_ratio": 0.0},
        }


class RandomBaseline(BaselineEngine):
    """
    Random baseline — lower bound on performance.

    Makes random decisions regardless of input.
    Any architecture should beat this.
    """

    def __init__(self, seed: int = 42):
        super().__init__()
        self.rng = random.Random(seed)

    def step(self, perception: Dict = None) -> Dict:
        self.cycle_count += 1
        mode = self.rng.choice(["fast", "slow", "loop"])
        return {
            "cycle": self.cycle_count,
            "perception": perception,
            "events": [],
            "level_crossings": [],
            "broadcasts": [],
            "mode": mode,
            "strange_loops_this_cycle": 0,
        }


class ThresholdBaseline(BaselineEngine):
    """
    Fixed threshold baseline — simple rule-based system.

    Uses a fixed salience threshold to decide attention.
    No learning, no adaptation, no self-reference.
    """

    def __init__(self, threshold: float = 0.5):
        super().__init__()
        self.threshold = threshold

    def step(self, perception: Dict = None) -> Dict:
        self.cycle_count += 1
        salience = 0.5
        if perception:
            salience = perception.get("salience", 0.5)

        mode = "slow" if salience > self.threshold else "fast"

        return {
            "cycle": self.cycle_count,
            "perception": perception,
            "events": [{"step": "threshold_check", "level": 0}],
            "level_crossings": [],
            "broadcasts": [{"event_type": "perception",
                           "is_self_referential": False}] if salience > self.threshold else [],
            "mode": mode,
            "strange_loops_this_cycle": 0,
        }


class EMABaseline(BaselineEngine):
    """
    Exponential moving average baseline — simple adaptive system.

    Tracks a running average of salience and adjusts its threshold.
    Has basic learning but no hierarchy, no meta-cognition, no
    self-reference.
    """

    def __init__(self, alpha: float = 0.1, initial_threshold: float = 0.5):
        super().__init__()
        self.alpha = alpha
        self.threshold = initial_threshold
        self.ema = initial_threshold

    def step(self, perception: Dict = None) -> Dict:
        self.cycle_count += 1
        salience = 0.5
        if perception:
            salience = perception.get("salience", 0.5)

        # Update EMA
        self.ema = self.alpha * salience + (1 - self.alpha) * self.ema

        # Adaptive threshold: attend to things above recent average
        attend = salience > self.ema
        mode = "slow" if attend else "fast"

        # Update confidence based on recent salience (crude learning)
        for key in self.confidence_states:
            old = self.confidence_states[key]
            self.confidence_states[key] = old * 0.99 + salience * 0.01

        return {
            "cycle": self.cycle_count,
            "perception": perception,
            "events": [{"step": "ema_update", "level": 0}],
            "level_crossings": [],
            "broadcasts": [{"event_type": "perception",
                           "is_self_referential": False}] if attend else [],
            "mode": mode,
            "strange_loops_this_cycle": 0,
        }


class FlatHierarchy(BaselineEngine):
    """
    Flat hierarchy baseline — uses the world model and self model
    but with no meta-cognitive layer and no downward causation.

    This is the key comparison: does the tangled hierarchy help?
    """

    def __init__(self):
        super().__init__()
        self.beliefs: List[Dict] = []
        self.mode = "fast"

    def step(self, perception: Dict = None) -> Dict:
        self.cycle_count += 1

        mode = "fast"
        if perception:
            complexity = perception.get("complexity", 0.5)
            if complexity > 0.7:
                mode = "slow"

            # Simple belief update
            salience = perception.get("salience", 0.5)
            self.beliefs.append({
                "cycle": self.cycle_count,
                "salience": salience,
                "complexity": complexity,
            })
            if len(self.beliefs) > 100:
                self.beliefs = self.beliefs[-100:]

            # Update confidence (flat — no meta-cognitive correction)
            for key in self.confidence_states:
                # Drift toward salience
                old = self.confidence_states[key]
                self.confidence_states[key] = old * 0.95 + salience * 0.05

        self.mode = mode

        return {
            "cycle": self.cycle_count,
            "perception": perception,
            "events": [{"step": "flat_process", "level": 0}],
            "level_crossings": [],
            "broadcasts": [],
            "mode": mode,
            "strange_loops_this_cycle": 0,
        }


# ============================================================================
# BASELINE REGISTRY
# ============================================================================

BASELINES = {
    "random": RandomBaseline,
    "threshold": ThresholdBaseline,
    "ema": EMABaseline,
    "flat": FlatHierarchy,
}


def create_baseline(name: str, **kwargs) -> BaselineEngine:
    """Create a baseline by name."""
    if name not in BASELINES:
        raise ValueError(f"Unknown baseline: {name}. Available: {list(BASELINES.keys())}")
    return BASELINES[name](**kwargs)


def run_baselines_on_benchmark(benchmark, seed: int = 42,
                                num_trials: int = 30) -> Dict[str, List]:
    """Run all baselines on a given benchmark."""
    from core.engine import StrangeLoopEngine

    results = {}

    # Ouroboros Loop (the system under test)
    results["ouroboros_loop"] = []
    for trial in range(num_trials):
        trial_seed = seed + trial * 1000
        engine = StrangeLoopEngine()
        result = benchmark.run(engine, trial_seed)
        result.trial = trial
        results["ouroboros_loop"].append(result)

    # Baselines
    for name, cls in BASELINES.items():
        results[name] = []
        for trial in range(num_trials):
            trial_seed = seed + trial * 1000
            # Baselines need the same interface
            # We wrap them to match what benchmarks expect
            baseline = cls(seed=trial_seed) if name == "random" else cls()
            # Baselines use the same self_model.confidence_states structure
            baseline_engine = baseline
            result = benchmark.run(baseline_engine, trial_seed)
            result.trial = trial
            results[name].append(result)

    return results
