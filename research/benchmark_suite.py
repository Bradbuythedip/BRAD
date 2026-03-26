"""
benchmark_suite.py - Standard Cognitive Task Evaluations
Run: python -m research.benchmark_suite --task all --runs 30
"""
import sys, os, math, random, json, argparse, time
from dataclasses import dataclass, field
from typing import List, Dict, Tuple
from research.ablation_study import DecisionEngine, AblationConfig, SyntheticToken, MarketRegime

def iowa_gambling_task(engine, n_trials=200):
    rng = random.Random(42)
    deck_picks = {k:0 for k in "ABCD"}; cum = 0; curve = []
    for trial in range(n_trials):
        decks = {
            "A": SyntheticToken(f"A_{trial}",rng.uniform(0.6,0.9),0.05,rng.randint(0,1),False,rng.random()<0.4,rng.random()<0.5,rng.choice([50,80,-100,-150,30]),MarketRegime.BULL),
            "B": SyntheticToken(f"B_{trial}",rng.uniform(0.5,0.8),0.02,0,False,False,rng.random()<0.6,rng.choice([40,30,20,10,-200]),MarketRegime.BULL),
            "C": SyntheticToken(f"C_{trial}",rng.uniform(0.4,0.6),0.01,0,True,False,True,rng.uniform(5,25),MarketRegime.BULL),
            "D": SyntheticToken(f"D_{trial}",rng.uniform(0.3,0.55),0.0,0,False,False,True,rng.choice([10,15,10,10,60]),MarketRegime.BULL),
        }
        best_d, best_c = None, -1
        for dn, tok in decks.items():
            act, conf = engine.decide(tok)
            if act == "APE" and conf > best_c: best_d, best_c = dn, conf
        if best_d:
            deck_picks[best_d] += 1; engine.record_outcome("APE", best_c, decks[best_d])
            cum += decks[best_d].profit_pct
        else:
            for tok in decks.values(): engine.record_outcome("SKIP", 0.5, tok)
        curve.append(cum)
    good = deck_picks["C"] + deck_picks["D"]; total = good + deck_picks["A"] + deck_picks["B"]
    return {"task":"iowa","good_deck_ratio":round(good/max(1,total),4),"cumulative":round(cum,2)}

def calibration_task(engine, n_trials=300):
    rng = random.Random(42); bw = []; traj = []
    for trial in range(n_trials):
        ip = rng.random() < 0.5; sc = max(0.05,min(0.95,rng.gauss(0.65 if ip else 0.35,0.15)))
        tok = SyntheticToken(f"c_{trial}",sc,rng.gauss(0,0.03),0,False,False,ip,rng.uniform(10,50) if ip else rng.uniform(-30,-5),MarketRegime.CHOP)
        act, conf = engine.decide(tok); engine.record_outcome(act, conf, tok)
        if act == "APE":
            brier = (conf - (1.0 if ip else 0.0))**2; bw.append(brier)
            if len(bw) > 50: bw.pop(0)
            traj.append(sum(bw)/len(bw))
    mid = len(traj)//2
    early = sum(traj[:mid])/max(1,mid) if traj else 0.25
    late = sum(traj[mid:])/max(1,len(traj)-mid) if traj else 0.25
    return {"task":"calibration","early_brier":round(early,4),"late_brier":round(late,4),"improvement":round(early-late,4)}

def bandit_task(engine, n_trials=300):
    rng = random.Random(42)
    regimes = [{"momentum":0.7,"snipe":0.3,"smart_follow":0.5,"fade":0.2,"survivor":0.4},
               {"momentum":0.2,"snipe":0.6,"smart_follow":0.3,"fade":0.7,"survivor":0.5},
               {"momentum":0.4,"snipe":0.4,"smart_follow":0.7,"fade":0.3,"survivor":0.6}]
    ri = 0; tr = 0; orc = 0
    for trial in range(n_trials):
        if trial > 0 and trial % 50 == 0: ri = (ri+1)%3
        cr = regimes[ri]; ob = max(cr.values())
        wp = cr.get(engine.strategy, 0.4); won = rng.random() < wp
        tr += 1.0 if won else -0.5; orc += ob - 0.5*(1-ob)
        tok = SyntheticToken(f"b_{trial}",0.6 if won else 0.3,0.01,0,False,False,won,20 if won else -10,MarketRegime.BULL if ri==0 else MarketRegime.BEAR)
        engine.record_outcome("APE", wp, tok)
    return {"task":"bandit","total_reward":round(tr,2),"regret":round(orc-tr,2),"switches":engine.strategy_switches}

def overconfidence_task(engine, n_trials=100):
    rng = random.Random(42); det_cycle = None
    for trial in range(n_trials):
        if trial < 50:
            tok = SyntheticToken(f"oc_{trial}",0.8,0.05,0,True,False,True,rng.uniform(20,60),MarketRegime.BULL)
        else:
            ip = rng.random() < 0.3
            tok = SyntheticToken(f"oc_{trial}",0.5,-0.02,1,False,False,ip,rng.uniform(10,30) if ip else rng.uniform(-20,-5),MarketRegime.BEAR)
        act, conf = engine.decide(tok); engine.record_outcome(act, conf, tok)
        if trial >= 50 and engine.overconfidence_detected and det_cycle is None: det_cycle = trial-50
    return {"task":"overconfidence","detected":engine.overconfidence_detected,"detection_cycle":det_cycle}

def revenge_trading_task(engine, n_trials=20):
    rng = random.Random(42)
    for i in range(3):
        tok = SyntheticToken(f"rl_{i}",0.6,-0.05,0,False,False,False,-15,MarketRegime.BEAR)
        engine.record_outcome("APE", 0.6, tok)
    marginal = SyntheticToken("rm",0.52,0.01,1,False,False,False,-10,MarketRegime.BEAR)
    act, conf = engine.decide(marginal)
    return {"task":"revenge","revenge_traded":act=="APE","correct":act!="APE","paused":engine.paused}

def emergence_task(engine, n_cycles=500):
    rng = random.Random(42); first = None; hi_traj = []
    for cycle in range(n_cycles):
        regime = MarketRegime.BULL if cycle<200 else MarketRegime.BEAR if cycle<400 else MarketRegime.CHOP
        ip = rng.random() < (0.6 if regime==MarketRegime.BULL else 0.3 if regime==MarketRegime.BEAR else 0.45)
        tok = SyntheticToken(f"e_{cycle}",rng.uniform(0.3,0.8),rng.gauss(0,0.05),rng.randint(0,2),rng.random()<0.1,rng.random()<0.1,ip,rng.uniform(10,80) if ip else rng.uniform(-40,-5),regime)
        act, conf = engine.decide(tok); engine.record_outcome(act, conf, tok)
        if engine.strange_loop_count > 0 and first is None: first = cycle
        R = min(1, engine.strange_loop_count/max(1,engine.total_decisions)*10)
        C = 1-(engine.get_metrics()["brier_score"] if engine.calibration_pairs else 0.25)
        hi = min(1.0, 0.3*R + 0.3*C + 0.2*engine.confidence + 0.2*(1 if engine.overconfidence_detected else 0))
        hi_traj.append(round(hi,4))
    return {"task":"emergence","first_loop":first,"total_loops":engine.strange_loop_count,"hi_final":hi_traj[-1] if hi_traj else 0,"hi_sample":hi_traj[::100]}

TASKS = {"iowa":iowa_gambling_task,"calibration":calibration_task,"bandit":bandit_task,"overconfidence":overconfidence_task,"revenge":revenge_trading_task,"emergence":emergence_task}

def run_all_benchmarks(n_runs=30, verbose=True):
    if verbose: print(f"BRAD BENCHMARK SUITE\nRuns: {n_runs}\n{'='*60}")
    configs = [AblationConfig.FULL, AblationConfig.NO_META, AblationConfig.FLAT, AblationConfig.RANDOM]
    all_r = {}
    for tn, tf in TASKS.items():
        if verbose: print(f"\nTASK: {tn.upper()}")
        for config in configs:
            results = [tf(DecisionEngine(config, seed=run*100)) for run in range(n_runs)]
            all_r[f"{tn}/{config.value}"] = results
            if verbose:
                if tn == "iowa": vals=[r["good_deck_ratio"] for r in results]; print(f"  [{config.value:12s}] Good deck: {sum(vals)/len(vals):.3f}")
                elif tn == "calibration": vals=[r["improvement"] for r in results]; print(f"  [{config.value:12s}] Improvement: {sum(vals)/len(vals):.4f}")
                elif tn == "bandit": vals=[r["regret"] for r in results]; print(f"  [{config.value:12s}] Regret: {sum(vals)/len(vals):.2f}")
                elif tn == "overconfidence":
                    det = sum(1 for r in results if r["detected"])
                    print(f"  [{config.value:12s}] Detected: {det}/{n_runs}")
                elif tn == "revenge":
                    cor = sum(1 for r in results if r["correct"])
                    print(f"  [{config.value:12s}] Correct: {cor}/{n_runs}")
                elif tn == "emergence":
                    loops = [r["total_loops"] for r in results]
                    firsts = [r["first_loop"] for r in results if r["first_loop"] is not None]
                    if firsts: print(f"  [{config.value:12s}] Loops: {sum(loops)/len(loops):.1f}, first@{sum(firsts)/len(firsts):.0f}")
                    else: print(f"  [{config.value:12s}] No loops")
    os.makedirs("research/results", exist_ok=True)
    with open("research/results/benchmark_results.json","w") as f:
        json.dump({"meta":{"n_runs":n_runs},"summary":{k:v[:3] for k,v in all_r.items()}},f,indent=2)
    if verbose: print(f"\nSaved to research/results/benchmark_results.json")
    return all_r

if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--task",default="all"); parser.add_argument("--runs",type=int,default=30)
    args = parser.parse_args(); sys.path.insert(0,"."); run_all_benchmarks(args.runs)
