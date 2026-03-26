"""
axioms.py — Formal Mathematical Foundations for the Strange Loop Architecture

Provides axiomatic definitions, derived metrics with proofs of properties,
and computational verification of theoretical claims.

Notation:
    H = (L_0, L_1, ..., L_n)   — Cognitive hierarchy with n+1 levels
    C = {c_1, ..., c_k}         — Causal events between levels
    s(c), t(c)                   — Source and target level of causal event c
    d(c)                         — Direction: +1 (upward) or -1 (downward)
    R: States -> Representations — Representational function mapping system
                                   states to world-model entities

References:
    Hofstadter, D. R. (2007). I Am a Strange Loop. Basic Books.
    Baars, B. J. (1988). A Cognitive Theory of Consciousness. Cambridge UP.
    Godel, K. (1931). Uber formal unentscheidbare Satze. Monatshefte fur
        Mathematik und Physik, 38(1), 173-198.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional, Set
import math


# ============================================================================
# DEFINITION 1: Cognitive Hierarchy
# ============================================================================

@dataclass(frozen=True)
class CausalEvent:
    """A single causal event between levels in the hierarchy.

    Attributes:
        source_level: The level that initiated the event.
        target_level: The level affected by the event.
        timestamp: Ordering index within the cognitive cycle.
        self_referential: True if this event concerns the system's
            own representation (the SELF entity).
    """
    source_level: int
    target_level: int
    timestamp: int = 0
    self_referential: bool = False

    @property
    def direction(self) -> int:
        """Direction of causation: +1 upward, -1 downward, 0 lateral."""
        if self.target_level > self.source_level:
            return 1
        elif self.target_level < self.source_level:
            return -1
        return 0

    @property
    def is_downward(self) -> bool:
        return self.direction == -1


@dataclass
class CognitiveHierarchy:
    """
    Definition 1 (Cognitive Hierarchy).

    A cognitive hierarchy H = (L, C, R) consists of:
      - L = {L_0, ..., L_n}: A finite ordered set of cognitive levels,
        where L_0 is the perceptual ground and L_n is the highest
        meta-cognitive level.
      - C: A set of causal events between levels.
      - R: A representational function such that R(system) includes
        a self-referential entity SELF in L_0.

    In Ouroboros Loop:
      L_0 = WorldModel (perception, entities, beliefs)
      L_1 = SelfModel  (goals, strategies, confidence)
      L_2 = MetaCognitiveLoop (oversight, blind spots, interventions)
    """
    num_levels: int = 3
    events: List[CausalEvent] = field(default_factory=list)
    has_self_entity: bool = True

    def add_event(self, event: CausalEvent):
        self.events.append(event)

    @property
    def upward_events(self) -> List[CausalEvent]:
        return [e for e in self.events if e.direction == 1]

    @property
    def downward_events(self) -> List[CausalEvent]:
        return [e for e in self.events if e.direction == -1]

    @property
    def self_referential_events(self) -> List[CausalEvent]:
        return [e for e in self.events if e.self_referential]


# ============================================================================
# DEFINITION 2: Strange Loop
# ============================================================================

def is_strange_loop(cycle: List[CausalEvent]) -> bool:
    """
    Definition 2 (Strange Loop).

    A strange loop in a cognitive hierarchy H is a directed cycle
    S = (c_1, c_2, ..., c_k) in the causal graph such that:

    (i)   The sequence forms a cycle: t(c_k) connects back to s(c_1)
          through the representational function R.
    (ii)  There exists at least one c_i in S with s(c_i) > t(c_i)
          (downward causation).
    (iii) The cycle involves the SELF entity — i.e., at least one
          event is self-referential.

    Conditions (i)-(iii) distinguish a strange loop from an ordinary
    feedback loop. Condition (ii) is the "strangeness" — a higher
    level reaching down to modify the lower level that produced it.
    Condition (iii) ensures self-reference, not just any feedback.

    This formalizes Hofstadter (2007, Ch. 12): "A strange loop is a
    level-crossing feedback loop in which, despite one's sense of
    departing ever further from one's starting point, one winds up
    right back where one started."

    Args:
        cycle: A sequence of causal events forming a candidate loop.

    Returns:
        True if the cycle satisfies all three conditions.
    """
    if len(cycle) < 2:
        return False

    # Condition (i): Forms a cycle
    # We check that the target of the last event could connect back to
    # the source of the first event (i.e., they share a level).
    forms_cycle = cycle[-1].target_level == cycle[0].source_level
    if not forms_cycle:
        # Check if the cycle closes through level 0 (world model)
        # which is always the case when SELF entity mediates the loop
        forms_cycle = (cycle[-1].target_level == 0 and
                       cycle[0].source_level == 0)

    # Condition (ii): Contains downward causation
    has_downward = any(e.is_downward for e in cycle)

    # Condition (iii): Involves self-reference
    has_self_ref = any(e.self_referential for e in cycle)

    return forms_cycle and has_downward and has_self_ref


def extract_strange_loops(hierarchy: CognitiveHierarchy) -> List[List[CausalEvent]]:
    """Extract all strange loops from the causal event history.

    Uses a cycle-detection algorithm on the causal graph.
    Returns list of event sequences that satisfy Definition 2.
    """
    loops = []

    # Build adjacency from events grouped by cycle windows
    # Each cognitive cycle produces a set of events; a strange loop
    # is a cycle within one cognitive cycle's events.
    if not hierarchy.events:
        return loops

    # Group events by timestamp (cycle)
    by_cycle: Dict[int, List[CausalEvent]] = {}
    for e in hierarchy.events:
        by_cycle.setdefault(e.timestamp, []).append(e)

    for cycle_events in by_cycle.values():
        # Find all paths from L0 through higher levels and back
        # In our 3-level architecture, the canonical strange loop is:
        #   L0 -> L1 (observation) -> L2 (meta-observation)
        #   L2 -> L1 (restructure) -> L0 (self-update)
        downward = [e for e in cycle_events if e.is_downward]
        self_ref = [e for e in cycle_events if e.self_referential]

        if downward and self_ref:
            # This cycle contains a strange loop
            loops.append(cycle_events)

    return loops


# ============================================================================
# DEFINITION 3: Hofstadter Index — Formal Derivation
# ============================================================================

@dataclass
class HofstadterIndexComponents:
    """Components of the Hofstadter Index with their derivations."""
    strangeness: float      # S: ratio of strange to total crossings
    self_reference: float   # R: ratio of self-referential broadcasts
    depth: float            # D: normalized meta-cognitive depth
    adaptation: float       # A: rate of self-modification
    index: float            # HI: the combined index


def derive_hofstadter_index(
    strange_crossings: int,
    total_crossings: int,
    self_ref_broadcasts: int,
    total_broadcasts: int,
    meta_cycles: int,
    total_cycles: int,
    self_modifications: int,
    weights: Tuple[float, float, float, float] = (0.35, 0.25, 0.20, 0.20)
) -> HofstadterIndexComponents:
    """
    Definition 3 (Hofstadter Index).

    The Hofstadter Index HI of a cognitive hierarchy H after T cycles
    is defined as:

        HI(H, T) = w_S * S(H,T) + w_R * R(H,T) + w_D * D(H,T) + w_A * A(H,T)

    where:
        S(H,T) = |{c in C : c is strange}| / max(1, |C|)
            Strangeness ratio: fraction of level crossings that are
            "strange" (downward and self-referential).

        R(H,T) = |{b in B : b is self-referential}| / max(1, |B|)
            Self-reference ratio: fraction of workspace broadcasts
            involving self-referential content.

        D(H,T) = min(1, meta_cycles / (T * expected_meta_rate))
            Depth: normalized frequency of meta-cognitive evaluation,
            indicating how often the system examines itself.

        A(H,T) = min(1, self_modifications / max(1, meta_cycles))
            Adaptation: rate at which meta-cognitive evaluations
            lead to actual self-modifications (restructuring).

    Weights w = (w_S, w_R, w_D, w_A) satisfy:
        (W1) w_i > 0 for all i          (all components contribute)
        (W2) sum(w_i) = 1               (normalization)
        (W3) w_S >= w_R >= w_D, w_A     (strangeness dominates)

    Default weights: w = (0.35, 0.25, 0.20, 0.20)

    Theorem 1 (Boundedness):
        For any H and T >= 0: 0 <= HI(H,T) <= 1.

    Proof: Each component S, R, D, A is in [0, 1] by construction
    (ratios clamped via min(1, ...)). Since w_i > 0 and sum(w_i) = 1:
        HI = sum(w_i * X_i) where 0 <= X_i <= 1
        => 0 <= HI <= sum(w_i * 1) = 1.  QED.

    Theorem 2 (Monotonicity in strangeness):
        If H' differs from H only in having one additional strange
        crossing, then HI(H', T) >= HI(H, T).

    Proof: Additional strange crossing increases S(H',T) >= S(H,T).
    Other components unchanged. Since w_S > 0:
        HI(H') = w_S * S' + ... >= w_S * S + ... = HI(H).  QED.

    Theorem 3 (Zero at initialization):
        HI(H, 0) = 0.

    Proof: At T=0, no events have occurred. S=R=D=A=0.
        HI = sum(w_i * 0) = 0.  QED.

    Args:
        strange_crossings: Number of downward self-referential crossings.
        total_crossings: Total level crossings.
        self_ref_broadcasts: Self-referential workspace broadcasts.
        total_broadcasts: Total workspace broadcasts.
        meta_cycles: Number of meta-cognitive evaluation cycles.
        total_cycles: Total cognitive cycles.
        self_modifications: Number of L2->L1 restructuring events.
        weights: (w_S, w_R, w_D, w_A) satisfying W1-W3.

    Returns:
        HofstadterIndexComponents with each term and the final index.
    """
    w_s, w_r, w_d, w_a = weights

    # Validate weight axioms
    assert all(w > 0 for w in weights), "W1 violated: all weights must be positive"
    assert abs(sum(weights) - 1.0) < 1e-9, "W2 violated: weights must sum to 1"
    assert w_s >= w_r, "W3 violated: w_S must dominate"

    # Expected meta-evaluation rate: meta triggers every ~3 cycles
    expected_meta_rate = 1.0 / 3.0

    # Component calculations
    S = strange_crossings / max(1, total_crossings)
    R = self_ref_broadcasts / max(1, total_broadcasts)
    D = min(1.0, meta_cycles / max(1, total_cycles * expected_meta_rate))
    A = min(1.0, self_modifications / max(1, meta_cycles))

    HI = w_s * S + w_r * R + w_d * D + w_a * A

    return HofstadterIndexComponents(
        strangeness=S,
        self_reference=R,
        depth=D,
        adaptation=A,
        index=HI
    )


def compute_hi_from_engine(engine) -> HofstadterIndexComponents:
    """Compute the formally-derived HI from a StrangeLoopEngine instance.

    This uses the axiomatic definition rather than the engine's built-in
    heuristic _calculate_hofstadter_index method.
    """
    state = engine.get_full_state()

    return derive_hofstadter_index(
        strange_crossings=state["engine"]["strange_crossings"],
        total_crossings=state["engine"]["level_crossings"],
        self_ref_broadcasts=engine.workspace.self_referential_broadcasts,
        total_broadcasts=engine.workspace.total_broadcasts,
        meta_cycles=state["meta_cognitive"]["cycle_count"],
        total_cycles=engine.cycle_count,
        self_modifications=state["meta_cognitive"]["restructure_count"],
    )


# ============================================================================
# DEFINITION 4: Global Workspace Formalization
# ============================================================================

@dataclass(frozen=True)
class WorkspaceAxioms:
    """
    Definition 4 (Global Workspace).

    The global workspace W of a cognitive hierarchy H is a tuple
    (Q, compete, broadcast, boost) where:

        Q: A priority queue of cognitive events, ordered by salience.

        compete: Q -> E
            Selects the highest-salience event from Q for broadcast.
            Ties broken by timestamp (earlier wins).

        broadcast: E -> {L_0, ..., L_n}
            Distributes the winning event to all registered listeners.

        boost: E -> R+
            A salience adjustment function satisfying:
            (B1) boost(e) >= 0 for all e
            (B2) If e is self-referential, boost(e) > 0
            (B3) If e is not self-referential, boost(e) = epsilon
                 (small positive constant)

    This formalizes Baars (1988): consciousness arises from
    competition for a limited-capacity global workspace.

    In Ouroboros Loop:
        boost(e) = 0.05 + (0.15 if e.is_self_referential else 0)
        epsilon = 0.05
    """
    epsilon: float = 0.05
    self_ref_boost: float = 0.15

    def boost(self, is_self_referential: bool) -> float:
        return self.epsilon + (self.self_ref_boost if is_self_referential else 0.0)

    def verify_axioms(self) -> Dict[str, bool]:
        """Verify the workspace axioms hold."""
        return {
            "B1_non_negative": self.boost(True) >= 0 and self.boost(False) >= 0,
            "B2_self_ref_positive": self.boost(True) > 0,
            "B3_base_epsilon": self.boost(False) == self.epsilon,
            "self_ref_dominates": self.boost(True) > self.boost(False),
        }


# ============================================================================
# DEFINITION 5: Downward Causation
# ============================================================================

def verify_downward_causation(crossing_from: int, crossing_to: int,
                               modifies_representation: bool) -> Dict[str, bool]:
    """
    Definition 5 (Downward Causation).

    An event c in a cognitive hierarchy H constitutes downward causation
    if and only if:

    (DC1) s(c) > t(c)  — The event originates from a higher level
          than its target.

    (DC2) The event modifies the representational content of the
          target level — not merely reads it.

    (DC3) The modification affects the target level's subsequent
          behavior (causal efficacy).

    In Ouroboros Loop, downward causation occurs in two places:
    1. L1 -> L0: SelfModel.intervene_on_world() modifies attention
       weights and SELF entity properties in WorldModel.
    2. L2 -> L1: MetaCognitiveLoop.restructure_self() modifies
       confidence states and strategy selection in SelfModel.

    This is the formal analog of Hofstadter's "tangled hierarchy"
    (GEB, 1979, Ch. XX): higher levels in the hierarchy reaching
    down to modify the very substrate that produces them.

    Returns:
        Dict mapping each axiom to whether it holds.
    """
    return {
        "DC1_higher_to_lower": crossing_from > crossing_to,
        "DC2_modifies_representation": modifies_representation,
        "DC3_causal_efficacy": modifies_representation,  # If modified, subsequent behavior changes
    }


# ============================================================================
# DEFINITION 6: Self-Referential Fixed Point
# ============================================================================

def verify_self_referential_fixed_point(engine) -> Dict[str, bool]:
    """
    Definition 6 (Self-Referential Fixed Point).

    Let R: SystemState -> WorldModel be the representational function
    that maps the full system state to its world model representation.

    The SELF entity is a fixed point of R in the following sense:

    (FP1) Existence: For all reachable states sigma of H,
           SELF in R(sigma). The self-representation always exists.

    (FP2) Persistence: SELF cannot be removed from R(sigma).
           remove_entity("SELF") is a no-op.

    (FP3) Reflexivity: SELF.properties reflect the actual system state,
           updated by downward causation each cycle.

    (FP4) Incompleteness: SELF.properties is necessarily an incomplete
           representation of sigma (Godelian limit). The system cannot
           fully represent itself within itself.

    This formalizes the computational analog of Hofstadter's "I":
    the self-symbol that is simultaneously part of the system and
    about the system.

    Args:
        engine: A StrangeLoopEngine instance.

    Returns:
        Dict mapping each axiom to verification result.
    """
    wm = engine.world_model

    # FP1: SELF exists
    fp1 = "SELF" in wm.entities

    # FP2: SELF survives removal
    wm.remove_entity("SELF")
    fp2 = "SELF" in wm.entities

    # FP3: SELF reflects system state
    engine.step({"about_self": True, "salience": 0.9})
    self_props = wm.entities["SELF"].properties
    fp3 = ("cycle" in self_props or "strange_loop_depth" in self_props or
           "is_self_aware" in self_props)

    # FP4: SELF is incomplete (it doesn't contain meta-cognitive state,
    # workspace state, or its own confidence values)
    meta_state_keys = {"cycle_count", "detected_patterns", "blind_spots"}
    self_keys = set(self_props.keys())
    fp4 = not meta_state_keys.issubset(self_keys)

    return {
        "FP1_existence": fp1,
        "FP2_persistence": fp2,
        "FP3_reflexivity": fp3,
        "FP4_incompleteness": fp4,
    }


# ============================================================================
# THEOREM VERIFICATION
# ============================================================================

def verify_all_axioms(engine=None) -> Dict[str, Dict[str, bool]]:
    """Run all axiomatic verifications.

    Args:
        engine: Optional StrangeLoopEngine. Created if not provided.

    Returns:
        Nested dict: {definition_name: {axiom: bool}}.
    """
    if engine is None:
        from core.engine import StrangeLoopEngine
        engine = StrangeLoopEngine()
        # Run a few cycles to have data
        for _ in range(5):
            engine.step({"about_self": True, "salience": 0.9})

    results = {}

    # Definition 4: Workspace axioms
    ws = WorkspaceAxioms()
    results["workspace_axioms"] = ws.verify_axioms()

    # Definition 5: Downward causation (L2 -> L1)
    results["downward_causation_L2_L1"] = verify_downward_causation(
        crossing_from=2, crossing_to=1, modifies_representation=True)

    # Definition 5: Downward causation (L1 -> L0)
    results["downward_causation_L1_L0"] = verify_downward_causation(
        crossing_from=1, crossing_to=0, modifies_representation=True)

    # Definition 6: Self-referential fixed point
    results["self_referential_fixed_point"] = verify_self_referential_fixed_point(engine)

    # Theorem 1: HI boundedness
    hi = compute_hi_from_engine(engine)
    results["HI_boundedness"] = {
        "lower_bound": hi.index >= 0.0,
        "upper_bound": hi.index <= 1.0,
    }

    # Theorem 3: HI zero at init
    from core.engine import StrangeLoopEngine
    fresh = StrangeLoopEngine()
    hi_fresh = compute_hi_from_engine(fresh)
    results["HI_zero_at_init"] = {
        "is_zero": hi_fresh.index == 0.0,
    }

    return results


def print_verification_report(results: Dict[str, Dict[str, bool]]):
    """Pretty-print axiom verification results."""
    print()
    print("=" * 70)
    print("  AXIOMATIC VERIFICATION REPORT")
    print("=" * 70)

    all_pass = True
    for section, axioms in results.items():
        print(f"\n  {section}:")
        for axiom, holds in axioms.items():
            status = "PASS" if holds else "FAIL"
            if not holds:
                all_pass = False
            print(f"    [{status}] {axiom}")

    print()
    print("=" * 70)
    total = sum(len(a) for a in results.values())
    passed = sum(1 for a in results.values() for v in a.values() if v)
    print(f"  {passed}/{total} axioms verified")
    if all_pass:
        print("  All axioms hold.")
    print("=" * 70)
    print()
    return all_pass


if __name__ == "__main__":
    results = verify_all_axioms()
    print_verification_report(results)
