"""
world_model.py — Level 0: The Ground Floor

A persistent, structured representation of the environment.
Unlike transformer attention (which is stateless), this maintains
explicit entities, relations, and predictions that persist across
cognitive cycles.

The critical property: the world model contains a representation
of the AGENT ITSELF as an entity. This is the seed of self-reference.
"""

from typing import List, Optional, Dict, Tuple
from .structures import (
    Entity, Relation, Belief, CognitiveEvent, 
    CognitiveEventType, ConfidenceLevel
)
import time


class WorldModel:
    """
    Level 0 of the tangled hierarchy.
    
    Maintains a knowledge graph of entities and relations,
    makes predictions, and critically — contains a representation
    of the agent itself as an entity within the world.
    """
    
    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.relations: List[Relation] = []
        self.beliefs: Dict[str, Belief] = {}
        self.predictions: List[Dict] = []
        self.attention_weights: Dict[str, float] = {}  # What to focus on
        self.cycle_count: int = 0
        
        # THE SEED OF SELF-REFERENCE
        # The agent exists as an entity in its own world model
        self._self_entity = Entity(
            id="SELF",
            name="self",
            entity_type="self",
            properties={
                "type": "cognitive_agent",
                "architecture": "strange_loop",
                "is_self_aware": False,  # Updated by meta-cognition
                "current_state": "initializing",
                "strange_loop_depth": 0
            },
            confidence=1.0,
            provenance="intrinsic"
        )
        self.entities["SELF"] = self._self_entity
    
    # ================================================================
    # ENTITY OPERATIONS
    # ================================================================
    
    def add_entity(self, entity: Entity) -> str:
        """Add an entity to the world model."""
        self.entities[entity.id] = entity
        self.attention_weights[entity.id] = entity.confidence
        return entity.id
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        return self.entities.get(entity_id)
    
    def update_entity(self, entity_id: str, properties: dict, confidence: float = None):
        """Update an entity's properties."""
        if entity_id in self.entities:
            self.entities[entity_id].update(properties, confidence)
    
    def remove_entity(self, entity_id: str):
        if entity_id != "SELF":  # Can't remove yourself
            self.entities.pop(entity_id, None)
            self.relations = [r for r in self.relations 
                            if r.source_id != entity_id and r.target_id != entity_id]
    
    # ================================================================
    # RELATION OPERATIONS
    # ================================================================
    
    def add_relation(self, relation: Relation) -> str:
        self.relations.append(relation)
        return relation.id
    
    def get_relations(self, entity_id: str, relation_type: str = None) -> List[Relation]:
        """Get all relations involving an entity."""
        results = [r for r in self.relations 
                   if r.source_id == entity_id or r.target_id == entity_id]
        if relation_type:
            results = [r for r in results if r.relation_type == relation_type]
        return results
    
    def find_path(self, source_id: str, target_id: str, max_depth: int = 5) -> List[str]:
        """Find a path between two entities through the relation graph."""
        visited = set()
        queue = [(source_id, [source_id])]
        
        while queue:
            current, path = queue.pop(0)
            if current == target_id:
                return path
            if current in visited or len(path) > max_depth:
                continue
            visited.add(current)
            
            for rel in self.get_relations(current):
                next_id = rel.target_id if rel.source_id == current else rel.source_id
                if next_id not in visited:
                    queue.append((next_id, path + [next_id]))
        
        return []  # No path found
    
    # ================================================================
    # BELIEF OPERATIONS  
    # ================================================================
    
    def add_belief(self, belief: Belief) -> str:
        # Check for contradictions with existing beliefs
        contradictions = self._find_contradictions(belief)
        if contradictions:
            belief.contradicting_evidence.extend(
                [f"Contradicts belief: {b.id}" for b in contradictions]
            )
        self.beliefs[belief.id] = belief
        return belief.id
    
    def revise_belief(self, belief_id: str, new_confidence: float, reason: str):
        if belief_id in self.beliefs:
            self.beliefs[belief_id].revise(new_confidence, reason)
    
    def get_contested_beliefs(self) -> List[Belief]:
        """Return beliefs that have contradicting evidence."""
        return [b for b in self.beliefs.values() if b.is_contested]
    
    def _find_contradictions(self, new_belief: Belief) -> List[Belief]:
        """Simple contradiction detection — can be made more sophisticated."""
        contradictions = []
        for existing in self.beliefs.values():
            # Check if any relations mark these as contradictory
            for rel in self.relations:
                if (rel.relation_type == "contradicts" and
                    ((rel.source_id == new_belief.id and rel.target_id == existing.id) or
                     (rel.source_id == existing.id and rel.target_id == new_belief.id))):
                    contradictions.append(existing)
        return contradictions
    
    # ================================================================
    # PREDICTION
    # ================================================================
    
    def make_prediction(self, description: str, basis: List[str], 
                       confidence: float = 0.5) -> Dict:
        """Generate a prediction based on current world state."""
        prediction = {
            "id": f"pred_{len(self.predictions)}",
            "description": description,
            "basis": basis,  # Entity/belief IDs that support this
            "confidence": confidence,
            "made_at": time.time(),
            "resolved": False,
            "was_correct": None
        }
        self.predictions.append(prediction)
        return prediction
    
    def resolve_prediction(self, prediction_id: str, was_correct: bool):
        """Resolve a prediction — this feeds back into self-model."""
        for pred in self.predictions:
            if pred["id"] == prediction_id:
                pred["resolved"] = True
                pred["was_correct"] = was_correct
                pred["resolved_at"] = time.time()
                break
    
    def get_prediction_accuracy(self) -> float:
        """How accurate have predictions been?"""
        resolved = [p for p in self.predictions if p["resolved"]]
        if not resolved:
            return 0.5  # No data
        correct = sum(1 for p in resolved if p["was_correct"])
        return correct / len(resolved)
    
    # ================================================================
    # SELF-REFERENCE — The seed of the strange loop
    # ================================================================
    
    def get_self(self) -> Entity:
        """Get the agent's representation of itself within the world."""
        return self._self_entity
    
    def update_self(self, properties: dict):
        """Update the self-representation. 
        THIS IS WHERE LEVEL-CROSSING HAPPENS.
        When the self-model or meta-cognitive loop calls this,
        a higher level is modifying a lower level's representation."""
        self._self_entity.update(properties)
    
    def get_self_relations(self) -> List[Relation]:
        """How does the self relate to other entities?"""
        return self.get_relations("SELF")
    
    # ================================================================
    # ATTENTION — What the world model is focusing on
    # ================================================================
    
    def set_attention(self, entity_id: str, weight: float):
        """Set attention weight for an entity. 
        Can be called by self-model (downward causation!)."""
        self.attention_weights[entity_id] = max(0.0, min(1.0, weight))
    
    def get_focus(self, top_n: int = 5) -> List[Tuple[str, float]]:
        """What is the world model currently attending to?"""
        sorted_attention = sorted(
            self.attention_weights.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        return sorted_attention[:top_n]
    
    # ================================================================
    # PERCEPTION PROCESSING
    # ================================================================
    
    def process_perception(self, perception: Dict) -> CognitiveEvent:
        """Process incoming perception and update world model."""
        self.cycle_count += 1
        
        # Create or update entities based on perception
        if "entities" in perception:
            for e_data in perception["entities"]:
                if e_data.get("id") in self.entities:
                    self.update_entity(e_data["id"], e_data.get("properties", {}))
                else:
                    entity = Entity(
                        name=e_data.get("name", "unknown"),
                        entity_type=e_data.get("type", "object"),
                        properties=e_data.get("properties", {}),
                        provenance="perception"
                    )
                    self.add_entity(entity)
        
        # Generate cognitive event
        event = CognitiveEvent(
            event_type=CognitiveEventType.PERCEPTION,
            content=perception,
            source_level=0,
            salience=perception.get("salience", 0.5),
            metadata={"cycle": self.cycle_count}
        )
        
        return event
    
    # ================================================================
    # INTROSPECTION
    # ================================================================
    
    def get_state_summary(self) -> Dict:
        """Summarize current world model state — used by higher levels."""
        return {
            "entity_count": len(self.entities),
            "relation_count": len(self.relations),
            "belief_count": len(self.beliefs),
            "contested_beliefs": len(self.get_contested_beliefs()),
            "prediction_accuracy": self.get_prediction_accuracy(),
            "focus": self.get_focus(3),
            "self_state": self._self_entity.properties,
            "cycle": self.cycle_count
        }
