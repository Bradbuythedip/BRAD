"""global_workspace.py — The Binding Mechanism"""

from typing import List, Dict, Optional, Callable
from .structures import CognitiveEvent
import heapq
import time

class GlobalWorkspace:
    def __init__(self, capacity: int = 100):
        self._competition_queue: List[tuple] = []
        self.current_broadcast: Optional[CognitiveEvent] = None
        self.broadcast_history: List[CognitiveEvent] = []
        self._listeners: Dict[str, Callable] = {}
        self.capacity = capacity
        self.total_events_submitted = 0
        self.total_broadcasts = 0
        self.self_referential_broadcasts = 0
    
    def submit(self, event: CognitiveEvent):
        self.total_events_submitted += 1
        adjusted_salience = event.salience + 0.05
        if event.is_self_referential:
            adjusted_salience += 0.15
        heapq.heappush(self._competition_queue, (-adjusted_salience, event.timestamp, event))
        while len(self._competition_queue) > self.capacity:
            heapq.heappop(self._competition_queue)
    
    def compete(self) -> Optional[CognitiveEvent]:
        if not self._competition_queue:
            return None
        neg_salience, timestamp, winner = heapq.heappop(self._competition_queue)
        self.current_broadcast = winner
        self.broadcast_history.append(winner)
        self.total_broadcasts += 1
        if winner.is_self_referential:
            self.self_referential_broadcasts += 1
        for name, callback in self._listeners.items():
            try:
                callback(winner)
            except:
                pass
        return winner
    
    def register_listener(self, name: str, callback: Callable):
        self._listeners[name] = callback
    
    def get_self_referential_ratio(self) -> float:
        if self.total_broadcasts == 0:
            return 0.0
        return self.self_referential_broadcasts / self.total_broadcasts
    
    def get_state_summary(self) -> Dict:
        return {
            "queue_size": len(self._competition_queue),
            "total_submitted": self.total_events_submitted,
            "total_broadcasts": self.total_broadcasts,
            "self_referential_ratio": self.get_self_referential_ratio()
        }
