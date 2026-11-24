"""Deep dig on Kalshi's hourly crypto rounds (23 Nov 2026, Jan: "check other parameters, dig deep"): every setting, not
just the real bot's. Needs khourly.py's data (bt_cache/khr, probe khr_fetch) and for `lastmin` kdocs' per-second
numbers (bt_cache/kidx). Each part is a small script kept as it was run; tables are built once and cached as
bt_cache/khr/*.pkl. Write-up: backtest/khourly.md "The deep dig".

  python3 khourly_sweep.py table            every market at 11 times before the close (run first)
  python3 khourly_sweep.py grid all take    time x price x cushion, buying at the ask (also: thru = sure fills of a
                                            waiting bid, touch = best case; KXBTCD instead of all = one coin)
  python3 khourly_sweep.py pool             buying the safe side at 96-99c, by cushion and time
  python3 khourly_sweep.py improve          a bid one cent in front of the best bid, every time / price / cushion
  python3 khourly_sweep.py offer [--log]    the one lead, sized: offer the safe side at 99c (bid 1c on the long shot), counted
                                            on the real buyers at 99c (needs bt_cache/khr/ls_*.json.gz, probe khr_lsfetch)
  python3 khourly_sweep.py lastmin          model of the last minute (the result is a 60-second average) vs real trades
"""
import os, sys
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bt_cache", "khr")
PARTS = {}
PARTS['table'] = r'''import sys, math, pickle, os
import khourly as kh, kcrypto as kc
MIN = (30, 25, 20, 15, 10, 7, 5, 4, 3, 2, 1)
rows = []
for s in ("KXBTCD", "KXETHD", "KXSOLD", "KXXRPD", "KXBNBD", "KXHYPED"):
    D = kh.load(s)
    for w in D["w"]:
        for m in MIN:
            t = w["close"] - 60 * m
            r = w["c"].get(t)
            if not r or r[0] is None or r[1] is None or not (0 <= r[0] <= r[1] <= 1) or r[1] - r[0] > 0.5:
                continue
            g = kh.gap_at(D, t)
            zy = kc.zscore(dict(w, strike=w["strike"] * g), t, m, "yes") if g else None
            if zy is None:
                continue
            # later minutes: lowest ask / bid seen for each side after t (for maker fills)
            later = [w["c"].get(t + 60 * i) for i in range(1, m + 1)]
            later = [x for x in later if x and x[0] is not None and x[1] is not None]
            min_ya = min([x[1] for x in later], default=None); max_yb = max([x[0] for x in later], default=None)
            vol_after = sum((x[4] or 0) for x in later)
            for side in ("yes", "no"):
                bid, ask = (r[0], r[1]) if side == "yes" else (1 - r[1], 1 - r[0])
                z = zy if side == "yes" else -zy
                # the side's ask later fell to our bid or under = someone sold through us for sure
                if side == "yes":
                    thru = min_ya is not None and min_ya <= bid + 1e-9
                    touch = later and min(x[0] for x in later) <= bid + 1e-9 and vol_after > 0
                else:
                    thru = max_yb is not None and (1 - max_yb) <= bid + 1e-9
                    touch = later and min(1 - x[1] for x in later) <= bid + 1e-9 and vol_after > 0
                rows.append((s, w["close"], m, side, round(bid, 2), round(ask, 2), z, w["res"] == side, r[4] or 0, bool(thru), bool(touch), w["ev"], w["t"]))
    print(s, len(rows), flush=True)
pickle.dump(rows, open(HERE + "/sweep.pkl", "wb"))
'''

PARTS['grid'] = r'''import pickle, os, sys, collections
rows = pickle.load(open(HERE + "/sweep.pkl", "rb"))
ts = sorted({r[1] for r in rows}); mid = ts[len(ts) // 2]
def pb(a):
    for lo, hi in ((0.01,0.05),(0.05,0.2),(0.2,0.4),(0.4,0.6),(0.6,0.8),(0.8,0.9),(0.9,0.95),(0.95,0.98),(0.98,0.985),(0.99,0.995),(1.0,1.01)):
        if lo - 1e-9 <= a < hi: return f"{lo:.2f}-{hi:.2f}"
def zb(z):
    for lo, hi in ((-99,-3),(-3,-2),(-2,-1),(-1,0),(0,1),(1,2),(2,3),(3,4),(4,6),(6,99)):
        if lo <= z < hi: return f"{lo}..{hi}"
coins = sys.argv[1].split(",") if len(sys.argv) > 1 and sys.argv[1] != "all" else None
mode = sys.argv[2] if len(sys.argv) > 2 else "take"
C = collections.defaultdict(lambda: [0, 0.0, 0.0, 0, 0.0, 0.0, 0.0])  # n, cost, pnl, n2, cost2, pnl2, vol
for s, close, m, side, bid, ask, z, won, vol, thru, touch, ev, tk in rows:
    if coins and s not in coins: continue
    if mode == "take":
        if ask >= 1 or ask <= 0: continue
        p = ask; cost = p + 0.07 * p * (1 - p)
    else:
        if bid <= 0 or bid >= 1: continue
        if not (thru if mode == "thru" else touch): continue
        p = bid; cost = p
    k = (m, pb(p), zb(z))
    c = C[k]; h = 0 if close < mid else 3
    c[h] += 1; c[h + 1] += cost; c[h + 2] += (1.0 if won else 0.0) - cost; c[6] += vol
out = []
for k, c in C.items():
    n = c[0] + c[3]
    if n < 150 or not c[1] or not c[4]: continue
    out.append((k, n, (c[2] + c[5]) / (c[1] + c[4]) * 100, c[2] / c[1] * 100, c[5] / c[4] * 100, c[0], c[3], c[6] / n))
both = [o for o in out if o[3] > 0 and o[4] > 0]
print(f"{mode} coins={coins}: {len(out)} cells with 150+ rows; ahead in both halves: {len(both)}; ahead overall: {sum(o[2] > 0 for o in out)}")
print("min | price | cushion | n | per $100 | first half | second half | contracts traded that minute (avg)")
for o in sorted(both, key=lambda o: -min(o[3], o[4]))[:int(sys.argv[3]) if len(sys.argv) > 3 else 25]:
    print(f"{o[0][0]:>2} | {o[0][1]} | {o[0][2]:>7} | {o[1]:>6} | {o[2]:+6.2f} | {o[3]:+6.2f} ({o[5]}) | {o[4]:+6.2f} ({o[6]}) | {o[7]:,.0f}")
'''

PARTS['pool'] = r'''import pickle, os, sys, collections
rows = pickle.load(open(HERE + "/sweep.pkl", "rb"))
ts = sorted({r[1] for r in rows}); mid = ts[len(ts) // 2]; days = (ts[-1] - ts[0]) / 86400
for coins in (("KXBTCD",), ("KXETHD",), ("KXSOLD", "KXXRPD", "KXBNBD", "KXHYPED")):
    print("\n", coins)
    print("ask | cushion | min | n | lost | rounds | rounds w/ a loss | per $100 | 1st | 2nd | a day | vol/min")
    for ask in (0.99, 0.98, 0.97, 0.96):
        for zlo, zhi in ((2, 3), (3, 4), (4, 6), (6, 99)):
            for m in (30, 20, 15, 10, 5, 3, 2, 1):
                g = [r for r in rows if r[0] in coins and r[2] == m and abs(r[5] - ask) < 1e-9 and zlo <= r[6] < zhi]
                if len(g) < 100: continue
                cost = ask + 0.07 * ask * (1 - ask)
                def pp(x):
                    return (sum((1.0 if r[7] else 0.0) - cost for r in x) / (cost * len(x)) * 100) if x else 0
                lost = [r for r in g if not r[7]]
                print(f"{ask:.2f} | {zlo}-{zhi} | {m:>2} | {len(g):>5} | {len(lost):>3} | {len({r[11] for r in g}):>4} | {len({r[11] for r in lost}):>2} | {pp(g):+.2f} | {pp([r for r in g if r[1] < mid]):+.2f} | {pp([r for r in g if r[1] >= mid]):+.2f} | {len(g) / days:.1f} | {sum(r[8] for r in g) / len(g):,.0f}")
'''

PARTS['improve'] = r'''import sys, pickle, os, collections
import khourly as kh, kcrypto as kc
S = HERE
MIN = (30, 25, 20, 15, 10, 7, 5, 4, 3, 2)
if not os.path.exists(S + "/imp.pkl"):
    rows = []
    for s in ("KXBTCD", "KXETHD", "KXSOLD", "KXXRPD", "KXBNBD", "KXHYPED"):
        D = kh.load(s)
        for w in D["w"]:
            for m in MIN:
                t = w["close"] - 60 * m
                r = w["c"].get(t)
                if not r or r[0] is None or r[1] is None or not (0 <= r[0] <= r[1] <= 1) or r[1] - r[0] < 0.02 - 1e-9 or r[1] - r[0] > 0.5:
                    continue
                g = kh.gap_at(D, t)
                zy = kc.zscore(dict(w, strike=w["strike"] * g), t, m, "yes") if g else None
                if zy is None:
                    continue
                for side in ("yes", "no"):
                    bid, ask, _, _ = kc.side_view(r, side)
                    price = round(bid + 0.01, 2)
                    st, _, to = kc.fill_after(w, t, side, price, True)
                    rows.append((s, w["close"], m, side, price, round(ask - bid, 2), zy if side == "yes" else -zy, w["res"] == side, st, to, w["ev"]))
    pickle.dump(rows, open(S + "/imp.pkl", "wb"))
rows = pickle.load(open(S + "/imp.pkl", "rb"))
ts = sorted({r[1] for r in rows}); mid = ts[len(ts) // 2]; days = (ts[-1] - ts[0]) / 86400
def pb(a):
    for lo, hi in ((0.02,0.2),(0.2,0.4),(0.4,0.6),(0.6,0.8),(0.8,0.9),(0.9,0.95),(0.95,0.995)):
        if lo - 1e-9 <= a < hi: return f"{lo:.2f}-{hi:.2f}"
def zb(z):
    for lo, hi in ((-99,-2),(-2,-1),(-1,0),(0,1),(1,2),(2,3),(3,4),(4,99)):
        if lo <= z < hi: return f"{lo}..{hi}"
print("improve-by-1c rows:", len(rows), "filled (trade at our price or lower):", sum(r[9] for r in rows))
for name, sel in (("all coins", None), ("bitcoin", ("KXBTCD",)), ("not bitcoin", ("KXETHD", "KXSOLD", "KXXRPD", "KXBNBD", "KXHYPED"))):
    g = [r for r in rows if r[9] and (not sel or r[0] in sel)]
    pnl = sum((1.0 if r[7] else 0) - r[4] for r in g); cost = sum(r[4] for r in g)
    print(f"{name}: {len(g)} fills, per $100 {pnl / cost * 100:+.2f}")
    C = collections.defaultdict(lambda: [0, 0.0, 0.0, 0, 0.0, 0.0])
    for r in g:
        c = C[(r[2], pb(r[4]), zb(r[6]))]; h = 0 if r[1] < mid else 3
        c[h] += 1; c[h + 1] += r[4]; c[h + 2] += (1.0 if r[7] else 0) - r[4]
    out = [(k, c) for k, c in C.items() if c[0] >= 60 and c[3] >= 60]
    both = [(k, c) for k, c in out if c[2] > 0 and c[5] > 0]
    print(f"  cells with 60+ fills in each half: {len(out)}, ahead in both: {len(both)}")
    for k, c in sorted(both, key=lambda x: -min(x[1][2] / x[1][1], x[1][5] / x[1][4]))[:8]:
        print(f"  {k[0]:>2} min | {k[1]} | cushion {k[2]:>6} | {c[0] + c[3]:>5} fills ({(c[0] + c[3]) / days:.1f} a day) | 1st {c[2] / c[1] * 100:+.2f} | 2nd {c[5] / c[4] * 100:+.2f}")
'''

PARTS['lastmin'] = r'''import sys, os, math, bisect, collections
import khourly as kh, kcrypto as kc
import numpy as np
PAIRS = {"KXBTCD": "KXBTC15M", "KXETHD": "KXETH15M", "KXSOLD": "KXSOL15M", "KXXRPD": "KXXRP15M", "KXBNBD": "KXBNB15M", "KXHYPED": "KXHYPE15M"}
SS = list(range(3, 58, 3))
X = {s: [] for s in SS}; Y = {s: [] for s in SS}; META = {s: [] for s in SS}
data = {}
for hs, qs in PAIRS.items():
    sec = (kc.rjson(f"bt_cache/kidx/{qs}.json.gz", {}) or {}).get("sec", {})
    D = kh.load(hs)
    byclose = collections.defaultdict(list)
    for w in D["w"]:
        byclose[w["close"]].append(w)
    ok = bad = 0
    for close, ws in byclose.items():
        seq = sec.get(str(close))
        if not seq or len(seq) < 120 or any(v is None for v in seq):
            continue
        F = seq[-1]
        if abs(F - ws[0]["settle"]) / F > 2e-5: bad += 1
        else: ok += 1
        dv = np.diff(np.array(seq[:60]))
        vol = float(np.sqrt(np.mean(dv ** 2))) / F + 1e-9      # per-second wobble of the averaged number, first minute of the two
        for s in SS:
            i = 119 - s
            v = seq[i]
            X[s].append([(v - seq[i - 5]) / F, (v - seq[i - 15]) / F, (v - seq[i - 30]) / F, (v - seq[i - 58]) / F])
            Y[s].append((F - v) / F); META[s].append((hs, close, vol, v))
        data[(hs, close)] = (seq, ws, D["tr"], vol)
    print(hs, "rounds with seconds:", ok + bad, "last number = settle:", ok, "differs:", bad, flush=True)
closes = sorted({m[1] for m in META[SS[0]]}); mid = closes[len(closes) // 2]
model = {}
print("\nseconds left | plain miss (latest number as the forecast) | model miss | (both as shares of the usual 1-second wobble, test half)")
for s in SS:
    x = np.array(X[s]); y = np.array(Y[s]); m = np.array([q[1] < mid for q in META[s]]); vol = np.array([q[2] for q in META[s]])
    b, *_ = np.linalg.lstsq(x[m], y[m], rcond=None)
    res = (y - x @ b) / vol
    model[s] = (b, np.sort(res[m]))
    if s % 9 == 3 or s in (30, 57):
        print(f"{s:>2} | {np.std(y[~m] / vol[~m]):.1f} | {np.std(res[~m]):.1f}")
def p_yes(seq, s_left, strike, vol):
    s = min(SS, key=lambda q: abs(q - s_left) if q >= s_left else 99)   # the model for at least this many seconds left
    i = 119 - s
    v = seq[i]; F0 = seq[-1]
    b, rs = model[s]
    pred = v + (np.array([(v - seq[i - 5]), (v - seq[i - 15]), (v - seq[i - 30]), (v - seq[i - 58])]) @ b)
    need = (strike - pred) / v / vol            # the final number must beat this (in wobble units) for Yes
    return 1 - bisect.bisect_left(rs, need) / len(rs)
out = []
for (hs, close), (seq, ws, TR, vol) in data.items():
    if close < mid: continue                     # only rounds the model never saw
    for w in ws:
        tr = TR.get(w["t"])
        if not tr: continue
        for ts, yp, cnt, tk in tr:
            left = close - ts
            if not (4 <= left <= 55) or not (0 < yp < 1): continue
            s_sig = int(math.ceil(left)) + 2     # we knew the number as of 2 seconds before the trade
            if s_sig > 57: continue
            py = p_yes(seq, s_sig, w["strike"], vol)
            side = "yes" if tk in ("y", "yes") else "no"
            price = yp if side == "yes" else 1 - yp
            pm = py if side == "yes" else 1 - py
            fee = 0.07 * price * (1 - price)
            out.append((hs, close, w["t"], left, side, price, pm, pm - price - fee, cnt, w["res"] == side, fee))
print("\ntrades in the last 55 seconds, test half:", len(out))
print("model says the buyer got it this much too cheap | trades | contracts | markets | won | per $100 if we had bought the same | per $100 first trade per market only")
for lo, hi in ((-1, -0.1), (-0.1, -0.03), (-0.03, 0), (0, 0.03), (0.03, 0.1), (0.1, 0.2), (0.2, 1)):
    g = [o for o in out if lo <= o[7] < hi]
    if not g: continue
    cost = sum((o[5] + o[10]) * o[8] for o in g); pnl = sum(((1.0 if o[9] else 0) - o[5] - o[10]) * o[8] for o in g)
    first = {}
    for o in sorted(g, key=lambda o: -o[3]): first.setdefault(o[2], o)
    f = list(first.values()); c1 = sum(o[5] + o[10] for o in f); p1 = sum((1.0 if o[9] else 0) - o[5] - o[10] for o in f)
    print(f"{lo:+.2f}..{hi:+.2f} | {len(g)} | {sum(o[8] for o in g):,.0f} | {len(f)} | {sum(o[9] for o in g)} | {pnl / cost * 100:+.2f} | {p1 / c1 * 100:+.2f} ({sum(o[9] for o in f)} won)")
import pickle; pickle.dump(out, open(HERE + "/lastmin.pkl", "wb"))
'''

PARTS['offer'] = r'''import sys, pickle, gzip, json, collections, os
HERE = globals().get("HERE") or "bt_cache/khr"
SER = ("KXBTCD", "KXETHD", "KXSOLD", "KXXRPD", "KXBNBD", "KXHYPED")
rows = pickle.load(open(HERE + "/sweep.pkl", "rb"))
ts = sorted({r[1] for r in rows}); mid = ts[len(ts) // 2]; days = (ts[-1] - ts[0]) / 86400
# signal: the long shot has NO buyer at all (bid 0) and its sell offer is 2c+ (so the safe side's best bid is 98c or
# less and nobody offers it at 99c): we bid 1c on the long shot = offer the safe side at 99c, first in line.
sig = {}
for r in rows:
    s, close, m, side, bid, ask, z, won, vol, thru, touch, ev, tk = r
    if m not in (30, 20, 10) or bid > 1e-9 or ask < 0.02 - 1e-9 or ask > 0.10 + 1e-9: continue
    cush = -z
    if not (1.5 <= cush < 5): continue
    k = (tk, m)
    sig[k] = dict(s=s, close=close, m=m, side=side, cush=cush, won=won, ev=ev, tk=tk, ask=ask)
print("signals:", len(sig), "days", round(days, 1))
T = {s: json.load(gzip.open(f"{HERE}/ls_{s}.json.gz")) for s in SER}
def sold(g, frm=None):
    """contracts takers bought of the safe side at 99c after our offer went up (we are first in line)"""
    tr = T[g["s"]].get(g["tk"])
    if tr is None: return None
    t0 = g["close"] - 60 * g["m"] if frm is None else frm
    yp, tk = (0.01, "n") if g["side"] == "yes" else (0.99, "y")
    return sum(c for t, p, c, sd in tr if t > t0 + 5 and t <= g["close"] and abs(p - yp) < 1e-6 and sd == tk)
miss = 0
for g in sig.values():
    g["sold"] = sold(g)
    if g["sold"] is None: miss += 1; g["sold"] = 0
print("signals without a trade list:", miss)
def zb(c):
    return "1.5-2" if c < 2 else "2-3" if c < 3 else "3-4" if c < 4 else "4-5"
def line(name, gs, N):
    n = f = w = 0; pnl = cost = 0.0; h = [0.0, 0.0]; rounds = set(); wr = set()
    for g in gs:
        got = min(N, int(g["sold"]))
        if got < 1: continue
        n += 1; f += got; cost += got * 0.01
        p = got * (0.99 if g["won"] else -0.01)
        pnl += p; h[0 if g["close"] < mid else 1] += p; rounds.add((g["s"], g["close"]))
        if g["won"]: w += 1; wr.add((g["s"], g["close"]))
    if not n: return
    print(f"  {name:<28} | {n:>5} orders filled ({n / days:5.1f} a day) | {f:>8} contracts | long shot won {w:>3} ({len(wr)} rounds) | P&L ${pnl:+9.2f} = ${pnl / days:+6.2f} a day | halves ${h[0]:+.0f} / ${h[1]:+.0f} | at risk a day ${cost / days:.2f}")
# one order per market: the earliest of 30 / 20 / 10 min that fits
first = {}
for (tk, m), g in sorted(sig.items(), key=lambda x: -x[0][1]):
    first.setdefault(tk, g)
F = list(first.values())
for N in (100, 400, 1000, 5000):
    print(f"\n=== one order per market, up to {N} contracts (${N / 100:.0f} at risk each), first signal of 30/20/10 min ===")
    for cl, ch in ((1.5, 2), (2, 3), (3, 4), (4, 5), (2, 4), (2, 5)):
        line(f"all coins cushion {cl}-{ch}", [g for g in F if cl <= g["cush"] < ch], N)
    for s in SER:
        line(f"{s} cushion 2-4", [g for g in F if g["s"] == s and 2 <= g["cush"] < 4], N)
print("\n=== by signal minute (each minute on its own), 400 contracts ===")
for m in (30, 20, 10):
    for cl, ch in ((1.5, 2), (2, 3), (3, 4), (4, 5)):
        line(f"{m} min cushion {cl}-{ch}", [g for g in sig.values() if g["m"] == m and cl <= g["cush"] < ch], 400)
print("\n=== fill share: of signals (cushion 2-4, first), how many got any fill / full 400 ===")
G = [g for g in F if 2 <= g["cush"] < 4]
print("  signals", len(G), "any fill", sum(g["sold"] >= 1 for g in G), "400+", sum(g["sold"] >= 400 for g in G), "| long shot won among ALL signals", sum(g["won"] for g in G), "among filled", sum(g["won"] for g in G if g["sold"] >= 1))
print("\n=== the winning rounds (cushion 2-4), biggest first ===")
W = collections.defaultdict(lambda: [0, 0])
for g in G:
    if g["won"] and g["sold"] >= 1: W[(g["s"], g["close"])][0] += 1; W[(g["s"], g["close"])][1] += min(400, int(g["sold"]))
import time
for k, v in sorted(W.items(), key=lambda x: -x[1][1])[:15]:
    print("  ", k[0], time.strftime("%d %b %H:%M", time.gmtime(k[1])), "markets", v[0], "contracts", v[1], f"${v[1] * 0.99:.0f}")
pickle.dump(F, open(HERE + "/offer.pkl", "wb"))
import exam
for N in (100, 400):
    bets = []
    for g in G:
        got = min(N, int(g["sold"]))
        if got >= 1:
            bets.append({"cost": got * 0.01, "pay": got * 1.0 if g["won"] else 0.0, "t": g["close"], "ev": f'{g["s"]}{g["close"]}'})
    exam.score(bets, f"Kalshi hourly crypto: offer the safe side at 99c, cushion 2-4, 10-30 min, real 99c buyers, up to {N} contracts", tries=1400,
               src="khourly_sweep.py offer", note="found by looking; loses when sized up", status="dropped", log="--log" in sys.argv)
'''

if __name__ == "__main__":
    part = sys.argv[1] if len(sys.argv) > 1 else "grid"
    sys.argv = [sys.argv[0]] + sys.argv[2:]
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    exec(compile(PARTS[part], part, "exec"), {"__name__": "__part__", "HERE": HERE})
