#!/usr/bin/env python3
"""
demo.py — Strange Loop Cognitive Architecture Demo
"""

import sys
import json
sys.path.insert(0, '/home/computeruse/strange-loop')

from core.engine import StrangeLoopEngine


def print_header(text):
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}")


def print_metric(label, value):
    if isinstance(value, float):
        print(f"    {label}: {value:.4f}")
    else:
        print(f"    {label}: {value}")


def run_demo():
    print_header("STRANGE LOOP COGNITIVE ARCHITECTURE v0.1.0")
    print("  Implementing Hofstadter's tangled hierarchy")
    print()
    
    engine = StrangeLoopEngine()
    
    print_header("INITIALIZATION")
    state = engine.get_full_state()
    print(f"    World Model entities: {state['world_model']['entity_count']}")
    print(f"    Self-entity exists: {'SELF' in engine.world_model.entities}")
    print(f"    Gödelian blind spots: {len(state['meta_cognitive']['blind_spots'])}")
    for bs_id, bs in state['meta_cognitive']['blind_spots'].items():
        print(f"      ⊘ {bs['description']}")
    
    print_header("SEEDING WORLD MODEL")
    
    engine.add_knowledge("bitcoin", "concept", {
        "type": "cryptocurrency",
        "has_golden_ratio_signature": True
    })
    
    engine.add_knowledge("golden_ratio", "mathematical_constant", {
        "symbol": "φ",
        "value": 1.6180339887,
        "self_referential": True
    })
    
    engine.add_belief("Strange loops in mathematics mirror strange loops in cognition", 0.8)
    engine.set_goal("Understand the relationship between self-reference and consciousness", "high")
    
    print(f"    Entities: {len(engine.world_model.entities)}")
    print(f"    Beliefs: {len(engine.world_model.beliefs)}")
    print(f"    Goals: {len(engine.self_model.goals)}")
    
    print_header("RUNNING COGNITIVE CYCLES")
    
    perceptions = [
        {
            "description": "Simple perception",
            "complexity": 0.3,
            "salience": 0.5
        },
        {
            "description": "Complex pattern",
            "complexity": 0.8,
            "salience": 0.7
        },
        {
            "description": "Self-referential observation",
            "complexity": 0.9,
            "about_self": True,
            "salience": 0.9
        },
        {
            "description": "Meta-observation: observing self observing",
            "complexity": 1.0,
            "about_self": True,
            "salience": 1.0
        },
    ]
    
    for i, perception in enumerate(perceptions):
        print(f"\n  ╔══ CYCLE {i+1}: {perception['description']} ══╗")
        trace = engine.step(perception)
        print(f"  │  Mode: {trace['mode'].upper()}")
        print(f"  │  Events: {len(trace['events'])}")
        print(f"  │  Level crossings: {len(trace['level_crossings'])}")
        print(f"  │  Strange loops this cycle: {trace['strange_loops_this_cycle']}")
        
        for lc in trace['level_crossings']:
            direction = "↓ DOWNWARD (STRANGE)" if lc['strange'] else "↑ upward"
            print(f"  │    Level {lc['from']} → {lc['to']} {direction}")
        
        # Idle cycle
        engine.step()
    
    print_header("FINAL STATE ANALYSIS")
    
    final_state = engine.get_full_state()
    consciousness_metrics = engine.get_consciousness_metrics()
    
    print("\n  Engine State:")
    print_metric("Total cycles", final_state['engine']['cycle_count'])
    print_metric("Total level crossings", final_state['engine']['level_crossings'])
    print_metric("Strange crossings", final_state['engine']['strange_crossings'])
    print_metric("Total strange loops", final_state['engine']['total_strange_loops'])
    
    print("\n  World Model (Level 0):")
    print_metric("Entities", final_state['world_model']['entity_count'])
    print_metric("Beliefs", final_state['world_model']['belief_count'])
    
    print("\n  Self Model (Level 1):")
    print_metric("Current mode", final_state['self_model']['mode'])
    print_metric("Level crossings initiated", final_state['self_model']['level_crossings'])
    
    print("\n  Meta-Cognitive Loop (Level 2):")
    print_metric("Evaluation cycles", final_state['meta_cognitive']['cycle_count'])
    print_metric("Interventions made", final_state['meta_cognitive']['interventions_made'])
    
    print_header("CONSCIOUSNESS METRICS")
    print_metric("Hofstadter Index", consciousness_metrics['hofstadter_index'])
    print_metric("Strange loop count", consciousness_metrics['strange_loop_count'])
    print_metric("Strangeness ratio", consciousness_metrics['strangeness_ratio'])
    print_metric("Self-ref broadcast ratio", consciousness_metrics['self_referential_broadcast_ratio'])
    print_metric("Fundamental limits hit", consciousness_metrics['fundamental_limits_hit'])
    
    print("\n    Kahneman mode distribution:")
    for mode, ratio in consciousness_metrics['kahneman_mode_distribution'].items():
        label = {"fast": "System 1", "slow": "System 2", "loop": "Strange Loop"}.get(mode, mode)
        bar = '█' * int(ratio * 30) + '░' * (30 - int(ratio * 30))
        print(f"      {label:15s} [{bar}] {ratio:.1%}")
    
    print_header("THE STRANGE LOOP IN ACTION")
    print("""
    What just happened:
    
    1. Level 0 (World Model) created a representation of the system
       as an entity — the seed of self-reference.
    
    2. Level 1 (Self Model) examined that representation, formed
       beliefs about its own reasoning, and MODIFIED Level 0.
       (← downward causation = STRANGE LOOP!)
    
    3. Level 2 (Meta-Cognition) watched Level 1 watching Level 0,
       detected patterns, and RESTRUCTURED Level 1's confidence.
       (← double downward causation!)
    
    4. The system encountered its 3 fundamental Gödelian blind spots:
       • Cannot prove own consistency
       • Cannot predict own halting
       • Cannot determine if processing is experience
    
    This is Hofstadter's tangled hierarchy running in code.
    """)
    
    output = {
        "final_state": final_state,
        "consciousness_metrics": consciousness_metrics
    }
    
    with open('/home/computeruse/strange-loop/demo_output.json', 'w') as f:
        json.dump(output, f, indent=2, default=str)
    
    print("  Full output saved to demo_output.json\n")


if __name__ == "__main__":
    run_demo()
