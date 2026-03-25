"""
market_world.py — Level 0: The Market Floor

Extends BRAD's WorldModel to represent the Solana memecoin market.
Tokens, wallets, liquidity pools, and market conditions are entities.
Beliefs are market hypotheses. Predictions are price/rug forecasts.

The SELF entity becomes "BRAD-as-trader" — a representation of the
trading system's own state within the market it's observing.
"""

from typing import Dict, List, Optional, Tuple
from core.structures import (
    Entity, Relation, Belief, CognitiveEvent,
    CognitiveEventType, ConfidenceLevel
)
from core.world_model import WorldModel
import time
import math


class TokenEntity:
    """Structured representation of a token in the market world."""

    __slots__ = (
        "mint", "name", "symbol", "source", "score", "score_history",
        "velocity", "acceleration", "rug_signals", "rug_details",
        "holder_count", "top_holder_pct", "liquidity_sol", "mcap_sol",
        "volume_5m", "buy_pressure", "created_at", "last_updated",
        "smart_money_in", "dev_wallet", "is_graduated", "entity_id",
    )

    def __init__(self, mint: str, data: Dict):
        self.mint = mint
        self.name = data.get("name", "")
        self.symbol = data.get("symbol", "")
        self.source = data.get("source", "pump")  # pump | bags
        self.score = data.get("score", 0.0)
        self.score_history: List[Tuple[float, float]] = []  # (timestamp, score)
        self.velocity = data.get("velocity", 0.0)
        self.acceleration = data.get("acceleration", 0.0)
        self.rug_signals = data.get("rug_signals", 0)
        self.rug_details: List[str] = data.get("rug_details", [])
        self.holder_count = data.get("holder_count", 0)
        self.top_holder_pct = data.get("top_holder_pct", 0.0)
        self.liquidity_sol = data.get("liquidity_sol", 0.0)
        self.mcap_sol = data.get("mcap_sol", 0.0)
        self.volume_5m = data.get("volume_5m", 0.0)
        self.buy_pressure = data.get("buy_pressure", 0.5)
        self.created_at = data.get("created_at", time.time())
        self.last_updated = time.time()
        self.smart_money_in = data.get("smart_money_in", False)
        self.dev_wallet = data.get("dev_wallet", "")
        self.is_graduated = data.get("is_graduated", False)
        self.entity_id: Optional[str] = None

    def update(self, data: Dict):
        """Update token with new data from Bondli scanner."""
        now = time.time()

        new_score = data.get("score", self.score)
        if new_score != self.score:
            self.score_history.append((now, self.score))
            # Keep last 50 score points
            if len(self.score_history) > 50:
                self.score_history = self.score_history[-50:]

        self.score = new_score
        self.velocity = data.get("velocity", self.velocity)
        self.acceleration = data.get("acceleration", self.acceleration)
        self.rug_signals = data.get("rug_signals", self.rug_signals)
        self.rug_details = data.get("rug_details", self.rug_details)
        self.holder_count = data.get("holder_count", self.holder_count)
        self.top_holder_pct = data.get("top_holder_pct", self.top_holder_pct)
        self.liquidity_sol = data.get("liquidity_sol", self.liquidity_sol)
        self.mcap_sol = data.get("mcap_sol", self.mcap_sol)
        self.volume_5m = data.get("volume_5m", self.volume_5m)
        self.buy_pressure = data.get("buy_pressure", self.buy_pressure)
        self.smart_money_in = data.get("smart_money_in", self.smart_money_in)
        self.is_graduated = data.get("is_graduated", self.is_graduated)
        self.last_updated = now

    def to_properties(self) -> Dict:
        return {
            "mint": self.mint,
            "name": self.name,
            "symbol": self.symbol,
            "source": self.source,
            "score": self.score,
            "velocity": self.velocity,
            "acceleration": self.acceleration,
            "rug_signals": self.rug_signals,
            "rug_details": self.rug_details,
            "holder_count": self.holder_count,
            "top_holder_pct": self.top_holder_pct,
            "liquidity_sol": self.liquidity_sol,
            "mcap_sol": self.mcap_sol,
            "volume_5m": self.volume_5m,
            "buy_pressure": self.buy_pressure,
            "smart_money_in": self.smart_money_in,
            "is_graduated": self.is_graduated,
            "age_seconds": time.time() - self.created_at,
        }

    @property
    def score_trend(self) -> str:
        """Classify the score trajectory."""
        if self.velocity > 0.05 and self.acceleration > 0:
            return "accelerating_up"
        elif self.velocity > 0.02:
            return "rising"
        elif self.velocity < -0.05 and self.acceleration < 0:
            return "accelerating_down"
        elif self.velocity < -0.02:
            return "falling"
        return "stable"


class MarketWorldModel(WorldModel):
    """
    Level 0 of the trading cognitive hierarchy.

    Extends BRAD's world model with:
    - Token entities from Bondli's scanner
    - Smart money wallet entities
    - Market regime as a persistent entity
    - Score-based attention weighting
    - Trading-specific predictions
    """

    def __init__(self, config=None):
        super().__init__()
        self.config = config
        self.tokens: Dict[str, TokenEntity] = {}  # mint -> TokenEntity
        self.smart_wallets: Dict[str, Dict] = {}   # wallet -> profile
        self._market_regime = "unknown"
        self._regime_history: List[Tuple[float, str]] = []
        self._token_event_count = 0

        # Update SELF entity for trading context
        self._self_entity.update({
            "type": "trading_agent",
            "architecture": "strange_loop_trader",
            "role": "bondli_cognitive_layer",
            "current_state": "initializing",
            "active_positions": 0,
            "total_trades": 0,
            "win_rate": 0.0,
            "pnl_sol": 0.0,
        })

        # Market regime entity
        self._regime_entity = Entity(
            id="MARKET_REGIME",
            name="market_regime",
            entity_type="regime",
            properties={
                "regime": "unknown",
                "confidence": 0.0,
                "bull_score": 0.0,
                "bear_score": 0.0,
                "chop_score": 0.0,
                "rug_frequency": 0.0,
                "avg_token_lifespan": 0.0,
            },
            provenance="market_analysis",
        )
        self.entities["MARKET_REGIME"] = self._regime_entity

    def ingest_token(self, mint: str, data: Dict) -> CognitiveEvent:
        """
        Ingest token data from Bondli's scanner/scorer.
        Returns a cognitive event for the global workspace.

        Called by Bondli via: POST /evaluate
        """
        self._token_event_count += 1

        if mint in self.tokens:
            token = self.tokens[mint]
            token.update(data)
            # Update existing entity
            if token.entity_id and token.entity_id in self.entities:
                self.entities[token.entity_id].update(token.to_properties())
        else:
            token = TokenEntity(mint, data)
            # Create world model entity
            entity = Entity(
                name=data.get("name", mint[:8]),
                entity_type="token",
                properties=token.to_properties(),
                confidence=data.get("score", 0.5),
                provenance="bondli_scanner",
            )
            token.entity_id = entity.id
            self.tokens[mint] = token
            self.add_entity(entity)

            # Relate token to market regime
            rel = Relation(
                source_id=entity.id,
                target_id="MARKET_REGIME",
                relation_type="exists_in",
                strength=1.0,
            )
            self.add_relation(rel)

        # Calculate salience based on score + novelty
        salience = self._calculate_token_salience(token)

        # Set attention weight
        if token.entity_id:
            self.set_attention(token.entity_id, salience)

        # Generate cognitive event
        event = CognitiveEvent(
            event_type=CognitiveEventType.PERCEPTION,
            content={
                "type": "token_update",
                "mint": mint,
                "score": token.score,
                "velocity": token.velocity,
                "acceleration": token.acceleration,
                "rug_signals": token.rug_signals,
                "trend": token.score_trend,
                "smart_money": token.smart_money_in,
                "salience": salience,
            },
            source_level=0,
            salience=salience,
            metadata={"cycle": self._token_event_count, "mint": mint},
        )

        # Auto-generate beliefs from strong signals
        self._auto_beliefs(token)

        return event

    def ingest_smart_wallet(self, wallet: str, profile: Dict) -> CognitiveEvent:
        """Ingest smart money wallet data."""
        self.smart_wallets[wallet] = profile

        entity = Entity(
            name=f"wallet_{wallet[:8]}",
            entity_type="smart_wallet",
            properties={
                "address": wallet,
                "win_rate": profile.get("win_rate", 0.0),
                "avg_profit": profile.get("avg_profit", 0.0),
                "total_trades": profile.get("total_trades", 0),
                "active_tokens": profile.get("active_tokens", []),
            },
            confidence=profile.get("win_rate", 0.5),
            provenance="smart_money_tracker",
        )
        self.add_entity(entity)

        # If smart wallet bought a token we're tracking, boost that token's attention
        for mint in profile.get("active_tokens", []):
            if mint in self.tokens and self.tokens[mint].entity_id:
                current_attention = self.attention_weights.get(
                    self.tokens[mint].entity_id, 0.5)
                self.set_attention(
                    self.tokens[mint].entity_id,
                    min(1.0, current_attention + 0.2))

        return CognitiveEvent(
            event_type=CognitiveEventType.PERCEPTION,
            content={"type": "smart_wallet", "wallet": wallet, "profile": profile},
            source_level=0,
            salience=0.7,
        )

    def update_regime(self, regime_data: Dict):
        """Update market regime from Bondli's regime-engine."""
        regime = regime_data.get("regime", "unknown")
        self._market_regime = regime
        self._regime_history.append((time.time(), regime))

        self._regime_entity.update({
            "regime": regime,
            "confidence": regime_data.get("confidence", 0.5),
            "bull_score": regime_data.get("bull_score", 0.0),
            "bear_score": regime_data.get("bear_score", 0.0),
            "chop_score": regime_data.get("chop_score", 0.0),
            "rug_frequency": regime_data.get("rug_frequency", 0.0),
            "avg_token_lifespan": regime_data.get("avg_token_lifespan", 0.0),
        })

    def get_token(self, mint: str) -> Optional[TokenEntity]:
        return self.tokens.get(mint)

    def get_top_tokens(self, n: int = 10) -> List[TokenEntity]:
        """Get top N tokens by attention weight."""
        scored = []
        for mint, token in self.tokens.items():
            if token.entity_id:
                weight = self.attention_weights.get(token.entity_id, 0.0)
                scored.append((weight, token))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [t for _, t in scored[:n]]

    def get_rug_candidates(self) -> List[TokenEntity]:
        """Get tokens showing rug signals."""
        return [t for t in self.tokens.values() if t.rug_signals >= 2]

    def get_regime(self) -> str:
        return self._market_regime

    def prune_stale_tokens(self, max_age_seconds: float = 600):
        """Remove tokens older than max_age that aren't in positions."""
        now = time.time()
        stale = [
            mint for mint, token in self.tokens.items()
            if (now - token.last_updated) > max_age_seconds
        ]
        for mint in stale:
            token = self.tokens.pop(mint)
            if token.entity_id:
                self.remove_entity(token.entity_id)

    def _calculate_token_salience(self, token: TokenEntity) -> float:
        """
        Calculate how much attention this token deserves.
        High score + smart money + momentum = high salience.
        Rug signals reduce salience (we want to ignore rugs, not focus on them).
        """
        base = token.score

        # Smart money boost
        if token.smart_money_in:
            base += 0.15

        # Momentum boost
        if token.score_trend in ("accelerating_up", "rising"):
            base += 0.1
        elif token.score_trend in ("accelerating_down", "falling"):
            base -= 0.1

        # Rug penalty
        base -= token.rug_signals * 0.1

        # Volume normalization (more volume = more interesting)
        if token.volume_5m > 0:
            vol_factor = min(0.1, math.log1p(token.volume_5m) * 0.02)
            base += vol_factor

        return max(0.0, min(1.0, base))

    def _auto_beliefs(self, token: TokenEntity):
        """Generate automatic beliefs from strong token signals."""
        # Strong rug signal
        if token.rug_signals >= 3:
            self.add_belief(Belief(
                content=f"Token {token.symbol} ({token.mint[:8]}) is likely a rug",
                confidence=min(0.95, 0.5 + token.rug_signals * 0.15),
                supporting_evidence=[f"rug_signals={token.rug_signals}"] + token.rug_details,
            ))

        # Smart money conviction
        if token.smart_money_in and token.score > 0.7:
            self.add_belief(Belief(
                content=f"Token {token.symbol} has smart money conviction",
                confidence=0.75,
                supporting_evidence=["smart_money_in=True", f"score={token.score}"],
            ))

        # Score deterioration
        if token.score_trend == "accelerating_down":
            self.add_belief(Belief(
                content=f"Token {token.symbol} score is deteriorating rapidly",
                confidence=0.8,
                supporting_evidence=[
                    f"velocity={token.velocity}",
                    f"acceleration={token.acceleration}",
                ],
            ))

    def get_market_summary(self) -> Dict:
        """Summary for higher cognitive levels."""
        total_tokens = len(self.tokens)
        if total_tokens == 0:
            return {
                "regime": self._market_regime,
                "token_count": 0,
                "avg_score": 0.0,
                "rug_candidates": 0,
                "smart_money_tokens": 0,
            }

        scores = [t.score for t in self.tokens.values()]
        return {
            "regime": self._market_regime,
            "token_count": total_tokens,
            "avg_score": sum(scores) / total_tokens,
            "max_score": max(scores),
            "min_score": min(scores),
            "rug_candidates": len(self.get_rug_candidates()),
            "smart_money_tokens": sum(
                1 for t in self.tokens.values() if t.smart_money_in),
            "regime_confidence": self._regime_entity.properties.get("confidence", 0.0),
            "top_attention": [
                (t.symbol, t.score, t.score_trend)
                for t in self.get_top_tokens(5)
            ],
        }

    def get_state_summary(self) -> Dict:
        """Override parent to include market data."""
        base = super().get_state_summary()
        base["market"] = self.get_market_summary()
        return base
