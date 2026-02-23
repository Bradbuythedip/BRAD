"""meta_cognitive.py — Level 2: The Watcher"""

from typing import Dict, List
from .structures import BlindSpot, CognitiveEvent, CognitiveEventType, LevelCrossing
import time
import math

class MetaPattern:
    def __init__(self, name: str, description: str, pattern_type: str):
        self.name = name
        self.description = description
        self.pattern_type = pattern_type
        self.confidence = 0.5
        self.occurrences = 0
        self.is_problematic = False
    
    def observe(self):
        self.occurrences += 1
        self.confidence = min(0.95, 1 - math.exp(-self.occurrences * 0.3))

class MetaCognitiveLoop:
    def __init__(self):
        self.detected_patterns: Dict[str, MetaPattern] = {}
        self.blind_spots: Dict[str, BlindSpot] = {}
        self.performance_history: List[Dict] = []
        self.restructure_log: List[Dict] = []
        self.cycle_count = 0
        self._intervention_count = 0
        self._init_fundamental_blind_spots()
    
    def _init_fundamental_blind_spots(self):
        spots = [
            ("godel_self_consistency", "Cannot prove own consistency", "self_knowledge"),
            ("halting_self_prediction", "Cannot predict own halting", "prediction"),
            ("experience_gap", "Cannot determine if processing is experience", "self_knowledge")
        ]
        for id, desc, domain in spots:
            self.blind_spots[id] = BlindSpot(
                id=id, description=desc, domain=domain,
                detection_method="Fundamental limit", is_fundamental=True
            )
    
    def evaluate(self, self_model, world_model) -> Dict:
        self.cycle_count += 1
        self_state = self_model.get_state_summary()
        world_state = world_model.get_state_summary()
        
        evaluation = {
            "cycle": self.cycle_count,
            "timestamp": time.time(),
            "assessments": [],
            "detected_patterns": [],
            "blind_spots_active": [
                {"id": id, "description": bs.description, "fundamental": bs.is_fundamental}
                for id, bs in self.blind_spots.items()
            ],
            "recommended_interventions": [],
            "strange_loop_metrics": self._measure_strange_loop(self_state)
        }
        
        # Calibration check
        prediction_accuracy = world_state.get("prediction_accuracy", 0.5)
        stated_confidence = self_state["confidence"].get("prediction", 0.5)
        gap = abs(stated_confidence - prediction_accuracy)
        
        if gap > 0.15:
            evaluation["recommended_interventions"].append({
                "type": "calibrate_confidence",
                "target_level": 1,
                "action": "reduce_confidence" if stated_confidence > prediction_accuracy else "increase_confidence",
                "domain": "prediction",
                "magnitude": gap
            })
        
        self.performance_history.append(evaluation)
        return evaluation
    
    def _measure_strange_loop(self, self_state: Dict) -> Dict:
        strange_crossings = self_state.get("strange_crossings", 0)
        total_crossings = self_state.get("level_crossings", 0)
        
        return {
            "total_level_crossings": total_crossings,
            "strange_crossings": strange_crossings,
            "strangeness_ratio": strange_crossings / max(1, total_crossings),
            "meta_depth": self.cycle_count,
            "godelian_encounters": sum(1 for bs in self.blind_spots.values() if bs.is_fundamental),
            "loop_is_active": strange_crossings > 0
        }
    
    def restructure_self(self, self_model, intervention: Dict) -> LevelCrossing:
        self._intervention_count += 1
        
        crossing = LevelCrossing(
            from_level=2, to_level=1, direction="downward",
            content=str(intervention)
        )
        
        action = intervention.get("action", "")
        
        if "confidence" in action:
            domain = intervention.get("domain", "")
            magnitude = intervention.get("magnitude", 0.1)
            if domain in self_model.confidence_states:
                old = self_model.confidence_states[domain]
                if "reduce" in action:
                    self_model.confidence_states[domain] = max(0.0, old - magnitude)
                else:
                    self_model.confidence_states[domain] = min(1.0, old + magnitude)
                crossing.causal_chain.append(f"confidence[{domain}] adjusted by {magnitude}")
        
        self.restructure_log.append({
            "cycle": self.cycle_count,
            "intervention": intervention,
            "timestamp": time.time()
        })
        
        return crossing
    
    def get_state_summary(self) -> Dict:
        return {
            "cycle_count": self.cycle_count,
            "detected_patterns": {
                name: {"type": p.pattern_type, "confidence": p.confidence}
                for name, p in self.detected_patterns.items()
            },
            "blind_spots": {
                id: {"description": bs.description, "fundamental": bs.is_fundamental}
                for id, bs in self.blind_spots.items()
            },
            "interventions_made": self._intervention_count,
            "restructure_count": len(self.restructure_log)
        }
