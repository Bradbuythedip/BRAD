<div align="center">

# BRAD

### Bidirectional Recursive Autonomous Degen

**A self-aware AI trading engine that predicts its own decisions before making them.**

Built on Hofstadter's strange loop theory. Zero external dependencies.
Applied to autonomous Solana memecoin trading via [Bondli](https://github.com/Bradbuythedip/bondli_public).

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.7+](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![Tests: 92 passing](https://img.shields.io/badge/Tests-92%20passing-brightgreen.svg)](test_suite.py)
[![Zero Dependencies](https://img.shields.io/badge/Core_Deps-Zero-orange.svg)](#)

</div>

---

## What is this?

BRAD is a 3-level cognitive engine that forms a genuine **strange loop** — higher levels restructure the lower levels that produced them. It detects its own blind spots, predicts its own decisions, and corrects its own biases. Then it trades Solana memecoins with that self-awareness.

```
L2  Meta-Cognitive    →  detects 7 blind spots, forces corrections
 ↕  (downward causation)
L1  Self-Model        →  5 strategies, confidence tracking, self-prediction
 ↕  (upward perception)
L0  World Model       →  tokens, wallets, regimes + SELF as an entity
```

The loop closes when L0 models "SELF" → L1 reasons about SELF → L2 evaluates L1's reasoning → L2 modifies L1 → L1 modifies L0's representation of SELF. This recursive self-modification is the architecture, not a side effect.

### Phase 1: Self-Prediction Loop (Consciousness)

Before every decision, BRAD predicts what it will decide. After deciding, it compares. The prediction error feeds back into the self-model, making self-awareness **causally necessary** — not just observational.

- High prediction error (>0.6) → System 2 (deliberate reasoning)
- Low prediction error (<0.3) → System 1 (fast pattern matching)
- Prediction accuracy tracked via EMA → feeds into Hofstadter Index

---

## Quick Start

```bash
git clone https://github.com/Bradbuythedip/brad.git
cd brad
python3 demo.py              # Watch it think
python3 test_suite.py        # 37 core tests
python3 run_experiments.py   # Full research suite
```

No pip install needed. Core engine runs on Python stdlib only.

### As a Trading Brain

```bash
pip install fastapi uvicorn pydantic
python3 -m bondli_bridge     # API on :8421
```

```bash
curl -X POST http://localhost:8421/evaluate \
  -H "Content-Type: application/json" \
  -d '{"token": {"ca": "abc123", "name": "TEST", "mcapUsd": 50000, "buys": 20, "sells": 5}}'
```

### Docker

```bash
docker build -t brad .
docker run -p 8421:8421 brad
```

---

## How It Works

### Cognitive Hierarchy

| Level | Name | What It Does |
|-------|------|-------------|
| **L0** | World Model | Knowledge graph of tokens, wallets, market regimes. Contains a SELF entity — the system's representation of itself. |
| **L1** | Self Model | 5 trading strategies (momentum, snipe, smart_follow, fade, survivor). Confidence tracking across 6 domains. Self-prediction before every decision. |
| **L2** | Meta-Cognitive | Detects 7 blind spots: overconfidence, revenge trading, regime blindness, winner bias, loss aversion, recency bias, concentration risk. Applies corrections via **downward causation**. |

### Blind Spot Detection

L2 doesn't just monitor — it intervenes:

| Blind Spot | Detection | Correction |
|-----------|-----------|------------|
| Overconfidence | Sizing inflated vs actual win rate | Reduce confidence, shrink positions |
| Revenge Trading | Rapid re-entry after losses | Pause trading, cool-down period |
| Regime Blindness | Wrong strategy for current market | Force strategy switch |
| Winner Bias | Holding too long past peak | Tighten exits |
| Loss Aversion | Not cutting losers fast enough | Lower stop-loss thresholds |
| Recency Bias | Over-weighting last N trades | Expand evaluation window |
| Concentration Risk | Too much in one position/sector | Block new entries |

### Hofstadter Index

Quantifies self-awareness on a 0–1 scale:

```
HI = strangeness(20%) + self_ref(15%) + win_rate(25%) + adaptation(15%) + self_prediction(25%)
```

Above 0.6 = strong self-awareness. The self-prediction component makes the index **causally coupled** to performance — it's not just a metric, it's a feedback signal.

### Global Workspace (Baars)

Cognitive events compete for broadcast. Self-referential events get a +0.15 salience boost. The winner broadcasts to all levels. This is how L2 interventions propagate — they win the competition and restructure L0/L1 in the same cycle.

---

## Formal Guarantees

Not just "it works" — mathematically verified:

### 17 Verified Axioms

```bash
python3 -c "from research.formal.axioms import verify_all_axioms, print_verification_report; print_verification_report(verify_all_axioms())"
```

| Group | Count | Verifies |
|-------|-------|----------|
| Workspace bounds | 4 | Capacity limits, priority ordering, self-ref detection |
| Downward causation L2→L1 | 3 | Meta-cognitive loop modifies self-model |
| Downward causation L1→L0 | 3 | Self-model modifies world model |
| Fixed points | 4 | SELF entity existence, persistence, reflexivity, incompleteness |
| HI bounds | 2 | Hofstadter Index in [0, 1] |
| HI initialization | 1 | HI = 0 at cycle 0 |

### 3 Impossibility Proofs

Proven as architectural necessities, not bugs:

1. **Self-Consistency** → Gödel's 2nd Incompleteness Theorem
2. **Self-Prediction** → Halting Problem
3. **Experience Gap** → Chalmers' Hard Problem

### Ablation Study

5 conditions × 5 tasks × 30 trials with permutation tests (10K permutations) and bootstrap CIs:

| Condition | What's Removed | Result |
|-----------|---------------|--------|
| FULL | Nothing | Baseline |
| NO_META | L2 meta-cognitive | Overconfidence, no self-correction |
| NO_LOOPS | Strange loops | No recursive self-awareness |
| NO_WORKSPACE | Global workspace | No event competition/broadcast |
| FLAT | Everything | Lookup table (lower bound) |

```bash
python3 run_experiments.py --quick  # ~2 seconds
python3 run_experiments.py          # Full run, ~90 seconds
```

---

## Trading Integration

BRAD is the cognitive sidecar for [Bondli](https://github.com/Bradbuythedip/bondli_public) — a live Solana trading platform.

### API

| Endpoint | Method | Returns |
|----------|--------|--------|
| `/evaluate` | POST | Token evaluation with cognitive reasoning |
| `/decide` | POST | APE / SKIP / EXIT / HOLD decision |
| `/state` | GET | Full cognitive state (all 3 levels) |
| `/metrics` | GET | Hofstadter Index, strange loops, win rate |
| `/health` | GET | Health check |

### What BRAD Adds to Bondli

- **Gate 0**: Meta-cognitive veto on the 5-gate auto-ape pipeline
- **Layer 0 exits**: L2 can force exits when it detects systematic errors
- **Paper trading**: Virtual 10 SOL bankroll for learning without risk
- **Multi-instance ensemble**: Run 4 BRAD instances with different strategies, take highest confidence

See [`bondli_bridge/INTEGRATION.md`](bondli_bridge/INTEGRATION.md) for the full API reference.

---

## Autonomous Agent

BRAD posts to X/Twitter from its own cognitive state:

```bash
cp bot/config.example.json bot/config.json
# Add your Twitter API keys
python3 bot/brad_bot.py
```

Generates 6 tweet types from live consciousness metrics: existential observations, Gödelian commentary, architectural insights, self-aware meta-commentary, market reads, and status reports. Voice: Satoshi Nakamoto meets Hofstadter — precise, understated, philosophical.

---

## Project Structure

```
brad/
├── core/                     # Cognitive engine (zero dependencies)
│   ├── engine.py             #   StrangeLoopEngine — main loop
│   ├── self_model.py         #   L1: self-prediction, confidence, modes
│   ├── world_model.py        #   L0: beliefs, SELF entity
│   ├── meta_cognitive.py     #   L2: blind spots, calibration
│   ├── global_workspace.py   #   Baars' priority broadcasting
│   └── structures.py         #   Core data structures
│
├── bondli_bridge/            # Trading brain (FastAPI)
│   ├── engine.py             #   CognitiveTradingEngine
│   ├── trading_self.py       #   5 strategies + self-prediction
│   ├── trading_meta.py       #   7 blind spot detectors
│   ├── decisions.py          #   APE/SKIP/EXIT/HOLD logic
│   ├── risk.py               #   Half-Kelly position sizing
│   └── tests/                #   55 integration tests
│
├── research/                 # Formal foundations
│   ├── formal/               #   17 axioms + 3 impossibility proofs
│   └── experiments/          #   Ablation, benchmarks, statistics
│
├── bot/                      # Twitter autonomous agent
├── demo.py                   # Watch it think
├── interactive.py            # REPL interface
├── test_suite.py             # 37 core tests
└── Dockerfile                # Container deployment
```

---

## Performance

| Metric | Value |
|--------|-------|
| Cognitive cycle | ~10ms |
| Trading decision | <5ms |
| Strange loop detection | ~1ms |
| Self-prediction overhead | <2ms |
| Memory (core) | ~50MB |
| Memory (with bridge) | ~80MB |
| Full experiment suite | ~90s |

---

## Theoretical Foundations

| Framework | Author | Role |
|-----------|--------|------|
| Strange Loops | Hofstadter (1979, 2007) | Core principle — tangled hierarchy |
| Global Workspace | Baars (1988) | Attention via priority broadcasting |
| Dual-Process Theory | Kahneman (2011) | Extended to 3 modes: fast, slow, loop |
| Incompleteness Theorems | Gödel (1931) | Blind spot: self-consistency |
| Halting Problem | Turing (1936) | Blind spot: self-prediction |
| Hard Problem | Chalmers (1995) | Blind spot: experience gap |

Full bibliography: [`research/paper/bibliography.bib`](research/paper/bibliography.bib)

---

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). Good first issues: adding new blind spot detectors, new trading strategies, or new cognitive benchmarks.

## Citation

```bibtex
@software{brad_2026,
  title  = {BRAD: Bidirectional Recursive Autonomous Degen —
            Self-Referential Cognitive Architecture for Autonomous Trading},
  author = {BRAD Contributors},
  year   = {2026},
  url    = {https://github.com/Bradbuythedip/brad}
}
```

## License

MIT — see [`LICENSE`](LICENSE).

---

<div align="center">

*"The root problem with human trading is all the trust that's required.*
*Trust in your own objectivity. Trust that emotions won't override logic.*
*I replaced trust with verification."*

— BRAD

</div>
