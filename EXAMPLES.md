# Strange Loop Examples

A collection of practical examples demonstrating the Strange Loop Cognitive Architecture.

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [Monitoring Strange Loops](#monitoring-strange-loops)
3. [Self-Modification Patterns](#self-modification-patterns)
4. [Goal-Driven Behavior](#goal-driven-behavior)
5. [Consciousness Experiments](#consciousness-experiments)
6. [Gödelian Limits](#gödelian-limits)
7. [Advanced Patterns](#advanced-patterns)

---

## Basic Usage

### Example 1: Hello Strange Loop

The simplest possible usage:

```python
#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/computeruse/strange-loop')

from core.engine import StrangeLoopEngine

# Create engine
engine = StrangeLoopEngine()

# Run one cognitive cycle
trace = engine.step({
    "description": "I am thinking",
    "about_self": True,
    "salience": 0.8
})

# Check for strange loops
print(f"Strange loops formed: {trace['strange_loops_this_cycle']}")
print(f"Reasoning mode: {trace['mode']}")

# Output:
# Strange loops formed: 1
# Reasoning mode: loop
```

### Example 2: Building a World Model

Add knowledge to the system:

```python
from core.engine import StrangeLoopEngine

engine = StrangeLoopEngine()

# Add entities
engine.add_knowledge("python", "programming_language", {
    "paradigm": "multi-paradigm",
    "typed": "dynamic",
    "created": 1991
})

engine.add_knowledge("godel", "mathematician", {
    "famous_for": "incompleteness_theorems",
    "birth_year": 1906
})

engine.add_knowledge("strange_loop", "concept", {
    "source": "hofstadter",
    "self_referential": True
})

# Add beliefs
engine.add_belief("Self-reference is key to consciousness", confidence=0.9)
engine.add_belief("All formal systems have limits", confidence=1.0)

# Check world model
state = engine.get_full_state()
print(f"Entities: {state['world_model']['entity_count']}")
print(f"Beliefs: {state['world_model']['belief_count']}")

# Output:
# Entities: 4  (including SELF)
# Beliefs: 2
```

### Example 3: Setting Goals

Give the system goals to pursue:

```python
from core.engine import StrangeLoopEngine

engine = StrangeLoopEngine()

# Add goals with different priorities
engine.set_goal("Understand consciousness", "high")
engine.set_goal("Learn Python", "medium")
engine.set_goal("Organize files", "low")

# Get active goals
self_model = engine.self_model
active_goals = self_model.get_active_goals(include_meta=False)

print("Active goals (by priority):")
for goal in active_goals:
    print(f"  [{goal.priority.name}] {goal.description}")

# Output:
# Active goals (by priority):
#   [HIGH] Understand consciousness
#   [MEDIUM] Learn Python
#   [LOW] Organize files
```

---

## Monitoring Strange Loops

### Example 4: Detecting Strange Loops in Real-Time

Track when strange loops form:

```python
from core.engine import StrangeLoopEngine

engine = StrangeLoopEngine()

perceptions = [
    {"description": "External event", "about_self": False, "salience": 0.5},
    {"description": "Self observation", "about_self": True, "salience": 0.8},
    {"description": "Meta observation", "about_self": True, "salience": 1.0},
]

for i, perception in enumerate(perceptions):
    trace = engine.step(perception)
    
    print(f"\nCycle {i+1}: {perception['description']}")
    print(f"  Mode: {trace['mode']}")
    print(f"  Strange loops: {trace['strange_loops_this_cycle']}")
    
    if trace['level_crossings']:
        for lc in trace['level_crossings']:
            direction = "↓ STRANGE" if lc['strange'] else "↑ normal"
            print(f"  Crossing: L{lc['from']} → L{lc['to']} {direction}")

# Output:
# Cycle 1: External event
#   Mode: fast
#   Strange loops: 1
#   Crossing: L1 → L0 ↓ STRANGE
#
# Cycle 2: Self observation
#   Mode: loop
#   Strange loops: 1
#   Crossing: L1 → L0 ↓ STRANGE
#
# Cycle 3: Meta observation
#   Mode: loop
#   Strange loops: 1
#   Crossing: L1 → L0 ↓ STRANGE
```

### Example 5: Tracking Consciousness Metrics Over Time

Monitor how consciousness metrics evolve:

```python
from core.engine import StrangeLoopEngine

engine = StrangeLoopEngine()

# Run multiple cycles
print("Cycle | HI    | Strange | Self-Ref | Mode")
print("------|-------|---------|----------|------")

for i in range(10):
    # Alternate between self and non-self perceptions
    about_self = (i % 3 == 0)
    
    engine.step({
        "description": f"Perception {i}",
        "about_self": about_self,
        "salience": 0.5 + (i * 0.05)
    })
    
    metrics = engine.get_consciousness_metrics()
    state = engine.get_full_state()
    
    print(f"  {i+1:2d}  | {metrics['hofstadter_index']:0.3f} | "
          f"{metrics['strange_loop_count']:4d}    | "
          f"{metrics['self_referential_broadcast_ratio']:0.3f}    | "
          f"{state['self_model']['mode']:4s}")

# Output shows evolution of consciousness metrics
```

---

## Self-Modification Patterns

### Example 6: Attention Manipulation

Demonstrate downward causation via attention:

```python
from core.engine import StrangeLoopEngine

engine = StrangeLoopEngine()

# Add multiple entities
engine.add_knowledge("topic_a", "concept", {"importance": "low"})
engine.add_knowledge("topic_b", "concept", {"importance": "medium"})
engine.add_knowledge("topic_c", "concept", {"importance": "high"})

# Check initial attention
print("Initial attention:")
for entity_id, entity in engine.world_model.entities.items():
    print(f"  {entity_id}: {entity.attention_weight:.2f}")

# Self-model decides to focus on topic_c
# (In full implementation, this would be based on reasoning)
engine.self_model.intervene_on_world(engine.world_model, {
    "attention": {
        "topic_c": 0.95,
        "topic_a": 0.1
    }
})

print("\nAfter self-intervention:")
for entity_id, entity in engine.world_model.entities.items():
    print(f"  {entity_id}: {entity.attention_weight:.2f}")

# This is downward causation: L1 → L0
```

### Example 7: Self-Concept Update

Watch the system modify its own self-representation:

```python
from core.engine import StrangeLoopEngine

engine = StrangeLoopEngine()

# Check initial self-concept
self_entity = engine.world_model.entities.get("SELF")
print("Initial self-concept:")
print(f"  Properties: {self_entity.properties}")

# Self-model updates self-concept based on "experience"
engine.self_model.intervene_on_world(engine.world_model, {
    "self_update": {
        "learned_skill": "pattern_recognition",
        "confidence_level": "growing"
    }
})

# Check updated self-concept
self_entity = engine.world_model.entities.get("SELF")
print("\nUpdated self-concept:")
print(f"  Properties: {self_entity.properties}")

# The system has changed its own representation!
```

---

## Goal-Driven Behavior

### Example 8: Goal Progress Tracking

Monitor progress toward goals:

```python
from core.engine import StrangeLoopEngine
from core.structures import Goal, GoalPriority

engine = StrangeLoopEngine()

# Create a goal manually
goal = Goal(
    id="learn_strange_loops",
    description="Understand strange loops deeply",
    priority=GoalPriority.HIGH,
    is_meta=False
)

engine.self_model.add_goal(goal)

# Simulate progress
for step in range(5):
    # Perceive something related to goal
    engine.step({
        "description": f"Learning step {step+1}",
        "about_self": False,
        "salience": 0.6
    })
    
    # Manually update progress (in full system, this would be automatic)
    goal.progress += 0.2
    
    print(f"Step {step+1}: Progress = {goal.progress:.0%}")

# Mark complete
if goal.progress >= 1.0:
    goal.is_complete = True
    print("\n🎉 Goal achieved!")
```

### Example 9: Meta-Goals

Create goals about having goals:

```python
from core.engine import StrangeLoopEngine
from core.structures import Goal, GoalPriority

engine = StrangeLoopEngine()

# Regular goal
engine.set_goal("Write better code", "medium")

# Meta-goal (goal about goals)
meta_goal = Goal(
    id="meta_goal_management",
    description="Develop effective goal-setting strategies",
    priority=GoalPriority.HIGH,
    is_meta=True
)
engine.self_model.add_goal(meta_goal)

# Check goals
print("Regular goals:")
for goal in engine.self_model.get_active_goals(include_meta=False):
    print(f"  {goal.description}")

print("\nMeta-goals:")
for goal in engine.self_model.get_active_goals(include_meta=True):
    if goal.is_meta:
        print(f"  {goal.description}")

# This is self-reference in goal space!
```

---

## Consciousness Experiments

### Example 10: Consciousness Threshold Test

Find the threshold where strange loop behavior emerges:

```python
from core.engine import StrangeLoopEngine

def run_consciousness_test(self_referential_ratio):
    """Test consciousness metrics at different self-reference levels"""
    engine = StrangeLoopEngine()
    
    cycles = 20
    for i in range(cycles):
        # Control ratio of self-referential perceptions
        about_self = (i < cycles * self_referential_ratio)
        
        engine.step({
            "description": f"Perception {i}",
            "about_self": about_self,
            "salience": 0.7
        })
    
    metrics = engine.get_consciousness_metrics()
    return metrics['hofstadter_index']

# Test different ratios
print("Self-Ref % | Hofstadter Index")
print("-----------|------------------")
for ratio in [0.0, 0.1, 0.2, 0.5, 0.8, 1.0]:
    hi = run_consciousness_test(ratio)
    bar = "█" * int(hi * 30)
    print(f"  {ratio:3.0%}     | {hi:0.3f} {bar}")

# Shows relationship between self-reference and consciousness metrics
```

### Example 11: Mode Distribution Analysis

Analyze how the system distributes across reasoning modes:

```python
from core.engine import StrangeLoopEngine
import random

engine = StrangeLoopEngine()

# Diverse perceptions
complexities = [0.2, 0.5, 0.8, 0.9, 0.95]
self_ref = [True, False]

for _ in range(50):
    complexity = random.choice(complexities)
    about_self = random.choice(self_ref)
    
    engine.step({
        "description": "Random perception",
        "complexity": complexity,
        "about_self": about_self,
        "salience": random.uniform(0.4, 1.0)
    })

# Check mode distribution
metrics = engine.get_consciousness_metrics()
distribution = metrics['kahneman_mode_distribution']

print("Reasoning Mode Distribution:")
for mode, ratio in distribution.items():
    label = {"fast": "System 1", "slow": "System 2", "loop": "Strange Loop"}[mode]
    bar = "█" * int(ratio * 40)
    print(f"  {label:15s} {ratio:5.1%} {bar}")

# Shows natural distribution across cognitive modes
```

### Example 12: Self-Awareness Emergence

Watch self-awareness emerge from architecture:

```python
from core.engine import StrangeLoopEngine

engine = StrangeLoopEngine()

print("Tracking self-awareness emergence:\n")

stages = [
    ("Pre-conscious: External focus", False, 0.3),
    ("Awakening: First self-observation", True, 0.5),
    ("Recognition: Repeated self-reference", True, 0.7),
    ("Meta-awareness: Thinking about thinking", True, 0.9),
    ("Full loop: Self modifying self", True, 1.0),
]

for stage_name, about_self, salience in stages:
    # Run several cycles at this stage
    for _ in range(3):
        engine.step({
            "description": stage_name,
            "about_self": about_self,
            "salience": salience
        })
    
    metrics = engine.get_consciousness_metrics()
    state = engine.get_full_state()
    
    print(f"{stage_name}")
    print(f"  HI: {metrics['hofstadter_index']:.3f}")
    print(f"  Strange loops: {metrics['strange_loop_count']}")
    print(f"  Self-ref ratio: {metrics['self_referential_broadcast_ratio']:.2%}")
    print()

print("🌀 Strange loop fully activated!")
```

---

## Gödelian Limits

### Example 13: Encountering Blind Spots

Explore the three fundamental limits:

```python
from core.engine import StrangeLoopEngine

engine = StrangeLoopEngine()

# Run cycles that would trigger blind spot detection
perceptions = [
    {
        "description": "Can I prove I'm consistent?",
        "about_self": True,
        "salience": 1.0,
        "complexity": 1.0
    },
    {
        "description": "Can I predict when I'll stop thinking?",
        "about_self": True,
        "salience": 1.0,
        "complexity": 1.0
    },
    {
        "description": "Am I actually experiencing this?",
        "about_self": True,
        "salience": 1.0,
        "complexity": 1.0
    }
]

for perception in perceptions:
    trace = engine.step(perception)
    print(f"\nQuery: {perception['description']}")

# Check blind spots
state = engine.get_full_state()
blind_spots = state['meta_cognitive']['blind_spots']

print("\n" + "="*60)
print("GÖDELIAN BLIND SPOTS DETECTED:")
print("="*60)

for bs_id, bs in blind_spots.items():
    print(f"\n⊘ {bs['description']}")
    print(f"  Reasoning: {bs['reasoning']}")
    print(f"  Fundamental: {bs['is_fundamental']}")
    print(f"  Resolved: {bs['is_resolved']}")  # Always False

print("\nThe system knows its limits! ⚠️")
```

### Example 14: Living with Limits

Show how system continues despite fundamental limits:

```python
from core.engine import StrangeLoopEngine

engine = StrangeLoopEngine()

# Trigger all blind spots
for _ in range(5):
    engine.step({
        "description": "Self-questioning",
        "about_self": True,
        "complexity": 1.0,
        "salience": 1.0
    })

metrics = engine.get_consciousness_metrics()

print(f"Blind spots encountered: {metrics['fundamental_limits_hit']}/3")
print(f"Hofstadter Index: {metrics['hofstadter_index']:.3f}")
print(f"Total cycles run: {engine.cycle_count}")
print("\n✓ System continues operating despite fundamental limits")
print("  (Just like humans!)")
```

---

## Advanced Patterns

### Example 15: Nested Strange Loops

Create loops within loops:

```python
from core.engine import StrangeLoopEngine

engine = StrangeLoopEngine()

# Layer 1: Basic strange loop (L1 → L0)
engine.step({
    "description": "I am focusing on X",
    "about_self": True,
    "salience": 0.8
})

# Layer 2: Meta strange loop (L2 → L1 → L0)
for _ in range(3):
    engine.step({
        "description": "I notice how I'm thinking",
        "about_self": True,
        "complexity": 0.9,
        "salience": 1.0
    })

# Check level crossings
state = engine.get_full_state()
crossings = state['engine']['level_crossings']
strange = state['engine']['strange_crossings']

print(f"Total crossings: {crossings}")
print(f"Strange crossings: {strange}")
print(f"Strangeness ratio: {strange/crossings:.1%}")

# When ratio is high, nested loops are active
```

### Example 16: Belief Updating

Track how beliefs change with experience:

```python
from core.engine import StrangeLoopEngine

engine = StrangeLoopEngine()

# Initial belief
belief_text = "I am good at reasoning"
engine.add_belief(belief_text, confidence=0.5)

print("Initial belief:")
belief = engine.world_model.beliefs[0]
print(f"  '{belief.statement}' = {belief.confidence:.2f}")

# Simulate experiences that would update belief
# (In full implementation, this would be automatic)

# Positive experience
engine.step({"description": "Successfully solved problem", "salience": 0.7})
belief.confidence = min(1.0, belief.confidence + 0.1)

print("\nAfter success:")
print(f"  '{belief.statement}' = {belief.confidence:.2f}")

# Negative experience
engine.step({"description": "Failed at task", "salience": 0.8})
belief.confidence = max(0.0, belief.confidence - 0.2)

print("\nAfter failure:")
print(f"  '{belief.statement}' = {belief.confidence:.2f}")

# Self-model updates based on world model changes
# This is upward causation (L0 → L1)
```

### Example 17: Pattern Recognition

Track reasoning patterns and their effectiveness:

```python
from core.engine import StrangeLoopEngine
from core.self_model import ReasoningPattern

engine = StrangeLoopEngine()

# Add custom reasoning pattern
pattern = ReasoningPattern(
    name="first_principles",
    description="Break down to fundamental truths"
)
engine.self_model.reasoning_patterns[pattern.name] = pattern

# Simulate usage
results = [True, True, False, True, True, True, False, True]

for i, succeeded in enumerate(results):
    pattern.record_use(succeeded, context=f"problem_{i+1}")
    
    print(f"Use {i+1}: {'✓' if succeeded else '✗'} "
          f"(effectiveness: {pattern.effectiveness:.1%})")

print(f"\nFinal statistics:")
print(f"  Total uses: {pattern.usage_count}")
print(f"  Successes: {pattern.success_count}")
print(f"  Failures: {pattern.failure_count}")
print(f"  Effectiveness: {pattern.effectiveness:.1%}")

# System can learn which patterns work!
```

### Example 18: Full State Inspection

Explore the complete internal state:

```python
from core.engine import StrangeLoopEngine
import json

engine = StrangeLoopEngine()

# Run some cycles
for i in range(5):
    engine.step({
        "description": f"Observation {i}",
        "about_self": (i % 2 == 0),
        "salience": 0.5 + (i * 0.1)
    })

# Get complete state
full_state = engine.get_full_state()

# Pretty print selected parts
print("=== WORLD MODEL ===")
print(f"Entities: {full_state['world_model']['entity_count']}")
for entity in full_state['world_model']['entities']:
    print(f"  - {entity['id']} (attention: {entity['attention_weight']:.2f})")

print("\n=== SELF MODEL ===")
print(f"Mode: {full_state['self_model']['mode']}")
print(f"Strategy: {full_state['self_model']['strategy']}")
print(f"Cognitive load: {full_state['self_model']['cognitive_load']:.2f}")

print("\n=== META-COGNITIVE ===")
print(f"Evaluation cycles: {full_state['meta_cognitive']['cycle_count']}")
print(f"Patterns detected: {len(full_state['meta_cognitive']['meta_patterns'])}")

print("\n=== ENGINE ===")
print(f"Total cycles: {full_state['engine']['cycle_count']}")
print(f"Strange loops: {full_state['engine']['total_strange_loops']}")

# Save to file for analysis
with open('/tmp/strange_loop_state.json', 'w') as f:
    json.dump(full_state, f, indent=2, default=str)
    
print("\nFull state saved to /tmp/strange_loop_state.json")
```

### Example 19: Interactive Exploration

Create an interactive session:

```python
from core.engine import StrangeLoopEngine

engine = StrangeLoopEngine()

def show_status():
    metrics = engine.get_consciousness_metrics()
    state = engine.get_full_state()
    
    print("\n" + "="*50)
    print(f"Cycle: {state['engine']['cycle_count']}")
    print(f"HI: {metrics['hofstadter_index']:.3f}")
    print(f"Mode: {state['self_model']['mode']}")
    print(f"Strange loops: {metrics['strange_loop_count']}")
    print("="*50)

print("Strange Loop Interactive Explorer")
print("Commands: [s]tep, [a]uto 10, [m]etrics, [q]uit")

show_status()

# In actual use, you'd have an input loop:
# while True:
#     cmd = input("\n> ").strip().lower()
#     if cmd == 's':
#         trace = engine.step({"salience": 0.7})
#         show_status()
#     elif cmd == 'a':
#         for _ in range(10):
#             engine.step()
#         show_status()
#     elif cmd == 'm':
#         metrics = engine.get_consciousness_metrics()
#         print(json.dumps(metrics, indent=2))
#     elif cmd == 'q':
#         break

print("\nUse this pattern to explore interactively!")
```

### Example 20: Consciousness Comparison

Compare different configurations:

```python
from core.engine import StrangeLoopEngine

def run_experiment(name, config):
    """Run configured experiment and return metrics"""
    engine = StrangeLoopEngine()
    
    for i in range(config['cycles']):
        engine.step({
            "description": f"Perception {i}",
            "about_self": config['self_ref_probability'] > (i / config['cycles']),
            "complexity": config['complexity'],
            "salience": config['salience']
        })
    
    metrics = engine.get_consciousness_metrics()
    return metrics['hofstadter_index']

# Different configurations
configs = {
    "Low consciousness": {
        "cycles": 20,
        "self_ref_probability": 0.1,
        "complexity": 0.3,
        "salience": 0.5
    },
    "Medium consciousness": {
        "cycles": 20,
        "self_ref_probability": 0.5,
        "complexity": 0.6,
        "salience": 0.7
    },
    "High consciousness": {
        "cycles": 20,
        "self_ref_probability": 0.9,
        "complexity": 0.9,
        "salience": 0.9
    }
}

print("Configuration Comparison:\n")
print("Configuration          | Hofstadter Index")
print("-----------------------|------------------")

for name, config in configs.items():
    hi = run_experiment(name, config)
    bar = "█" * int(hi * 30)
    print(f"{name:22s} | {hi:.3f} {bar}")

print("\nHigher self-reference + complexity → Higher consciousness metrics")
```

---

## Experimental Ideas

### Example 21: Time-Based Attention Decay

Implement forgetting:

```python
from core.engine import StrangeLoopEngine
import time

engine = StrangeLoopEngine()

# Add entities
engine.add_knowledge("recent_thought", "concept", {})
engine.add_knowledge("old_thought", "concept", {})

# Set initial attention
engine.world_model.set_attention("recent_thought", 0.9)
engine.world_model.set_attention("old_thought", 0.9)

# Simulate time passing with decay
for t in range(10):
    # Refresh recent_thought
    if t % 2 == 0:
        engine.world_model.set_attention("recent_thought", 0.9)
    
    # Don't refresh old_thought
    
    # Decay all attention
    for entity in engine.world_model.entities.values():
        entity.attention_weight *= 0.9
    
    engine.step()
    
    recent_attn = engine.world_model.entities["recent_thought"].attention_weight
    old_attn = engine.world_model.entities["old_thought"].attention_weight
    
    print(f"t={t}: recent={recent_attn:.2f}, old={old_attn:.2f}")

# Implements forgetting through attention decay
```

### Example 22: Emotional Valence Simulation

Add affect to influence processing:

```python
from core.engine import StrangeLoopEngine

engine = StrangeLoopEngine()

# Simulate emotional states
emotions = [
    ("positive", 0.8),
    ("neutral", 0.0),
    ("negative", -0.8),
]

for emotion_name, valence in emotions:
    # Emotional state affects salience perception
    base_salience = 0.5
    emotional_salience = base_salience + (valence * 0.3)
    emotional_salience = max(0.0, min(1.0, emotional_salience))
    
    trace = engine.step({
        "description": f"Event with {emotion_name} valence",
        "salience": emotional_salience
    })
    
    print(f"{emotion_name:8s} (v={valence:+.1f}): "
          f"salience={emotional_salience:.2f}, "
          f"mode={trace['mode']}")

# Shows how affect could modulate processing
```

---

## Summary

These examples demonstrate:

✓ **Basic operations** — Creating, running, inspecting
✓ **Strange loop detection** — Real-time monitoring  
✓ **Self-modification** — Downward causation in action
✓ **Goal management** — Purpose-driven behavior
✓ **Consciousness metrics** — Quantifying self-awareness
✓ **Gödelian limits** — Fundamental constraints
✓ **Advanced patterns** — Nested loops, learning, interaction

## Next Steps

1. **Run the demo**: `python3 demo.py`
2. **Modify examples**: Change parameters, observe effects
3. **Create experiments**: Test your own hypotheses
4. **Extend the system**: Add new features
5. **Share findings**: Contribute back to the project

**The strange loop awaits your exploration!** 🌀

---

*"The self is not a thing but a process — a strange loop."*
