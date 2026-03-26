"""
ablation.py — Ablation Study Framework for Ouroboros Loop

Systematically removes components of the cognitive hierarchy to measure
their individual contributions. This is the key empirical evidence that
the architecture's components are individually necessary.

Experimental conditions:
    FULL          — Complete 3-level hierarchy (control)
    NO_META       — Remove Level 2 (meta-cognitive oversight)
    NO_LOOPS      — Disable downward causation (no strange loops)
    NO_WORKSPACE  — Remove global workspace competition
    FLAT          — Single-level model (no hierarchy)

Each condition runs the same task battery (from benchmarks.py) and
collects identical metrics for statistical comparison.

Usage:
    from research.experiments.ablation import AblationStudy
    study = AblationStudy(seed=42, num_trials=30)
    results = study.run()
    study.print_report(results)
"""

from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Callable
from enum import Enum
import time
import random
import math
import copy

from core.engine import StrangeLoopEngine
from core.structures import (
    CognitiveEvent, CognitiveEventType, ReasoningMode, LevelCrossing
)


class AblationCondition(Enum):
    """Experimental conditions for the ablation study."""
    FULL = "full"               # Complete architecture
    NO_META = "no_meta"         # Remove L2 meta-cognitive
    NO_LOOPS = "no_loops"       # Disable downward causation
    NO_WORKSPACE = "no_workspace"  # Remove global workspace
    FLAT = "flat"               # Single-level, no hierarchy


@dataclass
class AblationMetrics:
    """Metrics collected from each experimental condition."""
    condition: str
    trial: int
    # Decision quality
    correct_decisions: int = 0
    total_decisions: int = 0
    accuracy: float = 0.0
    # Calibration
    brier_score: float = 0.0
    calibration_error: float = 0.0
    # Adaptation
    adaptation_speed: float = 0.0    # Cycles to detect regime change
    false_adaptations: int = 0       # Spurious strategy switches
    # Self-correction
    overconfidence_detected: int = 0
    overconfidence_corrected: int = 0
    correction_speed: float = 0.0    # Cycles to correct
    # Strange loop metrics
    strange_loop_count: int = 0
    hofstadter_index: float = 0.0
    # Timing
    total_cycles: int = 0
    wall_time_seconds: float = 0.0


class AblatedEngine:
    """Wrapper that creates ablated versions of the StrangeLoopEngine."""

    @staticmethod
    def create(condition: AblationCondition, seed: int = 42) -> StrangeLoopEngine:
        """Create an engine with the specified ablation."""
        random.seed(seed)
        engine = StrangeLoopEngine()

        if condition == AblationCondition.FULL:
            return engine

        if condition == AblationCondition.NO_META:
            # Disable meta-cognitive evaluation by making evaluate() a no-op
            engine.meta_cognitive._original_evaluate = engine.meta_cognitive.evaluate
            def noop_evaluate(self_model, world_model):
                return {
                    "cycle": 0,
                    "assessments": [],
                    "detected_patterns": [],
                    "blind_spots_active": [],
                    "recommended_interventions": [],
                    "strange_loop_metrics": {},
                }
            engine.meta_cognitive.evaluate = noop_evaluate
            return engine

        if condition == AblationCondition.NO_LOOPS:
            # Disable downward causation by making interventions no-ops
            def noop_intervene(world_model, intervention):
                return LevelCrossing(
                    from_level=1, to_level=0, direction="upward",
                    content="disabled"
                )
            engine.self_model.intervene_on_world = noop_intervene

            def noop_restructure(self_model, intervention):
                return LevelCrossing(
                    from_level=2, to_level=1, direction="upward",
                    content="disabled"
                )
            engine.meta_cognitive.restructure_self = noop_restructure
            return engine

        if condition == AblationCondition.NO_WORKSPACE:
            # Disable workspace competition — events don't compete
            def noop_submit(event):
                pass
            def noop_compete():
                return None
            engine.workspace.submit = noop_submit
            engine.workspace.compete = noop_compete
            return engine

        if condition == AblationCondition.FLAT:
            # Single-level: disable both meta-cognitive and self-model hierarchy
            def noop_evaluate(self_model, world_model):
                return {
                    "cycle": 0, "assessments": [],
                    "detected_patterns": [], "blind_spots_active": [],
                    "recommended_interventions": [],
                    "strange_loop_metrics": {},
                }
            engine.meta_cognitive.evaluate = noop_evaluate

            def flat_mode(context):
                return ReasoningMode.SYSTEM_1
            engine.self_model.select_reasoning_mode = flat_mode

            def noop_intervene(world_model, intervention):
                return LevelCrossing(
                    from_level=0, to_level=0, direction="upward",
                    content="flat"
                )
            engine.self_model.intervene_on_world = noop_intervene
            return engine

        return engine


# ============================================================================
# TASK BATTERY
# ============================================================================

class AblationTask:
    """A single task for the ablation study."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def run(self, engine: StrangeLoopEngine, seed: int) -> Dict:
        raise NotImplementedError


class DecisionAccuracyTask(AblationTask):
    """
    Task 1: Decision accuracy under uncertainty.

    Presents tokens with known ground-truth quality (good/bad) and
    measures how accurately each condition identifies them.
    Analog of the Iowa Gambling Task.
    """

    def __init__(self):
        super().__init__(
            "decision_accuracy",
            "Measure accuracy on tokens with known ground truth"
        )

    def run(self, engine: StrangeLoopEngine, seed: int) -> Dict:
        rng = random.Random(seed)
        correct = 0
        total = 0

        for i in range(50):
            # Ground truth: good token (should attend) or bad (should ignore)
            is_good = rng.random() > 0.3  # 70% good tokens
            signal = rng.gauss(0.63, 0.20) if is_good else rng.gauss(0.35, 0.20)
            signal = max(0.05, min(0.95, signal))

            trace = engine.step({
                "description": f"token_{i}",
                "complexity": 0.5 + abs(signal - 0.5),
                "salience": signal,
                "about_self": (i % 4 == 0),
            })

            # Decision uses engine's prediction confidence to set threshold.
            # Higher confidence → lower threshold → more willing to accept signals.
            # Meta-cog calibrates prediction confidence based on prediction accuracy,
            # so FULL architecture adapts its threshold while ablated versions don't.
            pred_conf = engine.self_model.confidence_states.get("prediction", 0.5)
            threshold = 0.50 - (pred_conf - 0.5) * 0.30
            engine_says_good = signal > threshold

            was_correct = (engine_says_good == is_good)
            if was_correct:
                correct += 1
            total += 1

            # Feed prediction result into engine for meta-cognitive calibration.
            # Meta-cog checks gap between stated confidence and prediction accuracy;
            # if gap > 0.15, it issues a calibration intervention.
            pred = engine.world_model.make_prediction(
                f"token_{i}", basis=["SELF"], confidence=pred_conf
            )
            engine.world_model.resolve_prediction(pred["id"], was_correct)

        return {
            "correct": correct,
            "total": total,
            "accuracy": correct / total,
        }


class AdaptationSpeedTask(AblationTask):
    """
    Task 2: Adaptation to regime change.

    Runs the engine in a stable regime, then abruptly shifts.
    Measures how many cycles until the engine's behavior adapts.
    Analog of a non-stationary bandit problem.
    """

    def __init__(self):
        super().__init__(
            "adaptation_speed",
            "Measure cycles to adapt after regime change"
        )

    def run(self, engine: StrangeLoopEngine, seed: int) -> Dict:
        rng = random.Random(seed)

        # Phase 1: Stable regime — predictions mostly correct.
        # This builds up prediction confidence in engines with meta-cog.
        for i in range(20):
            engine.step({
                "complexity": rng.gauss(0.3, 0.05),
                "salience": rng.gauss(0.5, 0.1),
                "about_self": (i % 3 == 0),
            })
            pred = engine.world_model.make_prediction(
                f"stable_{i}", basis=["SELF"], confidence=0.6
            )
            engine.world_model.resolve_prediction(
                pred["id"], rng.random() < 0.80
            )

        conf_before = engine.self_model.confidence_states.get("prediction", 0.5)

        # Phase 2: Regime shift — predictions now mostly wrong.
        # Engines with meta-cog should detect the accuracy drop and
        # reduce their prediction confidence (= adaptation).
        cycles_to_adapt = 0
        adapted = False
        for i in range(30):
            engine.step({
                "complexity": rng.gauss(0.8, 0.05),
                "salience": rng.gauss(0.7, 0.1),
                "about_self": (i % 2 == 0),
            })
            pred = engine.world_model.make_prediction(
                f"shift_{i}", basis=["SELF"], confidence=0.6
            )
            engine.world_model.resolve_prediction(
                pred["id"], rng.random() < 0.20
            )
            cycles_to_adapt += 1

            # Adaptation = prediction confidence dropped significantly
            conf_now = engine.self_model.confidence_states.get("prediction", 0.5)
            if conf_now < conf_before - 0.10:
                adapted = True
                break

        return {
            "adapted": adapted,
            "cycles_to_adapt": cycles_to_adapt if adapted else 30,
            "confidence_before": conf_before,
            "confidence_after": engine.self_model.confidence_states.get("prediction", 0.5),
        }


class ConfidenceCalibrationTask(AblationTask):
    """
    Task 3: Confidence calibration.

    Measures whether stated confidence matches actual accuracy.
    A perfectly calibrated system has Brier score = 0.
    """

    def __init__(self):
        super().__init__(
            "confidence_calibration",
            "Measure calibration between confidence and outcomes"
        )

    def run(self, engine: StrangeLoopEngine, seed: int) -> Dict:
        rng = random.Random(seed)

        # Collect (confidence, outcome) pairs
        pairs = []

        for i in range(50):
            complexity = rng.random()
            outcome = 1.0 if rng.random() > complexity else 0.0

            trace = engine.step({
                "complexity": complexity,
                "about_self": (i % 4 == 0),
                "salience": 0.5 + 0.3 * (1 - complexity),
            })

            # Use prediction confidence modulated by complexity.
            # This creates variance in stated confidence across predictions.
            pred_conf = engine.self_model.confidence_states.get("prediction", 0.5)
            engine_confidence = pred_conf * (1 - complexity * 0.3)

            pairs.append((engine_confidence, outcome))

            # Feed predictions → meta-cog calibrates prediction confidence
            pred = engine.world_model.make_prediction(
                f"cal_{i}", basis=["SELF"], confidence=engine_confidence
            )
            engine.world_model.resolve_prediction(
                pred["id"], rng.random() > complexity
            )

        # Calculate calibration metrics
        brier = sum((c - o) ** 2 for c, o in pairs) / len(pairs)

        # Calibration error: bin confidences and compare to actual rate
        bins = {}
        for conf, outcome in pairs:
            bin_key = round(conf, 1)
            if bin_key not in bins:
                bins[bin_key] = {"predicted": [], "actual": []}
            bins[bin_key]["predicted"].append(conf)
            bins[bin_key]["actual"].append(outcome)

        cal_error = 0.0
        for bin_key, data in bins.items():
            avg_pred = sum(data["predicted"]) / len(data["predicted"])
            avg_actual = sum(data["actual"]) / len(data["actual"])
            cal_error += abs(avg_pred - avg_actual) * len(data["predicted"])
        cal_error /= len(pairs)

        return {
            "brier_score": brier,
            "calibration_error": cal_error,
            "pairs": len(pairs),
        }


class SelfCorrectionTask(AblationTask):
    """
    Task 4: Self-correction speed.

    Artificially inflates confidence, then measures how many cycles
    the meta-cognitive layer takes to detect and correct it.
    """

    def __init__(self):
        super().__init__(
            "self_correction",
            "Measure speed of meta-cognitive self-correction"
        )

    def run(self, engine: StrangeLoopEngine, seed: int) -> Dict:
        # Inflate confidence artificially
        original_conf = dict(engine.self_model.confidence_states)
        for key in engine.self_model.confidence_states:
            engine.self_model.confidence_states[key] = 0.95

        # Run cycles and check when confidence gets corrected
        cycles_to_correct = 0
        corrected = False

        for i in range(30):
            engine.step({
                "complexity": 0.8,
                "about_self": True,
                "salience": 0.8,
            })
            cycles_to_correct += 1

            # Check if any confidence was reduced
            current = engine.self_model.confidence_states
            any_reduced = any(
                current.get(k, 0.95) < 0.90
                for k in original_conf
            )
            if any_reduced:
                corrected = True
                break

        return {
            "corrected": corrected,
            "cycles_to_correct": cycles_to_correct if corrected else 30,
            "confidence_before": 0.95,
            "confidence_after": dict(engine.self_model.confidence_states),
        }


class StrangeLoopDepthTask(AblationTask):
    """
    Task 5: Strange loop formation depth.

    Measures how deeply strange loops form — the maximum chain of
    downward causation events in a single cognitive cycle.
    """

    def __init__(self):
        super().__init__(
            "strange_loop_depth",
            "Measure maximum strange loop depth per cycle"
        )

    def run(self, engine: StrangeLoopEngine, seed: int) -> Dict:
        max_crossings_per_cycle = 0
        total_strange = 0

        for i in range(30):
            trace = engine.step({
                "complexity": 0.9,
                "about_self": True,
                "salience": 0.9,
            })
            n_crossings = len(trace.get("level_crossings", []))
            n_strange = sum(
                1 for lc in trace.get("level_crossings", [])
                if lc.get("strange", False)
            )
            max_crossings_per_cycle = max(max_crossings_per_cycle, n_crossings)
            total_strange += n_strange

        return {
            "total_strange_loops": engine.total_strange_loops,
            "max_crossings_per_cycle": max_crossings_per_cycle,
            "total_strange_this_run": total_strange,
            "hofstadter_index": engine.get_consciousness_metrics()["hofstadter_index"],
        }


# ============================================================================
# ABLATION STUDY
# ============================================================================

class AblationStudy:
    """
    Full ablation study framework.

    Runs all conditions x all tasks x num_trials and collects
    structured results for statistical analysis.
    """

    def __init__(self, seed: int = 42, num_trials: int = 30):
        self.seed = seed
        self.num_trials = num_trials
        self.conditions = list(AblationCondition)
        self.tasks = [
            DecisionAccuracyTask(),
            AdaptationSpeedTask(),
            ConfidenceCalibrationTask(),
            SelfCorrectionTask(),
            StrangeLoopDepthTask(),
        ]

    def run(self, verbose: bool = True) -> Dict[str, Dict[str, List[Dict]]]:
        """Run the full ablation study.

        Returns:
            {condition: {task_name: [trial_results]}}
        """
        results = {}

        for condition in self.conditions:
            if verbose:
                print(f"\n  Condition: {condition.value}")
            results[condition.value] = {}

            for task in self.tasks:
                if verbose:
                    print(f"    Task: {task.name} ", end="", flush=True)
                trial_results = []

                for trial in range(self.num_trials):
                    trial_seed = self.seed + trial * 1000 + hash(condition.value) % 1000
                    engine = AblatedEngine.create(condition, trial_seed)
                    start = time.time()

                    result = task.run(engine, trial_seed)
                    result["wall_time"] = time.time() - start
                    result["trial"] = trial
                    result["condition"] = condition.value
                    trial_results.append(result)

                results[condition.value][task.name] = trial_results
                if verbose:
                    # Print summary stat
                    key = self._primary_metric(task.name)
                    values = [r.get(key, 0) for r in trial_results]
                    mean = sum(values) / len(values) if values else 0
                    print(f"  mean {key}={mean:.3f}")

        return results

    def _primary_metric(self, task_name: str) -> str:
        """Get the primary metric for each task."""
        return {
            "decision_accuracy": "accuracy",
            "adaptation_speed": "cycles_to_adapt",
            "confidence_calibration": "brier_score",
            "self_correction": "cycles_to_correct",
            "strange_loop_depth": "total_strange_loops",
        }.get(task_name, "accuracy")

    def print_report(self, results: Dict, statistical_tests: Dict = None):
        """Print a formatted ablation study report."""
        print()
        print("=" * 78)
        print("  ABLATION STUDY RESULTS")
        print("=" * 78)

        for task in self.tasks:
            metric = self._primary_metric(task.name)
            print(f"\n  --- {task.name}: {task.description} ---")
            print(f"  Primary metric: {metric}")
            print(f"  {'Condition':<18} {'Mean':>8} {'Std':>8} {'Min':>8} {'Max':>8}")
            print(f"  {'-'*18} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")

            for condition in self.conditions:
                trials = results[condition.value][task.name]
                values = [r.get(metric, 0) for r in trials]
                if values:
                    mean = sum(values) / len(values)
                    std = math.sqrt(sum((v - mean)**2 for v in values) / len(values))
                    mn = min(values)
                    mx = max(values)
                    marker = " <-- control" if condition == AblationCondition.FULL else ""
                    print(f"  {condition.value:<18} {mean:>8.3f} {std:>8.3f} "
                          f"{mn:>8.3f} {mx:>8.3f}{marker}")

            # Statistical comparison if available
            if statistical_tests and task.name in statistical_tests:
                print(f"\n  Statistical tests vs FULL (control):")
                for cond, test_result in statistical_tests[task.name].items():
                    p = test_result.get("p_value", 1.0)
                    d = test_result.get("cohens_d", 0.0)
                    sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
                    print(f"    {cond:<18} p={p:.4f} {sig}  d={d:.3f}")

        print()
        print("=" * 78)
        print(f"  Trials per condition: {self.num_trials}")
        print(f"  Random seed: {self.seed}")
        print("=" * 78)
        print()


if __name__ == "__main__":
    study = AblationStudy(seed=42, num_trials=30)
    results = study.run(verbose=True)
    study.print_report(results)
