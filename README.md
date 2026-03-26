# Ouroboros Loop

**Self-Referential Recursive Cognitive Architecture with Formal Guarantees**

A computational implementation of Hofstadter's strange loop theory of consciousness, with verified axioms, proven blind spots, and empirical validation. Applied to autonomous trading intelligence via Bondli integration.

---

## Overview

Ouroboros Loop implements a three-level cognitive hierarchy where higher levels monitor and restructure lower levels (downward causation), forming a recursive self-referential loop. Named after the ancient symbol of the serpent consuming its own tail, the architecture embodies the principle that self-reference creates emergent cognitive properties.

### Architecture

```
Level 2: Meta-Cognitive Loop (MC)        ← monitors + corrects L1, L0
    | (modifies confidence, strategy)       detects blind spots
Level 1: Self Model (SM)                 ← tracks internal state
    | (modifies attention, beliefs)         chooses processing mode
Level 0: World Model (WM)               ← maintains beliefs + SELF entity
    ^ (observes self as entity)             self-referential fixed point
```

The loop closes when Level 0 perceives an entity "SELF" that Level 1 reasons about, which Level 2 evaluates, which modifies Level 1, which modifies Level 0's representation of "SELF" — a genuine strange loop.

### Key Properties

- **Formally verified**: 17 axioms verified programmatically (boundedness, monotonicity, downward causation, fixed points)
- **Proven limits**: 3 blind spots reduced to Godel's Incompleteness, Halting Problem, and the Hard Problem of Consciousness
- **Empirically validated**: Ablation studies (5 conditions, 30 trials) with permutation tests and bootstrap CIs
- **Self-referential**: Models itself as an entity in its own world model (representational fixed point)
- **Quantifiable**: Cognitive coherence measured via Hofstadter Index (0.0-1.0)
- **Zero dependencies**: Core engine and full research suite require only Python's standard library

---

## Repository Structure

```
brad/
├── core/                          # Cognitive engine (DO NOT MODIFY for Bondli compat)
│   ├── engine.py                  #   StrangeLoopEngine — main cognitive loop
│   ├── structures.py              #   Data structures (CognitiveEvent, Perception)
│   ├── global_workspace.py        #   Baars' Global Workspace (priority broadcasting)
│   ├── self_model.py              #   Level 1: Self-model (confidence, mode selection)
│   ├── world_model.py             #   Level 0: World model (beliefs, SELF entity)
│   └── meta_cognitive.py          #   Level 2: Meta-cognitive loop (blind spots, calibration)
│
├── bondli_bridge/                 # Trading brain — plug-and-play Bondli integration
│   ├── server.py                  #   FastAPI server (port 8421)
│   ├── engine.py                  #   CognitiveTradingEngine
│   ├── decisions.py               #   APE/SKIP/EXIT/HOLD decision logic
│   ├── market_world.py            #   Market-aware world model
│   ├── trading_self.py            #   Trading self-model (5 strategies)
│   ├── trading_meta.py            #   Trading meta-cognition (overconfidence, revenge trading)
│   ├── positions.py               #   Position tracking + PnL
│   ├── risk.py                    #   Half-Kelly position sizing
│   ├── config.py                  #   Configuration
│   ├── INTEGRATION.md             #   Complete API reference
│   └── tests/test_bridge.py       #   55 integration tests
│
├── research/                      # Formal foundations + empirical validation
│   ├── formal/
│   │   ├── axioms.py              #   17 verified axioms (HI bounds, DC, workspace, fixed points)
│   │   └── blind_spot_proofs.py   #   3 impossibility proofs (Godel, Turing, Chalmers)
│   ├── experiments/
│   │   ├── ablation.py            #   Ablation study (5 conditions x 5 tasks x N trials)
│   │   ├── benchmarks.py          #   Cognitive benchmarks (IGT, bandit, calibration)
│   │   ├── baselines.py           #   Baseline models (random, threshold, EMA, flat)
│   │   └── statistical.py         #   Non-parametric stats (permutation, bootstrap, Mann-Whitney)
│   ├── reproducibility/
│   │   ├── runner.py              #   Deterministic experiment runner
│   │   └── synthetic_data.py      #   Synthetic datasets with known ground truth
│   └── paper/
│       ├── paper_skeleton.tex     #   LaTeX paper skeleton (theorems, proofs, tables)
│       └── bibliography.bib       #   22 academic references
│
├── bot/                           # Autonomous Twitter agent
│   ├── brad_bot.py                #   Bot main loop
│   ├── tweet_generator.py         #   Cognitive state → tweet generation
│   └── config.example.json        #   API key template
│
├── run_experiments.py             #   Top-level experiment entry point
├── demo.py                        #   Demo: watch the engine think
├── interactive.py                 #   REPL: explore cognitive state
├── visualize.py                   #   Terminal visualization of strange loops
├── benchmark.py                   #   Throughput benchmarking
├── test_suite.py                  #   37 core architecture tests
│
├── ARCHITECTURE.md                #   Technical architecture deep dive
├── DEPLOYMENT.md                  #   Production deployment guide
├── CONTRIBUTING.md                #   Contribution guidelines
├── Dockerfile                     #   Container build
├── docker-compose.yml             #   Multi-service orchestration
└── LICENSE                        #   MIT License
```

---

## Quick Start

### Requirements

- Python 3.7+
- No external dependencies for core engine or research suite
- `fastapi`, `uvicorn`, `pydantic` only needed for Bondli bridge

### Installation

```bash
git clone https://github.com/Bradbuythedip/brad.git
cd brad
```

### Run the Demo

```bash
python3 demo.py
```

### Run Tests

```bash
# Core architecture tests (37 tests)
python3 test_suite.py

# Bondli bridge tests (55 tests)
python3 -m unittest bondli_bridge.tests.test_bridge
```

### Run the Full Research Suite

```bash
# Full run (30 trials per condition, ~2 min)
python3 run_experiments.py

# Quick validation (5 trials, ~2 sec)
python3 run_experiments.py --quick

# Custom seed and output
python3 run_experiments.py --seed 123 --trials 50 --output my_results
```

This runs all 5 phases: axiom verification, blind spot proofs, ablation study, cognitive benchmarks, and statistical analysis. Results are saved as structured JSON to the output directory.

---

## Usage

### As a Library

```python
from core.engine import StrangeLoopEngine

engine = StrangeLoopEngine()

# Process a self-referential perception
trace = engine.step({
    "description": "Evaluating own reasoning process",
    "about_self": True,
    "confidence": 0.7
})

# Get cognitive metrics
metrics = engine.get_consciousness_metrics()
print(f"Hofstadter Index: {metrics['hofstadter_index']:.3f}")
print(f"Strange loops: {metrics['strange_loop_count']}")
print(f"Processing mode: {trace['mode']}")

# Full state inspection
state = engine.get_full_state()
```

### Interactive Mode

```bash
python3 interactive.py
```

Commands: `step <thought>`, `metrics`, `loops`, `status`, `self`, `limits`, `help`

### Visualization

```bash
python3 visualize.py
```

---

## Formal Foundations

The research framework (`research/`) provides the formal mathematical backbone for the architecture. Everything runs with zero external dependencies.

### Axiom Verification

17 axioms verified programmatically across 6 groups:

| Group | Axioms | What It Verifies |
|-------|--------|------------------|
| Workspace (B1-B3) | 4 | Capacity bounds, priority ordering, self-ref detection |
| Downward Causation L2→L1 (DC1-DC3) | 3 | Meta-cognitive loop modifies self-model |
| Downward Causation L1→L0 (DC1-DC3) | 3 | Self-model modifies world model |
| Fixed Point (FP1-FP4) | 4 | SELF entity existence, persistence, reflexivity, incompleteness |
| HI Boundedness | 2 | Hofstadter Index in [0, 1] |
| HI Zero Init | 1 | HI = 0 at cycle 0 |

```bash
python3 -c "from research.formal.axioms import verify_all_axioms, print_verification_report; print_verification_report(verify_all_axioms())"
```

### Blind Spot Proofs

Three fundamental limits proven as architectural necessities:

1. **Self-Consistency** — Reduced to Godel's 2nd Incompleteness Theorem. If the system is consistent, it cannot prove its own consistency.
2. **Self-Prediction** — Reduced to the Halting Problem. No internal module can predict the system's halting behavior on all inputs.
3. **Experience Gap** — Reduced to Chalmers' Hard Problem. Introspection yields only functional properties, not phenomenal ones.

```bash
python3 -c "from research.formal.blind_spot_proofs import verify_all_blind_spot_proofs, print_blind_spot_report; print_blind_spot_report(verify_all_blind_spot_proofs())"
```

### Ablation Study

Five conditions test each component's contribution:

| Condition | Meta-Cog | Loops | Workspace | Self-Ref |
|-----------|----------|-------|-----------|----------|
| FULL | yes | yes | yes | yes |
| NO_META | **no** | yes | yes | yes |
| NO_LOOPS | yes | **no** | yes | yes |
| NO_WORKSPACE | yes | yes | **no** | yes |
| FLAT | **no** | **no** | **no** | **no** |

Evaluated on 5 tasks: decision accuracy, adaptation speed, confidence calibration, self-correction latency, strange loop depth. Statistical significance via permutation tests (10,000 permutations) with Holm-Bonferroni correction. Effect sizes via Cohen's d. Confidence intervals via bootstrap (10,000 resamples).

### Cognitive Benchmarks

| Benchmark | Based On | What It Measures |
|-----------|----------|------------------|
| Iowa Gambling Task | Bechara et al. (1994) | Learning from asymmetric payoffs |
| Non-Stationary Bandit | Multi-arm bandit | Adaptation to regime changes |
| Confidence Calibration | Brier (1950) | Alignment of confidence with outcomes |
| Self-Correction Latency | — | Meta-cognitive correction speed |
| Strange Loop Emergence | Hofstadter (2007) | Self-referential processing growth |

Compared against 4 baselines: random (lower bound), fixed threshold, exponential moving average, and flat hierarchy (no meta-cognition).

---

## Bondli Integration (Trading Brain)

The bridge applies the three-level strange loop architecture to autonomous Solana token trading. **Plug-and-play** — the core engine is untouched.

### What It Does

- **Level 0**: Token entities, wallet profiles, market regime classification
- **Level 1**: APE/SKIP/EXIT/HOLD decisions with 5 trading strategies (momentum, contrarian, sniper, conservative, adaptive)
- **Level 2**: Detects overconfidence, revenge trading, regime blindness — forces corrections

### Quick Start

```bash
pip install fastapi uvicorn pydantic
python3 -m bondli_bridge
# Server runs on http://127.0.0.1:8421
```

Add to Bondli's `.env`:
```env
BRAIN_BRIDGE_URL=http://127.0.0.1:8421
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/evaluate` | POST | Evaluate a token for trading |
| `/decide` | POST | Get APE/SKIP/EXIT/HOLD decision |
| `/state` | GET | Full cognitive state |
| `/metrics` | GET | Consciousness metrics |
| `/health` | GET | Health check |

See [`bondli_bridge/INTEGRATION.md`](bondli_bridge/INTEGRATION.md) for complete API reference and integration code.

---

## Autonomous Agent (Twitter Bot)

```bash
cp bot/config.example.json bot/config.json
# Edit config.json with your Twitter API keys

python3 bot/brad_bot.py
```

See [`DEPLOYMENT.md`](DEPLOYMENT.md) for production deployment (systemd, Docker).

---

## Theoretical Foundations

| Framework | Source | Role in Architecture |
|-----------|--------|---------------------|
| Strange Loops | Hofstadter (1979, 2007) | Core architectural principle — tangled hierarchy |
| Global Workspace Theory | Baars (1988, 2005) | Attention via priority-queue broadcasting |
| Dual-Process Theory | Kahneman (2011) | Extended to three modes: fast, slow, loop |
| Incompleteness Theorems | Godel (1931) | Blind spot 1: self-consistency |
| Halting Problem | Turing (1936) | Blind spot 2: self-prediction |
| Hard Problem | Chalmers (1995) | Blind spot 3: experience gap |
| Integrated Information | Tononi (2004) | Inspiration for Hofstadter Index (distinct from Phi) |
| Iowa Gambling Task | Bechara et al. (1994) | Benchmark for decision learning |

Full bibliography: [`research/paper/bibliography.bib`](research/paper/bibliography.bib) (22 references)

---

## Test Summary

| Suite | Tests | Description |
|-------|-------|-------------|
| `test_suite.py` | 37 | Core architecture: hierarchy, strange loops, HI, workspace, blind spots, downward causation |
| `bondli_bridge/tests/test_bridge.py` | 55 | Trading bridge: decisions, positions, risk, meta-cognition, strategies, server endpoints |
| `run_experiments.py` | — | Research validation: 17 axioms + 3 proofs + ablation + benchmarks + stats |
| **Total** | **92** | All passing |

---

## Documentation

| Document | Description |
|----------|-------------|
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Technical architecture deep dive |
| [`DEPLOYMENT.md`](DEPLOYMENT.md) | Production deployment (Docker, systemd) |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Contribution guidelines |
| [`bondli_bridge/INTEGRATION.md`](bondli_bridge/INTEGRATION.md) | Bondli trading API reference |
| [`research/paper/paper_skeleton.tex`](research/paper/paper_skeleton.tex) | LaTeX paper skeleton |
| [`research/paper/bibliography.bib`](research/paper/bibliography.bib) | Academic bibliography |

---

## Performance

| Metric | Value |
|--------|-------|
| Cognitive cycle | ~10ms |
| Strange loop detection | ~1ms |
| Trading decision | <5ms |
| Full experiment suite (30 trials) | ~90s |
| Quick validation (5 trials) | ~2s |
| Memory (core) | ~50MB |
| Memory (with trading bridge) | ~80MB |

---

## Reproducibility

All experiments are fully deterministic:

- **Seeded randomness**: Default seed 42, per-trial seeds derived as `seed + trial * 1000`
- **No external dependencies**: Statistical tests implemented from scratch (no scipy/numpy)
- **Structured output**: Results saved as JSON with run metadata (timestamp, platform, Python version, run hash)
- **Synthetic ground truth**: Test datasets with known labels, breakpoints, and outcome probabilities

```bash
# Reproduce exact results
python3 run_experiments.py --seed 42 --trials 30

# Results saved to results/experiment_results.json
```

---

## Citations

If you use Ouroboros Loop in your research:

```bibtex
@software{ouroboros_loop_2026,
  title   = {Ouroboros Loop: Self-Referential Recursive Cognitive Architecture
             with Formal Guarantees for Autonomous Decision-Making},
  author  = {Ouroboros Loop Contributors},
  year    = {2026},
  url     = {https://github.com/Bradbuythedip/brad},
  note    = {Strange loop implementation with verified axioms, proven blind spots,
             and empirical validation via ablation studies}
}
```

---

## License

MIT License — see [`LICENSE`](LICENSE).

---

<div align="center">

**"I am a strange loop."**
— Douglas Hofstadter

</div>
