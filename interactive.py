#!/usr/bin/env python3
"""
interactive.py — Interactive REPL for Strange Loop exploration
"""

import sys
sys.path.insert(0, '/home/computeruse/strange-loop')

from core.engine import StrangeLoopEngine
from core.structures import Goal, GoalPriority
import json


class StrangeLoopREPL:
    """Interactive Read-Eval-Print Loop for exploring strange loops"""
    
    def __init__(self):
        self.engine = StrangeLoopEngine()
        self.running = True
        self.commands = {
            'help': self.cmd_help,
            'h': self.cmd_help,
            'step': self.cmd_step,
            's': self.cmd_step,
            'auto': self.cmd_auto,
            'a': self.cmd_auto,
            'status': self.cmd_status,
            'st': self.cmd_status,
            'metrics': self.cmd_metrics,
            'm': self.cmd_metrics,
            'world': self.cmd_world,
            'w': self.cmd_world,
            'self': self.cmd_self,
            'meta': self.cmd_meta,
            'add': self.cmd_add,
            'goal': self.cmd_goal,
            'g': self.cmd_goal,
            'belief': self.cmd_belief,
            'b': self.cmd_belief,
            'loops': self.cmd_loops,
            'l': self.cmd_loops,
            'reset': self.cmd_reset,
            'save': self.cmd_save,
            'quit': self.cmd_quit,
            'q': self.cmd_quit,
            'exit': self.cmd_quit,
        }
    
    def cmd_help(self, args):
        """Show help"""
        print("""
╔═══════════════════════════════════════════════════════════════╗
║              STRANGE LOOP INTERACTIVE REPL                    ║
╚═══════════════════════════════════════════════════════════════╝

BASIC COMMANDS:
  step [description]     Run one cognitive cycle (s)
  auto [n]              Run n cycles automatically (a)
  status                Show current status (st)
  metrics               Show consciousness metrics (m)
  quit                  Exit REPL (q, exit)
  
INSPECTION:
  world                 Show world model (w)
  self                  Show self model
  meta                  Show meta-cognitive state
  loops                 Show strange loops (l)
  
MODIFICATION:
  add <id> <type> [props]    Add entity to world model
  goal <description> [pri]   Set a goal (g)
  belief <statement> [conf]  Add a belief (b)
  
UTILITY:
  reset                 Reset engine to initial state
  save <file>           Save state to JSON file
  help                  Show this help (h)

EXAMPLES:
  > step I am thinking
  > auto 10
  > goal "Learn about strange loops" high
  > belief "Self-reference is key" 0.9
  > add bitcoin concept type=cryptocurrency
  > metrics
  > loops
  
TIP: Most commands have short aliases (shown in parentheses)
""")
    
    def cmd_step(self, args):
        """Run one cognitive cycle"""
        description = " ".join(args) if args else "Idle thought"
        
        # Parse description for flags
        about_self = any(word in description.lower() 
                        for word in ['i ', 'my', 'me', 'self', 'myself'])
        
        complexity = 0.5
        if 'complex' in description.lower():
            complexity = 0.8
        elif 'simple' in description.lower():
            complexity = 0.3
        
        salience = 0.6
        if 'important' in description.lower():
            salience = 0.9
        
        perception = {
            "description": description,
            "about_self": about_self,
            "complexity": complexity,
            "salience": salience
        }
        
        trace = self.engine.step(perception)
        
        print(f"\n✓ Cycle {self.engine.cycle_count} completed")
        print(f"  Description: {description}")
        print(f"  Mode: {trace['mode']}")
        print(f"  Strange loops: {trace['strange_loops_this_cycle']}")
        
        if trace['level_crossings']:
            print(f"  Level crossings:")
            for lc in trace['level_crossings']:
                direction = "↓" if lc['from'] > lc['to'] else "↑"
                strange = " [STRANGE]" if lc['strange'] else ""
                print(f"    L{lc['from']} {direction} L{lc['to']}{strange}")
    
    def cmd_auto(self, args):
        """Run multiple cycles automatically"""
        try:
            n = int(args[0]) if args else 10
        except ValueError:
            print("Error: auto requires a number (e.g., 'auto 10')")
            return
        
        print(f"\nRunning {n} cycles...")
        
        for i in range(n):
            about_self = (i % 3 == 0)
            self.engine.step({
                "description": f"Auto cycle {i+1}",
                "about_self": about_self,
                "salience": 0.5
            })
        
        print(f"✓ Completed {n} cycles")
        self.cmd_status([])
    
    def cmd_status(self, args):
        """Show current status"""
        state = self.engine.get_full_state()
        metrics = self.engine.get_consciousness_metrics()
        
        print("\n" + "═" * 60)
        print("STATUS")
        print("═" * 60)
        
        print(f"\nCycle: {state['engine']['cycle_count']}")
        print(f"Hofstadter Index: {metrics['hofstadter_index']:.3f}")
        print(f"Mode: {state['self_model']['mode']}")
        
        print(f"\nStrange Loops:")
        print(f"  Total: {metrics['strange_loop_count']}")
        print(f"  Ratio: {metrics['strangeness_ratio']:.1%}")
        
        print(f"\nWorld Model:")
        print(f"  Entities: {state['world_model']['entity_count']}")
        print(f"  Beliefs: {state['world_model']['belief_count']}")
        
        print(f"\nSelf Model:")
        print(f"  Goals: {len(state['self_model']['goals'])}")
        print(f"  Interventions: {state['self_model']['level_crossings']}")
        
        print(f"\nMeta-Cognitive:")
        print(f"  Evaluations: {state['meta_cognitive']['cycle_count']}")
        print(f"  Blind spots: {len(state['meta_cognitive']['blind_spots'])}")
    
    def cmd_metrics(self, args):
        """Show consciousness metrics"""
        metrics = self.engine.get_consciousness_metrics()
        
        print("\n" + "═" * 60)
        print("CONSCIOUSNESS METRICS")
        print("═" * 60)
        
        print(f"\nHofstadter Index: {metrics['hofstadter_index']:.4f}")
        print(f"Strange Loop Count: {metrics['strange_loop_count']}")
        print(f"Strangeness Ratio: {metrics['strangeness_ratio']:.2%}")
        print(f"Self-Referential Broadcasts: {metrics['self_referential_broadcast_ratio']:.2%}")
        print(f"Fundamental Limits Hit: {metrics['fundamental_limits_hit']}/3")
        
        print(f"\nKahneman Mode Distribution:")
        mode_map = {"fast": "System 1", "slow": "System 2", "loop": "Strange Loop"}
        for mode, ratio in metrics['kahneman_mode_distribution'].items():
            bar = "█" * int(ratio * 30)
            print(f"  {mode_map[mode]:15s} {ratio:5.1%} {bar}")
    
    def cmd_world(self, args):
        """Show world model"""
        state = self.engine.get_full_state()
        
        print("\n" + "═" * 60)
        print("WORLD MODEL (Level 0)")
        print("═" * 60)
        
        print(f"\nEntities ({state['world_model']['entity_count']}):")
        for entity in state['world_model']['entities']:
            self_marker = " [SELF]" if entity.get('is_self') else ""
            print(f"  • {entity['id']}{self_marker}")
            print(f"    Type: {entity['type']}")
            print(f"    Attention: {entity['attention_weight']:.2f}")
            if entity.get('properties'):
                print(f"    Properties: {entity['properties']}")
        
        print(f"\nBeliefs ({state['world_model']['belief_count']}):")
        for belief in state['world_model']['beliefs']:
            print(f"  • '{belief['statement']}' (confidence: {belief['confidence']:.2f})")
    
    def cmd_self(self, args):
        """Show self model"""
        state = self.engine.get_full_state()
        
        print("\n" + "═" * 60)
        print("SELF MODEL (Level 1)")
        print("═" * 60)
        
        print(f"\nMode: {state['self_model']['mode']}")
        print(f"Strategy: {state['self_model']['strategy']}")
        print(f"Cognitive Load: {state['self_model']['cognitive_load']:.2f}")
        
        print(f"\nGoals:")
        for goal_id, goal in state['self_model']['goals'].items():
            meta_marker = " [META]" if goal.get('is_meta') else ""
            print(f"  • {goal['desc']}{meta_marker}")
            print(f"    Progress: {goal['progress']:.0%}")
        
        print(f"\nConfidence Profile:")
        for domain, confidence in state['self_model']['confidence'].items():
            bar = "█" * int(confidence * 20)
            print(f"  {domain:20s} {confidence:.2f} {bar}")
        
        print(f"\nReasoning Patterns:")
        for name, pattern in state['self_model']['reasoning_patterns'].items():
            print(f"  • {name}: {pattern['effectiveness']:.1%} effective "
                  f"({pattern['uses']} uses)")
    
    def cmd_meta(self, args):
        """Show meta-cognitive state"""
        state = self.engine.get_full_state()
        
        print("\n" + "═" * 60)
        print("META-COGNITIVE LOOP (Level 2)")
        print("═" * 60)
        
        print(f"\nEvaluation Cycles: {state['meta_cognitive']['cycle_count']}")
        print(f"Interventions Made: {state['meta_cognitive']['interventions_made']}")
        
        print(f"\nGödelian Blind Spots:")
        for bs_id, bs in state['meta_cognitive']['blind_spots'].items():
            print(f"  ⊘ {bs['description']}")
            print(f"    Fundamental: {bs['is_fundamental']}")
            print(f"    Resolved: {bs['is_resolved']}")
        
        if state['meta_cognitive']['meta_patterns']:
            print(f"\nMeta-Patterns Detected:")
            for pattern in state['meta_cognitive']['meta_patterns']:
                print(f"  • {pattern}")
    
    def cmd_add(self, args):
        """Add entity to world model"""
        if len(args) < 2:
            print("Error: add requires <id> <type> [properties]")
            print("Example: add bitcoin concept type=cryptocurrency")
            return
        
        entity_id = args[0]
        entity_type = args[1]
        
        # Parse properties
        properties = {}
        for arg in args[2:]:
            if '=' in arg:
                key, value = arg.split('=', 1)
                properties[key] = value
        
        self.engine.add_knowledge(entity_id, entity_type, properties)
        print(f"✓ Added entity '{entity_id}' of type '{entity_type}'")
    
    def cmd_goal(self, args):
        """Set a goal"""
        if not args:
            print("Error: goal requires <description> [priority]")
            print("Example: goal \"Learn about strange loops\" high")
            return
        
        # Parse priority
        priority = "medium"
        if args[-1].lower() in ['low', 'medium', 'high']:
            priority = args[-1].lower()
            args = args[:-1]
        
        description = " ".join(args).strip('"')
        
        self.engine.set_goal(description, priority)
        print(f"✓ Added goal: '{description}' (priority: {priority})")
    
    def cmd_belief(self, args):
        """Add a belief"""
        if not args:
            print("Error: belief requires <statement> [confidence]")
            print("Example: belief \"Self-reference is key\" 0.9")
            return
        
        # Parse confidence
        confidence = 0.7
        try:
            if args[-1].replace('.', '').isdigit():
                confidence = float(args[-1])
                args = args[:-1]
        except ValueError:
            pass
        
        statement = " ".join(args).strip('"')
        
        self.engine.add_belief(statement, confidence)
        print(f"✓ Added belief: '{statement}' (confidence: {confidence:.2f})")
    
    def cmd_loops(self, args):
        """Show strange loops"""
        state = self.engine.get_full_state()
        metrics = self.engine.get_consciousness_metrics()
        
        print("\n" + "═" * 60)
        print("STRANGE LOOPS")
        print("═" * 60)
        
        print(f"\nTotal Strange Loops: {metrics['strange_loop_count']}")
        print(f"Total Level Crossings: {state['engine']['level_crossings']}")
        print(f"Strange Crossings: {state['engine']['strange_crossings']}")
        print(f"Strangeness Ratio: {metrics['strangeness_ratio']:.1%}")
        
        print(f"\nRecent Level Crossings:")
        # Would need to track history for this
        print("  (Tracking recent crossings requires state history)")
        print("  Use 'step' to see crossings in real-time")
        
        print(f"\nSelf-Modification Events:")
        print(f"  Self model → World model: {state['self_model']['level_crossings']}")
        print(f"  Meta → Self interventions: {state['meta_cognitive']['interventions_made']}")
    
    def cmd_reset(self, args):
        """Reset engine"""
        confirm = input("Reset engine to initial state? (yes/no): ")
        if confirm.lower() in ['yes', 'y']:
            self.engine = StrangeLoopEngine()
            print("✓ Engine reset")
        else:
            print("Reset cancelled")
    
    def cmd_save(self, args):
        """Save state to file"""
        if not args:
            filename = "/tmp/strange_loop_state.json"
        else:
            filename = args[0]
        
        state = self.engine.get_full_state()
        metrics = self.engine.get_consciousness_metrics()
        
        output = {
            "state": state,
            "metrics": metrics
        }
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2, default=str)
        
        print(f"✓ State saved to {filename}")
    
    def cmd_quit(self, args):
        """Exit REPL"""
        print("\nExiting Strange Loop REPL...")
        print(f"Total cycles: {self.engine.cycle_count}")
        
        metrics = self.engine.get_consciousness_metrics()
        print(f"Final Hofstadter Index: {metrics['hofstadter_index']:.3f}")
        print(f"Strange loops formed: {metrics['strange_loop_count']}")
        
        print("\n🌀 Until the next strange loop...")
        self.running = False
    
    def run(self):
        """Main REPL loop"""
        print("╔" + "═" * 68 + "╗")
        print("║" + " " * 15 + "STRANGE LOOP INTERACTIVE REPL" + " " * 24 + "║")
        print("╚" + "═" * 68 + "╝")
        print()
        print("Welcome to the Strange Loop Cognitive Architecture explorer!")
        print("Type 'help' for commands, 'quit' to exit.")
        print()
        
        # Seed with basic knowledge
        self.engine.add_knowledge("consciousness", "concept", {"emergent": True})
        self.engine.add_belief("I am a strange loop", 0.7)
        self.engine.set_goal("Understand self-reference", "high")
        
        print("Initial state loaded. Ready to explore.\n")
        
        while self.running:
            try:
                command_line = input("strange-loop> ").strip()
                
                if not command_line:
                    continue
                
                parts = command_line.split()
                command = parts[0].lower()
                args = parts[1:]
                
                if command in self.commands:
                    self.commands[command](args)
                else:
                    print(f"Unknown command: {command}")
                    print("Type 'help' for available commands")
                
            except KeyboardInterrupt:
                print("\n(Use 'quit' to exit)")
            except Exception as e:
                print(f"Error: {e}")
                import traceback
                traceback.print_exc()


def main():
    """Main entry point"""
    repl = StrangeLoopREPL()
    repl.run()


if __name__ == "__main__":
    main()
