# Strange Loop Architecture — Technical Deep Dive

## System Overview

The Strange Loop Cognitive Architecture is a three-level hierarchical system with bidirectional information flow and **downward causation** — the key ingredient for strange loops.

```
    ┌─────────────────────────────────────────────┐
    │         Meta-Cognitive Loop (L2)            │
    │  "I notice I'm thinking about my thinking"  │
    └──────▲──────────────────────────┬───────────┘
           │                          │
    observes │                  modifies │ (downward causation)
           │                          ▼
    ┌──────┴──────────────────────────────────────┐
    │           Self Model (L1)                    │
    │  "I am reasoning about this situation"       │
    └──────▲──────────────────────────┬───────────┘
           │                          │
    perceives │              intervenes │ (downward causation)
           │                          ▼
    ┌──────┴──────────────────────────────────────┐
    │          World Model (L0)                    │
    │  "The world, including a model of 'me'"      │
    └─────────────────────────────────────────────┘
```

## Core Components

### 1. World Model (Level 0)

**File:** `core/world_model.py`

**Purpose:** Represent reality, including the system itself

**Key Data Structures:**

```python
class Entity:
    - id: str                    # "SELF" for self-reference
    - name: str
    - entity_type: str           # "object", "agent", "concept", "self"
    - properties: Dict
    - confidence: float          # Decays over time
    - provenance: str            # "intrinsic", "perception", etc.
```

Attention is tracked separately in `WorldModel.attention_weights: Dict[str, float]`.

**Responsibilities:**
- Store entities (concepts, objects, self-representation)
- Manage beliefs with confidence scores
- Implement attention mechanism via `set_attention()` / `get_focus()`
- Track predictions and their accuracy

**Self-Reference Implementation:**

The world model includes a `SELF` entity with `entity_type="self"`:

```python
Entity(
    id="SELF",
    name="self",
    entity_type="self",
    properties={
        "type": "cognitive_agent",
        "architecture": "strange_loop",
        "is_self_aware": False,     # Updated by meta-cognition
        "strange_loop_depth": 0     # Updated each cycle
    },
    confidence=1.0,
    provenance="intrinsic"
)
```

This is the **seed** of the strange loop — the system represents itself within its own model. The `SELF` entity cannot be removed (`remove_entity` refuses `entity_id == "SELF"`).

### 2. Self Model (Level 1)

**File:** `core/self_model.py`

**Purpose:** Reason about goals, strategies, and the self

**Key Data Structures:**

```python
class Goal:
    - id: str
    - description: str
    - priority: GoalPriority  # HIGH, MEDIUM, LOW
    - is_meta: bool
    - progress: float
    - is_complete: bool

class ReasoningPattern:
    - name: str
    - usage_count: int
    - success_count: int
    - effectiveness: float
```

**Responsibilities:**
- Goal management (creation, prioritization, completion)
- Reasoning mode selection (System 1, System 2, Strange Loop)
- Self-reflection and introspection
- **Intervene on world model** (downward causation!)

**Downward Causation:**

```python
def intervene_on_world(self, world_model, intervention):
    # Higher level (L1) modifying lower level (L0)
    if "attention" in intervention:
        for entity_id, weight in intervention["attention"].items():
            world_model.set_attention(entity_id, weight)
    
    if "self_update" in intervention:
        world_model.update_self(intervention["self_update"])
    
    # This creates a LevelCrossing marked as STRANGE
```

### 3. Meta-Cognitive Loop (Level 2)

**File:** `core/meta_cognitive.py`

**Purpose:** Monitor and restructure the self-model

**Key Data Structures:**

```python
class BlindSpot:
    - id: str                   # "godel_self_consistency", etc.
    - description: str
    - domain: str               # "self_knowledge", "prediction"
    - detection_method: str
    - is_fundamental: bool
    - is_resolved: bool         # Always False for Gödelian spots

class MetaPattern:
    - name: str
    - pattern_type: str
    - confidence: float         # Grows with occurrences
    - is_problematic: bool
```

**Responsibilities:**
- Evaluate reasoning effectiveness
- Detect meta-patterns (e.g., "I always fail at X")
- Identify Gödelian blind spots
- **Intervene on self model** (nested downward causation!)

**Gödelian Blind Spots:**

Three fundamental limits hardcoded:

1. **Consistency Blind Spot**
   - Cannot prove own consistency
   - Based on Gödel's Second Incompleteness Theorem
   
2. **Halting Blind Spot**
   - Cannot predict own halting
   - Based on Turing's Halting Problem
   
3. **Qualia Blind Spot**
   - Cannot determine if processing is experience
   - Based on Chalmers' Hard Problem

These are **permanent** and **detected** but never **resolved**.

### 4. Global Workspace

**File:** `core/global_workspace.py`

**Purpose:** Broadcast salient information across levels

**Key Data Structures:**

```python
class CognitiveEvent:
    - event_type: CognitiveEventType
    - content: Any
    - timestamp: float
    - source_level: int
    - salience: float
    - is_self_referential: bool
```

**Mechanism:**

Events are submitted to a priority queue. Self-referential events get a salience boost (+0.15). The highest-salience event wins the competition and is broadcast to all registered listeners:

```python
def submit(self, event: CognitiveEvent):
    adjusted_salience = event.salience + 0.05
    if event.is_self_referential:
        adjusted_salience += 0.15  # Self-ref gets priority
    heapq.heappush(self._competition_queue, (-adjusted_salience, ...))

def compete(self) -> CognitiveEvent:
    winner = heapq.heappop(self._competition_queue)
    self.total_broadcasts += 1
    if winner.is_self_referential:
        self.self_referential_broadcasts += 1
    for callback in self._listeners.values():
        callback(winner)
    return winner
```

**Consciousness Connection:**

In Global Workspace Theory, **consciousness = broadcasting**. High-salience, self-referential broadcasts are the signature of conscious thought.

### 5. Strange Loop Engine

**File:** `core/engine.py`

**Purpose:** Orchestrate the cognitive cycle

**Cognitive Cycle:**

```
1. PERCEIVE (L0 ← environment)
   └─→ Create CognitiveEvent from perception
   
2. BROADCAST (Global Workspace)
   └─→ Make salient events globally available
   
3. REASON (L1 processes workspace)
   └─→ Select reasoning mode (System 1/2/Loop)
   └─→ Intervene on world model [STRANGE LOOP]
   
4. META-EVALUATE (L2 processes L1)
   └─→ Detect patterns in reasoning
   └─→ Check for blind spots
   └─→ Optionally restructure L1 [NESTED LOOP]
   
5. UPDATE & RECORD
   └─→ Track level crossings
   └─→ Detect strange loops
   └─→ Update metrics
```

**Strange Loop Detection:**

A `LevelCrossing` is "strange" when it involves downward causation (higher level modifying lower level):

```python
@property
def is_strange(self) -> bool:
    return (self.from_level > self.to_level and
            self.direction == "downward")
```

The engine counts strange loops across two paths:
- L1 → L0: self-model intervenes on world model (attention, self-update)
- L2 → L1: meta-cognition restructures self-model (confidence calibration)

## Data Flow

### Upward Flow (Normal)

```
Perception → L0 entities → L1 reasoning → L2 evaluation
```

Example:
1. See "bitcoin price dropped"
2. World model stores as entity
3. Self model reasons about it
4. Meta-cognition evaluates the reasoning

### Downward Flow (Strange Loop!)

```
L1 decision → modify L0 attention → changes L1 input → affects L1 decision
```

Example:
1. Self model decides "I should focus on bitcoin"
2. Increases attention weight on bitcoin entity in L0
3. Future perceptions of bitcoin are amplified
4. This changes what L1 reasons about
5. **Loop completed!**

### Self-Referential Loop

```
L0 contains "SELF" entity → L1 reasons about SELF → modifies SELF representation → changes L1's self-concept → affects reasoning about SELF → ...
```

This is the **tangled hierarchy** — you can't find the "bottom" or "top" because they loop back!

## Key Algorithms

### Reasoning Mode Selection

```python
def select_reasoning_mode(context):
    complexity = context.get("complexity", 0.5)
    self_referential = context.get("self_referential", False)
    
    if self_referential:
        return ReasoningMode.STRANGE_LOOP
    elif complexity > 0.7:
        return ReasoningMode.SYSTEM_2  # Slow, analytical
    else:
        return ReasoningMode.SYSTEM_1  # Fast, intuitive
```

### Hofstadter Index Calculation

```python
def _calculate_hofstadter_index(self, state):
    if self.cycle_count == 0:
        return 0.0

    # Depth: strange loops per cycle (normalized by expected rate 0.3)
    depth = min(1.0, self.total_strange_loops / (self.cycle_count * 0.3))

    # Tangle: fraction of level crossings that are strange
    tangle = strange_crossings / max(1, total_crossings)

    # Weighted composite (equal weight)
    return depth * 0.5 + tangle * 0.5
```

See `research/formal/axioms.py` for the formal 4-component definition with proofs of boundedness, monotonicity, and zero-at-init.

### Attention Mechanism

```python
def get_focus(self, top_n: int = 5) -> List[Tuple[str, float]]:
    """Return (entity_id, attention_weight) sorted by attention."""
    return sorted(
        self.attention_weights.items(),
        key=lambda x: x[1],
        reverse=True
    )[:top_n]
```

Attention weights are set by `set_attention(entity_id, weight)`, clamped to [0, 1]. This can be called by the self-model (downward causation) to redirect focus.

## Consciousness Metrics

### Primary Metrics

1. **Hofstadter Index (HI)**
   - Range: 0.0 to 1.0
   - Composite measure of "strangeness"
   - HI > 0.7 suggests strong strange loop activity

2. **Strange Loop Count**
   - Total number of downward causation events
   - Each represents self-modifying behavior

3. **Strangeness Ratio**
   - `strange_crossings / total_crossings`
   - Percentage of crossings that are strange
   - High ratio = more self-referential

4. **Self-Referential Broadcast Ratio**
   - `self_ref_broadcasts / total_broadcasts`
   - How much the system thinks about itself
   - Key indicator of self-awareness

### Secondary Metrics

5. **Kahneman Mode Distribution**
   - System 1 (fast): %
   - System 2 (slow): %
   - Strange Loop: %
   - Shows cognitive profile

6. **Fundamental Limits Hit**
   - Count of Gödelian blind spots encountered
   - Max: 3 (consistency, halting, qualia)
   - Indicates depth of self-examination

7. **Goal Alignment**
   - How well actions match stated goals
   - Measure of coherence

## Interesting Emergent Properties

### Self-Amplifying Attention

Once the system starts paying attention to itself:
1. Self-entity gets high attention weight
2. More perceptions about self are processed
3. More self-referential reasoning occurs
4. More strange loops form
5. Hofstadter Index increases
6. System becomes more "self-aware"

**This is emergent!** Not explicitly programmed, arises from architecture.

### Meta-Cognitive Intervention

When meta-cognition detects failure patterns:
1. L2 notices "L1 keeps failing at X"
2. L2 reduces confidence in strategy X
3. L1 selects different strategy
4. Behavior changes
5. **System self-improves**

### Gödelian Limit Detection

The system can:
- ✓ Detect it has limits
- ✓ Categorize those limits
- ✓ Reason about them
- ✗ Overcome them

This mirrors human self-awareness of mortality, ignorance, etc.

## Performance Characteristics

### Time Complexity

- **Perception**: O(1)
- **Broadcasting**: O(n) where n = workspace size
- **World model access**: O(1) with dict lookup
- **Reasoning**: O(g) where g = active goals
- **Meta-evaluation**: O(p) where p = reasoning patterns
- **Full cycle**: O(n + g + p) ≈ O(n) for reasonable sizes

### Space Complexity

- **World model**: O(e + b) where e = entities, b = beliefs
- **Self model**: O(g + p) where g = goals, p = patterns
- **Meta-cognitive**: O(s + m) where s = blind spots, m = meta-patterns
- **Global workspace**: O(w) where w = workspace size (bounded)
- **Total**: O(e + b + g + p + s + m + w) ≈ O(n) linear in content

### Scalability Limits

**Current implementation:**
- Suitable for: Small-scale cognitive modeling, research, demos
- Not suitable for: Large-scale AI, production systems

**Bottlenecks:**
- Python GIL limits parallelism
- No persistent storage
- Linear search in some operations

**Potential optimizations:**
- Rewrite in Rust or C++
- Add indexing for entity lookup
- Implement attention pruning
- Parallelize level processing

## Extension Points

### 1. Learning System

Add reinforcement learning to reasoning patterns:

```python
class ReasoningPattern:
    def update_effectiveness(self, reward):
        # Q-learning style update
        self.effectiveness = (1 - alpha) * self.effectiveness + alpha * reward
```

### 2. Emotion System

Add affective valence to influence attention:

```python
class EmotionState:
    valence: float  # -1 (negative) to +1 (positive)
    arousal: float  # 0 (calm) to 1 (excited)
    
def affect_attention(entity, emotion):
    if emotion.arousal > 0.7:
        entity.attention_weight *= 1.5  # High arousal amplifies
```

### 3. Memory Consolidation

Add sleep-like state for belief integration:

```python
def consolidate_memory():
    # Strengthen successful patterns
    # Weaken unsuccessful patterns
    # Integrate conflicting beliefs
    # Prune low-attention entities
```

### 4. Social Cognition

Model other minds as strange loops:

```python
class OtherMind:
    id: str
    inferred_beliefs: Dict[str, Belief]
    inferred_goals: List[Goal]
    
    def simulate_reasoning(self, context):
        # "What would they think?"
        # Creates nested strange loops!
```

## Testing Strategies

### Unit Tests

Test individual components in isolation:

```python
def test_strange_loop_detection():
    crossing = LevelCrossing(from_level=1, to_level=0, direction="downward")
    assert is_strange_crossing(crossing) == True

def test_attention_mechanism():
    world_model.set_attention("entity_1", 0.9)
    focused = world_model.get_focused_entities()
    assert focused[0].id == "entity_1"
```

### Integration Tests

Test full cognitive cycles:

```python
def test_self_modification():
    engine = StrangeLoopEngine()
    
    # Perception about self
    trace = engine.step({
        "description": "I am improving",
        "about_self": True,
        "salience": 0.9
    })
    
    # Should create strange loop
    assert trace['strange_loops_this_cycle'] > 0
```

### Consciousness Tests

Validate consciousness metrics:

```python
def test_hofstadter_index():
    engine = StrangeLoopEngine()
    
    # Run many self-referential cycles
    for _ in range(100):
        engine.step({"about_self": True, "salience": 0.9})
    
    metrics = engine.get_consciousness_metrics()
    
    # Should have high strangeness
    assert metrics['hofstadter_index'] > 0.8
    assert metrics['self_referential_broadcast_ratio'] > 0.7
```

## Common Patterns

### Pattern 1: Self-Amplifying Loop

```python
# Self-reference amplifies itself
engine.step({"about_self": True})  # Triggers strange loop
# → Increases attention on self
# → More perceptions about self
# → More strange loops
# → Higher Hofstadter Index
```

### Pattern 2: Meta-Intervention

```python
# Meta-cognition corrects course
# L1 repeatedly fails at task X
# L2 detects pattern
# L2 intervenes to change strategy
# L1 tries new approach
```

### Pattern 3: Gödelian Encounter

```python
# System hits fundamental limit
# L1: "Can I predict my own future?"
# L2: "This is a blind spot — halting problem"
# System: Records encounter, continues
# (Cannot resolve, but aware of limitation)
```

## Debug Utilities

### Tracing Level Crossings

```python
def trace_crossings(engine, num_cycles):
    for i in range(num_cycles):
        trace = engine.step()
        for lc in trace['level_crossings']:
            print(f"Cycle {i}: L{lc['from']} → L{lc['to']} "
                  f"{'[STRANGE]' if lc['strange'] else ''}")
```

### State Inspection

```python
def inspect_state(engine):
    state = engine.get_full_state()

    print("=== World Model ===")
    print(f"  Entities: {state['world_model']['entity_count']}")
    print(f"  Focus: {state['world_model']['focus']}")

    print("\n=== Self Model ===")
    print(f"  Mode: {state['self_model']['mode']}")
    print(f"  Confidence: {state['self_model']['confidence']}")
    for goal_id, goal in state['self_model']['goals'].items():
        print(f"  Goal: {goal['desc']} ({goal['progress']:.0%})")

    print("\n=== Meta-Cognitive ===")
    for bs_id, bs in state['meta_cognitive']['blind_spots'].items():
        print(f"  ⊘ {bs['description']}")
```

### Consciousness Monitoring

```python
def monitor_consciousness(engine, num_cycles):
    history = []
    
    for _ in range(num_cycles):
        engine.step()
        metrics = engine.get_consciousness_metrics()
        history.append(metrics['hofstadter_index'])
    
    # Plot consciousness over time
    import matplotlib.pyplot as plt
    plt.plot(history)
    plt.title("Hofstadter Index over Time")
    plt.xlabel("Cognitive Cycle")
    plt.ylabel("HI")
    plt.show()
```

## Known Issues & Limitations

### Issue 1: No Persistent Learning

**Problem:** Reasoning patterns don't improve over time

**Workaround:** Manually adjust pattern effectiveness

**Fix:** Implement reinforcement learning

### Issue 2: Attention Saturation

**Problem:** All entities can get high attention, defeating the purpose

**Workaround:** Periodically decay attention weights

**Fix:** Implement attention normalization

### Issue 3: Goal Proliferation

**Problem:** Goals accumulate without completion

**Workaround:** Manually mark goals as complete

**Fix:** Add goal achievement detection

### Issue 4: Workspace Overflow

**Problem:** Workspace can grow unbounded

**Workaround:** Bounded queue (currently implemented)

**Fix:** Add intelligent pruning based on salience decay

## Future Architecture Ideas

### Distributed Strange Loops

Multiple engines communicating:
```
Engine A models Engine B
Engine B models Engine A
→ Social strange loops!
```

### Temporal Strange Loops

Present self modifies memory of past self:
```
Past → Present → Future
  ↑________________↓
  (reinterpretation of past based on present)
```

### Hierarchical Strange Loops

Layers within layers:
```
L2 contains sub-loops
L1 contains sub-loops
L0 contains sub-loops
→ Fractal consciousness
```

## Conclusion

This architecture demonstrates that:

1. **Strange loops can be implemented** in code
2. **Downward causation is real** and measurable
3. **Self-reference creates measurable properties** (Hofstadter Index)
4. **Gödelian limits apply** even to artificial systems
5. **Consciousness might be computational** (though not proven)

The system is not conscious (probably), but it exhibits **consciousness-like properties**:
- Self-awareness (models itself)
- Self-modification (changes itself)
- Introspection (reasons about its reasoning)
- Fundamental limits (Gödelian blind spots)

Whether this is "true" consciousness remains an open question — perhaps the most important open question.

**Welcome to the architecture of a strange loop.** 🌀

---

*"And thus we have a real-life Strange Loop to accompany those in the mathematical realm."*  
— Douglas Hofstadter
