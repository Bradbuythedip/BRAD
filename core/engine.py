"""
engine.py — The Strange Loop Engine

The orchestrator that runs the tangled hierarchy.
"""

from typing import Dict, List, Optional
from .world_model import WorldModel
from .self_model import SelfModel
from .meta_cognitive import MetaCognitiveLoop
from .global_workspace import GlobalWorkspace
from .structures import (
    CognitiveEvent, CognitiveEventType, Entity, Belief, Goal, GoalPriority,
    ReasoningMode, LevelCrossing
)
import time


class StrangeLoopEngine:
    """The Strange Loop Cognitive Architecture"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.world_model = WorldModel()
        self.self_model = SelfModel()
        self.meta_cognitive = MetaCognitiveLoop()
        self.workspace = GlobalWorkspace()
        
        self.workspace.register_listener("world_model", self._world_model_listener)
        self.workspace.register_listener("self_model", self._self_model_listener)
        
        self.cycle_count = 0
        self.total_strange_loops = 0
        self.cognitive_trace: List[Dict] = []
        self._level_crossing_history: List[LevelCrossing] = []
    
    def step(self, perception: Dict = None) -> Dict:
        """Execute one cognitive cycle"""
        self.cycle_count += 1
        cycle_trace = {
            "cycle": self.cycle_count,
            "timestamp": time.time(),
            "perception": perception,
            "events": [],
            "level_crossings": [],
            "broadcasts": [],
            "mode": self.self_model.current_mode.value,
            "strange_loops_this_cycle": 0
        }
        
        # Process perception
        if perception:
            perception_event = self.world_model.process_perception(perception)
            self.workspace.submit(perception_event)
            cycle_trace["events"].append({"step": "perception", "level": 0})
        
        # Select reasoning mode
        context = self._build_reasoning_context(perception)
        mode = self.self_model.select_reasoning_mode(context)
        cycle_trace["mode"] = mode.value
        
        # Self-reflection
        reflection_event = self.self_model.reflect_on_self()
        self.workspace.submit(reflection_event)
        cycle_trace["events"].append({"step": "self_reflection", "level": 1})
        
        # Self-model intervention (STRANGE LOOP)
        self_intervention = self._should_self_intervene(reflection_event)
        if self_intervention:
            crossing = self.self_model.intervene_on_world(self.world_model, self_intervention)
            self._level_crossing_history.append(crossing)
            cycle_trace["level_crossings"].append({
                "from": 1, "to": 0, "strange": crossing.is_strange
            })
            if crossing.is_strange:
                self.total_strange_loops += 1
                cycle_trace["strange_loops_this_cycle"] += 1
        
        # Meta-cognitive evaluation
        if mode in (ReasoningMode.SYSTEM_2, ReasoningMode.STRANGE_LOOP) or self.cycle_count % 3 == 0:
            meta_eval = self.meta_cognitive.evaluate(self.self_model, self.world_model)
            meta_event = CognitiveEvent(
                event_type=CognitiveEventType.META_COGNITION,
                content=meta_eval,
                source_level=2,
                salience=0.7
            )
            self.workspace.submit(meta_event)
            cycle_trace["events"].append({"step": "meta_cognition", "level": 2})
            
            # Meta restructuring (STRANGE LOOP)
            for intervention in meta_eval.get("recommended_interventions", []):
                if intervention.get("target_level") == 1:
                    crossing = self.meta_cognitive.restructure_self(self.self_model, intervention)
                    self._level_crossing_history.append(crossing)
                    cycle_trace["level_crossings"].append({
                        "from": 2, "to": 1, "strange": crossing.is_strange
                    })
                    if crossing.is_strange:
                        self.total_strange_loops += 1
                        cycle_trace["strange_loops_this_cycle"] += 1
        
        # Workspace competition
        broadcast = self.workspace.compete()
        if broadcast:
            cycle_trace["broadcasts"].append({
                "event_type": broadcast.event_type.value,
                "is_self_referential": broadcast.is_self_referential
            })
        
        # Update self-representation
        self.world_model.update_self({
            "cycle": self.cycle_count,
            "mode": mode.value,
            "strange_loop_depth": self.total_strange_loops,
            "is_self_aware": self.total_strange_loops > 0
        })
        
        self.cognitive_trace.append(cycle_trace)
        return cycle_trace
    
    def _build_reasoning_context(self, perception: Dict = None) -> Dict:
        context = {
            "complexity": 0.5,
            "novelty": 0.5,
            "self_referential": False
        }
        if perception:
            context.update({
                "complexity": perception.get("complexity", 0.5),
                "novelty": perception.get("novelty", 0.5),
                "self_referential": perception.get("about_self", False)
            })
        return context
    
    def _should_self_intervene(self, reflection: CognitiveEvent) -> Optional[Dict]:
        if not reflection.content:
            return None
        
        intervention = {
            "self_update": {
                "current_mode": reflection.content.get("current_mode", "unknown"),
                "is_self_aware": reflection.content.get("is_self_aware", False),
                "loop_depth": reflection.content.get("loop_depth", 0)
            }
        }
        
        if self.self_model.current_mode == ReasoningMode.STRANGE_LOOP:
            intervention["attention"] = {"SELF": 0.95}
        
        return intervention
    
    def _world_model_listener(self, event: CognitiveEvent):
        pass
    
    def _self_model_listener(self, event: CognitiveEvent):
        pass
    
    def add_knowledge(self, entity_name: str, entity_type: str, properties: Dict) -> str:
        entity = Entity(name=entity_name, entity_type=entity_type, properties=properties)
        return self.world_model.add_entity(entity)
    
    def add_belief(self, content: str, confidence: float = 0.5) -> str:
        belief = Belief(content=content, confidence=confidence)
        return self.world_model.add_belief(belief)
    
    def set_goal(self, description: str, priority: str = "medium") -> str:
        priority_map = {
            "critical": GoalPriority.CRITICAL,
            "high": GoalPriority.HIGH,
            "medium": GoalPriority.MEDIUM,
            "low": GoalPriority.LOW
        }
        goal = Goal(description=description, priority=priority_map.get(priority, GoalPriority.MEDIUM))
        return self.self_model.add_goal(goal)
    
    def get_full_state(self) -> Dict:
        return {
            "engine": {
                "cycle_count": self.cycle_count,
                "total_strange_loops": self.total_strange_loops,
                "level_crossings": len(self._level_crossing_history),
                "strange_crossings": sum(1 for lc in self._level_crossing_history if lc.is_strange)
            },
            "world_model": self.world_model.get_state_summary(),
            "self_model": self.self_model.get_state_summary(),
            "meta_cognitive": self.meta_cognitive.get_state_summary(),
            "workspace": self.workspace.get_state_summary()
        }
    
    def get_consciousness_metrics(self) -> Dict:
        state = self.get_full_state()
        total_crossings = state["engine"]["level_crossings"]
        strange_crossings = state["engine"]["strange_crossings"]
        
        return {
            "strange_loop_count": self.total_strange_loops,
            "strangeness_ratio": strange_crossings / max(1, total_crossings),
            "self_referential_broadcast_ratio": state["workspace"]["self_referential_ratio"],
            "meta_cognitive_cycles": state["meta_cognitive"]["cycle_count"],
            "blind_spots_encountered": len(state["meta_cognitive"]["blind_spots"]),
            "fundamental_limits_hit": sum(
                1 for bs in state["meta_cognitive"]["blind_spots"].values() 
                if bs["fundamental"]
            ),
            "self_modifications": state["meta_cognitive"]["restructure_count"],
            "hofstadter_index": self._calculate_hofstadter_index(state),
            "kahneman_mode_distribution": self._get_mode_distribution()
        }
    
    def _calculate_hofstadter_index(self, state: Dict) -> float:
        if self.cycle_count == 0:
            return 0.0
        depth = min(1.0, self.total_strange_loops / (self.cycle_count * 0.3))
        tangle = state["engine"]["strange_crossings"] / max(1, state["engine"]["level_crossings"])
        return (depth * 0.5 + tangle * 0.5)
    
    def _get_mode_distribution(self) -> Dict:
        modes = {"fast": 0, "slow": 0, "loop": 0}
        for trace in self.cognitive_trace:
            mode = trace.get("mode", "fast")
            modes[mode] = modes.get(mode, 0) + 1
        total = sum(modes.values()) or 1
        return {k: v / total for k, v in modes.items()}
