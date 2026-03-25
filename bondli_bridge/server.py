"""
server.py — FastAPI server for the Brain cognitive trading bridge.

Provides the HTTP interface between Bondli's Node.js backend and the
three-level cognitive trading engine. All endpoints are stateless from
the caller's perspective; internal state is maintained by the engine.

Start:
    python -m bondli_bridge.server
    uvicorn bondli_bridge.server:app --host 127.0.0.1 --port 8421

Connection:
    BRAIN_BRIDGE_URL=http://127.0.0.1:8421

Endpoints:
    POST /evaluate          — Evaluate token for entry (APE/SKIP/WATCH)
    POST /position/evaluate — Evaluate open position (EXIT/HOLD/PARTIAL_EXIT)
    POST /position/entry    — Record confirmed entry
    POST /position/exit     — Record confirmed exit
    POST /position/partial  — Record partial exit
    POST /regime            — Update market regime classification
    POST /smart-wallet      — Ingest smart money wallet profile
    POST /config            — Update configuration at runtime
    GET  /state             — Full cognitive state inspection
    GET  /metrics           — Cognitive and trading performance metrics
    GET  /config            — Current configuration
    GET  /decisions         — Recent decision log
    GET  /decisions/:mint   — Decision history for specific token
    GET  /health            — Health check
"""

import sys
import os

# Add project root to path so core/ is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
import uvicorn
import time
import logging

from .engine import TradingEngine
from .config import BridgeConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bondli_bridge")

# ================================================================
# CONFIG & ENGINE
# ================================================================

config = BridgeConfig.from_env()
engine = TradingEngine(config)

# ================================================================
# APP
# ================================================================

app = FastAPI(
    title="Brain — Cognitive Trading Bridge for Bondli",
    description="Recursive self-referential trading intelligence layer",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Bondli backend is on the same machine
    allow_methods=["*"],
    allow_headers=["*"],
)


# ================================================================
# REQUEST MODELS
# ================================================================

class TokenEvalRequest(BaseModel):
    """Token data from Bondli's scorer."""
    mint: str
    name: str = ""
    symbol: str = ""
    source: str = "pump"
    score: float = 0.0
    velocity: float = 0.0
    acceleration: float = 0.0
    rug_signals: int = 0
    rug_details: List[str] = Field(default_factory=list)
    holder_count: int = 0
    top_holder_pct: float = 0.0
    liquidity_sol: float = 0.0
    mcap_sol: float = 0.0
    volume_5m: float = 0.0
    buy_pressure: float = 0.5
    smart_money_in: bool = False
    dev_wallet: str = ""
    is_graduated: bool = False
    price_sol: float = 0.0


class PositionEvalRequest(BaseModel):
    """Position update from Bondli."""
    mint: str
    score: float = 0.0
    velocity: float = 0.0
    acceleration: float = 0.0
    rug_signals: int = 0
    rug_details: List[str] = Field(default_factory=list)
    price_sol: float = 0.0
    liquidity_sol: float = 0.0


class EntryRecord(BaseModel):
    """Record a confirmed entry from Bondli's trade router."""
    mint: str
    symbol: str = ""
    price_sol: float
    size_sol: float
    score: float = 0.0
    reasoning: List[str] = Field(default_factory=list)


class ExitRecord(BaseModel):
    """Record a confirmed exit."""
    mint: str
    exit_price_sol: float
    reason: str = ""


class PartialExitRecord(BaseModel):
    """Record a partial exit."""
    mint: str
    size_sol: float
    price_sol: float
    reason: str = ""


class RegimeUpdate(BaseModel):
    """Market regime from Bondli's regime engine."""
    regime: str  # bull, bear, chop, unknown
    confidence: float = 0.5
    bull_score: float = 0.0
    bear_score: float = 0.0
    chop_score: float = 0.0
    rug_frequency: float = 0.0
    avg_token_lifespan: float = 0.0


class SmartWalletData(BaseModel):
    """Smart money wallet profile."""
    wallet: str
    win_rate: float = 0.0
    avg_profit: float = 0.0
    total_trades: int = 0
    active_tokens: List[str] = Field(default_factory=list)


class ConfigUpdate(BaseModel):
    """Runtime config update."""
    risk: Optional[Dict] = None
    scoring: Optional[Dict] = None
    strategy: Optional[Dict] = None


# ================================================================
# ENDPOINTS
# ================================================================

@app.post("/evaluate")
async def evaluate_token(req: TokenEvalRequest):
    """
    Evaluate a token for APE/SKIP/WATCH.

    This is the main integration point. Bondli's scorer calls this
    after computing ML scores for a token.

    Returns:
        action: APE | SKIP | WATCH
        confidence: 0-1
        reasoning: [str] — why this decision
        position_size_sol: float (if APE)
        risk_factors: [str]
        risk_violations: [dict]
        cognitive: {cycle, strange_loops, strategy, regime}
    """
    try:
        decision = engine.evaluate_token(req.model_dump())
        return decision.to_dict()
    except Exception as e:
        logger.error(f"evaluate_token error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/position/evaluate")
async def evaluate_position(req: PositionEvalRequest):
    """
    Evaluate an open position for EXIT/HOLD/PARTIAL_EXIT.

    Bondli calls this on each scoring cycle for every open position.

    Returns:
        action: EXIT | HOLD | PARTIAL_EXIT
        confidence: 0-1
        reasoning: [str]
        pnl_pct: float
        pnl_sol: float
        exit_pct: float (if PARTIAL_EXIT)
    """
    try:
        decision = engine.evaluate_position(req.mint, req.model_dump())
        return decision.to_dict()
    except Exception as e:
        logger.error(f"evaluate_position error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/position/entry")
async def record_entry(req: EntryRecord):
    """
    Record that Bondli executed an entry.
    Called AFTER the swap is confirmed on-chain.
    """
    try:
        engine.record_entry(
            mint=req.mint,
            symbol=req.symbol,
            price_sol=req.price_sol,
            size_sol=req.size_sol,
            score=req.score,
            reasoning=req.reasoning,
        )
        return {"status": "recorded", "mint": req.mint}
    except Exception as e:
        logger.error(f"record_entry error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/position/exit")
async def record_exit(req: ExitRecord):
    """
    Record that Bondli executed an exit.
    Triggers meta-cognitive evaluation and strategy assessment.
    """
    try:
        result = engine.record_exit(
            mint=req.mint,
            exit_price_sol=req.exit_price_sol,
            reason=req.reason,
        )
        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"No open position for {req.mint}")
        return {"status": "recorded", "trade": result}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"record_exit error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/position/partial")
async def record_partial_exit(req: PartialExitRecord):
    """Record a partial exit (take profit)."""
    try:
        engine.record_partial_exit(
            mint=req.mint,
            size_sol=req.size_sol,
            price_sol=req.price_sol,
            reason=req.reason,
        )
        return {"status": "recorded", "mint": req.mint}
    except Exception as e:
        logger.error(f"record_partial_exit error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/regime")
async def update_regime(req: RegimeUpdate):
    """
    Update market regime from Bondli's regime engine.
    Affects strategy selection and position sizing.
    """
    try:
        engine.update_regime(req.model_dump())
        return {
            "status": "updated",
            "regime": req.regime,
            "confidence": req.confidence,
        }
    except Exception as e:
        logger.error(f"update_regime error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/smart-wallet")
async def ingest_smart_wallet(req: SmartWalletData):
    """Ingest smart money wallet profile."""
    try:
        engine.ingest_smart_wallet(req.wallet, req.model_dump())
        return {"status": "ingested", "wallet": req.wallet[:8]}
    except Exception as e:
        logger.error(f"smart_wallet error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/state")
async def get_state():
    """Full cognitive state — for debugging and monitoring."""
    return engine.get_state()


@app.get("/metrics")
async def get_metrics():
    """Consciousness + trading metrics combined."""
    return engine.get_metrics()


@app.get("/config")
async def get_config():
    """Current configuration."""
    return engine.get_config()


@app.post("/config")
async def update_config(req: ConfigUpdate):
    """Update configuration at runtime."""
    try:
        updates = {}
        if req.risk:
            updates["risk"] = req.risk
        if req.scoring:
            updates["scoring"] = req.scoring
        if req.strategy:
            updates["strategy"] = req.strategy
        engine.update_config(updates)
        return {"status": "updated", "config": engine.get_config()}
    except Exception as e:
        logger.error(f"update_config error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/decisions")
async def get_decisions(n: int = 20):
    """Recent decision log."""
    return {
        "decisions": engine.decision_log.get_recent(n),
        "stats": engine.decision_log.get_stats(),
    }


@app.get("/decisions/{mint}")
async def get_decisions_for_mint(mint: str):
    """Decisions for a specific token."""
    return {
        "mint": mint,
        "decisions": engine.decision_log.get_decisions_for_mint(mint),
    }


@app.get("/health")
async def health():
    """Health check for Docker/monitoring."""
    return {
        "status": "healthy",
        "uptime_seconds": time.time() - engine._started_at,
        "cycle_count": engine.cycle_count,
        "strange_loops": engine.total_strange_loops,
        "version": "1.0.0",
    }


# ================================================================
# MAIN
# ================================================================

def main():
    """Entry point for running the server."""
    uvicorn.run(
        "bondli_bridge.server:app",
        host=config.host,
        port=config.port,
        reload=config.debug,
        log_level="info",
    )


if __name__ == "__main__":
    main()
