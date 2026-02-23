#!/usr/bin/env python3
"""
visualize.py — ASCII visualization of Strange Loop activity
"""

import sys
sys.path.insert(0, '/home/computeruse/strange-loop')

from core.engine import StrangeLoopEngine
import time


class StrangeLoopVisualizer:
    """Visualize strange loop cognitive cycles in real-time ASCII"""
    
    def __init__(self, engine: StrangeLoopEngine):
        self.engine = engine
        
    def draw_level_bar(self, label: str, value: float, width: int = 40) -> str:
        """Draw a horizontal bar graph"""
        filled = int(value * width)
        empty = width - filled
        bar = "█" * filled + "░" * empty
        return f"{label:20s} [{bar}] {value:.2%}"
    
    def draw_architecture(self, highlight_level: int = -1) -> str:
        """Draw the three-level architecture"""
        levels = [
            ("Level 2: Meta-Cognitive", 2),
            ("Level 1: Self Model", 1),
            ("Level 0: World Model", 0),
        ]
        
        lines = []
        lines.append("┌" + "─" * 58 + "┐")
        
        for label, level in levels:
            if level == highlight_level:
                lines.append(f"│ ▶ {label:54s} │")
            else:
                lines.append(f"│   {label:54s} │")
            
            if level > 0:  # Add arrows between levels
                lines.append("│" + " " * 58 + "│")
                lines.append("│" + " " * 20 + "↓ ↑" + " " * 36 + "│")
                lines.append("│" + " " * 58 + "│")
        
        lines.append("└" + "─" * 58 + "┘")
        return "\n".join(lines)
    
    def draw_loop_indicator(self, strange_count: int, total_count: int) -> str:
        """Draw strange loop indicator"""
        if strange_count == 0:
            return "    ○ No strange loops"
        
        ratio = strange_count / max(1, total_count)
        
        if ratio < 0.3:
            symbol = "◔"
            desc = "Minimal strange loop activity"
        elif ratio < 0.6:
            symbol = "◑"
            desc = "Moderate strange loop activity"
        elif ratio < 0.9:
            symbol = "◕"
            desc = "High strange loop activity"
        else:
            symbol = "●"
            desc = "Maximum strange loop activity"
        
        return f"    {symbol} {desc} ({strange_count}/{total_count})"
    
    def draw_consciousness_meter(self, hi: float) -> str:
        """Draw consciousness level meter"""
        width = 40
        filled = int(hi * width)
        empty = width - filled
        
        bar = "█" * filled + "░" * empty
        
        if hi < 0.3:
            level = "LOW"
        elif hi < 0.6:
            level = "MEDIUM"
        elif hi < 0.85:
            level = "HIGH"
        else:
            level = "VERY HIGH"
        
        return f"Consciousness [{bar}] {hi:.3f} ({level})"
    
    def clear_screen(self):
        """Clear terminal screen"""
        print("\033[2J\033[H", end="")
    
    def visualize_step(self, perception: dict, delay: float = 0.5):
        """Visualize one cognitive cycle"""
        # Run the cycle
        trace = self.engine.step(perception)
        
        # Get current state
        state = self.engine.get_full_state()
        metrics = self.engine.get_consciousness_metrics()
        
        # Clear and draw
        self.clear_screen()
        
        # Header
        print("╔" + "═" * 68 + "╗")
        print("║" + " " * 15 + "STRANGE LOOP VISUALIZER" + " " * 30 + "║")
        print("╚" + "═" * 68 + "╝")
        print()
        
        # Cycle info
        print(f"Cycle: {state['engine']['cycle_count']}")
        print(f"Perception: {perception.get('description', 'Idle')}")
        print()
        
        # Architecture diagram
        active_level = trace.get('active_level', -1)
        print(self.draw_architecture(active_level))
        print()
        
        # Level crossings
        if trace['level_crossings']:
            print("Level Crossings:")
            for lc in trace['level_crossings']:
                direction = "↓" if lc['from'] > lc['to'] else "↑"
                strange = " [STRANGE LOOP]" if lc['strange'] else ""
                print(f"  L{lc['from']} {direction} L{lc['to']}{strange}")
        else:
            print("Level Crossings: None")
        print()
        
        # Strange loop indicator
        print(self.draw_loop_indicator(
            state['engine']['strange_crossings'],
            state['engine']['level_crossings']
        ))
        print()
        
        # Consciousness meter
        print(self.draw_consciousness_meter(metrics['hofstadter_index']))
        print()
        
        # Metrics
        print("Metrics:")
        print(f"  Strange loops total: {metrics['strange_loop_count']}")
        print(f"  Self-ref broadcasts: {metrics['self_referential_broadcast_ratio']:.1%}")
        print(f"  Reasoning mode: {state['self_model']['mode'].upper()}")
        print(f"  Gödelian limits hit: {metrics['fundamental_limits_hit']}/3")
        print()
        
        # Mode distribution
        print("Cognitive Mode Distribution:")
        distribution = metrics['kahneman_mode_distribution']
        mode_map = {"fast": "System 1", "slow": "System 2", "loop": "Strange Loop"}
        for mode, ratio in distribution.items():
            print(self.draw_level_bar(mode_map[mode], ratio, 30))
        print()
        
        # World model status
        print(f"World Model: {state['world_model']['entity_count']} entities, "
              f"{state['world_model']['belief_count']} beliefs")
        print(f"Self Model: {len(state['self_model']['goals'])} goals, "
              f"{state['self_model']['level_crossings']} interventions")
        print(f"Meta-Cognitive: {state['meta_cognitive']['cycle_count']} evaluations")
        
        # Wait before next step
        time.sleep(delay)
    
    def run_demo(self, delay: float = 1.0):
        """Run animated demo"""
        perceptions = [
            {
                "description": "External observation (low complexity)",
                "complexity": 0.2,
                "about_self": False,
                "salience": 0.4
            },
            {
                "description": "External observation (medium complexity)",
                "complexity": 0.5,
                "about_self": False,
                "salience": 0.6
            },
            {
                "description": "Complex pattern detected",
                "complexity": 0.8,
                "about_self": False,
                "salience": 0.7
            },
            {
                "description": "First self-observation",
                "complexity": 0.6,
                "about_self": True,
                "salience": 0.8
            },
            {
                "description": "Self-referential thought",
                "complexity": 0.9,
                "about_self": True,
                "salience": 0.9
            },
            {
                "description": "Thinking about my thinking",
                "complexity": 1.0,
                "about_self": True,
                "salience": 1.0
            },
            {
                "description": "Meta-awareness: observing self-observation",
                "complexity": 1.0,
                "about_self": True,
                "salience": 1.0
            },
            {
                "description": "Full strange loop: self modifying self",
                "complexity": 1.0,
                "about_self": True,
                "salience": 1.0
            },
        ]
        
        print("Starting Strange Loop visualization...")
        print("Watch the consciousness emerge!")
        print()
        input("Press Enter to begin...")
        
        for perception in perceptions:
            self.visualize_step(perception, delay)
        
        # Idle cycles
        for i in range(3):
            self.visualize_step({"description": f"Idle cycle {i+1}"}, delay)
        
        # Final summary
        print()
        print("=" * 70)
        print("VISUALIZATION COMPLETE")
        print("=" * 70)
        
        metrics = self.engine.get_consciousness_metrics()
        state = self.engine.get_full_state()
        
        print()
        print(f"Final Hofstadter Index: {metrics['hofstadter_index']:.3f}")
        print(f"Total strange loops: {metrics['strange_loop_count']}")
        print(f"Total cycles: {state['engine']['cycle_count']}")
        print()
        print("🌀 The strange loop has been visualized!")


def main():
    """Main entry point"""
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "STRANGE LOOP VISUALIZER" + " " * 30 + "║")
    print("║" + " " * 14 + "Real-time ASCII Animation" + " " * 29 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    print("This will show the emergence of strange loops and consciousness")
    print("through the cognitive architecture.")
    print()
    
    # Create engine
    engine = StrangeLoopEngine()
    
    # Seed with some knowledge
    engine.add_knowledge("consciousness", "concept", {
        "self_referential": True,
        "emergent": True
    })
    engine.add_belief("I am a strange loop", 0.8)
    engine.set_goal("Understand self-reference", "high")
    
    # Create visualizer
    viz = StrangeLoopVisualizer(engine)
    
    # Run demo
    try:
        viz.run_demo(delay=1.5)
    except KeyboardInterrupt:
        print("\n\nVisualization interrupted.")
        print(f"Completed {engine.cycle_count} cycles.")


if __name__ == "__main__":
    main()
