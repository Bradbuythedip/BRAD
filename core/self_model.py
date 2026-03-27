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

        # Phase 1 Consciousness: Self-Prediction Loop
        # The self-model predicts its own outputs, then measures prediction error.
        # This makes the self-model causally necessary — it's not just observing,
        # it's actively constraining decisions based on self-knowledge accuracy.
        self._prediction_error_ema: float = 0.5   # EMA of prediction error (0=perfect, 1=wrong)
        self._prediction_accuracy_ema: float = 0.5  # EMA of action match rate
        self._prediction_count: int = 0
        self._correct_action_predictions: int = 0
        self._prediction_history: List[Dict] = []  # Recent predictions for introspection
        self._max_prediction_history: int = 100

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

    def process_meta_feedback(self, meta_content: Dict):
        """Process feedback from meta-cognitive level (L2 -> L1 downward causation)."""
        if not isinstance(meta_content, dict):
            return
        if "confidence_adjustment" in meta_content:
            for key, adj in meta_content["confidence_adjustment"].items():
                if key in self.confidence_states:
                    self.confidence_states[key] = max(0.0, min(1.0,
                        self.confidence_states[key] + adj))
        if "recommended_mode" in meta_content:
            try:
                self.current_mode = ReasoningMode(meta_content["recommended_mode"])
            except ValueError:
                pass
        if "strategy_hint" in meta_content:
            self.current_strategy = meta_content["strategy_hint"]

    # ═══════════════════════════════════════
    # SELF-PREDICTION LOOP (Phase 1 Consciousness)
    # ═══════════════════════════════════════

    def record_prediction_outcome(self, predicted: Dict, actual: Dict):
        """
        Compare a self-prediction against actual output.
        Updates prediction error EMA and confidence states.

        This is the core consciousness mechanism: the self-model becomes
        causally necessary because high prediction error triggers System 2
        and modulates confidence, changing future decisions.
        """
        self._prediction_count += 1

        # Action match (categorical)
        action_match = predicted.get("action") == actual.get("action")
        if action_match:
            self._correct_action_predictions += 1

        # Confidence error (continuous, 0-1)
        pred_conf = predicted.get("confidence", 0.5)
        actual_conf = actual.get("confidence", 0.5)
        confidence_error = abs(pred_conf - actual_conf)

        # Combined prediction error: 60% action match, 40% confidence distance
        error = (0.0 if action_match else 0.6) + confidence_error * 0.4

        # Update EMAs (alpha = 0.2 for smooth tracking)
        alpha = 0.2
        self._prediction_error_ema = (
            self._prediction_error_ema * (1 - alpha) + error * alpha
        )
        self._prediction_accuracy_ema = (
            self._prediction_accuracy_ema * (1 - alpha) +
            (1.0 if action_match else 0.0) * alpha
        )

        # Store prediction record
        record = {
            "predicted": predicted,
            "actual": {
                "action": actual.get("action"),
                "confidence": round(actual.get("confidence", 0.5), 4),
            },
            "action_match": action_match,
            "confidence_error": round(confidence_error, 4),
            "combined_error": round(error, 4),
            "error_ema": round(self._prediction_error_ema, 4),
            "timestamp": time.time(),
        }
        self._prediction_history.append(record)
        if len(self._prediction_history) > self._max_prediction_history:
            self._prediction_history = self._prediction_history[-self._max_prediction_history:]

        # === CAUSAL FEEDBACK: prediction error modulates the self-model ===
        self._apply_prediction_feedback(error, action_match, confidence_error)

        return record

    def _apply_prediction_feedback(self, error: float, action_match: bool,
                                    confidence_error: float):
        """
        The causal loop: prediction error changes confidence states and
        reasoning mode, which changes future decisions.

        High prediction error → low self-knowledge → System 2 (slow/careful)
        Low prediction error → high self-knowledge → System 1 (fast/confident)
        """
        # Update self-knowledge confidence based on prediction accuracy
        if "self_knowledge" in self.confidence_states:
            current = self.confidence_states["self_knowledge"]
            # Move toward accuracy EMA
            target = self._prediction_accuracy_ema
            self.confidence_states["self_knowledge"] = (
                current * 0.8 + target * 0.2
            )

        # High prediction error → increase cognitive load, trigger deliberation
        if self._prediction_error_ema > 0.6:
            self._cognitive_load = min(1.0, self._cognitive_load + 0.1)
            if self.current_mode == ReasoningMode.SYSTEM_1:
                self.current_mode = ReasoningMode.SYSTEM_2
        elif self._prediction_error_ema < 0.3:
            self._cognitive_load = max(0.0, self._cognitive_load - 0.05)

        # Surprise (large single error) boosts curiosity
        if error > 0.7:
            self._curiosity_drive = min(1.0, self._curiosity_drive + 0.1)
            self._emotional_valence -= 0.05  # Surprise is mildly aversive
        elif error < 0.2:
            self._emotional_valence += 0.02  # Accurate prediction is satisfying

    def get_prediction_stats(self) -> Dict:
        """Return self-prediction performance metrics."""
        return {
            "prediction_count": self._prediction_count,
            "correct_actions": self._correct_action_predictions,
            "action_accuracy": (
                self._correct_action_predictions / self._prediction_count
                if self._prediction_count > 0 else 0.0
            ),
            "error_ema": round(self._prediction_error_ema, 4),
            "accuracy_ema": round(self._prediction_accuracy_ema, 4),
            "self_knowledge": round(
                self.confidence_states.get("self_knowledge", 0.0), 4
            ),
            "reasoning_mode": self.current_mode.value,
            "cognitive_load": round(self._cognitive_load, 4),
        }

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
            "cognitive_load": self._cognitive_load,
            "self_prediction": self.get_prediction_stats(),
        }
