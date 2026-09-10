# VELOCITY TRADER: one-shot build prompt

Paste this entire file as the first message to a coding agent that has the
`bondli` and `BRAD` repositories checked out side by side. It carries the
method first, then the design already worked through the method, then the
build order. The agent presents the design and stops, unless the last line of
this file says `APPROVED`.

Mission in one sentence: grow a fixed pool of capital autonomously across
several venues, with a worst case declared in a config file before the first
trade and that the bot cannot change at runtime. "Violently fast" means
signal-to-fill latency is bounded and measured per venue. "Accurate" means the
bot rejects almost everything and acts only where expected value after all
costs is positive at a stated confidence. Profit is the outcome of
edge x speed x survival, in that priority order. The design never trades
survival for speed.

---

## Part A. The method (sacred, verbatim)

Before you write any code, do this:

1. List the functional requirements. State what the system must do as
   outcomes, not as implementation. Number them FR1, FR2, and so on.
2. List the design parameters. State the specific modules, functions, or
   data structures that satisfy each FR. Number them DP1, DP2, and so on.
3. Build the design matrix. For each FR and DP pair, mark X if changing
   that DP changes that FR. Show me the matrix.
4. If the matrix is not diagonal or triangular, revise the DPs until it
   is. Tell me what you changed and why. Do not continue with a coupled
   design.
5. Choose the DP set with the least information content. If two designs
   satisfy the same FRs, take the one with fewer moving parts and fewer
   assumptions. Say why the one you picked is the simpler one.
6. For every interactive element, state the affordance, the signifier,
   the feedback on success, the feedback on failure, and the recovery
   path. Include the empty state, the loading state, and the partial
   state.
7. Stop here. Show me all of the above. Do not write code until I
   approve it.

Parts B through L are the answer to steps 1 through 6, already worked. Your
job is to re-derive them against the code you actually find in the two
repositories, correct anything that the code contradicts, present the result,
and then stop at Part M.

---

## Part B. Givens

Assumptions:

- A1. Edge exists only where the bot has information or speed the counterparty
  lacks. On pump.fun that is rug and holder forensics plus the bondli scorer.
  On Polymarket it is resolution latency (the fact is known, the price is not
  yet 0 or 1) and cross-market consistency (mutually exclusive outcomes whose
  prices do not sum to 1). On perpetual futures it is funding and basis, which
  is slow and is out of scope for the first release.
- A2. pump.fun returns are power-law, not Gaussian. Kelly must be fractional
  (quarter-Kelly, as bondli already uses). Polymarket payoffs are bounded in
  [0, 1] per share, so half-Kelly is safe there.
- A3. The bot's own behavior is a source of error: overconfidence, revenge
  entries, regime blindness, loss aversion, recency, concentration. This is
  BRAD's premise and it holds for code as much as for people.
- A4. Each venue fails differently. pump.fun: rug, exit liquidity, dev dump.
  Polymarket: thin books, leg risk on multi-outcome trades, resolution
  disputes through the UMA oracle. Perps: liquidation and funding flips.
- A5. The operator is absent. Every failure must degrade to "flat and halted"
  or "frozen with exits still running", never to "stuck in a position with
  nobody watching".
- A6. No LLM sits in the hot path. Decisions must be deterministic and
  replayable from the event log. An LLM may narrate state (as brad-mind.mjs
  does today) but may not decide, size, or execute.
- A7. Everything in the two repositories is reusable, but only the parts
  that satisfy an FR below are in scope.
- A8. Speed and accuracy are independent only if the code that makes them is
  independent. The reader of market data and the writer of orders are
  therefore separate modules with no shared state.

Constraints:

- C1. No market manipulation. No wash trading, no coordinated fleet wallets
  posing as retail, no spoofing, no "anti-detection". bondli's
  GAME_THEORY.md phases, fleet-trader.mjs, fleet-brains.mjs,
  anti-detection.mjs and the wash-volume parts of orchestrator.mjs are out of
  scope and must not be imported.
- C2. The operator verifies venue eligibility for their jurisdiction before
  enabling any venue. The bot never circumvents geo or KYC controls.
- C3. The risk envelope (per-trade cap, per-venue cap, portfolio cap, daily
  loss limit, max concurrent, max per correlated group) is read once at start
  from a file the process cannot write. No code path raises a cap.
- C4. Every venue starts in paper mode. Live is enabled per venue only by the
  operator, and only after the promotion gate in Part K passes.
- C5. Venue-specific code lives only in a feed adapter, an edge model, and an
  order router. Sizing, exit, ledger, governor, learner and supervisor are
  venue-agnostic.
- C6. Runtime is the existing stack: Node core (bondli) with the BRAD Python
  bridge as a sidecar over HTTP (bondli_bridge/server.py). No port to a new
  language.
- C7. All fees, tips, spreads and slippage are read from the venue at runtime
  or measured from fills, never hardcoded, and are subtracted before any
  expected-value comparison.
- C8. Every decision, including every rejection, is written with its reason
  before the next action is taken.

---

## Part C. Functional requirements (outcomes)

- FR1 Observe. Every tradable state change on an enabled venue reaches the
  decision layer as one normalized event within a per-venue bound T_obs, with
  both the venue timestamp and the observed timestamp on the event.
- FR2 Decide. For every opportunity the output is GO with (p_win, payoff,
  confidence, tier) or REJECT with the gate that killed it and the reason. GO
  is emitted only when expected value after all costs is positive at the
  stated confidence. Precision beats recall: an unexplained REJECT is
  acceptable, an unexplained GO is a defect.
- FR3 Size. For every GO the stake is chosen so that no cap in the risk
  envelope can be exceeded even if every open position hits its stop
  simultaneously. Stake may be zero. Nothing at runtime can raise a cap.
- FR4 Execute. A sized GO becomes a verified fill within T_exec and within the
  slippage cap, or becomes NO-TRADE with nothing at risk. Multi-leg trades
  never leave a partial leg open longer than T_unwind.
- FR5 Exit. Every position has, from the instant of entry, a plan (targets,
  stop, max hold, health rule) that closes it without operator action, and
  the plan fires within T_exit of its trigger.
- FR6 Record and expose. Every decision, order, fill, exit and outcome is
  persisted with reasons before the next action, and the operator can see
  holdings, PnL, throttle, regime, feed health and recent decisions, and can
  halt the bot with one action.
- FR7 Govern. Degradation of decision quality (losing streak, confidence gap,
  regime shift, concentration, revenge pattern, tilt) is detected from the
  ledger and becomes a throttle in [0, 1] or a halt before the daily loss
  limit is reached. A throttle can only reduce activity.
- FR8 Learn. Ranking quality improves from realized outcomes without
  changing any kill gate and without flipping a sacred prior. Every weight
  change is bounded, versioned and reversible.
- FR9 Survive. After any crash, disconnect or venue outage the bot reaches a
  known state (positions reconciled with the venue, then adopted or
  flattened) before taking new risk. A stale feed or dead router stops new
  entries while exits keep running.

---

## Part D. Design parameters (modules)

- DP1 Feed adapters, read-only, one per venue, all emitting the same
  `MarketEvent {venue, kind, id, payload, t_venue, t_observed}`.
  pump.fun: PumpPortal WebSocket plus RPC, reusing bondli
  `src/engine/price-feeds.mjs`, `alchemy-client.mjs` and the radar in
  `server.production.mjs`. Polymarket: CLOB market WebSocket for books and
  trades, Gamma REST for market metadata and negative-risk groups, plus one
  resolution-fact source per market category named in that market's rules.
  Perps: Hyperliquid WebSocket, present as a stub, disabled.
- DP2 Decision pipeline: a venue-agnostic gate runner plus one edge model per
  venue. Gates run cheapest first and every gate is a kill gate: Gate 0
  governor veto, Gate 1 hard disqualifiers, Gate 2 viability floors, Gate 3
  tier classification, Gate 4 execution window (signal freshness). Output is
  `Decision {action: GO|REJECT, p_win, payoff, confidence, tier, gate,
  reasons[]}`. The pipeline never consults the risk envelope; that is DP3's
  job. pump.fun edge model reuses bondli `src/autoape/pipeline.js` and
  `gates/*.js`, `rug-scanner.mjs`, `exit-liquidity-detector.mjs`,
  `survivorship-bias.mjs`, `smart-money-tracker.mjs`, `meme-intelligence.mjs`.
  Polymarket edge models are specified in Part J.
- DP3 Risk envelope plus fractional-Kelly sizer. Immutable `risk.json` read
  at boot. Quarter-Kelly on power-law venues, half-Kelly on bounded venues,
  multiplied by the governor's throttle, then clipped by every cap. Reuses
  `calcPositionSize` in bondli `server.production.mjs`,
  `src/autoape/sizing.js`, and BRAD `bondli_bridge/risk.py` RiskManager
  (max position, max exposure, max concurrent, max drawdown, daily PnL).
- DP4 Order routers, write-only, one per venue, each with a latency budget,
  a slippage cap and fill verification. Solana: bondli
  `src/engine/rpc-enhanced.mjs` smartSend (RPC and Jito raced, p75 priority
  fee clamped to 5k to 100k microlamports, skipPreflight) through
  `pumpfun-client.mjs` and `raydium-client.mjs`. Polymarket: signed CLOB
  orders, FOK for single-leg, all legs IOC with automatic unwind of any
  filled leg when another leg fails. Perps: IOC only, stub, disabled.
- DP5 Exit plan and position monitor. Plan is a pure function of (venue,
  tier) from a static table, attached at entry. Monitor evaluates on every
  tick in fixed order: Layer 1 score derivatives, sell-into-volume,
  graduation, Layer 3 trailing, Layer 2 absolute thresholds, from bondli
  `src/autoape/exit-plan.js`, plus `position-health.mjs` grades A to F.
  Polymarket: hold-to-redeem for resolved-fact trades, target and stop and
  max-hold for the rest. Exits execute through DP4.
- DP6 State store, append-only ledger, status endpoint and kill switch.
  One atomically written JSON snapshot for live state (fewer parts than
  Redis, same FR), an append-only JSONL ledger for
  decisions, orders, fills, exits and outcomes with reasons, a `/status`
  endpoint and page, and a `/halt` endpoint with `freeze` and `flatten`
  modes. Decision log shape follows BRAD `DecisionLog`.
- DP7 Meta-governor, reads the ledger only, writes `throttle` and `halt`.
  BRAD `bondli_bridge/trading_meta.py` blind spots (overconfidence,
  revenge_trading, regime_blindness, winner_bias, loss_aversion,
  recency_bias, concentration_risk), bondli `tilt-detector.mjs` levels 1 to 4,
  bondli `regime-engine.mjs` (EUPHORIA, RISK_ON, GRINDING, PVP, DEAD) mapped
  to a per-regime activity multiplier.
- DP8 Bounded learner, batch, offline. bondli
  `src/scoring/memetic/learning-pipeline.js` (permutation importance, 20
  percent blend rate, WEIGHT_CONSTRAINTS, SACRED_INVERSIONS) and
  `survivorship-bias.mjs` archetypes. Writes only the ranking weight vector
  that DP2's tier classifier reads. Gate code is checksummed and the learner
  cannot touch it. Every weight version is kept and can be rolled back.
- DP9 Supervisor, reconciliation and dead-man. Process manager restart (BRAD
  ships `ouroboros-bot.service`), startup reconciliation (venue positions vs
  ledger: adopt with the default exit plan or flatten), feed-staleness
  watchdog that blocks Gate 4 when a feed is older than its bound, router
  health probe that blocks new entries but not exits, and a dead-man alert
  if no heartbeat is written for N minutes.

---

## Part E. Design matrix

Rows are FRs, columns are DPs. X means changing that DP changes that FR.

```
            DP1  DP2  DP3  DP4  DP5  DP6  DP7  DP8  DP9
            feed dec  risk rout exit ledg gov  lrn  sup
FR1 observe  X    .    .    .    .    .    .    .    .
FR2 decide   .    X    .    .    .    .    .    .    .
FR3 size     .    .    X    .    .    .    .    .    .
FR4 execute  .    .    .    X    .    .    .    .    .
FR5 exit     X    .    .    X    X    .    .    .    .
FR6 record   .    .    .    .    .    X    .    .    .
FR7 govern   .    .    .    .    .    X    X    .    .
FR8 learn    .    X    .    .    .    X    .    X    .
FR9 survive  .    .    .    X    .    X    .    .    X
```

The matrix is lower triangular, so the design is decoupled: set the DPs in
numerical order and each FR is satisfied without revisiting an earlier one.
Off-diagonal entries and why they are acceptable:

- FR5 on DP1 and DP4: an exit can only fire as fast as the feed shows the
  trigger and the router fills the close. Both are designed before DP5.
- FR7 on DP6: the governor reads the ledger schema. DP6 is designed first.
- FR8 on DP2 and DP6: the learner reads outcomes from the ledger and writes
  the one weight vector DP2 exposes. Both are designed first.
- FR9 on DP4 and DP6: reconciliation flattens through the router and
  persists through the store. Both are designed first.

Runtime inputs that are not design couplings: the governor's throttle value
flows into the sizer as data, and the learner's weight vector flows into the
tier classifier as data. Changing how the governor or learner is built cannot
violate FR3 or FR2 because the caps and the kill gates are not theirs to
touch.

---

## Part F. Decoupling revisions (what changed and why)

The first-cut design was coupled in five places. Each was fixed by moving a
responsibility, not by adding a module.

1. Speed vs accuracy. A single "trading engine" observed, decided and sent.
   Latency work then touched decision code. Fix: split every venue into a
   read-only feed (DP1) and a write-only router (DP4) with no shared state,
   so the decision pipeline (DP2) is the only thing between them.
2. Governor vs sizer. BRAD's L2 restructures L1 by rewriting sizing
   parameters, which is a two-way loop between DP7 and DP3. Fix: the
   governor emits one scalar throttle and one halt flag, the sizer consumes
   them as inputs, and the caps live in an immutable file. The governor can
   shrink and stop, never grow.
3. Learner vs decision. Retraining the whole scorer meant a bad learner
   could break precision. Fix: kill gates are not learnable and are
   checksummed; the learner adjusts only the ranking weights inside bounds,
   with bondli's sacred inversions enforced (this is the WEIGHT_CONSTRAINTS
   and SACRED_INVERSIONS pattern, promoted to a design rule).
4. Exit vs entry. The entry decision computed expected value from the exit
   plan's targets while the exit plan adapted to the entry tier, a circle.
   Fix: the exit plan is a static function of (venue, tier), and the entry's
   payoff estimate comes from the ledger's realized payoff for that
   (venue, tier), not from the plan's targets.
5. Portfolio gate vs sizer. bondli's Gate 4 checks portfolio limits inside
   the decision pipeline using a preliminary size, so risk logic lived in two
   places. Fix: the pipeline judges edge only; the sizer applies every cap
   and may return zero. Both outcomes are logged with reasons, so nothing
   the operator could see today is lost.

Also removed as a coupling: "all financial markets" as a requirement. It is
now constraint C5 (venue code confined to feed, edge model, router). Adding a
venue is three files and no change to DP3, DP5 to DP9.

---

## Part G. Information axiom (why this set)

Three alternatives satisfy the same FRs.

- A. One bot per venue (bondli auto-ape as is, a separate Polymarket bot, a
  separate perps bot). Three copies of sizing, exit, ledger, governor and
  supervisor, and no single daily loss limit across venues, which means FR3
  cannot actually be guaranteed. More parts, weaker guarantee. Rejected.
- B. One venue-agnostic core (DP3, DP5 to DP9) with thin per-venue feed,
  edge model and router. One risk file, one ledger, one governor. Chosen.
- C. LLM in the loop for decisions (as brad-mind.mjs does for narration).
  Non-deterministic, 1 to 10 second latency, unbounded failure modes, not
  replayable. Highest information content of the three. Rejected for the
  hot path; allowed only as read-only narration of the ledger.

Venue scope for the first release, by the same axiom: pump.fun and
Polymarket only. pump.fun because the scorer, gates, router and exits
already exist in bondli, so the probability the system works as designed is
highest there. Polymarket because its two edge mechanisms are structural and
checkable from the order book and a fact source, not from a model. Perps and
equities get adapter stubs and stay disabled; enabling one later costs a feed,
an edge model and a router, nothing else.

Stack by the same axiom: keep Node core plus BRAD Python sidecar over HTTP,
which already exists in `bondli_bridge/server.py` and `brad-client.mjs`.
A port to one language would be cleaner on paper and cost more than the
whole first release.

---

## Part H. Interaction design (Norman)

Nine interactive elements. For each: affordance, signifier, success feedback,
failure feedback, recovery, and the empty, loading and partial states.

E1 `risk.json` (the only place capital and caps are set)
- Affordance: edit numbers. Signifier: a commented template with every cap,
  its unit, and a worked example, plus a `validate` command.
- Success: `validate` prints each cap and the implied worst day in currency.
  Failure: names the field and the rule it broke, refuses to start.
- Recovery: fix the field and run `validate` again; the previous good file is
  kept as `risk.json.last-good`.
- Empty: no file means `start` refuses and prints the template path.
  Loading: none. Partial: missing optional caps take the printed defaults;
  a missing required cap is a failure.

E2 Venue mode switch (`venue <name> off|paper|live`)
- Affordance: three states per venue. Signifier: `status` shows each venue
  with its mode, its paper record and whether the promotion gate is met.
- Success: prints the new mode and, for `live`, the starting live cap.
  Failure: `live` is refused with the unmet gate criteria listed.
- Recovery: keep running paper; the criteria update on every trade.
- Empty: no venues enabled means the bot idles and `status` says so.
  Loading: switching to `live` waits for the feed to be fresh and says
  "waiting for feed". Partial: `live` with a stale router falls back to
  `paper` and alerts.

E3 `start`
- Affordance: one command. Signifier: prints the plan: venues, modes, caps,
  and the reconciliation result, then "running".
- Success: heartbeat file written every 10 seconds, first `status` line
  printed. Failure: exit code and the one failing precondition (risk file,
  feed, router, reconciliation).
- Recovery: fix, run `start` again; nothing is at risk until "running".
- Empty: no positions and no venues yields "idle". Loading: "connecting to
  feeds" with a per-venue spinner and a timeout. Partial: one feed down
  starts the rest and marks the down venue `degraded`.

E4 `halt` (kill switch, also `POST /halt`)
- Affordance: one action, two modes: `freeze` (no new entries, exits still
  run) and `flatten` (close everything now). Signifier: the two modes are
  the only two arguments and `status` shows the current halt state in red.
- Success: prints the mode, then for `flatten` a line per position with the
  fill or the failure. Failure: any position that could not be closed is
  listed with the venue error and retried on a backoff schedule.
- Recovery: `resume` requires the operator to type the venue name; a halt is
  never lifted automatically.
- Empty: no positions means "frozen, nothing to flatten". Loading: "closing
  3 of 5" progress. Partial: closed positions are listed as done, unclosed as
  retrying, and the alert repeats until zero remain.

E5 `status` (CLI and one web page)
- Affordance: read. Signifier: one screen: mode per venue, positions with
  unrealized PnL and their exit plan, day PnL vs the daily limit as a bar,
  throttle, regime, feed age per venue, last 10 decisions with reasons.
- Success: renders within 1 second from the store. Failure: a stale-store
  banner with the age of the data.
- Recovery: the page keeps the last good snapshot and marks it stale.
- Empty: "no positions, no decisions yet" with the time the bot started.
  Loading: skeleton rows. Partial: a venue with no feed shows "no data" in
  its column and does not blank the others.

E6 `why <decision-id>` (decision log)
- Affordance: look up any GO or REJECT. Signifier: every decision line in
  `status` ends with its id.
- Success: prints the gate sequence, each gate's inputs and verdict, the
  size computation and the exit plan. Failure: "unknown id" with the nearest
  ids by time.
- Recovery: `why last` and `why <venue> last`.
- Empty: nothing logged yet. Loading: none. Partial: a decision recorded
  before a crash shows which stage it reached.

E7 `promote <venue>` (paper to live gate)
- Affordance: request live. Signifier: `status` shows the gate as a checklist
  with each criterion green or red.
- Success: mode becomes `live` at the starting cap and an alert is sent.
  Failure: the red criteria are printed; nothing changes.
- Recovery: keep trading paper; run `promote` again later.
- Empty: fewer than the minimum paper trades shows "N of M trades".
  Loading: none. Partial: expectancy positive but interval crossing zero
  shows "positive, not yet significant".

E8 Automatic restart and reconciliation
- Affordance: none required; the supervisor restarts the process.
  Signifier: an alert and a `status` banner "reconciled at <time>".
- Success: every venue position matches the ledger, adopted positions carry
  a default exit plan. Failure: a mismatch that cannot be adopted is
  flattened and reported, and the bot starts frozen.
- Recovery: operator reads the report and runs `resume <venue>`.
- Empty: no positions to reconcile means "clean start". Loading: "reconciling
  <venue>" per venue. Partial: one venue unreachable stays frozen while the
  others run.

E9 Alerts (push or Telegram)
- Affordance: read on a phone, act with one link. Signifier: every alert
  ends with a `halt freeze` link and a `status` link.
- Success: the alert reads "sent" in the ledger. Failure: delivery failure is
  logged and retried three times, then written to the status banner.
- Recovery: the status page shows every alert of the last 24 hours.
- Empty: none. Loading: none. Partial: a halt link tapped twice is
  idempotent and reports the existing halt.

---

## Part J. Venue edge models (DP2 plugins)

pump.fun (fast side)
- Signals: bondli scorer (40+ features), score velocity and acceleration,
  rug scanner (12+ signals, 3 or more moderate signals rejects), exit
  liquidity detector (who is selling into the buy), survivorship score
  (cosine similarity to the survivor archetype minus half the dead
  archetype), smart-money entries, dev wallet history.
- Gates: bondli's existing Gate 1 disqualifiers (serial rugger, dev
  self-pump, freeze authority, concentration, botted volume, curve over 80
  percent, too old) and Gate 2 floors (score, unique buyers, buy/sell ratio,
  curve SOL, sybil, structural diversity), then tiers GOD_CANDLE, STRONG,
  SPECULATIVE, WATCHLIST.
- Latency budget: observe 500 ms, decide 30 ms, send 150 ms, confirm one
  to two slots. Every stage measured and shown in `status`.
- Costs subtracted: priority fee, Jito tip, curve slippage, platform fee.

Polymarket (accurate side)
- Edge model 1, resolved fact: the market's rules name a source; that source
  says the event is decided; the winning side's best ask is below
  1 minus fees minus a margin. Buy, hold to redemption. Reject if the rules
  text and the fact source do not match exactly, or if the market is inside
  a dispute window.
- Edge model 2, consistency: for a mutually exclusive, exhaustive group
  (negative-risk event), if the sum of best asks on YES is below 1 minus
  fees minus a margin, buy every leg; if the sum of best bids is above 1
  plus fees plus a margin, sell every leg or buy every NO. All legs IOC,
  any leg unfilled unwinds the rest within T_unwind.
- Edge model 3, stale quote: only after models 1 and 2 have passed the
  promotion gate; off by default.
- Latency budget: observe 250 ms (book), 2 s (fact), decide 20 ms, send
  200 ms, fill confirmation from the CLOB.
- Costs subtracted: taker fee read per market from the API, spread, gas for
  redemption.

Perps and equities: adapter stubs only, `enabled: false`.

---

## Part K. Build order, acceptance tests, promotion gates

Build in DP order. Each step ends with its test green before the next starts.

1. DP6 store and ledger (everything else writes to it). Test T6: kill the
   process between "order sent" and "fill recorded"; on restart the ledger
   shows the stage reached.
2. DP1 feeds. Test T1: p95 of (t_observed minus t_venue) within T_obs per
   venue over a one-hour capture.
3. DP2 pipeline and edge models. Test T2: replaying the same event capture
   twice yields byte-identical decisions.
4. DP3 risk envelope. Test T3: property test with random GOs and random
   stops never exceeds any cap; attempts to raise a cap at runtime fail.
5. DP4 routers. Test T4: slippage cap honored on captured fills; a two-leg
   Polymarket order with one leg failing unwinds inside T_unwind.
6. DP5 exits. Test T5: every entry in the ledger has a plan; each plan
   layer fires in simulation at its trigger.
7. DP7 governor. Test T7: an injected losing streak produces throttle then
   halt before the daily limit.
8. DP8 learner. Test T8: after retraining, gate checksums are unchanged and
   no sacred inversion has flipped.
9. DP9 supervisor. Test T9: kill -9 with open paper positions; restart
   reconciles and exits still fire.

Promotion gate per venue (paper to live), all required:
- At least 200 paper trades on pump.fun, 50 on Polymarket.
- Realized expectancy after modeled costs is positive and the lower bound
  of its 90 percent confidence interval is above zero.
- p95 latency inside the budget at every stage.
- Zero risk-envelope violations and zero unplanned positions.
- Starting live cap is 10 percent of the paper stake; it may double after
  each further profitable window and never exceeds `risk.json`.

If the gate never passes on a venue, the correct output of this system is to
keep that venue in paper. A bot that does not trade where it has no edge is
working as designed.

---

## Part L. Reuse map

From bondli:
`src/autoape/pipeline.js`, `src/autoape/gates/*.js`, `src/autoape/sizing.js`,
`src/autoape/exit-plan.js`, `src/autoape/recovery.js`,
`src/engine/rpc-enhanced.mjs`, `src/engine/pumpfun-client.mjs`,
`src/engine/raydium-client.mjs`, `src/engine/price-feeds.mjs`,
`src/engine/rug-scanner.mjs`, `src/engine/exit-liquidity-detector.mjs`,
`src/engine/survivorship-bias.mjs`, `src/engine/smart-money-tracker.mjs`,
`src/engine/position-health.mjs`, `src/engine/tilt-detector.mjs`,
`src/engine/regime-engine.mjs`, `src/engine/portfolio-correlation.mjs`,
`src/scoring/memetic/learning-pipeline.js`, `src/engine/brad-client.mjs`,
`calcPositionSize` and `/api/auto-trade/simulate` in
`src/api/server.production.mjs`.

From BRAD:
`bondli_bridge/server.py`, `bondli_bridge/risk.py`,
`bondli_bridge/decisions.py`, `bondli_bridge/trading_meta.py`,
`bondli_bridge/trading_self.py`, `bondli_bridge/positions.py`,
`core/engine.py`, `ouroboros-bot.service`.

Explicitly excluded (constraint C1): `fleet-trader.mjs`, `fleet-brains.mjs`,
`anti-detection.mjs`, `launch-orchestrator.mjs`, `token-creator.mjs`,
`volume-engine.mjs`, the wash phases of `orchestrator.mjs`, and every
strategy in GAME_THEORY.md.

---

## Part M. Stop

Present Parts C through K as re-derived against the code you found, with
every correction called out. Then stop and wait for approval. Write no code
before approval, unless the line below reads `APPROVED`.

Approval: APPROVED (built in bondli/src/velocity, tests T1..T9 in bondli/tests/velocity)
