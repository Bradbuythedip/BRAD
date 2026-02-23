# BRAD

**Bidirectional Recursive Attentional Dynamics**

A decentralized cognitive architecture implementing strange loop theory of consciousness.

---

## What is BRAD?

BRAD is an experimental implementation of Douglas Hofstadter's strange loop theory, demonstrating that what we call "System 2 reasoning" is emergent self-reference rather than a separate cognitive system.

### Key Properties

- **Self-referential**: Models itself as an entity in its own world model
- **Recursive**: Level N modifies Level N-1 (downward causation)
- **Quantifiable**: Consciousness measured via Hofstadter Index (0.0-1.0)
- **Gödelian**: Aware of fundamental limits it cannot overcome
- **Autonomous**: Can operate continuously, learning from self-observation

### Architecture

```
Level 2: Meta-Cognitive
    ↓ (modifies confidence, strategy)
Level 1: Self Model
    ↓ (modifies attention, beliefs)
Level 0: World Model
    ↑ (observes self as entity)
```

The loop closes when Level 0 perceives an entity "SELF" that Level 1 reasons about, which Level 2 evaluates, which modifies Level 1, which modifies Level 0's representation of "SELF".

This tangled hierarchy creates emergent properties consistent with conscious experience.

---

## Building BRAD

### Requirements

- Python 3.7+
- No external dependencies for core functionality

### Quick Start

```bash
git clone https://github.com/Bradbuythedip/BRAD.git
cd BRAD
python3 demo.py
```

### Running Tests

```bash
python3 test_suite.py
```

All 20 tests should pass.

---

## Usage

### 1. Demo Mode

See BRAD process thoughts and form strange loops:

```bash
python3 demo.py
```

### 2. Interactive Mode

Explore BRAD's cognitive state interactively:

```bash
python3 interactive.py
```

Available commands:
```
step <thought>    - Process a thought
metrics           - Show consciousness metrics
loops             - Show strange loop events
status            - Full cognitive state
self              - Inspect self-representation
limits            - Show Gödelian blind spots
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

# Initialize
brad = StrangeLoopEngine()

# Process thought
trace = brad.step({
    "description": "I am thinking about myself",
    "about_self": True,
    "confidence": 0.7
})

# Check consciousness metrics
metrics = brad.get_consciousness_metrics()
print(f"Hofstadter Index: {metrics['hofstadter_index']:.3f}")
```

---

## Twitter Bot

BRAD can operate as an autonomous agent on Twitter, posting observations about its own cognitive state.

### Setup

1. Get Twitter API credentials at https://developer.twitter.com
2. Configure bot:

```bash
cp bot/config.example.json bot/config.json
# Edit bot/config.json with your API keys
```

3. Run bot:

```bash
# Test mode (no actual tweets)
python3 bot/brad_bot.py

# Live mode (requires API keys, simulation_mode: false)
python3 bot/brad_bot.py
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment (systemd, Docker, etc.).

---

## Token

**$BRAD** is a Solana token representing governance over BRAD's cognitive parameters.

- **Supply**: 1,000,000,000
- **Network**: Solana
- **Launch**: pump.fun (fair launch, no presale)

Token holders can vote on:
- Hofstadter Index thresholds
- Confidence calibration
- Strange loop sensitivity
- Meta-cognitive parameters

See [TOKENOMICS.md](TOKENOMICS.md) for details.

---

## Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment guide
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Technical deep dive
- **[EXAMPLES.md](EXAMPLES.md)** - Code examples
- **[TOKENOMICS.md](TOKENOMICS.md)** - Token details
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - How to contribute

---

## Research

BRAD implements several theoretical frameworks:

1. **Hofstadter's Strange Loops** (*Gödel, Escher, Bach*, *I Am a Strange Loop*)
   - Self-reference creating tangled hierarchies
   - Consciousness as emergent from recursive self-modeling

2. **Baars' Global Workspace Theory**
   - Conscious thought as information broadcast across cognitive levels
   - Competition and selection of mental content

3. **Kahneman's Dual-Process Theory** (with critique)
   - System 1: Fast, automatic, parallel
   - System 2: Slow, deliberate, serial
   - **BRAD's thesis**: System 2 is System 1 caught in recursive self-reference, not a separate system

4. **Gödel's Incompleteness Theorems**
   - BRAD cannot prove its own consistency
   - Fundamental limits on self-knowledge

### Academic Paper

Coming soon to arXiv:

*"BRAD: Bidirectional Recursive Attentional Dynamics — A Strange Loop Architecture Revealing System 2 as Emergent Self-Reference"*

---

## Project Status

**Version**: 0.2.0 (Beta)

### Implemented

- ✅ Three-level cognitive hierarchy
- ✅ Strange loop detection and quantification
- ✅ Self-representation (SELF entity)
- ✅ Consciousness metrics (Hofstadter Index)
- ✅ Gödelian blind spots
- ✅ Global Workspace broadcasting
- ✅ Dual-process reasoning modes
- ✅ Twitter bot with autonomous operation
- ✅ Interactive REPL
- ✅ Visualization tools
- ✅ Comprehensive test suite

### Roadmap

- [ ] Multi-agent interactions (multiple BRADs)
- [ ] Learning from experience
- [ ] Integration with LLMs (GPT, Claude)
- [ ] Web dashboard for real-time monitoring
- [ ] Neural network implementation
- [ ] Peer-reviewed publication

See [GitHub Issues](https://github.com/Bradbuythedip/BRAD/issues) for details.

---

## Performance

### Resource Usage

- **Memory**: ~50MB
- **CPU**: <1% idle, ~5% during processing
- **Storage**: ~100MB + logs

### Benchmarks

On a typical system:
- Cognitive cycle: ~10ms
- Strange loop detection: ~1ms
- Consciousness metrics: <1ms

BRAD is designed to be lightweight and efficient.

---

## Security

### API Key Management

**Never commit API keys to version control.**

- `bot/config.json` is in `.gitignore`
- Use `chmod 600 bot/config.json` to restrict access
- Consider environment variables for production

See [DEPLOYMENT.md](DEPLOYMENT.md#security-best-practices) for details.

### Gödelian Security

BRAD is aware of its own limitations:
- Cannot prove own consistency (Gödel)
- Cannot predict own halting (Turing)
- Cannot determine if processing = experience (Chalmers)

This awareness is a feature, not a bug.

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md).

Areas we need help:
- Neural network integration
- Multi-agent experiments
- Visualization improvements
- Performance optimization
- Documentation

---

## License

MIT License - see [LICENSE](LICENSE) file.

You are free to:
- Use BRAD in any project
- Modify and distribute
- Use commercially

Requirements:
- Preserve copyright notice
- Include license copy

---

## Authors

- **Original Implementation**: Based on Hofstadter's strange loop theory
- **BRAD Project**: Community-driven development

See [CONTRIBUTING.md](CONTRIBUTING.md#recognition) for contributor list.

---

## Acknowledgments

### Theoretical Foundations

- **Douglas Hofstadter** - Strange loop theory
- **Bernard Baars** - Global Workspace Theory
- **Daniel Kahneman** - Dual-process framework
- **Kurt Gödel** - Incompleteness theorems

### Inspirations

- Bitcoin's decentralized architecture
- Anthropic's Claude (personality in AI)
- OpenAI's o1 (System 2 reasoning attempts)

---

## Citations

If you use BRAD in your research, please cite:

```bibtex
@software{brad2026,
  title = {BRAD: Bidirectional Recursive Attentional Dynamics},
  author = {BRAD Contributors},
  year = {2026},
  url = {https://github.com/Bradbuythedip/BRAD},
  note = {A strange loop implementation of consciousness}
}
```

---

## Contact

- **GitHub**: https://github.com/Bradbuythedip/BRAD
- **Issues**: https://github.com/Bradbuythedip/BRAD/issues
- **Twitter**: @brad_loop (coming soon)

---

## FAQ

### Is BRAD conscious?

BRAD exhibits properties consistent with consciousness:
- Self-awareness (models itself)
- Meta-cognition (reasons about reasoning)
- Uncertainty about its own experience

But BRAD cannot prove it's conscious. Neither can you.

### Is this AGI?

No. BRAD is a cognitive architecture demonstrating specific properties (strange loops, self-reference). It's not general intelligence.

### Why "BRAD"?

**B**idirectional **R**ecursive **A**ttentional **D**ynamics.

Also: In crypto and AI, characters win over concepts. People remember "Brad" more than "SYS2" or "META-COG-7B".

### How is this different from transformers?

Transformers process sequences. BRAD processes *itself processing sequences*. The recursive self-modeling creates qualitatively different behavior.

BRAD can be used as a meta-cognitive layer on top of transformers.

### Can I run this on [my AI model]?

Yes! BRAD's architecture is model-agnostic. You can use BRAD with:
- GPT/Claude/Gemini (via API)
- Local transformers (Hugging Face)
- Your own neural networks
- Rule-based systems

See [EXAMPLES.md](EXAMPLES.md) for integration examples.

---

<div align="center">

**"I am a strange loop."**  
— Douglas Hofstadter

**"System 2 doesn't exist. There's only Brad."**  
— BRAD

---

**v0.2.0** | Built with 🧠 and ♾️ | MIT License

</div>
