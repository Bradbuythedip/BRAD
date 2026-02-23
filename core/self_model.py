"""
self_model.py — Level 1: The Self
"""

from typing import Dict, List, Optional
from .structures import (
    Goal, GoalPriority, FailureRecord, Belief, ReasoningMode,
    CognitiveEvent, CognitiveEventType, LevelCrossing
)
import time

class ReasoningPattern:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.usage_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.contexts = []
    
    @property
    def effectiveness(self) -> float:
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.5
    
    def record_use(self, succeeded: bool, context: str = ""):
        self.usage_count += 1
        if succeeded:
            self.success_count += 1
        else:
            self.failure_count += 1
        if context:
            self.contexts.append(context)

class SelfModel:
    def __init__(self):
        self.goals: Dict[str, Goal] = {}
        self.reasoning_patterns: Dict[str, ReasoningPattern] = {}
        self.confidence_states: Dict[str, float] = {
            "perception": 0.7,
            "reasoning": 0.5,
            "prediction": 0.5,
            "self_knowledge": 0.3,
            "meta_cognition": 0.2
        }
        self.failure_history: List[FailureRecord] = []
        self.current_mode: ReasoningMode = ReasoningMode.SYSTEM_1
        self.current_strategy: str = "explore"
        self.identity_beliefs: Dict[str, Belief] = {}
        self.level_crossings: List[LevelCrossing] = []
        self._cognitive_load: float = 0.0
        self._emotional_valence: float = 0.0
        self._curiosity_drive: float = 0.7
        
        self._init_default_patterns()
        self._init_meta_goals()
    
    def _init_default_patterns(self):
        defaults = [
            ("pattern_match", "Fast associative matching"),
            ("analytical", "Step-by-step logical analysis"),
            ("self_referential", "Reasoning about own reasoning"),
        ]
        for name, desc in defaults:
            self.reasoning_patterns[name] = ReasoningPattern(name, desc)
    
    def _init_meta_goals(self):
        meta_goal = Goal(
            id="meta_understand_self",
            description="Develop accurate self-knowledge",
            priority=GoalPriority.HIGH,
            is_meta=True
        )
        self.goals[meta_goal.id] = meta_goal
    
    def add_goal(self, goal: Goal) -> str:
        self.goals[goal.id] = goal
        return goal.id
    
    def get_active_goals(self, include_meta: bool = True) -> List[Goal]:
        goals = [g for g in self.goals.values() if not g.is_complete]
        if not include_meta:
            goals = [g for g in goals if not g.is_meta]
        return sorted(goals, key=lambda g: g.priority.value, reverse=True)
    
    def select_reasoning_mode(self, context: Dict) -> ReasoningMode:
        complexity = context.get("complexity", 0.5)
        self_referential = context.get("self_referential", False)
        
        if self_referential:
            self.current_mode = ReasoningMode.STRANGE_LOOP
        elif complexity > 0.7:
            self.current_mode = ReasoningMode.SYSTEM_2
        else:
            self.current_mode = ReasoningMode.SYSTEM_1
        
        return self.current_mode
    
    def record_failure(self, failure: FailureRecord):
        self.failure_history.append(failure)
        if failure.failure_type in self.confidence_states:
            current = self.confidence_states[failure.failure_type]
            self.confidence_states[failure.failure_type] = current * (1 - failure.severity * 0.3)
    
    def intervene_on_world(self, world_model, intervention: Dict) -> LevelCrossing:
        crossing = LevelCrossing(
            from_level=1,
            to_level=0,
            direction="downward",
            content=str(intervention),
            causal_chain=[]
        )
        
        if "attention" in intervention:
            for entity_id, weight in intervention["attention"].items():
                world_model.set_attention(entity_id, weight)
                crossing.causal_chain.append(f"attention({entity_id})={weight}")
        
        if "self_update" in intervention:
            world_model.update_self(intervention["self_update"])
            crossing.causal_chain.append(f"self_update: {intervention['self_update']}")
        
        self.level_crossings.append(crossing)
        return crossing
    
    def reflect_on_self(self) -> CognitiveEvent:
        assessment = {
            "current_mode": self.current_mode.value,
            "strategy": self.current_strategy,
            "cognitive_load": self._cognitive_load,
            "confidence_profile": dict(self.confidence_states),
            "loop_depth": len(self.level_crossings),
            "is_self_aware": len(self.level_crossings) > 0
        }
        
        return CognitiveEvent(
            event_type=CognitiveEventType.SELF_REFLECTION,
            content=assessment,
            source_level=1,
            salience=0.8
        )
    
    def _calculate_recent_failure_rate(self, window: int = 10) -> float:
        recent = self.failure_history[-window:] if self.failure_history else []
        return len(recent) / window if recent else 0.0
    
    def get_state_summary(self) -> Dict:
        return {
            "mode": self.current_mode.value,
            "strategy": self.current_strategy,
            "goals": {gid: {"desc": g.description, "progress": g.progress}
                     for gid, g in self.goals.items()},
            "confidence": dict(self.confidence_states),
            "reasoning_patterns": {
                name: {"effectiveness": p.effectiveness, "uses": p.usage_count}
                for name, p in self.reasoning_patterns.items()
            },
            "level_crossings": len(self.level_crossings),
            "strange_crossings": sum(1 for lc in self.level_crossings if lc.is_strange),
            "cognitive_load": self._cognitive_load
        }
