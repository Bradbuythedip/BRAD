"""
bondli_bridge — Plug-and-play cognitive trading layer for Bondli

Connects BRAD's strange loop architecture to Bondli's ML trading terminal.
Level 0 (Market) watches tokens. Level 1 (Trading) makes decisions.
Level 2 (Meta) catches bad patterns and forces corrections.

Usage from Bondli's Node.js backend:
    POST /evaluate    — score a token, get APE/SKIP
    POST /position    — update position, get EXIT/HOLD
    POST /regime      — update market regime
    GET  /state       — full cognitive state
    GET  /metrics     — consciousness + trading metrics
"""

__version__ = "1.0.0"
__description__ = "BRAD cognitive trading layer for Bondli"
