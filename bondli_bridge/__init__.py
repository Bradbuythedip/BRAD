"""
bondli_bridge — Recursive cognitive trading architecture for Bondli

Implements a three-level strange loop cognitive hierarchy for autonomous
trading decision-making on Solana. Based on Hofstadter's theory of
self-referential systems, adapted for real-time market microstructure.

Architecture:
    Level 0 (MarketWorldModel)   — Perceptual grounding: token entities,
                                    wallet entities, regime classification
    Level 1 (TradingSelfModel)   — Strategic reasoning: entry/exit decisions,
                                    strategy selection, position management
    Level 2 (TradingMetaCognitive) — Meta-cognitive oversight: blind spot
                                    detection, strategy evaluation,
                                    downward causation interventions

API surface (FastAPI, default port 8421):
    POST /evaluate    — Evaluate token for entry (APE/SKIP)
    POST /position    — Evaluate open position (EXIT/HOLD)
    POST /regime      — Update market regime classification
    GET  /state       — Full cognitive state inspection
    GET  /metrics     — Cognitive and trading performance metrics

Reference:
    Hofstadter, D. R. (1979). Godel, Escher, Bach: An Eternal Golden Braid.
    Kahneman, D. (2011). Thinking, Fast and Slow.
    Baars, B. J. (1988). A Cognitive Theory of Consciousness.
"""

__version__ = "1.0.0"
__description__ = "Brain — Recursive cognitive trading architecture for Bondli"
