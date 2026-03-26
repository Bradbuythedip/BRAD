"""
ablation_study.py - Systematic Component Removal Experiments
Run: python -m research.ablation_study --runs 50 --cycles 200
"""
import sys, os, math, random, json, argparse, time
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
from enum import Enum

class MarketRegime(Enum):
    BULL = "bull"
    BEAR = "bear"
    CHOP = "chop"

REGIME_WIN_RATES = {MarketRegime.BULL: 0.65, MarketRegime.BEAR: 0.30, MarketRegime.CHOP: 0.45}

@dataclass
class SyntheticToken:
    mint: str; score: float; velocity: float; rug_signals: int
    smart_money: bool; is_rug: bool; is_profitable: bool
    profit_pct: float; regime: MarketRegime

class SyntheticEnvironment:
    def __init__(self, seed=42):
        self.rng = random.Random(seed)
        self.regime = MarketRegime.BULL
        self.cycle = 0
        self.regime_shift_interval = 50
        self.rug_rate = 0.15

    def step(self) -> List[SyntheticToken]:
        self.cycle += 1
        if self.cycle % self.regime_shift_interval == 0:
            self.regime = self.rng.choice(list(MarketRegime))
        n = self.rng.randint(5, 10)
        tokens = []
        wr = REGIME_WIN_RATES[self.regime]
        for i in range(n):
            is_rug = self.rng.random() < self.rug_rate
            if is_rug:
                tokens.append(SyntheticToken(f"t_{self.cycle}_{i}", self.rng.uniform(0.3,0.8), self.rng.uniform(-0.1,0.05), self.rng.randint(1,4), False, True, False, self.rng.uniform(-80,-20), self.regime))
            else:
                ip = self.rng.random() < wr
                sc = max(0, min(1, self.rng.gauss(0.55 if ip else 0.35, 0.15)))
                tokens.append(SyntheticToken(f"t_{self.cycle}_{i}", sc, self.rng.gauss(0.02 if ip else -0.02, 0.05), 0 if self.rng.random()>0.1 else self.rng.randint(1,2), ip and self.rng.random()<0.2, False, ip, self.rng.uniform(5,200) if ip else self.rng.uniform(-30,-5), self.regime))
        return tokens

class AblationConfig(Enum):
    FULL="full"; NO_META="no_meta"; NO_LOOPS="no_loops"
    NO_WORKSPACE="no_workspace"; NO_SELF_REF="no_self_ref"
    FLAT="flat"; RANDOM="random"

DESCRIPTIONS = {
    AblationConfig.FULL: "Complete 3-level system",
    AblationConfig.NO_META: "No L2 meta-cognitive",
    AblationConfig.NO_LOOPS: "No downward causation",
    AblationConfig.NO_WORKSPACE: "No global workspace",
    AblationConfig.NO_SELF_REF: "No SELF entity",
    AblationConfig.FLAT: "Single level only",
    AblationConfig.RANDOM: "Random baseline",
}

class DecisionEngine:
    def __init__(self, config, seed=42):
        self.config = config; self.rng = random.Random(seed)
        self.confidence = 0.5; self.win_history = []
        self.consecutive_losses = 0; self.strategy = "momentum"
        self.paused = False; self.overconfidence_detected = False
        self.strategy_switches = 0; self.strange_loop_count = 0
        self.total_decisions = 0; self.apes = 0; self.skips = 0
        self.correct_apes = 0; self.correct_skips = 0
        self.rug_catches = 0; self.rug_misses = 0
        self.pnl_total = 0.0; self.pnl_history = []
        self.calibration_pairs = []

    def decide(self, token):
        self.total_decisions += 1
        if self.config == AblationConfig.RANDOM:
            return ("APE" if self.rng.random()>0.5 else "SKIP", 0.5)
        if self.config == AblationConfig.FLAT:
            if token.rug_signals >= 3: return ("SKIP", 0.9)
            return ("APE", token.score) if token.score >= 0.6 else ("SKIP", 1-token.score)
        conf = token.score
        if token.rug_signals >= 3: return ("SKIP", 0.95)
        if token.smart_money: conf += 0.15
        if token.velocity > 0.03: conf += 0.1
        elif token.velocity < -0.03: conf -= 0.15
        if self.paused: return ("SKIP", 0.9)
        if self.config != AblationConfig.NO_META:
            if len(self.win_history) >= 5:
                awr = sum(self.win_history[-10:]) / len(self.win_history[-10:])
                if self.confidence > awr + 0.2:
                    self.overconfidence_detected = True; conf -= 0.15
                    if self.config != AblationConfig.NO_LOOPS:
                        self.confidence = max(0.3, self.confidence-0.1)
                        self.strange_loop_count += 1
            if self.consecutive_losses >= 3 and self.config != AblationConfig.NO_LOOPS:
                self.paused = True; self.strange_loop_count += 1
                return ("SKIP", 0.95)
            if self.config != AblationConfig.NO_LOOPS and len(self.win_history)>=10:
                if sum(self.win_history[-10:])/10 < 0.3 and self.strategy == "momentum":
                    self.strategy = "survivor"; self.strategy_switches += 1
                    self.strange_loop_count += 1
        if self.config != AblationConfig.NO_WORKSPACE and self.config != AblationConfig.NO_SELF_REF:
            conf = conf * 0.85 + self.confidence * 0.15
        conf = max(0.0, min(1.0, conf))
        return ("APE", conf) if conf >= 0.55 else ("SKIP", max(0.5, 1.0-conf))

    def record_outcome(self, action, confidence, token):
        if action == "APE":
            self.apes += 1; won = token.is_profitable
            self.win_history.append(won)
            self.calibration_pairs.append((confidence, 1.0 if won else 0.0))
            if won: self.correct_apes += 1; self.consecutive_losses = 0
            else: self.consecutive_losses += 1
            if token.is_rug: self.rug_misses += 1
            pnl = token.profit_pct / 100 * 0.1
            self.pnl_total += pnl; self.pnl_history.append(self.pnl_total)
            self.confidence = self.confidence * 0.9 + (1.0 if won else 0.0) * 0.1
            if self.paused and self.consecutive_losses == 0: self.paused = False
        else:
            self.skips += 1
            if token.is_rug: self.rug_catches += 1; self.correct_skips += 1
            elif not token.is_profitable: self.correct_skips += 1

    def get_metrics(self):
        wr = self.correct_apes / max(1, self.apes)
        brier = sum((c-o)**2 for c,o in self.calibration_pairs) / max(1, len(self.calibration_pairs)) if self.calibration_pairs else 0.25
        max_dd = 0
        if self.pnl_history:
            rm = self.pnl_history[0]
            for p in self.pnl_history:
                rm = max(rm, p); dd = (rm-p)/max(0.001,rm); max_dd = max(max_dd, dd)
        return {"config": self.config.value, "win_rate": round(wr,4), "pnl_total": round(self.pnl_total,4),
                "brier_score": round(brier,4), "rug_detection_rate": round(self.rug_catches/max(1,self.rug_catches+self.rug_misses),4),
                "max_drawdown_pct": round(max_dd*100,2), "strategy_switches": self.strategy_switches,
                "strange_loops": self.strange_loop_count, "apes": self.apes, "skips": self.skips}

def run_experiment(config, n_cycles, seed):
    env = SyntheticEnvironment(seed=seed)
    engine = DecisionEngine(config, seed=seed)
    for _ in range(n_cycles):
        for token in env.step():
            action, conf = engine.decide(token)
            engine.record_outcome(action, conf, token)
    return engine.get_metrics()

def compute_stats(results):
    if not results: return {}
    keys = [k for k in results[0] if isinstance(results[0][k], (int,float))]
    stats = {}
    for key in keys:
        vals = [r[key] for r in results]; n = len(vals)
        mean = sum(vals)/n; std = math.sqrt(sum((x-mean)**2 for x in vals)/max(1,n-1))
        se = std/math.sqrt(n); ci = 1.96*se
        stats[key] = {"mean": round(mean,4), "std": round(std,4), "ci_low": round(mean-ci,4), "ci_high": round(mean+ci,4)}
    return stats

def cohens_d(g1, g2):
    n1,n2 = len(g1),len(g2); m1,m2 = sum(g1)/n1, sum(g2)/n2
    v1 = sum((x-m1)**2 for x in g1)/max(1,n1-1); v2 = sum((x-m2)**2 for x in g2)/max(1,n2-1)
    ps = math.sqrt(((n1-1)*v1+(n2-1)*v2)/max(1,n1+n2-2))
    return (m1-m2)/ps if ps > 0 else 0

def run_ablation_study(n_runs=50, n_cycles=200, verbose=True):
    if verbose: print(f"BRAD ABLATION STUDY\nRuns: {n_runs} | Cycles: {n_cycles}\n{'='*60}")
    all_results = {}
    for config in AblationConfig:
        if verbose: print(f"\n[{config.value}] {DESCRIPTIONS[config]}...")
        results = [run_experiment(config, n_cycles, run*1000+hash(config.value)%1000) for run in range(n_runs)]
        stats = compute_stats(results); all_results[config.value] = {"stats": stats, "raw": results}
        if verbose:
            s = stats
            print(f"  Win Rate: {s['win_rate']['mean']:.3f} +/- {s['win_rate']['std']:.3f}")
            print(f"  PnL:      {s['pnl_total']['mean']:.3f} | Brier: {s['brier_score']['mean']:.3f}")
            print(f"  Rug Det:  {s['rug_detection_rate']['mean']:.3f} | Loops: {s.get('strange_loops',{}).get('mean',0):.1f}")
    if verbose:
        print(f"\n{'='*60}\nCOMPARATIVE (vs full)")
        full_wr = [r["win_rate"] for r in all_results["full"]["raw"]]
        full_pnl = [r["pnl_total"] for r in all_results["full"]["raw"]]
        for config in AblationConfig:
            if config == AblationConfig.FULL: continue
            awr = [r["win_rate"] for r in all_results[config.value]["raw"]]
            apnl = [r["pnl_total"] for r in all_results[config.value]["raw"]]
            print(f"  {config.value:15s} WR d={cohens_d(full_wr,awr):.2f}  PnL d={cohens_d(full_pnl,apnl):.2f}")
    os.makedirs("research/results", exist_ok=True)
    with open("research/results/ablation_results.json","w") as f:
        json.dump({"meta":{"n_runs":n_runs,"n_cycles":n_cycles},"results":{k:v["stats"] for k,v in all_results.items()}},f,indent=2)
    return all_results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--runs",type=int,default=50); parser.add_argument("--cycles",type=int,default=200)
    args = parser.parse_args(); sys.path.insert(0,"."); run_ablation_study(args.runs, args.cycles)
