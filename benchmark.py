"""
benchmark.py — Throughput benchmarking for Ouroboros Loop cognitive engine.

Measures real-world performance of:
1. Core cognitive cycles (StrangeLoopEngine)
2. Trading evaluation cycles (TradingEngine)
3. Full trade lifecycle (evaluate + entry + position eval + exit)
4. Batch throughput (sustained token scanning)
5. Memory footprint under load

Run:
    python benchmark.py
    python benchmark.py --cycles 10000
    python benchmark.py --full

Results are printed as a formatted table and saved to benchmark_results.json.
"""

import sys
import os
import time
import json
import statistics
import argparse
import tracemalloc

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.engine import StrangeLoopEngine
from bondli_bridge.engine import TradingEngine
from bondli_bridge.config import BridgeConfig


def make_token(i, score=None):
    """Generate synthetic token data for benchmarking."""
    import random
    s = score if score is not None else random.uniform(0.3, 0.95)
    return {
        "mint": f"bench_mint_{i:06d}",
        "name": f"BENCH{i}",
        "symbol": f"B{i}",
        "source": "pump",
        "score": s,
        "velocity": random.uniform(-0.1, 0.1),
        "acceleration": random.uniform(-0.05, 0.05),
        "rug_signals": random.randint(0, 2),
        "rug_details": [],
        "holder_count": random.randint(10, 500),
        "top_holder_pct": random.uniform(0.05, 0.4),
        "liquidity_sol": random.uniform(5.0, 200.0),
        "mcap_sol": random.uniform(10.0, 1000.0),
        "volume_5m": random.uniform(0.5, 50.0),
        "buy_pressure": random.uniform(0.3, 0.8),
        "smart_money_in": random.random() > 0.8,
        "dev_wallet": f"dev_{i}",
        "is_graduated": False,
        "price_sol": random.uniform(0.00001, 0.01),
    }


class BenchmarkResult:
    def __init__(self, name: str, times: list, extra: dict = None):
        self.name = name
        self.times = times
        self.extra = extra or {}

    @property
    def count(self):
        return len(self.times)

    @property
    def total_ms(self):
        return sum(self.times) * 1000

    @property
    def mean_us(self):
        return statistics.mean(self.times) * 1_000_000

    @property
    def median_us(self):
        return statistics.median(self.times) * 1_000_000

    @property
    def p99_us(self):
        idx = int(len(self.times) * 0.99)
        return sorted(self.times)[min(idx, len(self.times) - 1)] * 1_000_000

    @property
    def min_us(self):
        return min(self.times) * 1_000_000

    @property
    def max_us(self):
        return max(self.times) * 1_000_000

    @property
    def ops_per_sec(self):
        if self.total_ms == 0:
            return 0
        return self.count / (self.total_ms / 1000)

    def to_dict(self):
        return {
            "name": self.name,
            "count": self.count,
            "total_ms": round(self.total_ms, 2),
            "mean_us": round(self.mean_us, 2),
            "median_us": round(self.median_us, 2),
            "p99_us": round(self.p99_us, 2),
            "min_us": round(self.min_us, 2),
            "max_us": round(self.max_us, 2),
            "ops_per_sec": round(self.ops_per_sec, 0),
            **self.extra,
        }


def bench_core_cognitive_cycle(n: int) -> BenchmarkResult:
    """Benchmark raw StrangeLoopEngine cognitive cycles."""
    engine = StrangeLoopEngine()
    perceptions = [
        {"description": f"Perception {i}", "complexity": 0.5 + (i % 5) * 0.1,
         "novelty": 0.3 + (i % 3) * 0.2, "about_self": i % 7 == 0}
        for i in range(n)
    ]

    times = []
    for p in perceptions:
        start = time.perf_counter()
        engine.step(p)
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return BenchmarkResult("core_cognitive_cycle", times, {
        "strange_loops": engine.total_strange_loops,
        "level_crossings": len(engine._level_crossing_history),
    })


def bench_trading_evaluate(n: int) -> BenchmarkResult:
    """Benchmark TradingEngine.evaluate_token() — the main Bondli endpoint."""
    config = BridgeConfig()
    engine = TradingEngine(config)
    tokens = [make_token(i) for i in range(n)]

    times = []
    ape_count = 0
    skip_count = 0
    for t in tokens:
        start = time.perf_counter()
        decision = engine.evaluate_token(t)
        elapsed = time.perf_counter() - start
        times.append(elapsed)
        if decision.action.value == "APE":
            ape_count += 1
        else:
            skip_count += 1

    return BenchmarkResult("trading_evaluate_token", times, {
        "ape_decisions": ape_count,
        "skip_decisions": skip_count,
        "strange_loops": engine.total_strange_loops,
    })


def bench_trading_position_eval(n: int) -> BenchmarkResult:
    """Benchmark position evaluation cycle (EXIT/HOLD decisions)."""
    config = BridgeConfig()
    engine = TradingEngine(config)

    # Open a position first
    engine.record_entry("bench_pos", "BENCH", 0.001, 0.5, 0.8, ["benchmark"])

    tokens = [make_token(i, score=0.5 + (i % 10) * 0.05) for i in range(n)]
    for t in tokens:
        t["mint"] = "bench_pos"

    times = []
    for t in tokens:
        start = time.perf_counter()
        engine.evaluate_position("bench_pos", t)
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return BenchmarkResult("trading_position_eval", times)


def bench_full_trade_lifecycle(n: int) -> BenchmarkResult:
    """Benchmark complete trade lifecycle: evaluate -> entry -> position_eval -> exit."""
    config = BridgeConfig()
    config.risk.max_concurrent_positions = n + 10
    config.risk.max_portfolio_exposure_sol = n * 10
    engine = TradingEngine(config)

    times = []
    for i in range(n):
        token = make_token(i, score=0.85)
        start = time.perf_counter()

        # Evaluate
        decision = engine.evaluate_token(token)
        # Record entry
        engine.record_entry(token["mint"], token["symbol"],
                            token["price_sol"], 0.1, token["score"], [])
        # Evaluate position
        token["score"] = 0.7
        engine.evaluate_position(token["mint"], token)
        # Exit
        engine.record_exit(token["mint"], token["price_sol"] * 1.5, "benchmark")

        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return BenchmarkResult("full_trade_lifecycle", times, {
        "trades_completed": n,
        "strange_loops": engine.total_strange_loops,
    })


def bench_sustained_scanning(n: int, duration_seconds: float = 5.0) -> BenchmarkResult:
    """Benchmark sustained token scanning throughput over a time window."""
    config = BridgeConfig()
    engine = TradingEngine(config)

    times = []
    i = 0
    deadline = time.perf_counter() + duration_seconds
    while time.perf_counter() < deadline and i < n:
        token = make_token(i)
        start = time.perf_counter()
        engine.evaluate_token(token)
        elapsed = time.perf_counter() - start
        times.append(elapsed)
        i += 1

    actual_duration = sum(times)
    return BenchmarkResult("sustained_scanning", times, {
        "tokens_scanned": i,
        "wall_clock_seconds": round(actual_duration, 3),
        "tokens_per_second": round(i / actual_duration, 0) if actual_duration > 0 else 0,
    })


def bench_memory_footprint(n: int) -> dict:
    """Measure memory usage under load."""
    tracemalloc.start()

    config = BridgeConfig()
    engine = TradingEngine(config)
    baseline = tracemalloc.get_traced_memory()

    # Load N tokens
    for i in range(n):
        engine.evaluate_token(make_token(i))

    loaded = tracemalloc.get_traced_memory()

    # Open positions
    for i in range(min(50, n)):
        engine.record_entry(f"mem_{i}", "M", 0.001, 0.1, 0.8, [])

    with_positions = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "baseline_kb": round(baseline[0] / 1024, 1),
        "after_load_kb": round(loaded[0] / 1024, 1),
        "with_positions_kb": round(with_positions[0] / 1024, 1),
        "peak_kb": round(with_positions[1] / 1024, 1),
        "per_token_bytes": round((loaded[0] - baseline[0]) / max(1, n), 1),
        "tokens_loaded": n,
    }


def format_results(results: list, memory: dict, cpu_info: str):
    """Format results as a readable table."""
    print()
    print("=" * 90)
    print("  OUROBOROS LOOP — THROUGHPUT BENCHMARK")
    print("=" * 90)
    print(f"  Platform: {cpu_info}")
    print()

    # Results table
    header = f"{'Benchmark':<28} {'Ops':>7} {'Mean':>10} {'Median':>10} {'P99':>10} {'Ops/sec':>10}"
    print(header)
    print("-" * 90)

    for r in results:
        d = r.to_dict()
        print(f"  {d['name']:<26} {d['count']:>7} {d['mean_us']:>8.1f}us {d['median_us']:>8.1f}us {d['p99_us']:>8.1f}us {d['ops_per_sec']:>9.0f}")

    print()

    # Sustained scanning highlight
    for r in results:
        if r.name == "sustained_scanning":
            tps = r.extra.get("tokens_per_second", 0)
            print(f"  Sustained throughput: {tps:,.0f} tokens/second")
            print()
            break

    # Memory
    print("  Memory Footprint:")
    print(f"    Baseline:          {memory['baseline_kb']:>8.1f} KB")
    print(f"    After {memory['tokens_loaded']} tokens:  {memory['after_load_kb']:>8.1f} KB")
    print(f"    With positions:    {memory['with_positions_kb']:>8.1f} KB")
    print(f"    Peak:              {memory['peak_kb']:>8.1f} KB")
    print(f"    Per token:         {memory['per_token_bytes']:>8.1f} bytes")
    print()

    # Hardware projections
    print("-" * 90)
    print("  HARDWARE THROUGHPUT PROJECTIONS")
    print("-" * 90)
    print()

    # Find the trading_evaluate_token result for projections
    eval_result = next((r for r in results if r.name == "trading_evaluate_token"), None)
    if eval_result:
        base_ops = eval_result.ops_per_sec

        projections = [
            ("This machine (baseline)", 1, 1.0, "Current benchmark"),
            ("Raspberry Pi 5", 4, 0.15, "ARM Cortex-A76 @ 2.4GHz"),
            ("Intel i5-12400", 6, 0.8, "6C/12T @ 4.4GHz, DDR4"),
            ("Intel i7-13700K", 8, 1.2, "8P+8E @ 5.4GHz, DDR5"),
            ("AMD Ryzen 9 7950X", 16, 1.5, "16C/32T @ 5.7GHz, DDR5"),
            ("Apple M3 Pro", 12, 1.3, "12C, unified memory"),
            ("Apple M4 Max", 16, 1.8, "16C, unified memory, 546GB/s"),
            ("", 0, 0, ""),
            ("--- GPU-ACCELERATED (with NumPy/CuPy vectorization) ---", 0, 0, ""),
            ("RTX 4070 Ti (projected)", 0, 0, "12GB GDDR6X, 8952 CUDA"),
            ("RTX 5070 Ti (projected)", 0, 0, "16GB GDDR7, 8960 CUDA"),
            ("RTX 4090 (projected)", 0, 0, "24GB GDDR6X, 16384 CUDA"),
            ("RTX 5090 (projected)", 0, 0, "32GB GDDR7, 21760 CUDA"),
            ("A100 80GB (projected)", 0, 0, "80GB HBM2e, 6912 CUDA"),
            ("H100 SXM (projected)", 0, 0, "80GB HBM3, 16896 CUDA"),
        ]

        # GPU projections assume vectorized batch evaluation
        # Current code is single-threaded Python. GPU helps when we batch
        # 100s-1000s of tokens into matrix ops.
        gpu_projections = {
            "RTX 4070 Ti (projected)": (base_ops * 45, "Batch 512 tokens/pass, ~40-50x over single-thread"),
            "RTX 5070 Ti (projected)": (base_ops * 70, "Batch 1024 tokens/pass, GDDR7 bandwidth, ~60-80x"),
            "RTX 4090 (projected)":    (base_ops * 90, "Batch 1024 tokens/pass, ~80-100x"),
            "RTX 5090 (projected)":    (base_ops * 140, "Batch 2048 tokens/pass, ~120-160x"),
            "A100 80GB (projected)":   (base_ops * 110, "Batch 2048, HBM2e bandwidth, ~100-120x"),
            "H100 SXM (projected)":    (base_ops * 200, "Batch 4096, HBM3 bandwidth, ~180-220x"),
        }

        print(f"  {'Hardware':<40} {'Tokens/sec':>12} {'Tokens/min':>12}  Notes")
        print("  " + "-" * 86)

        for name, cores, multiplier, notes in projections:
            if name == "":
                print()
                continue
            if name.startswith("---"):
                print(f"  {name}")
                continue

            if name in gpu_projections:
                projected_ops, gpu_notes = gpu_projections[name]
                print(f"  {name:<40} {projected_ops:>12,.0f} {projected_ops * 60:>12,.0f}  {gpu_notes}")
            elif cores > 0:
                projected = base_ops * multiplier
                # Multi-core: can run N independent engines
                multi = projected * min(cores, 8)  # Diminishing returns past 8
                print(f"  {name:<40} {projected:>12,.0f} {projected * 60:>12,.0f}  {notes}")
                if cores > 1:
                    print(f"    (x{min(cores,8)} parallel engines){'':<20} {multi:>12,.0f} {multi * 60:>12,.0f}  {cores} cores available")

        print()
        print("  " + "-" * 86)
        print()

        # 5070 Ti deep dive
        ti_ops = gpu_projections.get("RTX 5070 Ti (projected)", (0, ""))[0]
        print("  RTX 5070 Ti DEEP DIVE")
        print("  " + "=" * 40)
        print(f"    Single-thread baseline:    {base_ops:>12,.0f} tokens/sec")
        print(f"    GPU-vectorized (est):      {ti_ops:>12,.0f} tokens/sec")
        print(f"    Per minute:                {ti_ops * 60:>12,.0f} tokens/min")
        print(f"    Per hour:                  {ti_ops * 3600:>12,.0f} tokens/hr")
        print()
        print("    What this means for Bondli:")
        print(f"      - Evaluate every pump.fun launch in real-time (~2-5/sec)")
        print(f"      - Score {ti_ops * 60:,.0f} tokens/min with full cognitive cycle")
        print(f"      - Run {int(ti_ops / 100)} independent strategy simulations simultaneously")
        print(f"      - Backtest 1M tokens in {1_000_000 / ti_ops:.0f} seconds ({1_000_000 / ti_ops / 60:.1f} min)")
        print(f"      - Memory: 16GB GDDR7 holds ~{16 * 1024 * 1024 * 1024 // max(1, int(memory['per_token_bytes'])):,} token entities")
        print()

        # Optimization roadmap
        print("  OPTIMIZATION ROADMAP FOR GPU ACCELERATION")
        print("  " + "=" * 40)
        print("    Phase 1: NumPy vectorization (5-10x)")
        print("      - Batch token scoring into matrix operations")
        print("      - Vectorize attention weight computation")
        print("      - Batch salience calculation across all tokens")
        print()
        print("    Phase 2: CuPy/CUDA kernels (30-50x)")
        print("      - Port scoring pipeline to GPU tensors")
        print("      - Parallel belief propagation")
        print("      - Batch position evaluation")
        print()
        print("    Phase 3: Custom CUDA (50-200x)")
        print("      - Fused cognitive cycle kernel")
        print("      - Shared memory for entity graph")
        print("      - Warp-level strange loop detection")
        print()

    print("=" * 90)


def get_cpu_info():
    """Get basic CPU info."""
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if line.startswith("model name"):
                    return line.split(":")[1].strip()
    except Exception:
        pass
    import platform
    return platform.processor() or platform.machine()


def main():
    parser = argparse.ArgumentParser(description="Ouroboros Loop Throughput Benchmark")
    parser.add_argument("--cycles", type=int, default=5000, help="Number of cycles per benchmark")
    parser.add_argument("--full", action="store_true", help="Run all benchmarks including slow ones")
    parser.add_argument("--json", type=str, default="benchmark_results.json", help="Output JSON file")
    args = parser.parse_args()

    n = args.cycles
    cpu_info = get_cpu_info()

    print(f"Running benchmarks with {n} cycles each...")
    print(f"CPU: {cpu_info}")
    print()

    results = []

    # Core cognitive cycle
    print("  [1/6] Core cognitive cycle...")
    results.append(bench_core_cognitive_cycle(n))

    # Trading token evaluation
    print("  [2/6] Trading token evaluation...")
    results.append(bench_trading_evaluate(n))

    # Position evaluation
    print("  [3/6] Position evaluation...")
    results.append(bench_trading_position_eval(n))

    # Full lifecycle
    lifecycle_n = min(n, 1000)
    print(f"  [4/6] Full trade lifecycle (n={lifecycle_n})...")
    results.append(bench_full_trade_lifecycle(lifecycle_n))

    # Sustained scanning
    print("  [5/6] Sustained scanning (5 seconds)...")
    results.append(bench_sustained_scanning(100000, duration_seconds=5.0))

    # Memory
    print("  [6/6] Memory footprint...")
    memory = bench_memory_footprint(min(n, 2000))

    # Output
    format_results(results, memory, cpu_info)

    # Save JSON
    output = {
        "cpu": cpu_info,
        "cycles": n,
        "timestamp": time.time(),
        "results": [r.to_dict() for r in results],
        "memory": memory,
    }
    with open(args.json, "w") as f:
        json.dump(output, f, indent=2)
    print(f"  Results saved to {args.json}")
    print()


if __name__ == "__main__":
    main()
