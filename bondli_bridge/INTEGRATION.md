# Brain — Cognitive Trading Bridge Integration Guide

## Overview

Brain is a self-correcting cognitive trading layer that implements Hofstadter's strange loop architecture for autonomous decision-making. It sits between Bondli's ML scoring pipeline and its trade execution engine, providing structured entry/exit decisions with auditable reasoning chains.

The core mechanism: a three-level cognitive hierarchy where higher levels monitor and restructure lower levels (downward causation), creating a recursive self-referential loop that adapts to changing market conditions and corrects systematic decision-making errors.

```
Bondli Scanner --> ML Scorer --> Brain Bridge --> Auto-Ape Engine --> Trade Router
                                     ^                                  |
                                     +-------- trade outcomes ----------+
                                     (recursive self-correction loop)
```

## Architecture

```
Level 2: Meta-Cognitive Oversight (TradingMetaCognitive)
  Monitors Level 1 performance. Detects cognitive biases:
  - Overconfidence (position sizing inflated vs base rate)
  - Revenge trading (rapid re-entry after losses)
  - Regime blindness (strategy-regime mismatch)
  - Loss aversion (excessive hold duration on losers)
  Applies corrective interventions via downward causation.
          |
Level 1: Strategic Reasoning (TradingSelfModel)
  Produces APE/SKIP/EXIT/HOLD decisions.
  Manages strategies: momentum, snipe, smart_follow, fade, survivor.
  Tracks position performance. Modulates Level 0 attention.
  Position sizing via half-Kelly criterion.
          |
Level 0: Market Perception (MarketWorldModel)
  Tokens, wallets, and regime as structured entities.
  Score-based attention weighting.
  Automatic belief generation from strong signals.
  Feeds observations upward to Level 1.
```

## Quick Start

### 1. Start the Brain bridge server

```bash
pip install fastapi uvicorn pydantic
python -m bondli_bridge.server
# Server starts on http://127.0.0.1:8421
```

### 2. Add to Bondli's .env

```env
# Brain Cognitive Bridge
BRAIN_BRIDGE_URL=http://127.0.0.1:8421
BRAIN_PORT=8421
BRAIN_MAX_POSITION_SOL=1.0
BRAIN_MAX_POSITIONS=5
BRAIN_MAX_EXPOSURE_SOL=5.0
BRAIN_MIN_SCORE_APE=0.65
BRAIN_RUG_SIGNAL_MAX=2
```

### 3. Integrate with Bondli's Node.js backend

Add `brain-client.mjs` to Bondli's `src/engine/` directory (see below).

## API Reference

### POST /evaluate — Token Evaluation

Evaluates a token for entry. Called by Bondli's scorer after computing ML features.

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

Evaluates an open position for exit signals. Called on each scoring cycle.

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

Called after Bondli's trade router confirms the on-chain swap.

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

Triggers meta-cognitive evaluation and strategy performance assessment.

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

### POST /smart-wallet — Ingest Smart Money Profile

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

Returns the complete state of all three cognitive levels, risk state, and decision statistics.

### GET /metrics — Cognitive and Trading Metrics

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

### brain-client.mjs

Drop this into Bondli's `src/engine/` directory:

```javascript
// src/engine/brain-client.mjs
// Brain Cognitive Bridge client for Bondli

const BRAIN_URL = process.env.BRAIN_BRIDGE_URL || 'http://127.0.0.1:8421';
const TIMEOUT = 5000;

let brainAvailable = null;

async function brainFetch(path, method = 'GET', body = null) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), TIMEOUT);

  try {
    const opts = {
      method,
      headers: { 'Content-Type': 'application/json' },
      signal: controller.signal,
    };
    if (body) opts.body = JSON.stringify(body);

    const res = await fetch(`${BRAIN_URL}${path}`, opts);
    brainAvailable = true;
    return await res.json();
  } catch (err) {
    if (brainAvailable !== false) {
      console.warn(`[Brain] Bridge unavailable: ${err.message}`);
      brainAvailable = false;
    }
    return null;
  } finally {
    clearTimeout(timeout);
  }
}

// Periodic health check to detect reconnection
setInterval(async () => {
  if (!brainAvailable) {
    try {
      const res = await fetch(`${BRAIN_URL}/health`, {
        signal: AbortSignal.timeout(2000)
      });
      if (res.ok) {
        brainAvailable = true;
        console.log('[Brain] Bridge reconnected');
      }
    } catch {}
  }
}, 30000);

/**
 * Evaluate a token through the cognitive engine.
 * Returns null if Brain is unavailable (graceful degradation).
 */
export async function evaluateToken(tokenData) {
  const result = await brainFetch('/evaluate', 'POST', tokenData);
  if (!result) return null;
  return result;
}

/**
 * Evaluate an open position for exit signals.
 */
export async function evaluatePosition(mint, tokenData) {
  return brainFetch('/position/evaluate', 'POST', { mint, ...tokenData });
}

/**
 * Record a confirmed entry after on-chain swap.
 */
export async function recordEntry(mint, symbol, priceSol, sizeSol, score, reasoning = []) {
  return brainFetch('/position/entry', 'POST', {
    mint, symbol, price_sol: priceSol, size_sol: sizeSol, score, reasoning,
  });
}

/**
 * Record a confirmed exit. Triggers meta-cognitive evaluation.
 */
export async function recordExit(mint, exitPriceSol, reason) {
  return brainFetch('/position/exit', 'POST', {
    mint, exit_price_sol: exitPriceSol, reason,
  });
}

/**
 * Record a partial exit (take profit).
 */
export async function recordPartialExit(mint, sizeSol, priceSol, reason) {
  return brainFetch('/position/partial', 'POST', {
    mint, size_sol: sizeSol, price_sol: priceSol, reason,
  });
}

/**
 * Update market regime classification.
 */
export async function updateRegime(regimeData) {
  return brainFetch('/regime', 'POST', regimeData);
}

/**
 * Ingest smart money wallet profile.
 */
export async function ingestSmartWallet(wallet, profile) {
  return brainFetch('/smart-wallet', 'POST', { wallet, ...profile });
}

/**
 * Retrieve cognitive and trading metrics.
 */
export async function getMetrics() {
  return brainFetch('/metrics');
}

/**
 * Retrieve full cognitive state (diagnostic use).
 */
export async function getState() {
  return brainFetch('/state');
}

/**
 * Update configuration at runtime.
 */
export async function updateConfig(updates) {
  return brainFetch('/config', 'POST', updates);
}

/**
 * Check if Brain bridge is available.
 */
export function isAvailable() {
  return brainAvailable === true;
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
import brain from './brain-client.mjs';

async function scoreToken(token) {
  const mlScore = await computeMLScore(token);

  const brainDecision = await brain.evaluateToken({
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

  if (brainDecision) {
    mlScore.brainAction = brainDecision.action;
    mlScore.brainConfidence = brainDecision.confidence;
    mlScore.brainReasoning = brainDecision.reasoning;
    mlScore.brainPositionSize = brainDecision.position_size_sol;
    mlScore.brainStrategy = brainDecision.strategy;
  }

  return mlScore;
}
```

#### 2. In `autoape/pipeline.js` (entry decision):

```javascript
import brain from '../engine/brain-client.mjs';

if (brain.isAvailable() && score.brainAction) {
  if (score.brainAction === 'SKIP') {
    log(`[Brain] Skipping ${token.symbol}: ${score.brainReasoning.join(', ')}`);
    return;
  }
  if (score.brainAction === 'APE') {
    positionSize = score.brainPositionSize;
  }
}

// After confirmed swap:
await brain.recordEntry(token.mint, token.symbol, entryPrice, positionSize, score.score);
```

#### 3. In `autoape/exit-plan.js` (exit evaluation):

```javascript
import brain from '../engine/brain-client.mjs';

async function evaluateExit(position, latestScore) {
  const decision = await brain.evaluatePosition(position.mint, {
    score: latestScore.score,
    velocity: latestScore.velocity,
    acceleration: latestScore.acceleration,
    rug_signals: latestScore.rugSignals,
    price_sol: position.currentPrice,
  });

  if (decision?.action === 'EXIT') {
    log(`[Brain] EXIT ${position.symbol}: ${decision.reasoning.join(', ')}`);
    return { shouldExit: true, reason: decision.reasoning[0] };
  }

  if (decision?.action === 'PARTIAL_EXIT') {
    return {
      shouldPartialExit: true,
      exitPct: decision.exit_pct,
      reason: decision.reasoning[0],
    };
  }

  return { shouldExit: false };
}

// After confirmed exit:
await brain.recordExit(position.mint, exitPrice, reason);
```

#### 4. In `regime-engine.mjs` (regime updates):

```javascript
import brain from './brain-client.mjs';

async function onRegimeChange(regime) {
  await brain.updateRegime({
    regime: regime.type,
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
import brain from './brain-client.mjs';

async function trackWallet(wallet, stats) {
  await brain.ingestSmartWallet(wallet, {
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
  brain-bridge:
    build:
      context: ../BRAD
      dockerfile: bondli_bridge/Dockerfile
    ports:
      - "8421:8421"
    environment:
      - BRAIN_PORT=8421
      - BRAIN_MAX_POSITION_SOL=1.0
      - BRAIN_MAX_POSITIONS=5
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8421/health"]
      interval: 30s
      timeout: 5s
      retries: 3
```

## Theoretical Basis

The cognitive trading architecture is grounded in three established frameworks:

1. **Strange Loop Theory** (Hofstadter, 1979) — Self-referential hierarchies where higher levels modify lower levels create emergent properties. In this implementation, the meta-cognitive layer (L2) restructures the strategic layer (L1), which modulates the perceptual layer (L0), forming a recursive causal loop.

2. **Global Workspace Theory** (Baars, 1988) — Salient cognitive events compete for broadcast attention. Self-referential events receive a configurable salience boost, ensuring the system's self-monitoring signals propagate through the architecture.

3. **Dual Process Theory** (Kahneman, 2011) — The system operates in three modes: fast pattern matching (System 1), deliberate analytical evaluation (System 2), and recursive self-referential processing (Strange Loop mode). Mode selection is context-dependent and can be overridden by meta-cognitive intervention.

## Operational Mechanisms

1. **Score derivative exit signals** — Level 1 uses velocity and acceleration of ML scores as leading indicators, detecting deterioration approximately 2 scoring cycles before price impact.
2. **Cognitive bias detection** — Level 2 identifies overconfidence, revenge trading, regime blindness, and loss aversion through pattern analysis of decision history and performance metrics.
3. **Adaptive strategy selection** — When a strategy's effectiveness falls below threshold, the meta-cognitive layer forces a switch to the best-performing alternative for the current regime.
4. **Mandatory cooldown periods** — Three or more consecutive losses trigger an automatic trading pause, requiring meta-cognitive review before resumption.
5. **Confidence calibration** — The system continuously compares stated confidence levels against realized performance, adjusting position sizing when divergence exceeds tolerance.
