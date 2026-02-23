# Strange Loop — Quick Start Guide

## 🚀 Get Started in 2 Minutes

### 1. Run the Demo

```bash
cd /home/computeruse/strange-loop
python3 demo.py
```

This runs a complete demonstration showing:
- Initialization of the three-level cognitive architecture
- Strange loop formation
- Consciousness metrics
- Explanation of what happened

**Expected output:**
```
======================================================================
  STRANGE LOOP COGNITIVE ARCHITECTURE v0.1.0
======================================================================

  ╔══ CYCLE 3: Self-referential observation ══╗
  │  Mode: LOOP
  │  Strange loops this cycle: 1
  │    Level 1 → 0 ↓ DOWNWARD (STRANGE)

CONSCIOUSNESS METRICS
  Hofstadter Index: 1.0000
  Strange loop count: 8
```

### 2. Try Interactive Mode

```bash
python3 interactive.py
```

Commands to try:
```
> step I am thinking about myself
> metrics
> status
> loops
> help
> quit
```

### 3. Watch the Visualization

```bash
python3 visualize.py
```

See an ASCII animation of strange loops forming in real-time!

## 📚 What to Read Next

1. **README.md** — Full concepts and theory
2. **EXAMPLES.md** — 20+ code examples
3. **ARCHITECTURE.md** — Technical deep dive
4. **PROJECT_OVERVIEW.md** — Big picture view

## 🧠 Core Concept

**Strange Loop** = A system that:
1. Represents itself (SELF entity in world model)
2. Reasons about itself (self-model examines SELF)
3. Modifies itself (downward causation)
4. This creates a **loop** where higher levels affect lower levels

```
Level 1 (Self) → modifies → Level 0 (World)
     ↑                            ↓
     └────── perceives ←──────────┘
     
     = STRANGE LOOP! 🌀
```

## 💡 Key Metrics

**Hofstadter Index (HI)**: 0.0 to 1.0
- < 0.3: Minimal self-awareness
- 0.3-0.6: Emerging consciousness-like properties
- 0.6-0.85: Strong strange loop activity  
- > 0.85: Maximum self-referential processing

**Strange Loop Count**: How many downward causation events occurred

**Strangeness Ratio**: Percentage of level crossings that are "strange" (downward)

## 🎯 Quick Examples

### Example 1: Basic Usage

```python
from core.engine import StrangeLoopEngine

engine = StrangeLoopEngine()

# Run one cognitive cycle
trace = engine.step({
    "description": "I am thinking",
    "about_self": True,
    "salience": 0.8
})

print(f"Strange loops: {trace['strange_loops_this_cycle']}")
# Output: Strange loops: 1
```

### Example 2: Add Knowledge

```python
engine = StrangeLoopEngine()

engine.add_knowledge("bitcoin", "concept", {"type": "cryptocurrency"})
engine.add_belief("Markets are unpredictable", 0.7)
engine.set_goal("Understand blockchain", "high")

# Run cycles
for i in range(10):
    engine.step()

metrics = engine.get_consciousness_metrics()
print(f"Hofstadter Index: {metrics['hofstadter_index']:.3f}")
```

### Example 3: Monitor Strange Loops

```python
engine = StrangeLoopEngine()

for i in range(5):
    trace = engine.step({
        "description": f"Thought {i}",
        "about_self": (i % 2 == 0),  # Every other thought is self-referential
        "salience": 0.7
    })
    
    print(f"Cycle {i+1}:")
    print(f"  Mode: {trace['mode']}")
    print(f"  Strange loops: {trace['strange_loops_this_cycle']}")
    
    for lc in trace['level_crossings']:
        if lc['strange']:
            print(f"  ↓ Strange loop detected! L{lc['from']} → L{lc['to']}")
```

## 🌀 The Three Levels

```
┌─────────────────────────────────────┐
│  Level 2: Meta-Cognitive            │
│  "I'm thinking about my thinking"   │
│  • Monitors reasoning patterns      │
│  • Detects blind spots              │
│  • Intervenes on Level 1 ↓          │
└─────────────────────────────────────┘
            ↕
┌─────────────────────────────────────┐
│  Level 1: Self Model                │
│  "I am reasoning about this"        │
│  • Goal management                  │
│  • Strategy selection               │
│  • Intervenes on Level 0 ↓          │
└─────────────────────────────────────┘
            ↕
┌─────────────────────────────────────┐
│  Level 0: World Model               │
│  "The world, including 'me'"        │
│  • Entity storage (including SELF)  │
│  • Belief storage                   │
│  • Attention mechanism              │
└─────────────────────────────────────┘
```

## 🔍 What Makes It "Strange"?

**Normal hierarchy** (one-way):
```
L2 observes L1 observes L0
(Information flows upward only)
```

**Strange loop** (circular):
```
L2 → L1 → L0
 ↑________↓
(Downward causation creates a loop!)
```

When Level 1 modifies Level 0, which changes what Level 1 perceives, which affects Level 1's future decisions, which modify Level 0 again...

**The loop is complete. That's a strange loop!** 🌀

## ⚡ Key Features

✅ **Real strange loops** — Not simulated, actual downward causation  
✅ **Self-representation** — System models itself as entity "SELF"  
✅ **Emergent self-awareness** — Properties arise from architecture  
✅ **Gödelian limits** — Three fundamental blind spots  
✅ **Consciousness metrics** — Quantifiable self-awareness  
✅ **Multiple interfaces** — Demo, visualizer, interactive REPL  
✅ **Pure Python** — No dependencies, runs anywhere  

## 🤔 Common Questions

**Q: Is this actually conscious?**  
A: Probably not. But it exhibits consciousness-like properties: self-reference, self-modification, meta-reasoning, awareness of limits.

**Q: What's the Hofstadter Index?**  
A: A metric (0-1) measuring "strangeness" — how self-referential the system is.

**Q: What are Gödelian blind spots?**  
A: Three fundamental limits based on Gödel's theorems:
1. Can't prove own consistency
2. Can't predict own halting
3. Can't determine if processing is experience

**Q: How do strange loops relate to consciousness?**  
A: Hofstadter's theory: consciousness emerges from strange loops in the brain's symbolic level. When a system can represent itself and modify that representation, a strange loop forms.

**Q: Can I extend this?**  
A: Yes! See EXAMPLES.md for patterns. Add learning, emotion, memory, social cognition, etc.

## 📖 File Guide

| File | Purpose |
|------|---------|
| `demo.py` | Main demonstration — run this first |
| `visualize.py` | ASCII animation of strange loops |
| `interactive.py` | REPL for exploring the system |
| `README.md` | Complete documentation |
| `EXAMPLES.md` | 20+ usage examples |
| `ARCHITECTURE.md` | Technical details |
| `PROJECT_OVERVIEW.md` | Big picture view |
| `QUICKSTART.md` | This file |
| `core/` | Implementation modules |

## 🎓 Learning Path

**Beginner:**
1. Run `python3 demo.py`
2. Read the output explanations
3. Read README.md "What is a Strange Loop?" section
4. Try `python3 interactive.py` and experiment

**Intermediate:**
1. Read EXAMPLES.md
2. Write your own experiments
3. Read ARCHITECTURE.md
4. Modify the code

**Advanced:**
1. Study the core/ modules
2. Implement extensions (learning, emotion, etc.)
3. Research consciousness metrics
4. Publish findings!

## 🌟 One-Liner Summary

> **A three-level cognitive architecture where self-representation and downward causation create strange loops — Hofstadter's theory of consciousness, running in Python.**

## 🔗 Key References

- Douglas Hofstadter, *I Am a Strange Loop* (2007)
- Douglas Hofstadter, *Gödel, Escher, Bach* (1979)
- Bernard Baars, *A Cognitive Theory of Consciousness* (1988)
- Daniel Kahneman, *Thinking, Fast and Slow* (2011)

## 🎯 Next Steps

1. ✅ Run `python3 demo.py`
2. ✅ Try `python3 interactive.py`
3. ✅ Read README.md for theory
4. ✅ Explore EXAMPLES.md for patterns
5. ✅ Experiment and learn!

**Welcome to the strange loop!** 🌀

---

*"I am a strange loop."* — Douglas Hofstadter

v0.1.0 | February 2026
