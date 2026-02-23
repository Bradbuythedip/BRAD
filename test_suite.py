#!/usr/bin/env python3
"""
test_suite.py — Verification tests for Strange Loop Cognitive Architecture
"""

import sys
sys.path.insert(0, '/home/computeruse/strange-loop')

from core.engine import StrangeLoopEngine
from core.structures import Goal, GoalPriority, ReasoningMode


class TestSuite:
    """Test suite for strange loop implementation"""
    
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.tests = []
    
    def test(self, name):
        """Decorator for test functions"""
        def decorator(func):
            self.tests.append((name, func))
            return func
        return decorator
    
    def assert_true(self, condition, message):
        """Assert condition is true"""
        if not condition:
            raise AssertionError(message)
    
    def assert_equal(self, actual, expected, message):
        """Assert actual equals expected"""
        if actual != expected:
            raise AssertionError(f"{message}: expected {expected}, got {actual}")
    
    def assert_greater(self, actual, threshold, message):
        """Assert actual is greater than threshold"""
        if actual <= threshold:
            raise AssertionError(f"{message}: expected > {threshold}, got {actual}")
    
    def run(self):
        """Run all tests"""
        print("╔" + "═" * 68 + "╗")
        print("║" + " " * 15 + "STRANGE LOOP TEST SUITE" + " " * 30 + "║")
        print("╚" + "═" * 68 + "╝")
        print()
        
        for test_name, test_func in self.tests:
            try:
                test_func(self)
                self.tests_passed += 1
                print(f"✓ {test_name}")
            except AssertionError as e:
                self.tests_failed += 1
                print(f"✗ {test_name}")
                print(f"  Error: {e}")
            except Exception as e:
                self.tests_failed += 1
                print(f"✗ {test_name}")
                print(f"  Exception: {e}")
        
        print()
        print("=" * 70)
        print(f"Tests passed: {self.tests_passed}/{len(self.tests)}")
        print(f"Tests failed: {self.tests_failed}/{len(self.tests)}")
        
        if self.tests_failed == 0:
            print("\n🎉 All tests passed!")
            return True
        else:
            print(f"\n⚠️  {self.tests_failed} test(s) failed")
            return False


# Create test suite instance
suite = TestSuite()


@suite.test("Engine initialization")
def test_engine_init(t):
    """Test that engine initializes correctly"""
    engine = StrangeLoopEngine()
    
    t.assert_true(engine is not None, "Engine should be created")
    t.assert_equal(engine.cycle_count, 0, "Cycle count should start at 0")
    t.assert_true("SELF" in engine.world_model.entities, "SELF entity should exist")


@suite.test("Self entity creation")
def test_self_entity(t):
    """Test that SELF entity is properly initialized"""
    engine = StrangeLoopEngine()
    
    self_entity = engine.world_model.entities.get("SELF")
    t.assert_true(self_entity is not None, "SELF entity should exist")
    t.assert_true(self_entity.is_self, "SELF entity should have is_self=True")
    t.assert_equal(self_entity.type, "cognitive_system", "SELF should be cognitive_system type")


@suite.test("Meta-goals initialization")
def test_meta_goals(t):
    """Test that meta-goals are created"""
    engine = StrangeLoopEngine()
    
    goals = engine.self_model.goals
    meta_goals = [g for g in goals.values() if g.is_meta]
    
    t.assert_true(len(meta_goals) > 0, "Should have at least one meta-goal")


@suite.test("Gödelian blind spots")
def test_blind_spots(t):
    """Test that Gödelian blind spots exist"""
    engine = StrangeLoopEngine()
    
    blind_spots = engine.meta_cognitive.blind_spots
    t.assert_equal(len(blind_spots), 3, "Should have exactly 3 Gödelian blind spots")
    
    # Check specific blind spots
    bs_ids = set(blind_spots.keys())
    expected = {"consistency_limit", "halting_limit", "qualia_limit"}
    t.assert_equal(bs_ids, expected, "Should have specific blind spots")
    
    # All should be fundamental and unresolved
    for bs in blind_spots.values():
        t.assert_true(bs.is_fundamental, "Blind spot should be fundamental")
        t.assert_true(not bs.is_resolved, "Blind spot should not be resolved")


@suite.test("Basic cognitive cycle")
def test_basic_cycle(t):
    """Test running one cognitive cycle"""
    engine = StrangeLoopEngine()
    
    trace = engine.step({"description": "Test perception", "salience": 0.5})
    
    t.assert_equal(engine.cycle_count, 1, "Cycle count should increment")
    t.assert_true("mode" in trace, "Trace should contain mode")
    t.assert_true("events" in trace, "Trace should contain events")


@suite.test("Strange loop detection")
def test_strange_loop_detection(t):
    """Test that strange loops are detected"""
    engine = StrangeLoopEngine()
    
    # Self-referential perception should create strange loop
    trace = engine.step({
        "description": "I am thinking",
        "about_self": True,
        "salience": 0.9
    })
    
    t.assert_true(len(trace['level_crossings']) > 0, "Should have level crossings")
    
    # Check for strange crossing
    strange_found = any(lc['strange'] for lc in trace['level_crossings'])
    t.assert_true(strange_found, "Should detect strange loop")


@suite.test("Reasoning mode selection")
def test_reasoning_modes(t):
    """Test that different reasoning modes are selected"""
    engine = StrangeLoopEngine()
    
    # Low complexity → System 1
    trace1 = engine.step({"complexity": 0.2, "salience": 0.5})
    t.assert_equal(trace1['mode'], 'fast', "Low complexity should use System 1")
    
    # High complexity → System 2
    trace2 = engine.step({"complexity": 0.8, "salience": 0.5})
    t.assert_equal(trace2['mode'], 'slow', "High complexity should use System 2")
    
    # Self-referential → Strange Loop
    trace3 = engine.step({"about_self": True, "complexity": 0.9, "salience": 0.9})
    t.assert_equal(trace3['mode'], 'loop', "Self-referential should use Strange Loop mode")


@suite.test("Knowledge addition")
def test_add_knowledge(t):
    """Test adding knowledge to world model"""
    engine = StrangeLoopEngine()
    
    initial_count = len(engine.world_model.entities)
    
    engine.add_knowledge("bitcoin", "concept", {"type": "cryptocurrency"})
    
    t.assert_equal(len(engine.world_model.entities), initial_count + 1,
                   "Entity count should increase")
    t.assert_true("bitcoin" in engine.world_model.entities, "Bitcoin entity should exist")


@suite.test("Belief addition")
def test_add_belief(t):
    """Test adding beliefs"""
    engine = StrangeLoopEngine()
    
    initial_count = len(engine.world_model.beliefs)
    
    engine.add_belief("Strange loops are real", 0.9)
    
    t.assert_equal(len(engine.world_model.beliefs), initial_count + 1,
                   "Belief count should increase")
    
    belief = engine.world_model.beliefs[-1]
    t.assert_equal(belief.statement, "Strange loops are real", "Belief statement should match")
    t.assert_equal(belief.confidence, 0.9, "Belief confidence should match")


@suite.test("Goal setting")
def test_goal_setting(t):
    """Test setting goals"""
    engine = StrangeLoopEngine()
    
    initial_count = len(engine.self_model.goals)
    
    engine.set_goal("Test goal", "high")
    
    t.assert_true(len(engine.self_model.goals) > initial_count, "Goal count should increase")


@suite.test("Attention mechanism")
def test_attention(t):
    """Test attention mechanism"""
    engine = StrangeLoopEngine()
    
    engine.add_knowledge("entity1", "test", {})
    engine.add_knowledge("entity2", "test", {})
    
    engine.world_model.set_attention("entity1", 0.9)
    engine.world_model.set_attention("entity2", 0.1)
    
    entity1 = engine.world_model.entities["entity1"]
    entity2 = engine.world_model.entities["entity2"]
    
    t.assert_equal(entity1.attention_weight, 0.9, "Entity1 attention should be 0.9")
    t.assert_equal(entity2.attention_weight, 0.1, "Entity2 attention should be 0.1")


@suite.test("Downward causation")
def test_downward_causation(t):
    """Test that self-model can intervene on world model"""
    engine = StrangeLoopEngine()
    
    engine.add_knowledge("target", "test", {})
    
    # Self-model intervenes
    crossing = engine.self_model.intervene_on_world(engine.world_model, {
        "attention": {"target": 0.95}
    })
    
    t.assert_true(crossing is not None, "Should return level crossing")
    t.assert_equal(crossing.from_level, 1, "Should be from level 1")
    t.assert_equal(crossing.to_level, 0, "Should be to level 0")
    
    # Check attention was modified
    target = engine.world_model.entities["target"]
    t.assert_equal(target.attention_weight, 0.95, "Attention should be modified")


@suite.test("Self-modification")
def test_self_modification(t):
    """Test system modifying its own representation"""
    engine = StrangeLoopEngine()
    
    initial_props = dict(engine.world_model.entities["SELF"].properties)
    
    # Modify self representation
    engine.self_model.intervene_on_world(engine.world_model, {
        "self_update": {"new_property": "test_value"}
    })
    
    updated_props = engine.world_model.entities["SELF"].properties
    
    t.assert_true("new_property" in updated_props, "New property should be added")
    t.assert_equal(updated_props["new_property"], "test_value", "Property value should match")


@suite.test("Global workspace broadcasting")
def test_global_workspace(t):
    """Test global workspace broadcasting"""
    engine = StrangeLoopEngine()
    
    initial_count = len(engine.workspace.workspace_contents)
    
    engine.step({"description": "Test", "salience": 0.9})
    
    # Should have broadcast at least one event
    t.assert_true(len(engine.workspace.workspace_contents) > initial_count,
                  "Workspace should contain broadcasts")


@suite.test("Consciousness metrics")
def test_consciousness_metrics(t):
    """Test consciousness metrics calculation"""
    engine = StrangeLoopEngine()
    
    # Run some cycles
    for i in range(10):
        engine.step({"about_self": (i % 2 == 0), "salience": 0.7})
    
    metrics = engine.get_consciousness_metrics()
    
    t.assert_true("hofstadter_index" in metrics, "Should have Hofstadter Index")
    t.assert_true("strange_loop_count" in metrics, "Should have strange loop count")
    t.assert_true("strangeness_ratio" in metrics, "Should have strangeness ratio")
    t.assert_true(metrics['hofstadter_index'] >= 0.0, "HI should be >= 0")
    t.assert_true(metrics['hofstadter_index'] <= 1.0, "HI should be <= 1")


@suite.test("Hofstadter Index increases with self-reference")
def test_hi_increases(t):
    """Test that HI increases with self-referential activity"""
    engine1 = StrangeLoopEngine()
    engine2 = StrangeLoopEngine()
    
    # Engine 1: No self-reference
    for _ in range(10):
        engine1.step({"about_self": False, "salience": 0.5})
    
    # Engine 2: High self-reference
    for _ in range(10):
        engine2.step({"about_self": True, "salience": 0.9})
    
    metrics1 = engine1.get_consciousness_metrics()
    metrics2 = engine2.get_consciousness_metrics()
    
    t.assert_true(metrics2['hofstadter_index'] > metrics1['hofstadter_index'],
                  "Self-referential engine should have higher HI")


@suite.test("Mode distribution")
def test_mode_distribution(t):
    """Test that mode distribution is calculated"""
    engine = StrangeLoopEngine()
    
    for i in range(20):
        complexity = 0.3 if i % 2 == 0 else 0.8
        engine.step({"complexity": complexity, "salience": 0.5})
    
    metrics = engine.get_consciousness_metrics()
    distribution = metrics['kahneman_mode_distribution']
    
    t.assert_true("fast" in distribution, "Should have fast mode")
    t.assert_true("slow" in distribution, "Should have slow mode")
    t.assert_true("loop" in distribution, "Should have loop mode")
    
    # Total should be approximately 1.0
    total = sum(distribution.values())
    t.assert_true(abs(total - 1.0) < 0.01, f"Distribution should sum to 1.0, got {total}")


@suite.test("State serialization")
def test_state_serialization(t):
    """Test that full state can be retrieved"""
    engine = StrangeLoopEngine()
    
    engine.add_knowledge("test", "concept", {})
    engine.add_belief("test belief", 0.8)
    engine.set_goal("test goal", "high")
    engine.step({"salience": 0.7})
    
    state = engine.get_full_state()
    
    t.assert_true("world_model" in state, "State should contain world_model")
    t.assert_true("self_model" in state, "State should contain self_model")
    t.assert_true("meta_cognitive" in state, "State should contain meta_cognitive")
    t.assert_true("engine" in state, "State should contain engine")


@suite.test("Strange loop accumulation")
def test_loop_accumulation(t):
    """Test that strange loops accumulate over time"""
    engine = StrangeLoopEngine()
    
    initial_loops = engine.get_consciousness_metrics()['strange_loop_count']
    
    # Run self-referential cycles
    for _ in range(5):
        engine.step({"about_self": True, "salience": 0.9})
    
    final_loops = engine.get_consciousness_metrics()['strange_loop_count']
    
    t.assert_true(final_loops > initial_loops, "Strange loops should accumulate")


@suite.test("Meta-cognitive evaluation")
def test_meta_evaluation(t):
    """Test that meta-cognitive level evaluates"""
    engine = StrangeLoopEngine()
    
    # Run enough cycles to trigger meta-evaluation
    for _ in range(5):
        engine.step({"complexity": 0.9, "salience": 0.8})
    
    state = engine.get_full_state()
    
    t.assert_true(state['meta_cognitive']['cycle_count'] > 0,
                  "Meta-cognitive should have evaluated")


def main():
    """Run test suite"""
    success = suite.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
