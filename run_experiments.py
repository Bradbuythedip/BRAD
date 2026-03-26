#!/usr/bin/env python3
"""
run_experiments.py — Top-Level Experiment Runner

Entry point for reproducing all experiments in the Ouroboros Loop paper.

Usage:
    python run_experiments.py                  # Run all experiments
    python run_experiments.py --seed 42        # Custom seed
    python run_experiments.py --trials 30      # Custom trial count
    python run_experiments.py --quick          # Quick run (5 trials)
    python run_experiments.py --output results # Custom output directory

This script runs:
    1. Formal axiom verification
    2. Blind spot proof verification
    3. Ablation study (5 conditions x 5 tasks x N trials)
    4. Cognitive benchmarks (5 benchmarks x N trials)
    5. Statistical analysis (permutation tests, bootstrap CIs)
    6. Synthetic data generation
"""

import sys
import os
import argparse

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from research.reproducibility.runner import ExperimentRunner, ExperimentConfig
from research.reproducibility.synthetic_data import SyntheticDataGenerator


def main():
    parser = argparse.ArgumentParser(
        description="Ouroboros Loop — Reproducible Experiment Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run_experiments.py                  # Full run (30 trials)
    python run_experiments.py --quick          # Quick validation (5 trials)
    python run_experiments.py --seed 123       # Different seed
    python run_experiments.py --no-benchmarks  # Skip benchmarks
        """,
    )

    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed (default: 42)")
    parser.add_argument("--trials", type=int, default=30,
                        help="Number of trials per condition (default: 30)")
    parser.add_argument("--output", type=str, default="results",
                        help="Output directory (default: results)")
    parser.add_argument("--quick", action="store_true",
                        help="Quick run with 5 trials")
    parser.add_argument("--quiet", action="store_true",
                        help="Suppress verbose output")

    parser.add_argument("--no-axioms", action="store_true",
                        help="Skip axiom verification")
    parser.add_argument("--no-blind-spots", action="store_true",
                        help="Skip blind spot proofs")
    parser.add_argument("--no-ablation", action="store_true",
                        help="Skip ablation study")
    parser.add_argument("--no-benchmarks", action="store_true",
                        help="Skip cognitive benchmarks")
    parser.add_argument("--no-stats", action="store_true",
                        help="Skip statistical analysis")
    parser.add_argument("--no-synthetic", action="store_true",
                        help="Skip synthetic data generation")

    args = parser.parse_args()

    if args.quick:
        args.trials = 5

    # Generate synthetic data first
    if not args.no_synthetic:
        print("\n  Generating synthetic datasets...")
        gen = SyntheticDataGenerator(seed=args.seed)
        data_dir = os.path.join(args.output, "synthetic_data")
        manifest = gen.save_all(output_dir=data_dir)
        print(f"  Generated {len(manifest['datasets'])} datasets in {data_dir}/")

    # Run experiment suite
    config = ExperimentConfig(
        seed=args.seed,
        num_trials=args.trials,
        output_dir=args.output,
        run_axiom_verification=not args.no_axioms,
        run_blind_spot_proofs=not args.no_blind_spots,
        run_ablation=not args.no_ablation,
        run_benchmarks=not args.no_benchmarks,
        run_statistical_tests=not args.no_stats,
        verbose=not args.quiet,
    )

    runner = ExperimentRunner(config)
    results = runner.run_all()

    # Print summary
    sections = list(results.keys())
    print(f"\n  Completed {len(sections)} experiment sections:")
    for s in sections:
        print(f"    - {s}")
    print(f"\n  Results saved to: {args.output}/")
    print(f"  To compile the paper:")
    print(f"    cd research/paper && pdflatex paper_skeleton && bibtex paper_skeleton && pdflatex paper_skeleton")
    print()


if __name__ == "__main__":
    main()
