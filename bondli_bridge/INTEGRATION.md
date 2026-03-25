# BRAD Cognitive Bridge — Bondli Integration Guide

## What This Is

A self-correcting cognitive layer that sits between Bondli's ML scorer and its auto-ape engine. BRAD's strange loop architecture watches its own trading performance and forces corrections before more money is lost.

```
Bondli Scanner → ML Scorer → BRAD Bridge → Auto-Ape Engine → Trade Router
                                  ↑                              |
                                  └──── trade outcomes ──────────┘
                                  (strange loop: learns from results)
```

## Architecture

```
Level 2: Trading Meta-Cognitive
  Watches Level 1's performance. Detects:
  - Overconfidence (sizing up after wins)
  - Revenge trading (aping after losses)
  - Regime blindness (wrong strategy for market)
  - Loss aversion (holding losers too long)
  Forces strategy switches and pauses (DOWNWARD CAUSATION)
          ↓
Level 1: Trading Self-Model
  Makes APE/SKIP/EXIT/HOLD decisions.
  Manages strategies: momentum, snipe, smart_follow, fade, survivor.
  Tracks position performance. Intervenes on Level 0 attention.
  (DOWNWARD CAUSATION on Level 0)
          ↓
Level 0: Market World Model
  Tokens, wallets, and regime as entities.
  Score-based attention weighting.
  Auto-generates beliefs from strong signals.
  Feeds upward to Level 1.
```

## Quick Start

### 1. Start the BRAD bridge server

```bash
cd /path/to/BRAD
pip install fastapi uvicorn pydantic
python -m bondli_bridge.server
# Server starts on http://127.0.0.1:8421
```

### 2. Add to Bondli's .env

```env
# BRAD Cognitive Bridge
BRAD_BRIDGE_URL=http://127.0.0.1:8421
BRAD_PORT=8421
BRAD_MAX_POSITION_SOL=1.0
BRAD_MAX_POSITIONS=5
BRAD_MAX_EXPOSURE_SOL=5.0
BRAD_MIN_SCORE_APE=0.65
BRAD_RUG_SIGNAL_MAX=2
```

### 3. Integrate with Bondli's Node.js backend

Add `brad-client.mjs` to Bondli's `src/engine/` directory (see below).

## API Endpoints

### POST /evaluate — Token Evaluation

Called by Bondli's scorer after computing ML features.

**Request:**
```json
{
  "mint": "TokenMintAddress",
  "name": "PEPE",
  "symbol": "PEPE",
  "source": "pump",
  "score": 0.82,
  "velocity": 0.03,
  "acceleration": 0.01,
  "rug_signals": 0,
  "rug_details": [],
  "holder_count": 150,
  "top_holder_pct": 0.12,
  "liquidity_sol": 45.0,
  "mcap_sol": 200.0,
  "volume_5m": 12.5,
  "buy_pressure": 0.72,
  "smart_money_in": true,
  "dev_wallet": "DevWalletAddress",
  "is_graduated": false,
  "price_sol": 0.00023
}
```

**Response:**
```json
{
  "action": "APE",
  "mint": "TokenMintAddress",
  "confidence": 0.847,
  "reasoning": [
    "ML score: 0.820",
    "Score above ape threshold",
    "Score velocity positive (0.0300) - improving",
    "Smart money detected in token",
    "Position size: 0.1234 SOL"
  ],
  "risk_factors": [],
  "risk_violations": [],
  "strategy": "momentum",
  "position_size_sol": 0.1234,
  "cognitive": {
    "cycle": 42,
    "strange_loops": 7,
    "strategy": "momentum",
    "paused": false,
    "regime": "bull",
    "hofstadter_index": 0.65
  },
  "timestamp": 1711324800.0
}
```

### POST /position/evaluate — Position Evaluation

Called on each scoring cycle for open positions.

**Request:**
```json
{
  "mint": "TokenMintAddress",
  "score": 0.45,
  "velocity": -0.08,
  "acceleration": -0.03,
  "rug_signals": 1,
  "price_sol": 0.00018
}
```

**Response:**
```json
{
  "action": "EXIT",
  "confidence": 0.85,
  "reasoning": [
    "Score derivatives signal exit: v=-0.0800, a=-0.0300",
    "Deterioration detected 2 cycles before price drop"
  ],
  "pnl_pct": -0.217,
  "pnl_sol": -0.0434
}
```

### POST /position/entry — Record Confirmed Entry

Called AFTER Bondli's trade router confirms the swap on-chain.

```json
{
  "mint": "TokenMintAddress",
  "symbol": "PEPE",
  "price_sol": 0.00023,
  "size_sol": 0.5,
  "score": 0.82,
  "reasoning": ["ML score: 0.82", "Smart money detected"]
}
```

### POST /position/exit — Record Confirmed Exit

Triggers meta-cognitive evaluation and strategy assessment.

```json
{
  "mint": "TokenMintAddress",
  "exit_price_sol": 0.00045,
  "reason": "take_profit"
}
```

### POST /regime — Update Market Regime

```json
{
  "regime": "bull",
  "confidence": 0.8,
  "bull_score": 0.82,
  "bear_score": 0.1,
  "chop_score": 0.08,
  "rug_frequency": 0.15,
  "avg_token_lifespan": 3600
}
```

### POST /smart-wallet — Ingest Smart Money

```json
{
  "wallet": "WalletAddress",
  "win_rate": 0.85,
  "avg_profit": 2.5,
  "total_trades": 120,
  "active_tokens": ["mint1", "mint2"]
}
```

### GET /state — Full Cognitive State

Returns the complete state of all three cognitive levels, risk state, and decision stats.

### GET /metrics — Trading + Consciousness Metrics

```json
{
  "hofstadter_index": 0.65,
  "strange_loop_count": 12,
  "total_trades": 45,
  "win_rate": 0.62,
  "total_pnl_sol": 3.45,
  "active_strategy": "momentum",
  "forced_strategy_switches": 2,
  "forced_pauses": 1,
  "performance_trend": "improving"
}
```

### GET /health — Health Check

```json
{
  "status": "healthy",
  "uptime_seconds": 3600,
  "cycle_count": 450,
  "strange_loops": 23
}
```

## Bondli Integration Code

### brad-client.mjs

Drop this into Bondli's `src/engine/` directory:

```javascript
// src/engine/brad-client.mjs
// BRAD Cognitive Bridge client for Bondli

const BRAD_URL = process.env.BRAD_BRIDGE_URL || 'http://127.0.0.1:8421';
const TIMEOUT = 5000; // 5s timeout — don't block the pipeline

let bradAvailable = null; // null = unknown, true/false = cached

async function bradFetch(path, method = 'GET', body = null) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), TIMEOUT);

  try {
    const opts = {
      method,
      headers: { 'Content-Type': 'application/json' },
      signal: controller.signal,
    };
    if (body) opts.body = JSON.stringify(body);

    const res = await fetch(`${BRAD_URL}${path}`, opts);
    bradAvailable = true;
    return await res.json();
  } catch (err) {
    if (bradAvailable !== false) {
      console.warn(`[BRAD] Bridge unavailable: ${err.message}`);
      bradAvailable = false;
    }
    return null;
  } finally {
    clearTimeout(timeout);
  }
}

// Periodic health check to detect when BRAD comes back online
setInterval(async () => {
  if (!bradAvailable) {
    try {
      const res = await fetch(`${BRAD_URL}/health`, {
        signal: AbortSignal.timeout(2000)
      });
      if (res.ok) {
        bradAvailable = true;
        console.log('[BRAD] Bridge reconnected');
      }
    } catch {}
  }
}, 30000);

/**
 * Evaluate a token through BRAD's cognitive engine.
 * Falls back gracefully if BRAD is unavailable.
 */
export async function evaluateToken(tokenData) {
  const result = await bradFetch('/evaluate', 'POST', tokenData);
  if (!result) return null; // Bondli proceeds with its own logic
  return result;
}

/**
 * Evaluate an open position.
 */
export async function evaluatePosition(mint, tokenData) {
  return bradFetch('/position/evaluate', 'POST', { mint, ...tokenData });
}

/**
 * Record a confirmed entry.
 */
export async function recordEntry(mint, symbol, priceSol, sizeSol, score, reasoning = []) {
  return bradFetch('/position/entry', 'POST', {
    mint, symbol, price_sol: priceSol, size_sol: sizeSol, score, reasoning,
  });
}

/**
 * Record a confirmed exit.
 */
export async function recordExit(mint, exitPriceSol, reason) {
  return bradFetch('/position/exit', 'POST', {
    mint, exit_price_sol: exitPriceSol, reason,
  });
}

/**
 * Record a partial exit (take profit).
 */
export async function recordPartialExit(mint, sizeSol, priceSol, reason) {
  return bradFetch('/position/partial', 'POST', {
    mint, size_sol: sizeSol, price_sol: priceSol, reason,
  });
}

/**
 * Update market regime.
 */
export async function updateRegime(regimeData) {
  return bradFetch('/regime', 'POST', regimeData);
}

/**
 * Ingest smart money wallet.
 */
export async function ingestSmartWallet(wallet, profile) {
  return bradFetch('/smart-wallet', 'POST', { wallet, ...profile });
}

/**
 * Get cognitive metrics.
 */
export async function getMetrics() {
  return bradFetch('/metrics');
}

/**
 * Get full state (for debugging).
 */
export async function getState() {
  return bradFetch('/state');
}

/**
 * Update config at runtime.
 */
export async function updateConfig(updates) {
  return bradFetch('/config', 'POST', updates);
}

/**
 * Check if BRAD bridge is available.
 */
export function isAvailable() {
  return bradAvailable === true;
}

export default {
  evaluateToken,
  evaluatePosition,
  recordEntry,
  recordExit,
  recordPartialExit,
  updateRegime,
  ingestSmartWallet,
  getMetrics,
  getState,
  updateConfig,
  isAvailable,
};
```

### Integration Points in Bondli

#### 1. In `meme-intelligence.mjs` (after scoring):

```javascript
import brad from './brad-client.mjs';

// After computing ML score for a token:
async function scoreToken(token) {
  const mlScore = await computeMLScore(token); // existing logic

  // Ask BRAD for cognitive evaluation
  const bradDecision = await brad.evaluateToken({
    mint: token.mint,
    name: token.name,
    symbol: token.symbol,
    score: mlScore.score,
    velocity: mlScore.velocity,
    acceleration: mlScore.acceleration,
    rug_signals: mlScore.rugSignals,
    rug_details: mlScore.rugDetails,
    holder_count: token.holderCount,
    top_holder_pct: token.topHolderPct,
    liquidity_sol: token.liquiditySol,
    mcap_sol: token.mcapSol,
    volume_5m: token.volume5m,
    buy_pressure: token.buyPressure,
    smart_money_in: token.smartMoneyIn,
    dev_wallet: token.devWallet,
    source: token.source,
  });

  // BRAD enhances the decision — or graceful fallback
  if (bradDecision) {
    mlScore.bradAction = bradDecision.action;
    mlScore.bradConfidence = bradDecision.confidence;
    mlScore.bradReasoning = bradDecision.reasoning;
    mlScore.bradPositionSize = bradDecision.position_size_sol;
    mlScore.bradStrategy = bradDecision.strategy;
  }

  return mlScore;
}
```

#### 2. In `autoape/pipeline.js` (entry decision):

```javascript
import brad from '../engine/brad-client.mjs';

// In the entry decision logic:
if (brad.isAvailable() && score.bradAction) {
  if (score.bradAction === 'SKIP') {
    log(`[BRAD] Skipping ${token.symbol}: ${score.bradReasoning.join(', ')}`);
    return; // BRAD says no
  }
  if (score.bradAction === 'APE') {
    // Use BRAD's position size
    positionSize = score.bradPositionSize;
  }
}

// After confirmed swap:
await brad.recordEntry(token.mint, token.symbol, entryPrice, positionSize, score.score);
```

#### 3. In `autoape/exit-plan.js` (exit evaluation):

```javascript
import brad from '../engine/brad-client.mjs';

// On each scoring cycle for open positions:
async function evaluateExit(position, latestScore) {
  const bradDecision = await brad.evaluatePosition(position.mint, {
    score: latestScore.score,
    velocity: latestScore.velocity,
    acceleration: latestScore.acceleration,
    rug_signals: latestScore.rugSignals,
    price_sol: position.currentPrice,
  });

  if (bradDecision?.action === 'EXIT') {
    log(`[BRAD] EXIT signal for ${position.symbol}: ${bradDecision.reasoning.join(', ')}`);
    return { shouldExit: true, reason: bradDecision.reasoning[0] };
  }

  if (bradDecision?.action === 'PARTIAL_EXIT') {
    return {
      shouldPartialExit: true,
      exitPct: bradDecision.exit_pct,
      reason: bradDecision.reasoning[0],
    };
  }

  return { shouldExit: false };
}

// After confirmed exit:
await brad.recordExit(position.mint, exitPrice, reason);
```

#### 4. In `regime-engine.mjs` (regime updates):

```javascript
import brad from './brad-client.mjs';

// When regime changes:
async function updateRegime(regime) {
  await brad.updateRegime({
    regime: regime.type,        // bull, bear, chop
    confidence: regime.confidence,
    bull_score: regime.bullScore,
    bear_score: regime.bearScore,
    chop_score: regime.chopScore,
    rug_frequency: regime.rugFrequency,
    avg_token_lifespan: regime.avgLifespan,
  });
}
```

#### 5. In `smart-money-tracker.mjs`:

```javascript
import brad from './brad-client.mjs';

// When a profitable wallet is identified:
async function trackWallet(wallet, stats) {
  await brad.ingestSmartWallet(wallet, {
    win_rate: stats.winRate,
    avg_profit: stats.avgProfit,
    total_trades: stats.totalTrades,
    active_tokens: stats.activeTokens,
  });
}
```

## Docker Deployment

Add to Bondli's `docker-compose.yml`:

```yaml
  brad-bridge:
    build:
      context: ../BRAD
      dockerfile: bondli_bridge/Dockerfile
    ports:
      - "8421:8421"
    environment:
      - BRAD_PORT=8421
      - BRAD_MAX_POSITION_SOL=1.0
      - BRAD_MAX_POSITIONS=5
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8421/health"]
      interval: 30s
      timeout: 5s
      retries: 3
```

## How the Strange Loop Helps Trading

1. **Score derivatives fire first** — BRAD's exit Layer 1 uses velocity + acceleration before price drops
2. **Meta-cognitive catches bad patterns** — Overconfidence, revenge trading, regime blindness detected and corrected
3. **Automatic strategy switching** — When momentum stops working, meta-cognitive forces switch to snipe/survivor
4. **Forced pauses** — 3+ consecutive losses triggers mandatory cooldown
5. **Self-correcting risk** — Confidence calibration adjusts position sizing based on actual vs expected performance

The system literally watches itself trade and restructures its own decision-making. That's the strange loop.
