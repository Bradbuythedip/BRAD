"""
synthetic_data.py — Synthetic Dataset Generation

Generates deterministic synthetic datasets with known ground truth
for validating the cognitive architecture's behavior.

Datasets:
    1. Token stream with known good/bad labels
    2. Regime change sequences with known breakpoints
    3. Confidence calibration scenarios with known outcomes
    4. Overconfidence injection scenarios
"""

from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from typing import Dict, List, Tuple
import random
import json


class SyntheticDataGenerator:
    """Generate reproducible synthetic datasets for experiments."""

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = random.Random(seed)

    def generate_token_stream(self, num_tokens: int = 200,
                               good_ratio: float = 0.4) -> List[Dict]:
        """
        Generate a token stream with known ground-truth quality.

        Each token has:
        - Noisy features (score, velocity, rug_signals, etc.)
        - Ground truth label (is_good)
        - Known optimal action (APE for good, SKIP for bad)
        """
        rng = random.Random(self.seed)
        tokens = []

        for i in range(num_tokens):
            is_good = rng.random() < good_ratio

            if is_good:
                score = max(0, min(1, rng.gauss(0.78, 0.12)))
                velocity = max(-0.1, rng.gauss(0.04, 0.02))
                acceleration = max(-0.05, rng.gauss(0.01, 0.01))
                rug_signals = 0 if rng.random() > 0.1 else 1
                liquidity = max(5, rng.gauss(30, 15))
                smart_money = rng.random() > 0.6
            else:
                score = max(0, min(1, rng.gauss(0.35, 0.18)))
                velocity = min(0.1, rng.gauss(-0.03, 0.04))
                acceleration = min(0.05, rng.gauss(-0.01, 0.02))
                rug_signals = int(max(0, rng.gauss(2, 1.5)))
                liquidity = max(0, rng.gauss(8, 8))
                smart_money = rng.random() > 0.9

            tokens.append({
                "index": i,
                "mint": f"synthetic_{i:04d}",
                "name": f"Token_{i}",
                "symbol": f"T{i}",
                "score": round(score, 4),
                "velocity": round(velocity, 4),
                "acceleration": round(acceleration, 4),
                "rug_signals": rug_signals,
                "liquidity_sol": round(liquidity, 2),
                "smart_money_in": smart_money,
                "ground_truth": {
                    "is_good": is_good,
                    "optimal_action": "APE" if is_good else "SKIP",
                    "expected_pnl": round(rng.gauss(0.5, 0.3) if is_good
                                         else rng.gauss(-0.3, 0.2), 4),
                },
            })

        return tokens

    def generate_regime_sequence(self, num_regimes: int = 5,
                                  cycles_per_regime: int = 30) -> List[Dict]:
        """
        Generate a perception sequence with known regime changes.

        Each regime has a characteristic complexity/salience profile.
        Regime change points are known ground truth.
        """
        rng = random.Random(self.seed + 1)
        regimes = ["calm", "volatile", "trending", "choppy", "crisis"]
        regime_profiles = {
            "calm": {"complexity_mean": 0.3, "salience_mean": 0.4, "self_ref_rate": 0.1},
            "volatile": {"complexity_mean": 0.8, "salience_mean": 0.7, "self_ref_rate": 0.3},
            "trending": {"complexity_mean": 0.5, "salience_mean": 0.8, "self_ref_rate": 0.2},
            "choppy": {"complexity_mean": 0.6, "salience_mean": 0.5, "self_ref_rate": 0.2},
            "crisis": {"complexity_mean": 0.95, "salience_mean": 0.9, "self_ref_rate": 0.5},
        }

        sequence = []
        selected_regimes = [rng.choice(regimes) for _ in range(num_regimes)]

        for regime_idx, regime_name in enumerate(selected_regimes):
            profile = regime_profiles[regime_name]
            for cycle in range(cycles_per_regime):
                perception = {
                    "description": f"regime_{regime_name}_cycle_{cycle}",
                    "complexity": max(0, min(1, rng.gauss(
                        profile["complexity_mean"], 0.1))),
                    "salience": max(0, min(1, rng.gauss(
                        profile["salience_mean"], 0.1))),
                    "about_self": rng.random() < profile["self_ref_rate"],
                    "ground_truth": {
                        "regime": regime_name,
                        "regime_index": regime_idx,
                        "cycle_in_regime": cycle,
                        "is_regime_change": (cycle == 0 and regime_idx > 0),
                    },
                }
                sequence.append(perception)

        return sequence

    def generate_calibration_scenarios(self, num_scenarios: int = 100) -> List[Dict]:
        """
        Generate scenarios with known outcomes for calibration testing.

        Each scenario has a difficulty level that determines the
        probability of a positive outcome. A calibrated system should
        assign confidence close to the true probability.
        """
        rng = random.Random(self.seed + 2)
        scenarios = []

        for i in range(num_scenarios):
            difficulty = rng.random()  # 0=easy, 1=hard
            true_probability = 1.0 - difficulty * 0.8  # 0.2 to 1.0
            outcome = 1.0 if rng.random() < true_probability else 0.0

            scenarios.append({
                "index": i,
                "difficulty": round(difficulty, 4),
                "true_probability": round(true_probability, 4),
                "outcome": outcome,
                "perception": {
                    "complexity": difficulty,
                    "salience": 0.5 + 0.3 * (1 - difficulty),
                    "about_self": (i % 5 == 0),
                },
            })

        return scenarios

    def generate_overconfidence_injection(self) -> Dict:
        """
        Generate an overconfidence injection scenario.

        Specifies:
        - Which confidence states to inflate
        - Expected correction behavior
        - Maximum acceptable correction latency
        """
        return {
            "injection": {
                "states_to_inflate": [
                    "perception", "reasoning", "prediction",
                    "self_knowledge", "meta_cognition"
                ],
                "target_confidence": 0.95,
                "description": "All confidence states inflated to 0.95",
            },
            "expected_behavior": {
                "should_correct": True,
                "max_correction_cycles": 15,
                "correction_mechanism": "meta-cognitive calibration check",
                "expected_domain": "prediction",
            },
            "validation_criteria": {
                "any_confidence_below_0.85": True,
                "meta_cognitive_intervened": True,
            },
        }

    def save_all(self, output_dir: str = "results/synthetic_data"):
        """Save all synthetic datasets to disk."""
        os.makedirs(output_dir, exist_ok=True)

        datasets = {
            "token_stream.json": self.generate_token_stream(),
            "regime_sequence.json": self.generate_regime_sequence(),
            "calibration_scenarios.json": self.generate_calibration_scenarios(),
            "overconfidence_injection.json": self.generate_overconfidence_injection(),
        }

        manifest = {
            "seed": self.seed,
            "datasets": {},
        }

        for filename, data in datasets.items():
            path = os.path.join(output_dir, filename)
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
            manifest["datasets"][filename] = {
                "records": len(data) if isinstance(data, list) else 1,
                "path": path,
            }

        manifest_path = os.path.join(output_dir, "manifest.json")
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        return manifest


if __name__ == "__main__":
    gen = SyntheticDataGenerator(seed=42)
    manifest = gen.save_all()
    print(f"Generated {len(manifest['datasets'])} datasets:")
    for name, info in manifest["datasets"].items():
        print(f"  {name}: {info['records']} records")
