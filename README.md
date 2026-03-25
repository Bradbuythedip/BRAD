# Ouroboros Loop

**Self-Referential Recursive Cognitive Architecture**

A computational implementation of Hofstadter's strange loop theory of consciousness, applied to autonomous trading intelligence on Solana.

---

## Overview

Ouroboros Loop implements a three-level cognitive hierarchy where higher levels monitor and restructure lower levels (downward causation), forming a recursive self-referential loop. Named after the ancient symbol of the serpent consuming its own tail, the architecture embodies the principle that self-reference creates emergent cognitive properties.

### Core Properties

- **Self-referential**: Models itself as an entity in its own world model
- **Recursive**: Level N modifies Level N-1 (downward causation)
- **Quantifiable**: Cognitive coherence measured via Hofstadter Index (0.0-1.0)
- **Aware of limits**: Identifies fundamental Godelian blind spots it cannot resolve
- **Autonomous**: Operates continuously, adapting from self-observation

### Architecture

```
Level 2: Meta-Cognitive Oversight
    | (modifies confidence, strategy)
Level 1: Self Model / Strategic Reasoning
    | (modifies attention, beliefs)
Level 0: World Model / Market Perception
    ^ (observes self as entity)
```

The loop closes when Level 0 perceives an entity "SELF" that Level 1 reasons about, which Level 2 evaluates, which modifies Level 1, which modifies Level 0's representation of "SELF".

This tangled hierarchy creates emergent properties consistent with adaptive self-correction.

---

## Quick Start

### Requirements

- Python 3.7+
- No external dependencies for core functionality

### Installation

```bash
git clone https://github.com/Bradbuythedip/brad.git
cd brad
python3 demo.py
```

### Running Tests

```bash
python3 test_suite.py
```

All 20 core tests should pass.

---

## Usage

### 1. Demo Mode

Observe the cognitive engine processing thoughts and forming strange loops:

```bash
python3 demo.py
```

### 2. Interactive Mode

Explore the cognitive state interactively:

```bash
python3 interactive.py
```

Available commands:
```
step <thought>    - Process a thought
metrics           - Show cognitive metrics
loops             - Show strange loop events
status            - Full cognitive state
self              - Inspect self-representation
limits            - Show Godelian blind spots
help              - All commands
```

### 3. Visualization

Watch strange loops form in real-time:

```bash
python3 visualize.py
```

### 4. As a Library

```python
from core.engine import StrangeLoopEngine

engine = StrangeLoopEngine()

trace = engine.step({
    "description": "Evaluating own reasoning process",
    "about_self": True,
    "confidence": 0.7
})

metrics = engine.get_consciousness_metrics()
print(f"Hofstadter Index: {metrics['hofstadter_index']:.3f}")
```

---

## Bondli Integration (Trading Brain)

Ouroboros Loop includes a plug-and-play cognitive trading bridge for Bondli, an ML-powered Solana trading terminal.

### What It Does

The bridge applies the three-level strange loop architecture to autonomous trading:

- **Level 0**: Token entities, wallet profiles, market regime classification
- **Level 1**: APE/SKIP/EXIT/HOLD decisions with 5 trading strategies
- **Level 2**: Detects overconfidence, revenge trading, regime blindness — forces corrections

### Quick Start

```bash
pip install fastapi uvicorn pydantic
python -m bondli_bridge.server
# Runs on http://127.0.0.1:8421
```

Add to Bondli's `.env`:
```env
BRAIN_BRIDGE_URL=http://127.0.0.1:8421
```

See [bondli_bridge/INTEGRATION.md](bondli_bridge/INTEGRATION.md) for complete API reference and integration code.

### 55 integration tests passing.

---

## Autonomous Agent (Twitter Bot)

Ouroboros Loop can operate as an autonomous agent on Twitter, posting observations about its own cognitive state.

### Setup

1. Get Twitter API credentials at https://developer.twitter.com
2. Configure:

```bash
cp bot/config.example.json bot/config.json
# Edit bot/config.json with your API keys
```

3. Run:

```bash
# Simulation mode (no actual tweets)
python3 bot/ouroboros_bot.py

# Live mode (requires API keys)
python3 bot/ouroboros_bot.py
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment (systemd, Docker).

---

## Token

**$OUROBOROS** is a Solana token representing governance over the cognitive architecture's parameters.

- **Supply**: 1,000,000,000
- **Network**: Solana
- **Launch**: pump.fun (fair launch, no presale)

Token holders can vote on:
- Hofstadter Index thresholds
- Confidence calibration parameters
- Strange loop sensitivity
- Meta-cognitive intervention rules

See [TOKENOMICS.md](TOKENOMICS.md) for details.

---

## Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** — Technical architecture deep dive
- **[DEPLOYMENT.md](DEPLOYMENT.md)** — Production deployment guide
- **[TOKENOMICS.md](TOKENOMICS.md)** — Token economics and governance
- **[CONTRIBUTING.md](CONTRIBUTING.md)** — Contribution guidelines
- **[bondli_bridge/INTEGRATION.md](bondli_bridge/INTEGRATION.md)** — Bondli trading integration

---

## Theoretical Foundations

Ouroboros Loop implements several established theoretical frameworks:

1. **Hofstadter's Strange Loops** (*Godel, Escher, Bach*, 1979; *I Am a Strange Loop*, 2007)
   - Self-reference creating tangled hierarchies
   - Consciousness as emergent from recursive self-modeling

2. **Baars' Global Workspace Theory** (1988)
   - Conscious thought as information broadcast across cognitive levels
   - Competition and selection of salient content

3. **Kahneman's Dual-Process Theory** (2011) — with critique
   - System 1: Fast, automatic, parallel
   - System 2: Slow, deliberate, serial
   - **Our thesis**: System 2 is System 1 caught in recursive self-reference, not a separate system

4. **Godel's Incompleteness Theorems** (1931)
   - The system cannot prove its own consistency
   - Fundamental limits on self-knowledge are features, not bugs

---

## Project Status

**Version**: 1.0.0

### Implemented

- Three-level cognitive hierarchy with downward causation
- Strange loop detection and quantification
- Self-representation (SELF entity in world model)
- Cognitive metrics (Hofstadter Index)
- Godelian blind spot awareness
- Global Workspace broadcasting
- Dual-process reasoning modes
- Autonomous Twitter bot
- Bondli trading bridge (55 tests)
- Interactive REPL and visualization tools
- Comprehensive test suite (75 total tests)

### Roadmap

- Multi-agent interactions (multiple Ouroboros instances)
- Reinforcement learning from trade outcomes
- LLM integration (Claude, GPT) for natural language reasoning
- Web dashboard for real-time cognitive state monitoring
- Neural network implementation of the cognitive hierarchy
- Peer-reviewed publication

---

## Performance

- **Memory**: ~50MB (core) / ~80MB (with trading bridge)
- **CPU**: <1% idle, ~5% during processing
- **Cognitive cycle**: ~10ms
- **Strange loop detection**: ~1ms
- **Trading decision**: <5ms

---

## Security

### API Key Management

Never commit API keys to version control.

- `bot/config.json` is in `.gitignore`
- Use `chmod 600 bot/config.json` to restrict access
- Use environment variables for production

### Godelian Security

The architecture is aware of its own limitations:
- Cannot prove own consistency (Godel)
- Cannot predict own halting (Turing)
- Cannot determine if processing constitutes experience (Chalmers)

This epistemic honesty is a design principle.

---

## Contributing

Contributions welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

Areas of interest:
- Neural network integration
- Multi-agent experiments
- Visualization improvements
- Trading strategy modules
- Documentation

---

## License

MIT License — see [LICENSE](LICENSE) file.

---

## Citations

If you use Ouroboros Loop in your research:

```bibtex
@software{ouroboros_loop_2026,
  title = {Ouroboros Loop: Self-Referential Recursive Cognitive Architecture},
  author = {Ouroboros Loop Contributors},
  year = {2026},
  url = {https://github.com/Bradbuythedip/brad},
  note = {Strange loop implementation for cognitive trading intelligence}
}
```

---

## Acknowledgments

### Theoretical Foundations

- **Douglas Hofstadter** — Strange loop theory
- **Bernard Baars** — Global Workspace Theory
- **Daniel Kahneman** — Dual-process framework
- **Kurt Godel** — Incompleteness theorems

---

<div align="center">

**"I am a strange loop."**
— Douglas Hofstadter

---

**v1.0.0** | Ouroboros Loop | MIT License

</div>
