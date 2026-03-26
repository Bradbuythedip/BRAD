"""
runner.py — Reproducible Experiment Runner

Provides deterministic, seeded execution of all experiments with
structured JSON output for analysis and reproduction.

Usage:
    from research.reproducibility.runner import ExperimentRunner
    runner = ExperimentRunner(seed=42, output_dir="results")
    runner.run_all()
"""

from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import json
import time
import random
import hashlib
import platform
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional
from datetime import datetime


@dataclass
class ExperimentConfig:
    """Configuration for a reproducible experiment run."""
    seed: int = 42
    num_trials: int = 30
    output_dir: str = "results"
    run_axiom_verification: bool = True
    run_blind_spot_proofs: bool = True
    run_ablation: bool = True
    run_benchmarks: bool = True
    run_statistical_tests: bool = True
    verbose: bool = True


@dataclass
class RunMetadata:
    """Metadata for experiment reproducibility."""
    timestamp: str = ""
    seed: int = 0
    num_trials: int = 0
    python_version: str = ""
    platform: str = ""
    run_hash: str = ""
    total_wall_time: float = 0.0

    @classmethod
    def create(cls, config: ExperimentConfig) -> RunMetadata:
        now = datetime.now()
        return cls(
            timestamp=now.isoformat(),
            seed=config.seed,
            num_trials=config.num_trials,
            python_version=sys.version,
            platform=platform.platform(),
            run_hash=hashlib.sha256(
                f"{config.seed}-{now.isoformat()}".encode()
            ).hexdigest()[:12],
        )


class ExperimentRunner:
    """
    Deterministic experiment runner with full reproducibility.

    Runs all experiments (axiom verification, blind spot proofs,
    ablation studies, benchmarks) with seeded randomness and
    saves structured results to JSON.
    """

    def __init__(self, config: ExperimentConfig = None):
        self.config = config or ExperimentConfig()
        self.metadata = RunMetadata.create(self.config)
        self.results = {}

    def run_all(self) -> Dict:
        """Run all configured experiments."""
        start = time.time()

        if self.config.verbose:
            print()
            print("=" * 70)
            print("  OUROBOROS LOOP — REPRODUCIBLE EXPERIMENT SUITE")
            print("=" * 70)
            print(f"  Seed: {self.config.seed}")
            print(f"  Trials: {self.config.num_trials}")
            print(f"  Run hash: {self.metadata.run_hash}")
            print("=" * 70)

        if self.config.run_axiom_verification:
            self._run_axiom_verification()

        if self.config.run_blind_spot_proofs:
            self._run_blind_spot_proofs()

        if self.config.run_ablation:
            self._run_ablation()

        if self.config.run_benchmarks:
            self._run_benchmarks()

        if self.config.run_statistical_tests:
            self._run_statistical_analysis()

        self.metadata.total_wall_time = time.time() - start

        # Save results
        self._save_results()

        if self.config.verbose:
            print()
            print("=" * 70)
            print(f"  Complete. Wall time: {self.metadata.total_wall_time:.1f}s")
            print(f"  Results saved to: {self.config.output_dir}/")
            print("=" * 70)
            print()

        return self.results

    def _run_axiom_verification(self):
        if self.config.verbose:
            print("\n  [1/5] Axiom Verification")
        from research.formal.axioms import verify_all_axioms, print_verification_report
        results = verify_all_axioms()
        if self.config.verbose:
            print_verification_report(results)
        self.results["axiom_verification"] = _serialize(results)

    def _run_blind_spot_proofs(self):
        if self.config.verbose:
            print("\n  [2/5] Blind Spot Proofs")
        from research.formal.blind_spot_proofs import (
            verify_all_blind_spot_proofs, print_blind_spot_report)
        results = verify_all_blind_spot_proofs()
        if self.config.verbose:
            print_blind_spot_report(results)
        self.results["blind_spot_proofs"] = _serialize(results)

    def _run_ablation(self):
        if self.config.verbose:
            print("\n  [3/5] Ablation Study")
        from research.experiments.ablation import AblationStudy
        study = AblationStudy(
            seed=self.config.seed,
            num_trials=self.config.num_trials
        )
        results = study.run(verbose=self.config.verbose)
        study.print_report(results)
        self.results["ablation"] = _serialize(results)

    def _run_benchmarks(self):
        if self.config.verbose:
            print("\n  [4/5] Cognitive Benchmarks")
        from research.experiments.benchmarks import BenchmarkSuite
        suite = BenchmarkSuite(
            seed=self.config.seed,
            num_trials=self.config.num_trials
        )
        results = suite.run(verbose=self.config.verbose)
        suite.print_report(results)
        # Convert BenchmarkResult objects to dicts
        serialized = {}
        for name, trials in results.items():
            serialized[name] = [
                {"metrics": t.metrics, "trial": t.trial,
                 "seed": t.seed, "wall_time": t.wall_time}
                for t in trials
            ]
        self.results["benchmarks"] = serialized

    def _run_statistical_analysis(self):
        if self.config.verbose:
            print("\n  [5/5] Statistical Analysis")

        if "ablation" not in self.results:
            if self.config.verbose:
                print("    Skipping (no ablation data)")
            return

        from research.experiments.statistical import (
            compare_conditions, print_comparison_table,
            descriptive_stats
        )

        ablation = self.results["ablation"]
        stats_results = {}

        # For each task, compare all conditions against FULL
        for task_name in next(iter(ablation.values())).keys():
            control_trials = ablation.get("full", {}).get(task_name, [])
            if not control_trials:
                continue

            # Determine primary metric
            primary = self._primary_metric(task_name)
            control_values = [t.get(primary, 0) for t in control_trials
                            if isinstance(t, dict)]

            if not control_values:
                continue

            conditions = {}
            for cond_name, tasks in ablation.items():
                if cond_name == "full":
                    continue
                trials = tasks.get(task_name, [])
                values = [t.get(primary, 0) for t in trials
                         if isinstance(t, dict)]
                if values:
                    conditions[cond_name] = values

            if conditions:
                comparison = compare_conditions(
                    control_values, conditions,
                    test="permutation",
                    seed=self.config.seed
                )
                if self.config.verbose:
                    print_comparison_table(comparison, f"{task_name}/{primary}")

                stats_results[task_name] = {
                    name: {
                        "p_value": r.p_value,
                        "effect_size": r.effect_size,
                        "ci_lower": r.ci_lower,
                        "ci_upper": r.ci_upper,
                        "significant": r.significant_05,
                    }
                    for name, r in comparison.items()
                }

        self.results["statistical_tests"] = stats_results

    def _primary_metric(self, task_name: str) -> str:
        return {
            "decision_accuracy": "accuracy",
            "adaptation_speed": "cycles_to_adapt",
            "confidence_calibration": "brier_score",
            "self_correction": "cycles_to_correct",
            "strange_loop_depth": "total_strange_loops",
        }.get(task_name, "accuracy")

    def _save_results(self):
        os.makedirs(self.config.output_dir, exist_ok=True)

        # Full results
        output = {
            "metadata": {
                "timestamp": self.metadata.timestamp,
                "seed": self.metadata.seed,
                "num_trials": self.metadata.num_trials,
                "python_version": self.metadata.python_version,
                "platform": self.metadata.platform,
                "run_hash": self.metadata.run_hash,
                "total_wall_time": self.metadata.total_wall_time,
            },
            "results": self.results,
        }

        path = os.path.join(self.config.output_dir, "experiment_results.json")
        with open(path, "w") as f:
            json.dump(output, f, indent=2, default=str)

        # Summary file
        summary_path = os.path.join(self.config.output_dir, "summary.txt")
        with open(summary_path, "w") as f:
            f.write("OUROBOROS LOOP — EXPERIMENT SUMMARY\n")
            f.write(f"Run: {self.metadata.run_hash}\n")
            f.write(f"Seed: {self.metadata.seed}\n")
            f.write(f"Trials: {self.metadata.num_trials}\n")
            f.write(f"Time: {self.metadata.total_wall_time:.1f}s\n")
            f.write(f"Date: {self.metadata.timestamp}\n")
            f.write("\nSections completed:\n")
            for section in self.results:
                f.write(f"  - {section}\n")


def _serialize(obj):
    """Recursively serialize objects for JSON."""
    if isinstance(obj, dict):
        return {str(k): _serialize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_serialize(v) for v in obj]
    if isinstance(obj, bool):
        return obj
    if isinstance(obj, (int, float, str)):
        return obj
    return str(obj)


if __name__ == "__main__":
    config = ExperimentConfig(
        seed=42,
        num_trials=30,
        output_dir="results",
        verbose=True,
    )
    runner = ExperimentRunner(config)
    runner.run_all()
