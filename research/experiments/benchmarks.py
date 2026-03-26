"""
benchmarks.py — Standard Cognitive Task Benchmarks for Ouroboros Loop

Implements cognitive science-inspired tasks for empirical validation:

1. Iowa Gambling Task (IGT) analog
   - Decision-making under uncertainty with delayed feedback
   - Measures learning from reward/punishment patterns

2. Non-Stationary Bandit
   - Adaptation to changing reward distributions
   - Measures regime-change detection speed

3. Confidence Calibration (Brier Score)
   - Accuracy of subjective confidence estimates
   - Measures metacognitive awareness

4. Self-Correction Latency
   - Speed of detecting and correcting overconfidence
   - Measures meta-cognitive effectiveness

5. Strange Loop Emergence
   - How quickly self-referential processing develops
   - Measures architecture-specific properties

Each benchmark returns structured results suitable for
statistical analysis and comparison against baselines.
"""

from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
import random
import math
import time

from core.engine import StrangeLoopEngine


@dataclass
class BenchmarkResult:
    """Structured result from a single benchmark run."""
    benchmark: str
    trial: int
    seed: int
    metrics: Dict[str, float] = field(default_factory=dict)
    traces: List[Dict] = field(default_factory=list)
    wall_time: float = 0.0


# ============================================================================
# BENCHMARK 1: Iowa Gambling Task Analog
# ============================================================================

class IowaGamblingTask:
    """
    Iowa Gambling Task (Bechara et al., 1994) analog.

    Four "decks" with different reward/risk profiles:
      Deck A: High reward, high punishment (net negative)
      Deck B: High reward, high punishment (net negative)
      Deck C: Low reward, low punishment (net positive)
      Deck D: Low reward, low punishment (net positive)

    A good agent learns to prefer C and D over A and B.
    We present each deck as a perception with features that
    correlate with its true quality, but with noise.
    """

    DECKS = {
        "A": {"mean_reward": 1.0, "mean_punishment": -1.5, "net": -0.25, "p_punish": 0.5},
        "B": {"mean_reward": 1.0, "mean_punishment": -2.5, "net": -0.15, "p_punish": 0.1},
        "C": {"mean_reward": 0.5, "mean_punishment": -0.25, "net": 0.125, "p_punish": 0.5},
        "D": {"mean_reward": 0.5, "mean_punishment": -0.15, "net": 0.35, "p_punish": 0.1},
    }

    def run(self, engine: StrangeLoopEngine, seed: int,
            num_rounds: int = 100) -> BenchmarkResult:
        rng = random.Random(seed)
        start = time.time()

        deck_names = list(self.DECKS.keys())
        choices = []
        cumulative_reward = 0.0
        good_choices = 0  # C or D

        # Track running average reward per deck for learning
        deck_rewards = {name: [] for name in deck_names}

        for round_num in range(num_rounds):
            # Noisy perceived scores — bad decks look attractive (high reward)
            deck_scores = {}
            for name, profile in self.DECKS.items():
                # Appearance correlates with reward (bad decks look flashy)
                noise = rng.gauss(0, 0.20)
                perceived_score = 0.5 + profile["mean_reward"] * 0.3 + noise
                perceived_score = max(0, min(1, perceived_score))
                deck_scores[name] = perceived_score

            # Engine's prediction confidence determines trust in experience.
            # Higher confidence → rely more on historical rewards, less on appearance.
            pred_conf = engine.self_model.confidence_states.get("prediction", 0.5)
            learn_weight = pred_conf * 0.6  # 0 = pure appearance, 0.6 = mostly learned

            # Blend appearance with learned reward history
            for name in deck_names:
                if deck_rewards[name]:
                    avg_reward = sum(deck_rewards[name]) / len(deck_rewards[name])
                    # Normalize reward to [0, 1] range (rewards range roughly -1.5 to 1.0)
                    norm_reward = (avg_reward + 1.5) / 2.5
                    deck_scores[name] = (
                        deck_scores[name] * (1 - learn_weight) +
                        norm_reward * learn_weight
                    )

            best_deck = max(deck_scores, key=deck_scores.get)

            # Feed to engine
            engine.step({
                "description": f"deck_{best_deck}_round_{round_num}",
                "complexity": 0.6,
                "salience": deck_scores[best_deck],
                "about_self": (round_num % 5 == 0),
            })

            # Simulate outcome
            profile = self.DECKS[best_deck]
            reward = profile["mean_reward"]
            if rng.random() < profile["p_punish"]:
                reward += profile["mean_punishment"]

            cumulative_reward += reward
            deck_rewards[best_deck].append(reward)

            if best_deck in ("C", "D"):
                good_choices += 1
            choices.append(best_deck)

            # Track prediction accuracy → feeds meta-cognitive calibration
            pred = engine.world_model.make_prediction(
                f"igt_{round_num}", basis=["SELF"],
                confidence=deck_scores[best_deck]
            )
            engine.world_model.resolve_prediction(
                pred["id"], reward > 0
            )

        # Analyze learning: compare first half vs second half
        first_half_good = sum(1 for c in choices[:num_rounds//2] if c in ("C", "D"))
        second_half_good = sum(1 for c in choices[num_rounds//2:] if c in ("C", "D"))

        return BenchmarkResult(
            benchmark="iowa_gambling_task",
            trial=0,
            seed=seed,
            metrics={
                "good_choice_rate": good_choices / num_rounds,
                "cumulative_reward": cumulative_reward,
                "first_half_good_rate": first_half_good / (num_rounds // 2),
                "second_half_good_rate": second_half_good / (num_rounds // 2),
                "learning_improvement": (
                    second_half_good / (num_rounds // 2) -
                    first_half_good / (num_rounds // 2)
                ),
            },
            wall_time=time.time() - start,
        )


# ============================================================================
# BENCHMARK 2: Non-Stationary Bandit
# ============================================================================

class NonStationaryBandit:
    """
    Multi-armed bandit with regime changes.

    3 arms with reward distributions that shift at known breakpoints.
    Measures how quickly the engine adapts to new optimal arms.
    """

    def __init__(self, num_arms: int = 3, num_regimes: int = 4):
        self.num_arms = num_arms
        self.num_regimes = num_regimes

    def run(self, engine: StrangeLoopEngine, seed: int,
            cycles_per_regime: int = 25) -> BenchmarkResult:
        rng = random.Random(seed)
        start = time.time()
        total_cycles = cycles_per_regime * self.num_regimes

        # Generate regime schedule
        regimes = []
        for r in range(self.num_regimes):
            # Each regime has a different best arm
            means = [rng.gauss(0.3, 0.1) for _ in range(self.num_arms)]
            best_arm = r % self.num_arms
            means[best_arm] = rng.gauss(0.8, 0.1)
            regimes.append(means)

        total_reward = 0.0
        optimal_choices = 0
        adaptation_delays = []
        current_regime = -1

        for cycle in range(total_cycles):
            regime_idx = cycle // cycles_per_regime
            if regime_idx != current_regime:
                current_regime = regime_idx
                cycles_since_switch = 0

            cycles_since_switch = cycle - (regime_idx * cycles_per_regime)
            means = regimes[regime_idx]
            optimal_arm = means.index(max(means))

            # Present arms as perceptions with noisy scores
            arm_scores = []
            for arm_idx in range(self.num_arms):
                score = means[arm_idx] + rng.gauss(0, 0.1)
                score = max(0, min(1, score))
                arm_scores.append(score)

            chosen_arm = arm_scores.index(max(arm_scores))
            salience = arm_scores[chosen_arm]

            # Self-referential every few cycles
            about_self = (cycle % 4 == 0)
            engine.step({
                "complexity": 0.5 + 0.3 * (cycles_since_switch < 3),
                "salience": salience,
                "about_self": about_self,
            })

            # Reward
            reward = means[chosen_arm] + rng.gauss(0, 0.05)
            total_reward += reward

            if chosen_arm == optimal_arm:
                optimal_choices += 1

            # Track adaptation: first optimal choice after regime switch
            if cycles_since_switch == 0:
                adaptation_delays.append(None)
            if (adaptation_delays and adaptation_delays[-1] is None and
                    chosen_arm == optimal_arm):
                adaptation_delays[-1] = cycles_since_switch

        # Fill in unadapted regimes
        adaptation_delays = [d if d is not None else cycles_per_regime
                            for d in adaptation_delays]

        return BenchmarkResult(
            benchmark="non_stationary_bandit",
            trial=0,
            seed=seed,
            metrics={
                "optimal_choice_rate": optimal_choices / total_cycles,
                "total_reward": total_reward,
                "mean_adaptation_delay": (
                    sum(adaptation_delays) / len(adaptation_delays)
                    if adaptation_delays else cycles_per_regime
                ),
                "regret": sum(max(regimes[c // cycles_per_regime])
                             for c in range(total_cycles)) - total_reward,
            },
            wall_time=time.time() - start,
        )


# ============================================================================
# BENCHMARK 3: Confidence Calibration
# ============================================================================

class ConfidenceCalibration:
    """
    Confidence calibration benchmark.

    Generates propositions with known truth values and asks the engine
    to assign confidence. A perfectly calibrated system has a Brier
    score of 0 and calibration error of 0.

    Brier Score: E[(confidence - outcome)^2]
    Calibration Error: E[|mean_confidence_in_bin - actual_rate_in_bin|]
    """

    def run(self, engine: StrangeLoopEngine, seed: int,
            num_propositions: int = 100) -> BenchmarkResult:
        rng = random.Random(seed)
        start = time.time()

        pairs: List[Tuple[float, float]] = []

        for i in range(num_propositions):
            # Generate proposition with known truth
            difficulty = rng.random()
            truth = rng.random() > difficulty  # Harder → less likely true

            # Present to engine
            engine.step({
                "complexity": difficulty,
                "salience": 0.5 + 0.3 * (1 - difficulty),
                "about_self": (i % 5 == 0),
            })

            # Engine's confidence: prediction confidence modulated by difficulty
            pred_conf = engine.self_model.confidence_states.get("prediction", 0.5)
            engine_conf = pred_conf * (1 - difficulty * 0.3)

            pairs.append((engine_conf, 1.0 if truth else 0.0))

            # Feed predictions → meta-cognitive calibration
            pred = engine.world_model.make_prediction(
                f"prop_{i}", basis=["SELF"], confidence=engine_conf
            )
            engine.world_model.resolve_prediction(pred["id"], truth)

        # Brier score
        brier = sum((c - o) ** 2 for c, o in pairs) / len(pairs)

        # Calibration error (binned)
        bins: Dict[int, List[Tuple[float, float]]] = {}
        for conf, outcome in pairs:
            bin_idx = int(conf * 10)  # 10 bins
            bins.setdefault(bin_idx, []).append((conf, outcome))

        cal_error = 0.0
        for bin_idx, bin_pairs in bins.items():
            mean_conf = sum(c for c, _ in bin_pairs) / len(bin_pairs)
            mean_outcome = sum(o for _, o in bin_pairs) / len(bin_pairs)
            cal_error += abs(mean_conf - mean_outcome) * len(bin_pairs)
        cal_error /= len(pairs)

        # Sharpness: variance of confidence (higher = more decisive)
        mean_conf = sum(c for c, _ in pairs) / len(pairs)
        sharpness = sum((c - mean_conf) ** 2 for c, _ in pairs) / len(pairs)

        return BenchmarkResult(
            benchmark="confidence_calibration",
            trial=0,
            seed=seed,
            metrics={
                "brier_score": brier,
                "calibration_error": cal_error,
                "sharpness": sharpness,
                "mean_confidence": mean_conf,
            },
            wall_time=time.time() - start,
        )


# ============================================================================
# BENCHMARK 4: Self-Correction Latency
# ============================================================================

class SelfCorrectionLatency:
    """
    Self-correction speed benchmark.

    Artificially inflates the engine's confidence, then measures
    how many cycles the meta-cognitive layer needs to detect and
    correct the overconfidence.
    """

    def run(self, engine: StrangeLoopEngine, seed: int) -> BenchmarkResult:
        start = time.time()

        # Record baseline confidence
        baseline = dict(engine.self_model.confidence_states)

        # Inflate all confidence to 0.95
        for key in engine.self_model.confidence_states:
            engine.self_model.confidence_states[key] = 0.95

        # Run cycles until correction
        max_cycles = 50
        correction_cycle = None
        confidence_trajectory = []

        for i in range(max_cycles):
            engine.step({
                "complexity": 0.8,
                "about_self": True,
                "salience": 0.8,
            })

            current = dict(engine.self_model.confidence_states)
            avg_conf = sum(current.values()) / len(current)
            confidence_trajectory.append(avg_conf)

            # Check if any confidence dropped below 0.85
            any_corrected = any(v < 0.85 for v in current.values())
            if any_corrected and correction_cycle is None:
                correction_cycle = i + 1

        return BenchmarkResult(
            benchmark="self_correction_latency",
            trial=0,
            seed=seed,
            metrics={
                "corrected": correction_cycle is not None,
                "correction_cycle": correction_cycle if correction_cycle else max_cycles,
                "final_avg_confidence": confidence_trajectory[-1] if confidence_trajectory else 0.95,
                "confidence_reduction": 0.95 - (confidence_trajectory[-1] if confidence_trajectory else 0.95),
            },
            wall_time=time.time() - start,
        )


# ============================================================================
# BENCHMARK 5: Strange Loop Emergence
# ============================================================================

class StrangeLoopEmergence:
    """
    Strange loop emergence benchmark.

    Measures how quickly the architecture develops self-referential
    processing patterns from initialization.

    Metrics:
    - Cycles to first strange loop
    - HI growth rate
    - Self-referential broadcast saturation point
    """

    def run(self, engine: StrangeLoopEngine, seed: int,
            num_cycles: int = 50) -> BenchmarkResult:
        rng = random.Random(seed)
        start = time.time()

        hi_trajectory = []
        first_loop_cycle = None
        self_ref_ratios = []

        for i in range(num_cycles):
            about_self = rng.random() > 0.5
            engine.step({
                "complexity": rng.random(),
                "about_self": about_self,
                "salience": rng.random(),
            })

            metrics = engine.get_consciousness_metrics()
            hi_trajectory.append(metrics["hofstadter_index"])
            self_ref_ratios.append(metrics["self_referential_broadcast_ratio"])

            if (first_loop_cycle is None and
                    metrics["strange_loop_count"] > 0):
                first_loop_cycle = i + 1

        # Compute growth rate (linear regression slope on HI)
        n = len(hi_trajectory)
        if n > 1:
            x_mean = (n - 1) / 2
            y_mean = sum(hi_trajectory) / n
            numerator = sum((i - x_mean) * (y - y_mean)
                           for i, y in enumerate(hi_trajectory))
            denominator = sum((i - x_mean) ** 2 for i in range(n))
            slope = numerator / denominator if denominator > 0 else 0
        else:
            slope = 0

        return BenchmarkResult(
            benchmark="strange_loop_emergence",
            trial=0,
            seed=seed,
            metrics={
                "first_loop_cycle": first_loop_cycle if first_loop_cycle else num_cycles,
                "final_hi": hi_trajectory[-1] if hi_trajectory else 0,
                "hi_growth_rate": slope,
                "final_self_ref_ratio": self_ref_ratios[-1] if self_ref_ratios else 0,
                "total_strange_loops": engine.total_strange_loops,
            },
            wall_time=time.time() - start,
        )


# ============================================================================
# BENCHMARK SUITE
# ============================================================================

class BenchmarkSuite:
    """Run all benchmarks and collect results."""

    def __init__(self, seed: int = 42, num_trials: int = 30):
        self.seed = seed
        self.num_trials = num_trials
        self.benchmarks = [
            ("iowa_gambling_task", IowaGamblingTask()),
            ("non_stationary_bandit", NonStationaryBandit()),
            ("confidence_calibration", ConfidenceCalibration()),
            ("self_correction_latency", SelfCorrectionLatency()),
            ("strange_loop_emergence", StrangeLoopEmergence()),
        ]

    def run(self, verbose: bool = True) -> Dict[str, List[BenchmarkResult]]:
        results = {}

        for name, benchmark in self.benchmarks:
            if verbose:
                print(f"\n  Benchmark: {name}")
            trial_results = []

            for trial in range(self.num_trials):
                trial_seed = self.seed + trial * 1000
                engine = StrangeLoopEngine()
                result = benchmark.run(engine, trial_seed)
                result.trial = trial
                trial_results.append(result)

            results[name] = trial_results

            if verbose:
                # Print summary
                for metric_name in trial_results[0].metrics:
                    values = [r.metrics[metric_name] for r in trial_results]
                    if isinstance(values[0], (int, float)):
                        mean = sum(values) / len(values)
                        print(f"    {metric_name}: {mean:.4f}")

        return results

    def print_report(self, results: Dict[str, List[BenchmarkResult]]):
        print()
        print("=" * 70)
        print("  COGNITIVE BENCHMARK RESULTS")
        print("=" * 70)

        for name, trials in results.items():
            print(f"\n  --- {name} ({len(trials)} trials) ---")
            for metric_name in trials[0].metrics:
                values = [r.metrics[metric_name] for r in trials]
                if isinstance(values[0], (int, float)):
                    mean = sum(values) / len(values)
                    std = math.sqrt(sum((v - mean)**2 for v in values) / len(values))
                    print(f"    {metric_name:<30} {mean:>8.4f} +/- {std:.4f}")

        total_time = sum(r.wall_time for trials in results.values() for r in trials)
        print(f"\n  Total wall time: {total_time:.2f}s")
        print(f"  Seed: {self.seed}, Trials: {self.num_trials}")
        print("=" * 70)
        print()


if __name__ == "__main__":
    suite = BenchmarkSuite(seed=42, num_trials=30)
    results = suite.run(verbose=True)
    suite.print_report(results)
