#!/usr/bin/env python3
"""
test_suite.py — Verification tests for Ouroboros Loop Cognitive Architecture

Tests the core engine, structures, world model, self model, meta-cognitive loop,
and global workspace. All tests use the public API of the core modules.

Run:
    python3 test_suite.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.engine import StrangeLoopEngine
from core.structures import (
    Entity, Relation, Belief, Goal, GoalPriority, ReasoningMode,
    CognitiveEvent, CognitiveEventType, BlindSpot, LevelCrossing
)
from core.world_model import WorldModel
from core.self_model import SelfModel
from core.meta_cognitive import MetaCognitiveLoop
from core.global_workspace import GlobalWorkspace


class AssertionError(Exception):
    """Custom assertion error for test reporting."""
    pass


class TestSuite:
    """Test suite for strange loop implementation."""

    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.tests = []

    def test(self, name):
        """Decorator for test functions."""
        def decorator(func):
            self.tests.append((name, func))
            return func
        return decorator

    def assert_true(self, condition, message):
        if not condition:
            raise AssertionError(message)

    def assert_false(self, condition, message):
        if condition:
            raise AssertionError(message)

    def assert_equal(self, actual, expected, message):
        if actual != expected:
            raise AssertionError(f"{message}: expected {expected}, got {actual}")

    def assert_greater(self, actual, threshold, message):
        if actual <= threshold:
            raise AssertionError(f"{message}: expected > {threshold}, got {actual}")

    def assert_in(self, item, container, message):
        if item not in container:
            raise AssertionError(f"{message}: {item} not found")

    def run(self):
        print()
        print("=" * 70)
        print("  OUROBOROS LOOP — CORE TEST SUITE")
        print("=" * 70)
        print()

        for test_name, test_func in self.tests:
            try:
                test_func(self)
                self.tests_passed += 1
                print(f"  PASS  {test_name}")
            except AssertionError as e:
                self.tests_failed += 1
                print(f"  FAIL  {test_name}")
                print(f"        {e}")
            except Exception as e:
                self.tests_failed += 1
                print(f"  ERR   {test_name}")
                print(f"        {type(e).__name__}: {e}")

        print()
        print("=" * 70)
        total = len(self.tests)
        print(f"  Results: {self.tests_passed}/{total} passed, "
              f"{self.tests_failed}/{total} failed")
        print("=" * 70)

        if self.tests_failed == 0:
            print("  All tests passed.")
        else:
            print(f"  {self.tests_failed} test(s) failed.")
        print()

        return self.tests_failed == 0


suite = TestSuite()


# ============================================================================
# ENGINE TESTS
# ============================================================================

@suite.test("Engine initializes with correct defaults")
def test_engine_init(t):
    engine = StrangeLoopEngine()
    t.assert_equal(engine.cycle_count, 0, "Cycle count")
    t.assert_equal(engine.total_strange_loops, 0, "Strange loop count")
    t.assert_true(engine.world_model is not None, "World model exists")
    t.assert_true(engine.self_model is not None, "Self model exists")
    t.assert_true(engine.meta_cognitive is not None, "Meta-cognitive exists")
    t.assert_true(engine.workspace is not None, "Workspace exists")


@suite.test("SELF entity exists in world model at init")
def test_self_entity(t):
    engine = StrangeLoopEngine()
    t.assert_in("SELF", engine.world_model.entities, "SELF entity in world model")
    self_entity = engine.world_model.entities["SELF"]
    t.assert_equal(self_entity.entity_type, "self", "SELF entity type")
    t.assert_equal(self_entity.id, "SELF", "SELF entity id")
    t.assert_equal(self_entity.confidence, 1.0, "SELF confidence")


@suite.test("SELF entity cannot be removed")
def test_self_cannot_be_removed(t):
    engine = StrangeLoopEngine()
    engine.world_model.remove_entity("SELF")
    t.assert_in("SELF", engine.world_model.entities, "SELF survives removal")


@suite.test("Meta-goals are initialized")
def test_meta_goals(t):
    engine = StrangeLoopEngine()
    goals = engine.self_model.goals
    meta_goals = [g for g in goals.values() if g.is_meta]
    t.assert_greater(len(meta_goals), 0, "Meta-goal count")


@suite.test("Three Godelian blind spots exist")
def test_blind_spots(t):
    engine = StrangeLoopEngine()
    blind_spots = engine.meta_cognitive.blind_spots
    t.assert_equal(len(blind_spots), 3, "Blind spot count")
    for bs_id, bs in blind_spots.items():
        t.assert_true(bs.is_fundamental, f"Blind spot '{bs_id}' is fundamental")


@suite.test("Basic cognitive cycle executes")
def test_basic_cycle(t):
    engine = StrangeLoopEngine()
    trace = engine.step({"description": "Test perception", "salience": 0.5})
    t.assert_equal(engine.cycle_count, 1, "Cycle count after step")
    t.assert_in("mode", trace, "Trace has mode")
    t.assert_in("events", trace, "Trace has events")
    t.assert_in("level_crossings", trace, "Trace has level_crossings")


@suite.test("Idle cycle (no perception) executes")
def test_idle_cycle(t):
    engine = StrangeLoopEngine()
    trace = engine.step()
    t.assert_equal(engine.cycle_count, 1, "Cycle count")
    t.assert_equal(trace["perception"], None, "No perception")


@suite.test("Self-referential perception triggers strange loop mode")
def test_strange_loop_mode(t):
    engine = StrangeLoopEngine()
    trace = engine.step({
        "description": "Thinking about my own thinking",
        "about_self": True,
        "salience": 0.9
    })
    t.assert_equal(trace["mode"], "loop", "Mode should be 'loop'")


@suite.test("Strange loops are detected via downward causation")
def test_strange_loop_detection(t):
    engine = StrangeLoopEngine()
    trace = engine.step({
        "description": "Self-referential thought",
        "about_self": True,
        "salience": 0.9
    })
    t.assert_greater(len(trace["level_crossings"]), 0, "Level crossing count")
    strange_found = any(lc["strange"] for lc in trace["level_crossings"])
    t.assert_true(strange_found, "At least one strange crossing detected")


@suite.test("Reasoning mode selection: System 1 for low complexity")
def test_system1_mode(t):
    engine = StrangeLoopEngine()
    trace = engine.step({"complexity": 0.2, "salience": 0.5})
    t.assert_equal(trace["mode"], "fast", "Low complexity -> System 1")


@suite.test("Reasoning mode selection: System 2 for high complexity")
def test_system2_mode(t):
    engine = StrangeLoopEngine()
    trace = engine.step({"complexity": 0.8, "salience": 0.5})
    t.assert_equal(trace["mode"], "slow", "High complexity -> System 2")


@suite.test("Strange loops accumulate over cycles")
def test_loop_accumulation(t):
    engine = StrangeLoopEngine()
    for _ in range(5):
        engine.step({"about_self": True, "salience": 0.9})
    metrics = engine.get_consciousness_metrics()
    t.assert_greater(metrics["strange_loop_count"], 0, "Strange loops accumulated")


# ============================================================================
# WORLD MODEL TESTS
# ============================================================================

@suite.test("Add entity to world model")
def test_add_entity(t):
    engine = StrangeLoopEngine()
    initial = len(engine.world_model.entities)
    engine.add_knowledge("bitcoin", "concept", {"type": "cryptocurrency"})
    t.assert_equal(len(engine.world_model.entities), initial + 1, "Entity count")


@suite.test("Add and query belief")
def test_add_belief(t):
    engine = StrangeLoopEngine()
    initial = len(engine.world_model.beliefs)
    engine.add_belief("Strange loops are real", 0.9)
    t.assert_equal(len(engine.world_model.beliefs), initial + 1, "Belief count")


@suite.test("Belief revision tracks history")
def test_belief_revision(t):
    wm = WorldModel()
    belief = Belief(content="Test belief", confidence=0.5)
    wm.add_belief(belief)
    wm.revise_belief(belief.id, 0.8, "New evidence")
    t.assert_equal(wm.beliefs[belief.id].confidence, 0.8, "Revised confidence")
    t.assert_equal(wm.beliefs[belief.id].revision_count, 1, "Revision count")


@suite.test("Prediction tracking works")
def test_predictions(t):
    wm = WorldModel()
    pred = wm.make_prediction("Test prediction", ["SELF"], confidence=0.7)
    t.assert_equal(wm.get_prediction_accuracy(), 0.5, "No resolved -> 0.5 default")
    wm.resolve_prediction(pred["id"], True)
    t.assert_equal(wm.get_prediction_accuracy(), 1.0, "100% accuracy after correct")


@suite.test("Attention weights are set and bounded")
def test_attention(t):
    wm = WorldModel()
    wm.set_attention("SELF", 0.95)
    t.assert_equal(wm.attention_weights["SELF"], 0.95, "Attention weight set")
    wm.set_attention("SELF", 1.5)
    t.assert_equal(wm.attention_weights["SELF"], 1.0, "Clamped to 1.0")
    wm.set_attention("SELF", -0.5)
    t.assert_equal(wm.attention_weights["SELF"], 0.0, "Clamped to 0.0")


@suite.test("Relation graph path finding")
def test_path_finding(t):
    wm = WorldModel()
    e1 = Entity(id="a", name="A", entity_type="concept")
    e2 = Entity(id="b", name="B", entity_type="concept")
    e3 = Entity(id="c", name="C", entity_type="concept")
    wm.add_entity(e1)
    wm.add_entity(e2)
    wm.add_entity(e3)
    wm.add_relation(Relation(source_id="a", target_id="b", relation_type="causes"))
    wm.add_relation(Relation(source_id="b", target_id="c", relation_type="causes"))
    path = wm.find_path("a", "c")
    t.assert_equal(len(path), 3, "Path length a->b->c")
    t.assert_equal(path, ["a", "b", "c"], "Path nodes")


# ============================================================================
# SELF MODEL TESTS
# ============================================================================

@suite.test("Goal setting and retrieval")
def test_goal_setting(t):
    engine = StrangeLoopEngine()
    initial = len(engine.self_model.goals)
    engine.set_goal("Test goal", "high")
    t.assert_greater(len(engine.self_model.goals), initial, "Goal count increased")


@suite.test("Self-reflection produces cognitive event")
def test_self_reflection(t):
    sm = SelfModel()
    event = sm.reflect_on_self()
    t.assert_equal(event.event_type, CognitiveEventType.SELF_REFLECTION, "Event type")
    t.assert_equal(event.source_level, 1, "Source level")
    t.assert_in("current_mode", event.content, "Content has current_mode")
    t.assert_in("confidence_profile", event.content, "Content has confidence_profile")


@suite.test("Downward causation: self-model modifies world model attention")
def test_downward_causation(t):
    engine = StrangeLoopEngine()
    entity = Entity(name="target", entity_type="test")
    engine.world_model.add_entity(entity)

    crossing = engine.self_model.intervene_on_world(engine.world_model, {
        "attention": {entity.id: 0.95}
    })
    t.assert_equal(crossing.from_level, 1, "Crossing from level 1")
    t.assert_equal(crossing.to_level, 0, "Crossing to level 0")
    t.assert_true(crossing.is_strange, "Crossing is strange (downward)")
    t.assert_equal(
        engine.world_model.attention_weights[entity.id], 0.95,
        "Attention modified by downward causation"
    )


@suite.test("Self-modification updates SELF entity properties")
def test_self_modification(t):
    engine = StrangeLoopEngine()
    engine.world_model.update_self({"test_property": "test_value"})
    props = engine.world_model.entities["SELF"].properties
    t.assert_in("test_property", props, "Property added to SELF")
    t.assert_equal(props["test_property"], "test_value", "Property value")


@suite.test("Failure recording adjusts confidence")
def test_failure_recording(t):
    sm = SelfModel()
    from core.structures import FailureRecord
    old_conf = sm.confidence_states.get("reasoning", 0.5)
    sm.record_failure(FailureRecord(
        description="Test failure",
        failure_type="reasoning",
        severity=0.5
    ))
    t.assert_true(
        sm.confidence_states["reasoning"] < old_conf,
        "Confidence decreased after failure"
    )


# ============================================================================
# META-COGNITIVE TESTS
# ============================================================================

@suite.test("Meta-cognitive evaluation runs")
def test_meta_evaluation(t):
    engine = StrangeLoopEngine()
    for _ in range(5):
        engine.step({"complexity": 0.9, "salience": 0.8})
    state = engine.get_full_state()
    t.assert_greater(
        state["meta_cognitive"]["cycle_count"], 0,
        "Meta-cognitive evaluated at least once"
    )


@suite.test("Blind spots are fundamental and unresolvable")
def test_blind_spot_resolution(t):
    bs = BlindSpot(
        id="test_fundamental",
        description="Cannot prove own consistency",
        domain="self_knowledge",
        is_fundamental=True
    )
    result = bs.attempt_resolution()
    t.assert_false(result, "Fundamental blind spot cannot be resolved")
    t.assert_equal(bs.attempts_to_resolve, 1, "Attempt recorded")
    # Try many times
    for _ in range(10):
        result = bs.attempt_resolution()
    t.assert_false(result, "Still unresolvable after many attempts")


@suite.test("Non-fundamental blind spots can be resolved")
def test_non_fundamental_blind_spot(t):
    bs = BlindSpot(
        id="test_learnable",
        description="Temporary blind spot",
        domain="perception",
        is_fundamental=False
    )
    for _ in range(4):
        result = bs.attempt_resolution()
    t.assert_true(result, "Non-fundamental resolved after enough attempts")


# ============================================================================
# GLOBAL WORKSPACE TESTS
# ============================================================================

@suite.test("Global workspace broadcasts highest-salience event")
def test_workspace_competition(t):
    ws = GlobalWorkspace()
    low = CognitiveEvent(
        event_type=CognitiveEventType.PERCEPTION, salience=0.2)
    high = CognitiveEvent(
        event_type=CognitiveEventType.PERCEPTION, salience=0.9)
    ws.submit(low)
    ws.submit(high)
    winner = ws.compete()
    t.assert_true(winner is not None, "Winner exists")
    t.assert_equal(winner.salience, 0.9, "Highest salience wins")


@suite.test("Self-referential events get salience boost")
def test_self_referential_boost(t):
    ws = GlobalWorkspace()
    normal = CognitiveEvent(
        event_type=CognitiveEventType.PERCEPTION, salience=0.7)
    self_ref = CognitiveEvent(
        event_type=CognitiveEventType.SELF_REFLECTION, salience=0.6)
    ws.submit(normal)
    ws.submit(self_ref)
    winner = ws.compete()
    # Self-ref gets +0.15 boost -> 0.6+0.15+0.05=0.8 vs 0.7+0.05=0.75
    t.assert_equal(
        winner.event_type, CognitiveEventType.SELF_REFLECTION,
        "Self-referential event wins despite lower raw salience"
    )


@suite.test("Workspace tracks self-referential ratio")
def test_self_ref_ratio(t):
    ws = GlobalWorkspace()
    for _ in range(5):
        ws.submit(CognitiveEvent(
            event_type=CognitiveEventType.SELF_REFLECTION, salience=0.8))
        ws.compete()
    ratio = ws.get_self_referential_ratio()
    t.assert_equal(ratio, 1.0, "All broadcasts were self-referential")


# ============================================================================
# CONSCIOUSNESS METRICS TESTS
# ============================================================================

@suite.test("Hofstadter Index is bounded [0, 1]")
def test_hi_bounded(t):
    engine = StrangeLoopEngine()
    metrics = engine.get_consciousness_metrics()
    t.assert_true(metrics["hofstadter_index"] >= 0.0, "HI >= 0")
    t.assert_true(metrics["hofstadter_index"] <= 1.0, "HI <= 1")
    # After many self-referential cycles
    for _ in range(50):
        engine.step({"about_self": True, "salience": 1.0})
    metrics = engine.get_consciousness_metrics()
    t.assert_true(metrics["hofstadter_index"] >= 0.0, "HI >= 0 after cycles")
    t.assert_true(metrics["hofstadter_index"] <= 1.0, "HI <= 1 after cycles")


@suite.test("Self-referential activity increases strange loop count")
def test_self_ref_increases_loops(t):
    engine_flat = StrangeLoopEngine()
    engine_loop = StrangeLoopEngine()
    for _ in range(10):
        engine_flat.step({"about_self": False, "complexity": 0.3, "salience": 0.5})
        engine_loop.step({"about_self": True, "complexity": 0.9, "salience": 0.9})
    m_flat = engine_flat.get_consciousness_metrics()
    m_loop = engine_loop.get_consciousness_metrics()
    # Self-referential engine triggers meta-cognitive more often (System 2/Strange Loop
    # modes trigger meta-eval, whereas System 1 only triggers every 3rd cycle)
    t.assert_true(
        m_loop["meta_cognitive_cycles"] >= m_flat["meta_cognitive_cycles"],
        "Self-referential engine has >= meta-cognitive cycles"
    )
    t.assert_true(
        m_loop["self_referential_broadcast_ratio"] >=
        m_flat["self_referential_broadcast_ratio"],
        "Self-referential engine has higher self-ref broadcast ratio"
    )


@suite.test("Mode distribution sums to 1.0")
def test_mode_distribution(t):
    engine = StrangeLoopEngine()
    for i in range(20):
        complexity = 0.3 if i % 3 == 0 else (0.8 if i % 3 == 1 else 0.5)
        about_self = (i % 3 == 2)
        engine.step({"complexity": complexity, "about_self": about_self, "salience": 0.5})
    metrics = engine.get_consciousness_metrics()
    dist = metrics["kahneman_mode_distribution"]
    t.assert_in("fast", dist, "Has fast mode")
    t.assert_in("slow", dist, "Has slow mode")
    t.assert_in("loop", dist, "Has loop mode")
    total = sum(dist.values())
    t.assert_true(abs(total - 1.0) < 0.01, f"Distribution sums to 1.0 (got {total})")


@suite.test("Full state serialization contains all sections")
def test_state_serialization(t):
    engine = StrangeLoopEngine()
    engine.add_knowledge("test", "concept", {})
    engine.add_belief("test belief", 0.8)
    engine.set_goal("test goal", "high")
    engine.step({"salience": 0.7})
    state = engine.get_full_state()
    for key in ["engine", "world_model", "self_model", "meta_cognitive", "workspace"]:
        t.assert_in(key, state, f"State contains {key}")


@suite.test("Consciousness metrics contain all expected fields")
def test_metrics_fields(t):
    engine = StrangeLoopEngine()
    engine.step({"about_self": True, "salience": 0.9})
    metrics = engine.get_consciousness_metrics()
    expected_fields = [
        "strange_loop_count", "strangeness_ratio",
        "self_referential_broadcast_ratio", "meta_cognitive_cycles",
        "blind_spots_encountered", "fundamental_limits_hit",
        "self_modifications", "hofstadter_index",
        "kahneman_mode_distribution"
    ]
    for field in expected_fields:
        t.assert_in(field, metrics, f"Metrics contains {field}")


# ============================================================================
# STRUCTURE TESTS
# ============================================================================

@suite.test("LevelCrossing.is_strange detects downward causation")
def test_level_crossing_strangeness(t):
    downward = LevelCrossing(from_level=2, to_level=1, direction="downward")
    t.assert_true(downward.is_strange, "Downward 2->1 is strange")

    upward = LevelCrossing(from_level=0, to_level=1, direction="upward")
    t.assert_false(upward.is_strange, "Upward 0->1 is not strange")


@suite.test("CognitiveEvent.is_self_referential classification")
def test_event_self_referential(t):
    perception = CognitiveEvent(event_type=CognitiveEventType.PERCEPTION)
    t.assert_false(perception.is_self_referential, "Perception is not self-ref")

    reflection = CognitiveEvent(event_type=CognitiveEventType.SELF_REFLECTION)
    t.assert_true(reflection.is_self_referential, "Self-reflection is self-ref")

    meta = CognitiveEvent(event_type=CognitiveEventType.META_COGNITION)
    t.assert_true(meta.is_self_referential, "Meta-cognition is self-ref")

    blind = CognitiveEvent(event_type=CognitiveEventType.BLIND_SPOT)
    t.assert_true(blind.is_self_referential, "Blind spot is self-ref")


@suite.test("Entity confidence decay over time")
def test_entity_decay(t):
    import time
    e = Entity(name="test", confidence=1.0)
    e.last_updated = time.time() - 100  # 100 seconds ago
    e.decay(rate=0.01)
    t.assert_true(e.confidence < 1.0, "Confidence decayed")
    t.assert_true(e.confidence >= 0.0, "Confidence bounded at 0")


def main():
    success = suite.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
