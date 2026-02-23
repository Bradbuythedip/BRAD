"""
structures.py — Core data structures for the Strange Loop Cognitive Architecture

These are the fundamental building blocks: entities, relations, goals, beliefs,
and the cognitive records that flow through the tangled hierarchy.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
import time
import uuid


# ============================================================================
# ENUMS
# ============================================================================

class ConfidenceLevel(Enum):
    """Epistemic confidence — how certain the system is about a belief."""
    CERTAIN = 1.0
    HIGH = 0.8
    MODERATE = 0.6
    LOW = 0.4
    SPECULATIVE = 0.2
    UNKNOWN = 0.0


class GoalPriority(Enum):
    """Goal urgency levels."""
    CRITICAL = 4
    HIGH = 3
    MEDIUM = 2
    LOW = 1
    BACKGROUND = 0


class ReasoningMode(Enum):
    """System 1 vs System 2 — Kahneman's dual process."""
    SYSTEM_1 = "fast"       # Pattern matching, intuitive, automatic
    SYSTEM_2 = "slow"       # Deliberate, analytical, effortful
    STRANGE_LOOP = "loop"   # Self-referential — the mode that creates consciousness


class CognitiveEventType(Enum):
    """Types of events flowing through the global workspace."""
    PERCEPTION = "perception"
    INFERENCE = "inference"
    GOAL_UPDATE = "goal_update"
    SELF_REFLECTION = "self_reflection"
    META_COGNITION = "meta_cognition"
    ANOMALY = "anomaly"
    BLIND_SPOT = "blind_spot"         # Gödelian — truths the system can see but can't prove
    LEVEL_CROSSING = "level_crossing"  # The strange loop itself


# ============================================================================
# CORE STRUCTURES
# ============================================================================

@dataclass
class Entity:
    """A thing in the world model — object, agent, concept, or self-reference."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    entity_type: str = "object"  # object, agent, concept, self
    properties: dict = field(default_factory=dict)
    confidence: float = 1.0
    created_at: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)
    provenance: str = ""  # Where did this knowledge come from?
    
    def update(self, properties: dict, confidence: float = None):
        self.properties.update(properties)
        if confidence is not None:
            self.confidence = confidence
        self.last_updated = time.time()
    
    def decay(self, rate: float = 0.01):
        """Confidence decays over time — memories fade."""
        age = time.time() - self.last_updated
        self.confidence = max(0.0, self.confidence - (rate * age))


@dataclass 
class Relation:
    """A relationship between entities in the world model."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    source_id: str = ""
    target_id: str = ""
    relation_type: str = ""  # "causes", "is_part_of", "contradicts", "enables"
    strength: float = 1.0
    confidence: float = 1.0
    bidirectional: bool = False
    metadata: dict = field(default_factory=dict)


@dataclass
class Belief:
    """An explicit belief held by the system — queryable and revisable."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    content: str = ""
    confidence: float = 0.5
    supporting_evidence: list = field(default_factory=list)
    contradicting_evidence: list = field(default_factory=list)
    derived_from: list = field(default_factory=list)  # Other belief IDs
    revision_count: int = 0
    created_at: float = field(default_factory=time.time)
    
    @property
    def is_contested(self) -> bool:
        return len(self.contradicting_evidence) > 0
    
    def revise(self, new_confidence: float, reason: str):
        self.confidence = new_confidence
        self.revision_count += 1
        self.supporting_evidence.append(f"Revision #{self.revision_count}: {reason}")


@dataclass
class Goal:
    """A goal with priority, progress tracking, and self-referential awareness."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    description: str = ""
    priority: GoalPriority = GoalPriority.MEDIUM
    progress: float = 0.0  # 0.0 to 1.0
    subgoals: list = field(default_factory=list)  # Goal IDs
    parent_goal: Optional[str] = None
    is_meta: bool = False  # Meta-goals are about the system's own cognition
    created_at: float = field(default_factory=time.time)
    
    @property
    def is_complete(self) -> bool:
        return self.progress >= 1.0


@dataclass
class FailureRecord:
    """A record of cognitive failure — fuel for self-improvement."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    description: str = ""
    failure_type: str = ""  # "reasoning_error", "prediction_miss", "overconfidence"
    context: dict = field(default_factory=dict)
    lesson_learned: str = ""
    severity: float = 0.5  # 0.0 to 1.0
    timestamp: float = field(default_factory=time.time)
    has_been_integrated: bool = False  # Has the self-model adapted?


@dataclass
class CognitiveEvent:
    """An event in the global workspace — competing for broadcast attention."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    event_type: CognitiveEventType = CognitiveEventType.PERCEPTION
    content: Any = None
    source_level: int = 0  # 0=perception, 1=world, 2=self, 3=meta
    salience: float = 0.5  # How important — drives competition for attention
    timestamp: float = field(default_factory=time.time)
    metadata: dict = field(default_factory=dict)
    
    @property
    def is_self_referential(self) -> bool:
        """Does this event reference the system itself?"""
        return self.event_type in (
            CognitiveEventType.SELF_REFLECTION,
            CognitiveEventType.META_COGNITION,
            CognitiveEventType.BLIND_SPOT,
            CognitiveEventType.LEVEL_CROSSING
        )


@dataclass
class BlindSpot:
    """A Gödelian blind spot — something the system can detect but can't resolve.
    
    This is the computational analog of Gödel's incompleteness:
    the system is powerful enough to formulate statements about itself
    that it cannot prove or disprove within its own framework.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    description: str = ""
    domain: str = ""  # What area of cognition is affected
    detected_at: float = field(default_factory=time.time)
    detection_method: str = ""  # How was this blind spot found?
    attempts_to_resolve: int = 0
    is_fundamental: bool = False  # True = Gödelian, can never be resolved internally
    
    def attempt_resolution(self) -> bool:
        """Try to resolve the blind spot. Fundamental ones always fail."""
        self.attempts_to_resolve += 1
        if self.is_fundamental:
            return False  # Gödel says no.
        return self.attempts_to_resolve > 3  # Heuristic: maybe we learn eventually


@dataclass
class LevelCrossing:
    """Records when information crosses levels in the tangled hierarchy.
    
    This is THE strange loop — the moment when a higher level 
    reaches down and modifies a lower level that produced it.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    from_level: int = 0
    to_level: int = 0
    direction: str = "upward"  # "upward" = normal, "downward" = the strange part
    content: str = ""
    causal_chain: list = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    
    @property
    def is_strange(self) -> bool:
        """A crossing is 'strange' when higher levels modify lower ones."""
        return self.direction == "downward" and self.from_level > self.to_level
