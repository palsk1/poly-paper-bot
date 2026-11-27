#!/usr/bin/env python3
"""Buy AND sell inside one crypto window (26 Nov 2026, Jan: "What about a bot that buys and sells inside the 15 or
5 minute windows?"). PAPER ONLY, research: reads the speed check's logs, never trades.

Every other test in this repo holds a bet to the end of its window. This one gets out before the end: buy the Up
or Down share when it looks too cheap, sell it again seconds or minutes later. Polymarket 5-minute windows
(Bitcoin 17-26 Nov, ETH and SOL from 25 Nov) and Kalshi 15-minute windows (7 coins, 25-26 Nov) from release
`speed-data`.

    python3 swing.py prep /path/speed-2026*.jsonl.gz    # logs -> bt_cache/sw/<day>.npz + <day>.k.pkl.gz
    python3 swing.py facts                               # what a round trip costs, how prices move
    python3 swing.py grid                                # every rule family, learn days vs fresh days
    python3 swing.py report                              # backtest/swing.md

How a trade is priced (see backtest/swing.md "How the test works"):
  - Polymarket: the top of the Up book on a 0.1 s grid by OUR box's clock. Buying Up pays the best ask, selling
    Up gets the best bid; Down is the mirror (buy at 1 - bid, sell at 1 - ask). An order decided at step t trades
    at the prices of step t + delay (0.5 s to 2 s), and only if the price is still within the limit.
  - Taker fee both ways: 0.07 x shares x p x (1 - p) (what we measured on real fills).
  - A waiting order below / above the best price fills only when a later real trade prints THROUGH its price
    ("sure" fills), or AT its price ("lucky" fills, shown apart as the hopeful end).
  - Anything still held at the end is paid $1 or $0 by the real result.
"""
import collections
import glob
import gzip
import json
import math
import os
import pickle
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "bt_cache", "sw")
WIN = 300
STEP = 100            # ms per grid step
NS = WIN * 1000 // STEP
FEE = 0.07
KFEE = 0.07
FIRST = 120           # no decisions in the first 12 s of a Polymarket window: the box's book feed reconnects there
                      # (about 1 book update in 6 gets through in seconds 1-11), so the recorded book is stale


# ---------------------------------------------------------------- prep
def prep(paths):
    os.makedirs(CACHE, exist_ok=True)
    for p in sorted(paths):
        day = os.path.basename(p).split("-")[1][:8]
        px = collections.defaultdict(list)                       # coin -> [(r, price)]  Binance spot
        wins = collections.defaultdict(lambda: {"bk": [], "tr": []})
        res, cle = {}, {}
        kb, kt, kw, kres = collections.defaultdict(list), collections.defaultdict(list), {}, {}
        with gzip.open(p, "rt") as fh:
            for line in fh:
                k = line[6:9]
                if k not in ('bn"', 'bk"', 'tr"', 'res', 'ax"', 'kb"', 'kt"', 'kw"', 'kre', 'cl"'):
                    continue
                try:
                    o = json.loads(line)
                except ValueError:
                    continue
                k = o["k"]
                if k == "bn":
                    px["btc"].append((o["r"], o["p"]))
                elif k == "cl":
                    px["cl"].append((o["r"], o["p"]))
                    cle[o["e"]] = o["p"]
                elif k == "ax":
                    px[o["s"].lower()].append((o["r"], o["p"]))
                elif k == "bk":
                    if o.get("o") == "Up":
                        wins[(o.get("c", "btc"), o["w"])]["bk"].append((o["r"], o.get("bb") or 0.0, o.get("bs") or 0.0, o.get("ba") or 0.0, o.get("as") or 0.0))
                elif k == "tr":
                    up = o["o"] == "Up"
                    buy = str(o.get("sd")).upper() == "BUY"
                    side = 1 if up == buy else 0                 # 1 = someone bought Up in a hurry (or sold Down)
                    q = o["p"] if up else round(1 - o["p"], 4)
                    wins[(o.get("c", "btc"), o["w"])]["tr"].append((o["r"], side, q, float(o.get("s") or 0)))
                elif k == "res":
                    res[(o.get("c", "btc"), o["w"])] = o["up_won"]
                elif k == "kb":
                    kb[o["t"]].append((o["r"], o.get("yb") or 0.0, o.get("ys") or 0.0, o.get("nb") or 0.0, o.get("ns") or 0.0))
                elif k == "kt":
                    kt[o["t"]].append((o["e"], o["yp"], o["n"], 1 if o.get("tk") == "yes" else 0))
                elif k == "kw":
                    kw[o["t"]] = (o["sr"], o["open"], o["close"], o.get("strike"))
                elif k == "kres":
                    kres[o["t"]] = o["yes"]
        pxa = {c: (np.array([x[0] for x in v], dtype=np.int64), np.array([x[1] for x in v], dtype=np.float64)) for c, v in px.items()}
        keys = sorted(k for k in wins if k in res and len(wins[k]["bk"]) > 50)
        n = len(keys)
        G = {f: np.zeros((n, NS), dtype=np.float32) for f in ("bb", "ba", "bs", "as", "sp", "cl", "bas")}
        G["age"] = np.zeros((n, NS), dtype=np.float32)
        meta = np.zeros((n, 5), dtype=np.float64)                # w, up_won, coin id, start spot, Chainlink at the start
        coins = ["btc", "eth", "sol"]
        trs = []
        for i, key in enumerate(keys):
            c, w = key
            ev = wins[key]["bk"]
            ev.sort(key=lambda x: x[0])
            t = np.array([x[0] for x in ev], dtype=np.int64)
            grid = w * 1000 + np.arange(NS, dtype=np.int64) * STEP
            idx = np.searchsorted(t, grid, side="right") - 1
            arr = np.array([x[1:] for x in ev], dtype=np.float32)
            ok = idx >= 0
            for j, f in enumerate(("bb", "bs", "ba", "as")):
                G[f][i, ok] = arr[idx[ok], j]
            G["age"][i] = 60000
            G["age"][i, ok] = np.minimum(grid[ok] - t[idx[ok]], 60000)   # ms since the last book update we heard
            s0 = 0.0
            if c in pxa and len(pxa[c][0]):
                pt, pp = pxa[c]
                ii = np.searchsorted(pt, grid, side="right") - 1
                G["sp"][i, ii >= 0] = pp[ii[ii >= 0]]
                # spot history of the 15 minutes before, every 5 s, for the swing size
                hg = w * 1000 - np.arange(0, 901, 5, dtype=np.int64) * 1000
                hi = np.searchsorted(pt, hg, side="right") - 1
                hp = np.where(hi >= 0, pp[np.maximum(hi, 0)], 0.0)
                s0 = hp[0]
                good = (hp[:-1] > 0) & (hp[1:] > 0)
                sig = float(np.std(np.log(hp[:-1][good] / hp[1:][good])) / math.sqrt(5)) if good.sum() >= 100 else 0.0
            else:
                sig = 0.0
            if c == "btc" and "cl" in pxa:
                ct, cp = pxa["cl"]
                ii = np.searchsorted(ct, grid, side="right") - 1
                G["cl"][i, ii >= 0] = cp[ii[ii >= 0]]
                # Binance minus Chainlink, middle value of the last 60 s (as known at each step, 1 s samples)
                g1 = w * 1000 - 60000 + np.arange(0, 360000, 1000, dtype=np.int64)
                b1 = np.searchsorted(pt, g1, side="right") - 1
                c1 = np.searchsorted(ct, g1, side="right") - 1
                df = np.where((b1 >= 0) & (c1 >= 0), pp[np.maximum(b1, 0)] - cp[np.maximum(c1, 0)], np.nan)
                for sec in range(WIN):
                    win_ = df[sec:sec + 61]
                    win_ = win_[np.isfinite(win_)]
                    G["bas"][i, sec * 10:(sec + 1) * 10] = np.median(win_) if len(win_) else 0.0
            meta[i] = (w, 1.0 if res[key] else 0.0, coins.index(c), s0, cle.get(w * 1000, 0.0))
            G.setdefault("sig", np.zeros(n, dtype=np.float64))[i] = sig
            tr = wins[key]["tr"]
            tr.sort(key=lambda x: x[0])
            trs.append(np.array([((x[0] - w * 1000), x[1], x[2], x[3]) for x in tr], dtype=np.float32).reshape(-1, 4))
        np.savez_compressed(os.path.join(CACHE, f"{day}.npz"), meta=meta, **G)
        with gzip.open(os.path.join(CACHE, f"{day}.tr.pkl.gz"), "wb") as fh:
            pickle.dump(trs, fh, protocol=4)
        kout = {}
        for tk, v in kb.items():
            if len(v) >= 30:
                c = tk.split("-")[0][2:-3].lower()
                sp = pxa.get(c)
                v.sort()
                rr = np.array([x[0] for x in v], dtype=np.int64)
                spv = None
                if sp is not None and len(sp[0]):
                    ii = np.searchsorted(sp[0], rr, side="right") - 1
                    spv = np.where(ii >= 0, sp[1][np.maximum(ii, 0)], 0.0)
                kout[tk] = {"w": kw.get(tk), "yes": kres.get(tk), "kb": np.array(v, dtype=np.float64), "sp": spv,
                            "kt": np.array(sorted(kt.get(tk, [])), dtype=np.float64).reshape(-1, 4)}
        with gzip.open(os.path.join(CACHE, f"{day}.k.pkl.gz"), "wb") as fh:
            pickle.dump(kout, fh, protocol=4)
        print(day, n, "poly windows", len(kout), "kalshi windows", flush=True)



# ---------------------------------------------------------------- load: every window twice (Up share, Down share)
LEARN = ("20261117", "20261118", "20261119", "20261120", "20261121")      # rules are picked on these days only


def norm_cdf(x):
    return 0.5 * (1 + np.vectorize(math.erf)(x / math.sqrt(2)))


class Data:
    """A = price to buy the share now, B = price to sell it now (0 = nobody there), F = fair price from Binance,
    TH / TL = highest / lowest real trade price in that 0.1 s step (share terms; nan = no trade),
    THB = highest price a hurried BUYER paid, TLS = lowest price a hurried SELLER took. Rows: Up shares, then Down."""

    def __init__(self, coin=0, days=None):
        ms, bbs, bas, sps, sigs, dayi, trs, cls, bss = [], [], [], [], [], [], [], [], []
        ages, szb, sza = [], [], []
        self.days = []
        for f in sorted(glob.glob(os.path.join(CACHE, "*.npz"))):
            day = os.path.basename(f)[:8]
            if days and day not in days:
                continue
            d = np.load(f)
            sel = d["meta"][:, 2] == coin
            if not sel.any():
                continue
            with gzip.open(f[:-4] + ".tr.pkl.gz", "rb") as fh:
                tr = pickle.load(fh)
            self.days.append(day)
            ms.append(d["meta"][sel]); bbs.append(d["bb"][sel]); bas.append(d["ba"][sel]); sps.append(d["sp"][sel])
            cls.append(d["cl"][sel]); bss.append(d["bas"][sel])
            if "age" in d.files:
                ages.append(d["age"][sel]); szb.append(d["bs"][sel]); sza.append(d["as"][sel])
            sigs.append(d["sig"][sel]); dayi += [len(self.days) - 1] * int(sel.sum())
            trs += [tr[i] for i in np.where(sel)[0]]
        meta = np.concatenate(ms); bb = np.concatenate(bbs); ba = np.concatenate(bas); sp = np.concatenate(sps)
        sig = np.concatenate(sigs)
        n = len(meta)
        self.n = n
        self.day = np.concatenate([np.array(dayi), np.array(dayi)])
        self.w = np.concatenate([meta[:, 0], meta[:, 0]])
        up = meta[:, 1]
        self.pay = np.concatenate([up, 1 - up]).astype(np.float32)
        nan = np.float32(np.nan)
        ua = np.where(ba > 0, ba, nan); ub = bb
        da = np.where(bb > 0, 1 - bb, nan); db = np.where(ba > 0, 1 - ba, 0).astype(np.float32)
        self.A = np.concatenate([ua, da]).astype(np.float32)
        self.B = np.concatenate([ub, db]).astype(np.float32)
        left = (NS - np.arange(NS)) * STEP / 1000.0
        s0 = meta[:, 3][:, None]
        with np.errstate(divide="ignore", invalid="ignore"):
            z = np.log(np.where(sp > 0, sp, np.nan) / s0) / (sig[:, None] * np.sqrt(left)[None, :])
            fu = norm_cdf(z).astype(np.float32)
        fu[(sig <= 0) | (meta[:, 3] <= 0)] = nan
        # better: Binance moved onto Chainlink's level (the windows settle on Chainlink), start = Chainlink at the start
        cl = np.concatenate(cls); bs_ = np.concatenate(bss); c0 = meta[:, 4][:, None]
        with np.errstate(divide="ignore", invalid="ignore"):
            z2 = np.log(np.where(sp > 0, sp - bs_, np.nan) / np.where(c0 > 0, c0, np.nan)) / (sig[:, None] * np.sqrt(left)[None, :])
            f2 = norm_cdf(z2).astype(np.float32)
            zc = np.log(np.where(cl > 0, cl, np.nan) / np.where(c0 > 0, c0, np.nan)) / (sig[:, None] * np.sqrt(left)[None, :])
            fc = norm_cdf(zc).astype(np.float32)
        f2[(sig <= 0)] = nan; fc[(sig <= 0)] = nan
        f2 = np.where(np.isfinite(f2), f2, fu)
        self.F = np.concatenate([f2, 1 - f2])                    # fair price from Binance (heard now)
        self.FC = np.concatenate([fc, 1 - fc])                   # fair price from Chainlink's own feed (about 1 s old)
        self.Z = np.concatenate([z, -z]).astype(np.float32)
        th = np.full((n, NS), nan); tl = np.full((n, NS), nan); thb = np.full((n, NS), nan); tls = np.full((n, NS), nan)
        vol = np.zeros((n, NS), dtype=np.float32)
        for i, t in enumerate(trs):
            if not len(t):
                continue
            k = (t[:, 0] // STEP).astype(int)
            ok = (k >= 0) & (k < NS)
            for kk, sd, q, s in zip(k[ok], t[ok, 1], t[ok, 2], t[ok, 3]):
                if not (th[i, kk] >= q): th[i, kk] = q
                if not (tl[i, kk] <= q): tl[i, kk] = q
                if sd > 0.5:
                    if not (thb[i, kk] >= q): thb[i, kk] = q
                else:
                    if not (tls[i, kk] <= q): tls[i, kk] = q
                vol[i, kk] += s
        self.TH = np.concatenate([th, 1 - tl]); self.TL = np.concatenate([tl, 1 - th])
        self.THB = np.concatenate([thb, 1 - tls]); self.TLS = np.concatenate([tls, 1 - thb])
        self.VOL = np.concatenate([vol, vol])
        with np.errstate(invalid="ignore"):
            self.M = np.where((self.B > 0) & np.isfinite(self.A), (self.A + self.B) / 2, nan).astype(np.float32)
        if ages:
            ag = np.concatenate(ages)
            self.AGE = np.concatenate([ag, ag])                  # ms since the box last heard a book update
            self.SZ = np.concatenate([np.concatenate(sza), np.concatenate(szb)])   # shares on offer at the price we would pay
        self.idx = np.arange(NS)[None, :]
        self.rows = np.arange(2 * n)
        self.NS, self.sps, self.first, self.endstop_s = NS, 1000 // STEP, FIRST, 10
        self.lags_s, self.holds_s = (1, 5, 15, 30, 60), (5, 15, 30, 60)
        self.fee = fee
        self.min_maker_d = 1
        lset = set(LEARN) if coin == 0 else {"20261125"}
        self.is_learn = lambda d_: d_ in lset
        self.learn = np.isin(self.day, [i for i, d in enumerate(self.days) if d in lset])



# ---------------------------------------------------------------- Kalshi 15-minute windows
KSERIES = ("KXBTC15M", "KXETH15M", "KXSOL15M", "KXXRP15M", "KXDOGE15M", "KXHYPE15M", "KXBNB15M")


def kfee(p, n=10):
    """Kalshi's fee for buying or selling n contracts in a hurry, per contract (rounded up to a cent an order).
    A waiting order pays nothing on these series."""
    return np.ceil(KFEE * n * p * (1 - p) * 100 - 1e-9) / 100 / n


class _K:
    def finish(self, yb, ya, th, tl, thb, tls, yes, days, dayi, closes):
        nan = np.float32(np.nan)
        n = len(yes)
        self.n, self.days = n, days
        self.w = np.concatenate([closes, closes])
        self.day = np.concatenate([dayi, dayi])
        self.pay = np.concatenate([yes, 1 - yes]).astype(np.float32)
        with np.errstate(invalid="ignore"):
            A1 = np.where((ya > 0) & (ya < 1), ya, nan); B1 = np.where((yb > 0) & (yb < 1), yb, 0)
            A2 = np.where((yb > 0) & (yb < 1), 1 - yb, nan); B2 = np.where((ya > 0) & (ya < 1), 1 - ya, 0)
        self.A = np.concatenate([A1, A2]).astype(np.float32); self.B = np.concatenate([B1, B2]).astype(np.float32)
        self.TH = np.concatenate([th, 1 - tl]).astype(np.float32); self.TL = np.concatenate([tl, 1 - th]).astype(np.float32)
        self.THB = np.concatenate([thb, 1 - tls]).astype(np.float32); self.TLS = np.concatenate([tls, 1 - thb]).astype(np.float32)
        with np.errstate(invalid="ignore"):
            self.M = np.where((self.B > 0) & np.isfinite(self.A), (self.A + self.B) / 2, nan).astype(np.float32)
        self.idx = np.arange(self.NS)[None, :]
        self.rows = np.arange(2 * n)
        self.fee = kfee
        self.learn = np.isin(self.day, [i for i, d in enumerate(days) if self.is_learn(d)])


class KMin(_K):
    """Kalshi, 12 Sep - 9 Nov, one look a minute (kspeed's candles: best bid / ask at each minute's end, and the
    lowest / highest trade inside the minute). 15 steps a window; nothing is traded at the last one."""

    def __init__(self, series=KSERIES):
        import time as _t
        self.NS, self.sps, self.first, self.endstop_s, self.min_maker_d = 15, 1 / 60, 0, 60, 1
        self.lags_s, self.holds_s = (60, 120, 180, 300), (60, 120, 180, 300)
        rows = []
        for sr in series:
            with gzip.open(os.path.join(HERE, "bt_cache", "kc", f"markets_{sr}.json.gz"), "rt") as fh:
                ms = json.load(fh)
            with gzip.open(os.path.join(HERE, "bt_cache", "ks", f"full_{sr}.json.gz"), "rt") as fh:
                cs = json.load(fh)
            for m in ms:
                c = cs.get(m["t"])
                if not c or len(c) < 12 or m.get("res") not in ("yes", "no"):
                    continue
                g = np.full((4, 15), np.nan, dtype=np.float32)
                for r in c:
                    j = (r[0] - m["open"]) // 60 - 1
                    if 0 <= j < 15:
                        for q in range(4):
                            if r[1 + q] is not None:
                                g[q, j] = r[1 + q]
                rows.append((m["close"], g, 1.0 if m["res"] == "yes" else 0.0))
        rows.sort(key=lambda x: x[0])
        dn = [_t.strftime("%Y%m%d", _t.gmtime(r[0])) for r in rows]
        days = sorted(set(dn))
        half = days[len(days) // 2]
        self.is_learn = lambda d_: d_ < half
        G = np.stack([r[1] for r in rows])
        yb, ya, lo, hi = G[:, 0], G[:, 1], G[:, 2], G[:, 3]
        yes = np.array([r[2] for r in rows])
        dayi = np.array([days.index(d_) for d_ in dn])
        # the candle does not say who was in a hurry: the "lucky" fill = a trade AT our price
        self.finish(yb, ya, hi, lo, hi, lo, yes, days, dayi, np.array([r[0] for r in rows], dtype=np.float64))


class KSec(_K):
    """Kalshi, 25-26 Nov, from the speed box: best bid / ask every 10 s (every second in the last 7 minutes) and
    every trade. 900 steps of one second."""

    def __init__(self):
        self.NS, self.sps, self.first, self.endstop_s, self.min_maker_d = 900, 1, 15, 10, 1
        self.lags_s, self.holds_s = (10, 30, 60, 120), (15, 30, 60, 120)
        self.is_learn = lambda d_: d_ == "20261125"
        Y, Aa, TH, TL, THB, TLS, yes, dn, cl_ = [], [], [], [], [], [], [], [], []
        self.guess = 0
        for f in sorted(glob.glob(os.path.join(CACHE, "*.k.pkl.gz"))):
            with gzip.open(f, "rb") as fh:
                kk = pickle.load(fh)
            for tk, v in kk.items():
                kb = v["kb"]
                op = int(kb[len(kb) // 2, 0] // 900000) * 900
                if v["w"] and abs(v["w"][1] - op) > 1:
                    op = int(v["w"][1])
                res = v["yes"]
                if res is None:
                    last = kb[-1]
                    if kb[-1, 0] < (op + 880) * 1000:
                        continue
                    if last[1] >= 0.9:
                        res = True
                    elif last[3] >= 0.9:
                        res = False
                    else:
                        continue
                    self.guess += 1
                grid = (op + np.arange(900)) * 1000 + 999
                ii = np.searchsorted(kb[:, 0], grid, side="right") - 1
                if (ii >= 0).sum() < 600:
                    continue
                yb = np.where(ii >= 0, kb[np.maximum(ii, 0), 1], 0); nb = np.where(ii >= 0, kb[np.maximum(ii, 0), 3], 0)
                th = np.full(900, np.nan); tl = np.full(900, np.nan); thb = np.full(900, np.nan); tls = np.full(900, np.nan)
                for e, yp, n_, ty in v["kt"]:
                    j = int(e // 1000) - op
                    if 0 <= j < 900:
                        if not th[j] >= yp: th[j] = yp
                        if not tl[j] <= yp: tl[j] = yp
                        if ty > 0.5:
                            if not thb[j] >= yp: thb[j] = yp
                        else:
                            if not tls[j] <= yp: tls[j] = yp
                Y.append(yb); Aa.append(np.where(nb > 0, 1 - nb, 0)); TH.append(th); TL.append(tl); THB.append(thb); TLS.append(tls)
                yes.append(1.0 if res else 0.0); dn.append(os.path.basename(f)[:8]); cl_.append(op + 900.0 + KSERIES.index(tk.split('-')[0]) * 0.001)
        days = sorted(set(dn))
        self.finish(np.array(Y), np.array(Aa), np.array(TH), np.array(TL), np.array(THB), np.array(TLS), np.array(yes), days,
                    np.array([days.index(d_) for d_ in dn]), np.array(cl_))


def fee(p):
    return FEE * p * (1 - p)


def lag(X, k):
    """X as it was k steps ago (nan before that)."""
    out = np.full_like(X, np.nan)
    if k < X.shape[1]:
        out[:, k:] = X[:, :-k] if k else X
    return out


def first_true(mask):
    return mask.any(1), mask.argmax(1)


def exits(D, te, p, live, tp=0.0, sl=0.0, hold=0, endstop=0, d=10, mk_tp=False, lucky=False, fstop=None):
    """Sell a share bought at step te for p. Returns (value got per share, exit step, kind) for rows in `live`.
    tp: sell when the bid is p + tp (mk_tp: a waiting sell offer at p + tp instead, no fee)
    sl: sell at the bid when it falls to p - sl;  hold: sell after this many steps;  endstop: sell this many steps
    before the end;  nothing fires -> held to the end and paid $1 or $0."""
    N = len(p)
    idx = D.idx
    after = idx > te[:, None]
    cond = np.zeros(D.B.shape, dtype=bool)
    if tp and not mk_tp:
        cond |= D.B >= (p + tp - 1e-6)[:, None]
    if sl:
        cond |= D.B <= (p - sl + 1e-6)[:, None]
    if hold:
        cond |= idx >= (te + hold)[:, None]
    if endstop:
        cond |= idx >= D.NS - endstop
    if fstop is not None:
        cond |= fstop
    cond &= after
    hx, u = first_true(cond)
    ux = np.where(hx, u + d, D.NS + 5)
    uxc = np.minimum(ux, D.NS - 1)
    s = D.B[D.rows, uxc]
    sold = hx & (ux < D.NS) & (s > 0)
    val = np.where(sold, s - D.fee(s), D.pay)
    xt = np.where(sold, ux, D.NS)
    kind = np.where(sold, 1, 0)                                   # 1 = sold at the bid, 0 = held to the end
    if mk_tp and tp:
        q = np.round(p + tp, 3)
        placed = idx >= (te + max(d, D.min_maker_d))[:, None]
        with np.errstate(invalid="ignore"):
            if lucky:
                fm = (D.B >= q[:, None] - 1e-6) | (D.THB >= q[:, None] - 1e-6)
            else:
                fm = (D.B >= q[:, None] - 1e-6) | (D.TH > q[:, None] + 1e-6)
        fm &= placed
        hm, um = first_true(fm)
        mfirst = hm & (um <= xt) & (q < 1.0)
        val = np.where(mfirst, q, val)
        xt = np.where(mfirst, um, xt)
        kind = np.where(mfirst, 2, kind)                          # 2 = our waiting offer was taken
    return val, xt, kind


def run_taker(D, mask, t0=0, t1=None, d=10, slip=0.0, rounds=1, guard=None, **ex):
    """Buy at the ask when `mask` is true (decided at step t, traded at t + d, only if the ask then is at most
    the ask seen + slip), then leave by `exits`. Returns a dict of arrays, one row per finished trade."""
    NS = D.NS
    t1 = NS - 2 if t1 is None else t1
    start = np.full(len(D.rows), t0)
    out = collections.defaultdict(list)
    miss = 0
    done = np.zeros(len(D.rows), dtype=int)
    for _ in range(rounds * 3):
        start = np.where(done >= rounds, NS + 1, start)
        m = mask & (D.idx >= start[:, None]) & (D.idx <= t1)
        has, t = first_true(m)
        if not has.any():
            break
        te = np.minimum(t + d, NS - 1)
        p0 = D.A[D.rows, t]; p = D.A[D.rows, te]
        with np.errstate(invalid="ignore"):
            ok = has & (t + d < NS - 1) & np.isfinite(p) & (p <= p0 + slip + 1e-6) & (p > 0) & (p < 1)
        if guard is not None:
            ok &= guard[D.rows, te]                             # e.g. the book was fresh and big enough when we traded
        miss += int((has & ~ok).sum())
        pz = np.where(ok, p, 0.5)
        val, xt, kind = exits(D, te, pz, ok, d=d, **ex)
        r = np.where(ok)[0]
        out["row"].append(r); out["te"].append(te[r]); out["p"].append(pz[r]); out["val"].append(val[r])
        out["xt"].append(xt[r]); out["kind"].append(kind[r]); out["cost"].append(pz[r] + D.fee(pz[r]))
        start = np.where(ok, xt + 1, np.where(has, te + 1, NS + 1))
        done += ok
    res = {k: (np.concatenate(v) if v else np.array([])) for k, v in out.items()}
    res["miss"] = miss
    return res


def run_maker(D, Q, d=10, lucky=False, rounds=1, t0=0, **ex):
    """A waiting BUY order at Q[row, step] (nan = no order), as decided from what was known d steps earlier.
    Filled the first time a real trade prints below it (or the ask comes down to it). No fee on the buy."""
    NS = D.NS
    QL = lag(Q, max(d, D.min_maker_d))
    start = np.full(len(D.rows), t0)
    out = collections.defaultdict(list)
    for _ in range(rounds):
        with np.errstate(invalid="ignore"):
            if lucky:
                fm = (D.A <= QL + 1e-6) | (D.TLS <= QL + 1e-6)
            else:
                fm = (D.A <= QL + 1e-6) | (D.TL < QL - 1e-6)
        fm &= (D.idx >= start[:, None]) & (D.idx < NS - 1 - D.first)
        has, t = first_true(fm)
        if not has.any():
            break
        p = np.where(has, QL[D.rows, t], 0.5)
        val, xt, kind = exits(D, t, p, has, d=d, lucky=lucky, **ex)
        r = np.where(has)[0]
        out["row"].append(r); out["te"].append(t[r]); out["p"].append(p[r]); out["val"].append(val[r])
        out["xt"].append(xt[r]); out["kind"].append(kind[r]); out["cost"].append(p[r])
        start = np.where(has, xt + 1, NS + 1)
    res = {k: (np.concatenate(v) if v else np.array([])) for k, v in out.items()}
    res["miss"] = 0
    return res


def score(D, res, shares=10):
    """Plain numbers for one rule: bets, profit per $100 put down, dollars a day at `shares` a bet, by part of the data."""
    if "row" not in res or not len(res["row"]):
        return None
    pnl = (res["val"] - res["cost"]) * shares
    cost = res["cost"] * shares
    lr = D.learn[res["row"]]
    LEARN = [d_ for d_ in D.days if D.is_learn(d_)]
    dd = D.day[res["row"]]
    byday = np.array([pnl[dd == i].sum() for i in range(len(D.days))])
    ndl = sum(1 for d_ in D.days if d_ in LEARN); ndf = len(D.days) - ndl
    def per100(s):
        return float(pnl[s].sum() / cost[s].sum() * 100) if s.any() else 0.0
    return {"n": len(pnl), "n_learn": int(lr.sum()), "n_fresh": int((~lr).sum()),
            "per100_learn": per100(lr), "per100_fresh": per100(~lr), "per100": per100(np.ones(len(pnl), bool)),
            "day_learn": float(pnl[lr].sum() / max(ndl, 1)), "day_fresh": float(pnl[~lr].sum() / max(ndf, 1)),
            "worst_day": float(byday.min()), "best_day": float(byday.max()), "days_up": int((byday > 0).sum()),
            "win": float((pnl > 0).mean()), "avg_cost": float(cost.mean()),
            "held": float((res["kind"] == 0).mean()), "mk": float((res["kind"] == 2).mean()),
            "hold_s": float(np.mean(res["xt"] - res["te"]) / D.sps), "miss": res["miss"], "byday": byday}




# ---------------------------------------------------------------- the grid: every family of rule
def cents(x):
    return f"{int(round(x * 100))}c"


def secs(x):
    return f"{int(x)}s" if x < 120 else f"{int(x / 60)}min"


def taker_exits(D):
    S = lambda sec: max(1, int(round(sec * D.sps)))
    es = int(D.endstop_s * D.sps)
    out = [("hold to the end", {})]
    out += [(f"sell after {secs(h)}", {"hold": S(h)}) for h in D.holds_s]
    out += [(f"sell at +{cents(tp)} / stop -{cents(sl)}", {"tp": tp, "sl": sl, "endstop": es})
            for tp, sl in ((.03, .03), (.05, .05), (.10, .05), (.05, .10), (.10, .10), (.20, .10))]
    out += [(f"offer at +{cents(tp)}" + (f" / stop -{cents(sl)}" if sl else " / else hold"), {"tp": tp, "sl": sl, "mk_tp": True})
            for tp in (.02, .03, .05, .10) for sl in (0, .05, .10)]
    out += [(f"offer at +{cents(tp)} / out after {secs(D.holds_s[-1])}", {"tp": tp, "hold": S(D.holds_s[-1]), "mk_tp": True}) for tp in (.02, .05)]
    out += [(f"stop -{cents(sl)} / else hold", {"sl": sl}) for sl in (.05, .10, .20, .30)]
    out += [(f"sell at +{cents(tp)} / else hold", {"tp": tp}) for tp in (.05, .10, .20)]
    return out


def maker_exits(D):
    S = lambda sec: max(1, int(round(sec * D.sps)))
    out = [("hold to the end", {})]
    out += [(f"offer at +{cents(tp)}" + (f" / stop -{cents(sl)}" if sl else " / else hold"), {"tp": tp, "sl": sl, "mk_tp": True})
            for tp in (.01, .02, .03, .05, .10) for sl in (0, .03, .05, .10)]
    out += [(f"offer at +{cents(tp)} / out after {secs(h)}", {"tp": tp, "hold": S(h), "mk_tp": True})
            for tp in (.01, .02, .05) for h in (D.holds_s[1], D.holds_s[-1])]
    out += [(f"sell after {secs(h)}", {"hold": S(h)}) for h in (D.holds_s[0], D.holds_s[-2])]
    out += [(f"stop -{cents(sl)} / else hold", {"sl": sl}) for sl in (.05, .10, .20, .30)]
    out += [(f"sell at +{cents(tp)} / else hold", {"tp": tp}) for tp in (.05, .10, .20)]
    return out


def taker_masks(D):
    """(family, name, mask). The mask says 'buy this share now' from what was known at that step."""
    A, B, M, idx, NS = D.A, D.B, D.M, D.idx, D.NS
    F, FC = getattr(D, "F", None), getattr(D, "FC", None)
    S = lambda sec: max(1, int(round(sec * D.sps)))
    with np.errstate(invalid="ignore"):
        band = (A >= 0.08) & (A <= 0.92) & (idx >= D.first) & (idx <= NS - 1 - S(D.endstop_s * 3))
        if F is not None:
            for x in (.03, .05, .08, .12, .20):
                yield "cheap vs Binance", f"ask {cents(x)}+ under the Binance fair price", band & (A <= F - x)
                if FC is not None:
                    yield "cheap vs Chainlink", f"ask {cents(x)}+ under the Chainlink fair price", band & (A <= FC - x)
        for hs in D.lags_s:
            h = S(hs)
            dM = M - lag(M, h)
            dF = (F - lag(F, h)) if F is not None else None
            for x in (.05, .08, .12, .20):
                yield "buy the dip", f"fell {cents(x)}+ in {secs(hs)}", band & (dM <= -x)
                if dF is not None:
                    yield "buy the dip, coin calm", f"fell {cents(x)}+ in {secs(hs)}, fair price fell under a third of that", band & (dM <= -x) & (dF >= -x / 3)
                yield "follow the move", f"rose {cents(x)}+ in {secs(hs)}", band & (dM >= x)
        if F is not None:
            for x in (.04, .06, .10, .15):
                for hs in (1, 2, 5):
                    h = S(hs)
                    yield "coin moved, share did not", f"fair +{cents(x)} in {secs(hs)}, share under half of that", band & (F - lag(F, h) >= x) & (M - lag(M, h) < x / 2)
        for fr in (.04, .2, .4, .6, .8):
            t = int(fr * NS)
            for lo, hi in ((.08, .30), (.30, .45), (.45, .55), (.55, .70), (.70, .92)):
                yield "time and price", f"at {secs(t / D.sps)}, ask {cents(lo)}-{cents(hi)}", (idx == t) & (A >= lo) & (A < hi)


def maker_quotes(D):
    """(family, name, Q). Q = the price of our waiting buy order at each step (nan = none)."""
    A, B, M, idx, NS = D.A, D.B, D.M, D.idx, D.NS
    F = getattr(D, "F", None)
    S = lambda sec: max(1, int(round(sec * D.sps)))
    nan = np.float32(np.nan)
    last = NS - 1 - S(D.endstop_s * 3)
    with np.errstate(invalid="ignore"):
        band = (B >= 0.08) & (B <= 0.92) & (idx >= D.first) & (idx <= last)
        for k in (0, .01, .02, .03, .05, .08):
            yield "bid under the price", f"bid {cents(k)} under the best bid", np.where(band, np.round(B - k, 2), nan)
        if F is not None:
            for k in (.03, .05, .08, .12):
                q = np.floor(np.minimum(B, F - k) * 100) / 100
                yield "bid under Binance fair", f"bid {cents(k)} under the Binance fair price (never above the best bid)", np.where(band & (q > 0.02), q, nan)
        for hs in D.lags_s[1:4]:
            h = S(hs)
            for x in (.05, .10):
                dM = M - lag(M, h)
                yield "bid after a fall", f"join the best bid after a {cents(x)}+ fall in {secs(hs)}", np.where(band & (dM <= -x), B, nan)
                yield "bid after a rise", f"join the best bid after a {cents(x)}+ rise in {secs(hs)}", np.where(band & (dM >= x), B, nan)
        for q in (.20, .30, .35, .40, .44, .47, .49):
            for fr in (.1, .9):
                yield "fixed bids on both sides", f"bid {cents(q)} on both sides, first {secs(fr * NS / D.sps)}", np.where((idx >= D.first) & (idx <= int(fr * NS)), np.float32(q), nan) + 0 * A
        for lo, hi in ((.10, .30), (.30, .45), (.45, .55), (.55, .70), (.70, .90)):
            yield "join the bid by price", f"join the best bid while it is {cents(lo)}-{cents(hi)}", np.where(band & (B >= lo) & (B < hi), B, nan)
        for lo, hi in ((.80, .90), (.88, .97)):
            for fr in (.5, .8):
                yield "late favourite bid", f"join the best bid at {cents(lo)}-{cents(hi)} in the last {secs((1 - fr) * NS / D.sps)}", np.where((B >= lo) & (B <= hi) & (idx >= int(fr * NS)) & (idx <= last), B, nan)
        for a, b in ((0, .3), (.3, .6), (.6, .9)):
            yield "join the bid by time", f"join the best bid, {secs(a * NS / D.sps)}-{secs(b * NS / D.sps)}", np.where((B >= 0.08) & (B <= 0.92) & (idx >= max(D.first, int(a * NS))) & (idx <= int(b * NS)), B, nan)


_D = None


def _one(job):
    kind, fam, name, ex_name, ex, d, lucky, key = job
    D = _D
    if kind == "T":
        r = run_taker(D, _MASKS[key], d=d, **ex, **({"lucky": True} if lucky else {}))
    else:
        r = run_maker(D, _QS[key], d=d, lucky=lucky, **ex)
    sc = score(D, r)
    if sc is None:
        return None
    sc["byday"] = [round(float(x), 2) for x in sc["byday"]]
    sc.update({"kind": kind, "family": fam, "rule": name, "exit": ex_name, "delay": d / D.sps, "lucky": lucky})
    return sc


def grid(D, out, delays_s):
    global _D, _MASKS, _QS
    import multiprocessing as mp
    _D = D
    _MASKS = {(f, n): m for f, n, m in taker_masks(D)}
    _QS = {(f, n): q for f, n, q in maker_quotes(D)}
    jobs = []
    for d_s in delays_s:
        d = int(round(d_s * D.sps))
        for (f, n) in _MASKS:
            for en, ex in taker_exits(D):
                jobs.append(("T", f, n, en, ex, d, False, (f, n)))
                if ex.get("mk_tp"):
                    jobs.append(("T", f, n, en, ex, d, True, (f, n)))
        for (f, n) in _QS:
            for en, ex in maker_exits(D):
                for lucky in (False, True):
                    jobs.append(("M", f, n, en, ex, d, lucky, (f, n)))
    print(out, len(jobs), "rules to test on", D.n, "windows,", len(D.days), "days", flush=True)
    with mp.get_context("fork").Pool(4) as pool:
        rows = [r for r in pool.imap_unordered(_one, jobs, chunksize=8) if r]
    with open(os.path.join(CACHE, f"{out}.json"), "w") as fh:
        json.dump({"days": D.days, "learn": [d_ for d_ in D.days if D.is_learn(d_)], "windows": D.n, "rows": rows}, fh)
    print("saved", len(rows), flush=True)


# ---------------------------------------------------------------- one rule again, as exam bets
def find_rule(D, kind, family, rule):
    gen = taker_masks(D) if kind == "T" else maker_quotes(D)
    for f, n, x in gen:
        if f == family and n == rule:
            return x
    raise KeyError(rule)


def rerun(D, row):
    ex = dict(taker_exits(D) if row["kind"] == "T" else maker_exits(D))[row["exit"]]
    d = int(round(row["delay"] * D.sps))
    x = find_rule(D, row["kind"], row["family"], row["rule"])
    if row["kind"] == "T":
        return run_taker(D, x, d=d, **ex, **({"lucky": True} if row["lucky"] else {}))
    return run_maker(D, x, d=d, lucky=row["lucky"], **ex)


def exam_bets(D, res, fresh_only=True, shares=10):
    """One exam bet per trade; trades in the same window (either side, any coin of that quarter hour) are one event."""
    out = []
    for r, c, v in zip(res["row"], res["cost"], res["val"]):
        if fresh_only and D.learn[r]:
            continue
        w = float(D.w[r])
        out.append({"cost": float(c) * shares, "pay": float(v) * shares, "ev": int(w), "t": w, "sh": shares})
    return out

# ---------------------------------------------------------------- facts
def facts(coin=0):
    D = Data(coin)
    n = D.n
    A, B, M = D.A[:n], D.B[:n], D.M[:n]
    print(f"{('Bitcoin', 'ETH', 'SOL')[coin]}: {n:,} windows, {D.days[0]} to {D.days[-1]}")
    print("\nA round trip (buy now, sell right away) costs, per share, by price of the share:")
    for lo, hi in ((0.05, 0.2), (0.2, 0.4), (0.4, 0.6), (0.6, 0.8), (0.8, 0.95)):
        s = (M >= lo) & (M < hi)
        gap = (A - B)[s]
        f2 = (fee(A) + fee(B))[s]
        print(f"  {lo:.2f}-{hi:.2f}: gap {gap.mean()*100:.2f}c + fees {f2.mean()*100:.2f}c = {(gap+f2).mean()*100:.2f}c   (with a waiting sell order on the way out: {(gap + fee(A)[s]).mean()*100:.2f}c)")
    print("\nHow far the middle price moves (average size of the move, cents):")
    for h in (10, 50, 150, 300, 600, 1200):
        dM = M[:, h:] - M[:, :-h]
        print(f"  over {h/10:>5.0f} s: {np.nanmean(np.abs(dM))*100:.2f}c   moves of 5c+: {np.nanmean(np.abs(dM) >= 0.05)*100:.1f} in 100")
    print("\nDoes a move keep going or bounce back? (next move as a share of the last move; + = keeps going, - = bounces)")
    for h in (10, 30, 50, 150, 300, 600):
        past = M[:, h:-h] - M[:, :-2 * h]
        nxt = M[:, 2 * h:] - M[:, h:-h]
        ok = np.isfinite(past) & np.isfinite(nxt)
        big = ok & (np.abs(past) >= 0.05)
        b_all = (past[ok] * nxt[ok]).sum() / (past[ok] ** 2).sum()
        b_big = (past[big] * nxt[big]).sum() / (past[big] ** 2).sum()
        print(f"  {h/10:>4.0f} s then {h/10:>4.0f} s: all moves {b_all:+.3f}, moves of 5c+ {b_big:+.3f}  ({int(big.sum())} looks)")
    print("\nWhen the share is X cents under the Binance fair price, how much of the gap closes? (middle price, no costs)")
    F = D.F[:n]
    gapv = F - M
    for h in (10, 50, 150, 300, 600):
        nxt = M[:, h:] - M[:, :-h]
        g = gapv[:, :-h]
        for lo, hi in ((0.03, 0.06), (0.06, 0.10), (0.10, 0.30)):
            s = np.isfinite(nxt) & np.isfinite(g) & (np.abs(g) >= lo) & (np.abs(g) < hi) & (M[:, :-h] > 0.1) & (M[:, :-h] < 0.9)
            mv = (np.sign(g[s]) * nxt[s]).mean() * 100 if s.any() else float("nan")
            print(f"  gap {lo*100:.0f}-{hi*100:.0f}c, {h/10:>3.0f} s later: {mv:+.2f}c toward fair ({int(s.sum())} looks)", end=";")
        print()


# ---------------------------------------------------------------- report
SETS = (("btc", "Polymarket Bitcoin 5-minute, 17-26 Nov (10 looks a second)"),
        ("eth", "Polymarket ETH 5-minute, 25-26 Nov"),
        ("sol", "Polymarket SOL 5-minute, 25-26 Nov"),
        ("ksec", "Kalshi 15-minute, 7 coins, 25-26 Nov (a look every 1-10 s)"),
        ("kmin", "Kalshi 15-minute, 7 coins, 12 Sep - 9 Nov (a look a minute)"))
SPEED = "coin moved, share did not"


def usd(x):
    return f"{'+' if x >= 0 else '-'}${abs(x):.2f}"


def load_grid(name):
    p = os.path.join(CACHE, f"grid_{name}.json")
    if not os.path.exists(p):
        return None
    with open(p) as fh:
        return json.load(fh)


def tables():
    import statistics
    L = []
    best = {}
    for name, title in SETS:
        g = load_grid(name)
        if not g:
            continue
        R = g["rows"]
        nd_l = len(g["learn"]); nd_f = len(g["days"]) - nd_l
        minn = 100 if name in ("btc", "kmin") else 40
        L += [f"### {title}", "",
              f"{g['windows']:,} windows, {len(R):,} rule versions. Rules were looked at on the first {nd_l} day(s) and checked on the other {nd_f}.", "",
              "| Kind of rule | Versions | Ahead on the first days | ...and still ahead on the fresh days | Middle version, fresh days, per $100 | Best version on the first days: what it then did on fresh days |",
              "|---|---|---|---|---|---|"]
        groups = collections.defaultdict(list)
        for r in R:
            if r["n_learn"] < minn or r["n_fresh"] < minn:
                continue
            how = "buy at the offer" if r["kind"] == "T" else ("waiting bid, sure fills only" if not r["lucky"] else "waiting bid, always first in line (hopeful)")
            if r["kind"] == "T" and r["lucky"]:
                continue
            groups[(how, r["family"])].append(r)
        for (how, fam), v in sorted(groups.items()):
            pos = [x for x in v if x["per100_learn"] > 0]
            both = [x for x in pos if x["per100_fresh"] > 0]
            b = max(v, key=lambda x: x["per100_learn"])
            L.append(f"| {fam} ({how}) | {len(v)} | {len(pos)} | {len(both)} | {usd(statistics.median(x['per100_fresh'] for x in v))} | {usd(b['per100_learn'])} then {usd(b['per100_fresh'])} ({b['rule']}; {b['exit']}) |")
            if fam != SPEED and not b["lucky"]:
                k = (name, "T" if how.startswith("buy") else "M")
                if k not in best or b["per100_learn"] > best[k]["per100_learn"]:
                    best[k] = b
        allv = [x for v in groups.values() for x in v if x["family"] != SPEED and not (x["kind"] == "M" and x["lucky"])]
        pos = [x for x in allv if x["per100_learn"] > 0]
        L += ["", f"Without the speed family and the hopeful fills: {len(allv):,} versions, {len(pos)} ahead on the first days, "
              f"{sum(1 for x in pos if x['per100_fresh'] > 0)} of those still ahead on the fresh days, {sum(1 for x in allv if x['per100_fresh'] > 0)} ahead on the fresh days at all.", ""]
    return L, best


NICE = {"btc": "Polymarket BTC", "eth": "Polymarket ETH", "sol": "Polymarket SOL", "ksec": "Kalshi, by the second", "kmin": "Kalshi, by the minute"}


def exit_table():
    import statistics
    L = ["| Data | Way out | Rules | Against just holding to the end, per $100 (middle rule) | Better than holding in |", "|---|---|---|---|---|"]
    for name, title in SETS:
        g = load_grid(name)
        if not g:
            continue
        R = g["rows"]
        base = {(r["kind"], r["lucky"], r["rule"], r["delay"]): r for r in R if r["exit"] == "hold to the end"}
        diff = collections.defaultdict(list)
        for r in R:
            b = base.get((r["kind"], False, r["rule"], r["delay"]))
            if not b or r["exit"] == "hold to the end" or b["n"] < 200 or r["family"] == SPEED:
                continue
            if r["kind"] == "M" and r["lucky"]:
                continue                                       # the buy side stays "sure fills"; only the way out varies
            ex = r["exit"]
            if ex.startswith("sell after"):
                k = "sell after a set time (5 s to 5 min)"
            elif ex.startswith("stop"):
                k = "stop-loss only (sell if it falls 5-30c)"
            elif ex.startswith("sell at +") and "stop" in ex:
                k = "take profit + stop-loss, selling at the bid"
            elif ex.startswith("sell at +"):
                k = "take profit only, selling at the bid"
            elif r["kind"] == "T" and r["lucky"]:
                k = "waiting sell offer 1-10c higher, hopeful fills (always first in line)"
            else:
                k = "waiting sell offer 1-10c higher, sure fills only"
            diff[k].append(r["per100"] - b["per100"])
        for k, v in sorted(diff.items()):
            L.append(f"| {NICE[name]} | {k} | {len(v)} | {usd(statistics.median(v))} | {sum(1 for x in v if x > 0)} of {len(v)} |")
    return L


def speed_table():
    g = load_grid("btc")
    L = []
    if not g:
        return L
    R = [r for r in g["rows"] if r["family"] == SPEED and not r["lucky"]]
    L += ["| Rule | Way out | Bets (first / fresh days) | Per $100 first days | Per $100 fresh days | A day at 10 shares a bet, fresh days | Worst day | Bets won | Seconds held |", "|---|---|---|---|---|---|---|---|---|"]
    rule = "fair +6c in 2s, share under half of that"
    for r in sorted([x for x in R if x["rule"] == rule], key=lambda x: -x["per100_fresh"]):
        L.append(f"| {r['rule']} | {r['exit']} | {r['n_learn']} / {r['n_fresh']} | {usd(r['per100_learn'])} | {usd(r['per100_fresh'])} | {usd(r['day_fresh'])} | {usd(r['worst_day'])} | {r['win']*100:.0f} in 100 | {r['hold_s']:.0f} |")
    return L


def stop_table():
    L = ["| Data | Bet | Way out | Bets | Per $100 | Worst day at 10 shares a bet |", "|---|---|---|---|---|---|"]
    for name in ("kmin", "ksec", "btc"):
        g = load_grid(name)
        if not g:
            continue
        for r in sorted(g["rows"], key=lambda x: (x["rule"], x["delay"], -x["per100"])):
            if r["family"] != "late favourite bid" or r["lucky"] or (name == "kmin" and r["delay"] > 0):
                continue
            if not (r["exit"] == "hold to the end" or r["exit"].startswith("stop")):
                continue
            if "88c-97c" not in r["rule"]:
                continue
            L.append(f"| {NICE[name]} | {r['rule']} | {r['exit']} | {r['n']:,} | {usd(r['per100'])} | {usd(r['worst_day'])} |")
    return L


def report_data():
    """Everything the report needs that is not in the grid files, printed for the write-up."""
    L, best = tables()
    print("\n".join(L))
    print("\n".join(exit_table()))
    print("\n".join(speed_table()))
    print("\n".join(stop_table()))
    return best


def exams():
    """The shared exam (exam.py) on the fresh days only: per data set, the rule that was best on the first days."""
    sys.path.insert(0, HERE)
    import exam
    _, best = tables()
    cards = []
    made = {}

    def data(name):
        if name not in made:
            made[name] = KMin() if name == "kmin" else KSec() if name == "ksec" else Data(("btc", "eth", "sol").index(name))
        return made[name]

    for name in ("btc", "ksec", "kmin"):
        g = load_grid(name)
        minn = 100 if name in ("btc", "kmin") else 40
        real = [r for r in g["rows"] if r["family"] != SPEED and not r["lucky"] and r["held"] < 0.5
                and r["n_learn"] >= minn and r["n_fresh"] >= minn]
        row = max(real, key=lambda r: r["per100_learn"])        # picked on the first days only
        D = data(name)
        res = rerun(D, row)
        how = "buy at the offer" if row["kind"] == "T" else "waiting bid"
        c = exam.score(exam_bets(D, res), f"Buy and sell inside the window, {name}: best of {len(real)} rules on the first days, graded on fresh days ({how}; {row['rule']}; {row['exit']})",
                       tries=len(g["rows"]), src="swing.py exams", status="dropped")
        cards.append((name, how, row, c))
    g = load_grid("btc")
    D = data("btc")
    for ex in ("sell after 60s", "hold to the end"):
        row = [r for r in g["rows"] if r["family"] == SPEED and r["rule"] == "fair +6c in 2s, share under half of that" and r["exit"] == ex and not r["lucky"]][0]
        res = rerun(D, row)
        c = exam.score(exam_bets(D, res), f"Speed buy on BTC 5-min 1 s late (not in the first 12 s), {ex}, fresh days, PAPER fills",
                       tries=len(g["rows"]), src="swing.py exams", status="open")
        cards.append(("btc", "speed", row, c))
    with open(os.path.join(CACHE, "exams.json"), "w") as fh:
        json.dump([{"set": a, "how": b, "rule": r["rule"], "exit": r["exit"], "learn": r["per100_learn"], "fresh": r["per100_fresh"],
                    "card": {k: v for k, v in c.items() if isinstance(v, (int, float, str, bool, type(None)))}} for a, b, r, c in cards], fh)
    return cards


def speed():
    """The one family that is ahead on paper (the coin jumped, the share has not moved yet): harder and harder
    conditions, and three ways out. Rules on the first 5 days, check on the other 5."""
    D = Data(0)
    A, B, M, F, idx = D.A, D.B, D.M, D.F, D.idx
    S = lambda sec: int(sec * D.sps)
    L = ["| Rule | Bought | Way out | Bets a day | Per $100, first days | Per $100, fresh days | A day at 10 shares, fresh days | Worst day | Days ahead |", "|---|---|---|---|---|---|---|---|---|"]
    with np.errstate(invalid="ignore"):
        band = (A >= 0.08) & (A <= 0.92) & (idx >= D.first) & (idx <= D.NS - 301)
        base = band & (F - lag(F, 20) >= .06) & (M - lag(M, 20) < .03)
        fresh = D.AGE < 1000
        big = D.SZ >= 20
    rows = []
    for dname, d in (("0.5 s late", 5), ("1 s late", 10), ("2 s late", 20), ("5 s late", 50)):
        for gname, mask, guard in (("any offer still there", base, None),
                                   ("book heard in the last second", base & fresh, fresh),
                                   ("...and 20+ shares on offer", base & fresh & big, fresh & big)):
            for ename, ex in (("hold to the end", {}), ("sell after 60s", {"hold": S(60)}), ("sell after 15s", {"hold": S(15)}),
                              ("sell at +10c / stop -10c", {"tp": .10, "sl": .10, "endstop": 100})):
                r = run_taker(D, mask, d=d, guard=guard, **ex)
                sc = score(D, r)
                if not sc:
                    continue
                nd = len(D.days)
                L.append(f"| coin's fair price +6c in 2 s, share moved under 3c | {dname}, {gname} | {ename} | {sc['n'] / nd:.0f} | {usd(sc['per100_learn'])} | {usd(sc['per100_fresh'])} | {usd(sc['day_fresh'])} | {usd(sc['worst_day'])} | {sc['days_up']} of {nd} |")
                rows.append({"late": dname, "guard": gname, "exit": ename, **{k: v for k, v in sc.items() if k != "byday"}, "byday": [round(float(x), 2) for x in sc["byday"]]})
                if d == 10 and guard is not None and gname.startswith("...") and ename == "hold to the end":
                    sz = D.SZ[r["row"], r["te"]]
                    L2 = (f"Shares on offer at the price we would pay (1 s late, fresh book, 20+): middle {np.median(sz):.0f}, "
                          f"one in four under {np.percentile(sz, 25):.0f}, one in four over {np.percentile(sz, 75):.0f}. "
                          f"Middle price paid {np.median(r['p']) * 100:.0f}c.")
    with open(os.path.join(CACHE, "speed.json"), "w") as fh:
        json.dump({"rows": rows, "note": L2}, fh)
    print("\n".join(L)); print(L2)
    return L, L2


def report():
    import contextlib, io, statistics
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        facts(0)
    fact_lines = buf.getvalue().strip().split("\n")
    T, _ = tables()
    grids = {n: load_grid(n) for n, _ in SETS}
    total = sum(len(g["rows"]) for g in grids.values() if g)

    def real_swings(name):
        g = grids[name]
        minn = 100 if name in ("btc", "kmin") else 40
        return [r for r in g["rows"] if r["family"] != SPEED and not r["lucky"] and r["held"] < 0.5 and r["n_learn"] >= minn and r["n_fresh"] >= minn]

    sw = {n: real_swings(n) for n in grids if grids[n]}
    n_sw = sum(len(v) for v in sw.values())
    n_both = sum(1 for v in sw.values() for r in v if r["per100_learn"] > 0 and r["per100_fresh"] > 0)
    n_learn = sum(1 for v in sw.values() for r in v if r["per100_learn"] > 0)
    med = {n: statistics.median(r["per100_fresh"] for r in v) for n, v in sw.items() if v}
    mk_n = mk_sure = mk_luck = 0
    for n_, g in grids.items():
        minn = 100 if n_ in ("btc", "kmin") else 40
        for r in g["rows"]:
            if r["kind"] != "M" or r["n_learn"] < minn or r["n_fresh"] < minn:
                continue
            both = r["per100_learn"] > 0 and r["per100_fresh"] > 0
            if r["lucky"]:
                mk_luck += both
            else:
                mk_n += 1
                mk_sure += both
    with open(os.path.join(CACHE, "exams.json")) as fh:
        ex = json.load(fh)
    with open(os.path.join(CACHE, "speed.json")) as fh:
        spd = json.load(fh)
    sp = {(r["late"], r["guard"], r["exit"]): r for r in spd["rows"]}
    k_hold = sp[("1 s late", "...and 20+ shares on offer", "hold to the end")]
    k_sell = sp[("1 s late", "...and 20+ shares on offer", "sell after 60s")]
    h_hold = sp[("0.5 s late", "...and 20+ shares on offer", "hold to the end")]
    l_hold = sp[("2 s late", "...and 20+ shares on offer", "hold to the end")]
    nd = len(grids["btc"]["days"])
    L = ["# Buy and sell inside one crypto window (26 Nov 2026)", "",
         "Jan: \"What about a bot that buys and sells inside the 15 or 5 minute windows?\" and \"this one you will have to do loads of different tests for\".", "",
         "Paper research only. Nothing live was changed.", "",
         "## Short answer", "",
         f"- **Buying a share and selling it again before the window ends loses money, on both sites, in every version tried.** "
         f"{total:,} rule versions in all; {n_sw:,} of them really sell inside the window (not counting the speed family below). "
         f"{n_learn} were ahead on the days they were picked from, and {n_both} of those were still ahead on days they had never seen. That is what luck alone gives.",
         f"- **Why:** a buy-then-sell on Polymarket costs about 5c a share at middle prices (1.4c gap between buyers and sellers + 3.5c in two fees). "
         "Kalshi is about the same (1.3c gap + 3.5c fees). The price would have to snap back by more than that, and it does not: after a jump, about a twentieth of it comes back in the next 30-60 seconds (a 10c jump gives back half a cent).",
         "- **Selling early is the costly part.** For the same buys, getting out before the end (after a set time, at a take-profit, at a stop-loss, or with a waiting sell offer) did worse than just holding to the end in almost every rule, by $2 to $6 per $100. See \"Selling early against holding\".",
         f"- **Waiting offers on both legs do not rescue it.** Waiting bids get filled exactly when the price is falling through them. Of {mk_n:,} waiting-bid versions, {mk_sure} were ahead on both halves of the days with sure fills and {mk_luck} even if we were always first in line; all of those are two days of SOL, and are late bids on the likely side held to the end, so not a swing at all.",
         f"- **The one family that is ahead on paper is the speed bot we already have** (the coin jumped, the share has not moved yet). It is a race: half a second late it shows {usd(h_hold['per100_fresh'])} per $100 on fresh days, one second late {usd(k_hold['per100_fresh'])}, two seconds late {usd(l_hold['per100_fresh'])}. "
         f"Adding a sale inside the window makes it worse, not better: one second late, holding made {usd(k_hold['per100_fresh'])} per $100 and selling after 60 seconds {usd(k_sell['per100_fresh'])}.",
         "- **A stop-loss on the real Kalshi bot's kind of bet does not pay either.** By the minute it looks almost free, but second by second the price dips and comes back, and the stop sells at the bottom.",
         "- **Side-find that matters for the real speed bot:** the box is nearly blind for the first 11 seconds of every 5-minute window (its price feed reconnects there). All 8 real orders that were killed although the offer \"stayed\" were sent in those seconds. Details at the end.", "",
         "## The four numbers (rough guesses)", "",
         "| | Buy cheap, sell back (any version) | Speed buy + sell after 60 s | Speed buy, hold to the end (what the real bot does) |", "|---|---|---|---|",
         f"| Most it makes in an average day | Nothing. A $5 bet loses about {abs(med['btc']) * 0.05 * 100:.0f} cents on Polymarket and about {abs(med['kmin']) * 0.05 * 100:.0f} cents on Kalshi, every time | Paper: about {usd(k_sell['day_fresh'])} a day at 10 shares a bet, if every order filled one second late | Paper: about {usd(k_hold['day_fresh'])} a day at 10 shares a bet, same if |",
         "| Money needed in the account | $5-10 a bet, back within a minute | About $5 a bet, back in a minute: $10-15 is plenty | About $5 a bet, back within 5 minutes: $15-25 out at once |",
         f"| Bet size where it stops growing | Does not apply | About $25 a bet. The offer we would buy holds 150 shares in the middle case, but under 54 shares one time in four | Same |",
         f"| A bad day | 50 bets a day would lose about ${abs(med['btc']) * 0.05 * 50:.0f} | Paper worst day {usd(k_sell['worst_day'])}; ahead on {k_sell['days_up']} of {nd} days | Paper worst day {usd(k_hold['worst_day'])}; ahead on {k_hold['days_up']} of {nd} days. Real money so far: 4 orders filled of 38, -$2.64 |", "",
         "Paper means: the test assumes our order gets the offer it saw one second earlier. The real bot's orders mostly did not (34 of 38 killed on 26 Nov). So the right-hand columns are a ceiling, not a forecast.", "",
         "## What a buy-then-sell costs, and how prices move (Bitcoin 5-minute, Polymarket)", "", "```"] + fact_lines + ["```", "",
         "Read it like this: prices swing a lot (4c in 5 seconds on average), which is why the idea looks tempting. But the swings do not come back. A move is followed by a tiny bit more of the same in the next 1-5 seconds (that is the speed race) and a tiny bounce after 30-60 seconds, both far smaller than the 5c it costs to get in and out.", "",
         "## Every family of rule, picked on the first days and checked on fresh days", "",
         "How to read the tables: a rule is \"looked at\" on the first days and then checked on the later days it never saw. \"Sure fills only\" = our waiting order counts as filled only when a real trade went through its price. \"Always first in line\" is the hopeful end: filled the moment anyone trades at our price.", ""] + T
    L += ["## Selling early against holding to the end", "",
          "Same buys, different ways out. A minus means the way out did worse than simply holding the share to the end of the window.", ""] + exit_table() + ["",
          "Why holding wins: selling costs a second fee and a second trip across the gap, and there is no bounce to collect. A waiting sell offer saves the fee, but it only fills when the price is running up through it, so it sells the winners cheap and keeps the losers.", "",
          "## The one family ahead: the coin jumped and the share has not moved yet", "",
          "This is the speed bot's own signal, tested here with ways out. Not in the first 12 seconds of a window (see the recording flaw below).", ""]
    Ls, note = speed_lines(spd)
    L += Ls + ["", note, "",
               "So it is a race that is over inside two seconds, and the money is in holding, not in selling. The real bot's answer times were 0.3 to 1.7 seconds on 26 Nov.", "",
               "## A stop-loss for late bids on the likely side (the real Kalshi bot's kind of bet)", "",
               "Bid on the side priced 88-97c late in the window, as the real bot does (without its Binance cushion check, so these lose a little where the real rule wins a little). Question: does selling when the price falls help?", ""] + stop_table() + ["",
               "By the minute (59 days) a stop costs only a few cents per $100 and trims the worst day. Second by second (only 2 days, but the truer picture) it costs $2-3 per $100, because the price often dips 10c and comes back, and the stop has sold at the dip. Not worth adding to the real bot.", "",
               "## The shared exam", "", "| Test | Bets | Per $100 | Luck range | Verdict |", "|---|---|---|---|---|"]
    for e in ex:
        c = e["card"]
        L.append(f"| {c['name']} | {c['bets']:,} | {usd(c['per100'])} | {usd(c['lo100'])} to {usd(c['hi100'])} | {c['verdict']} |")
    L += ["", "The two speed lines are paper fills. The exam cannot know that real orders mostly get killed.", "",
          "## How the test works", "",
          "- **Polymarket:** the speed box's log (release `speed-data`): the best buy and sell price of the Up share with sizes, every real trade, and Binance / Chainlink prices, all on our box's clock. Laid on a grid of 10 looks a second. Buying pays the best sell offer, selling gets the best buy order; the Down share is the mirror. An order decided at one look trades at the prices 1 second later (0.5-5 s in the speed table), and only if the price is not worse than the one it saw.",
          "- **Fees:** Polymarket 0.07 x shares x price x (1 - price) on every hurried buy and sell (what we measured on real fills). Kalshi 0.07 x contracts x price x (1 - price), rounded up to a cent an order. Waiting orders pay nothing.",
          "- **Waiting orders:** counted as filled only when a later real trade printed through their price (\"sure\"), or at their price (\"hopeful\", shown apart). The truth is in between; no version was ahead even at the hopeful end.",
          "- **Kalshi:** two sources. 25-26 Nov from the speed box (book every 10 s, every second in the last 7 minutes, every trade), and 12 Sep - 9 Nov by the minute (`kspeed`'s candles: bid and ask at each minute's end, lowest and highest trade in the minute).",
          "- **Learn days and fresh days:** Bitcoin 17-21 Nov against 22-26 Nov; ETH, SOL and Kalshi-by-the-second 25 Nov against 26 Nov; Kalshi-by-the-minute the first 29 days against the last 30.",
          "- **Checks done:** two rules were re-counted with a slow, plain loop and matched the fast replay to the cent (3,002 waiting-bid fills; 600 random windows of a buy / take-profit / stop rule). A share bought at a random moment and held loses about the gap plus the fee, as it should.", "",
          "## Traps found (for the next dig)", "",
          "- **The speed box is nearly blind in seconds 1-11 of every 5-minute window.** On 24 Nov it logged about 24 book updates in second 0, none in second 1, about 4-6 a second in seconds 2-10, then 25-30 a second. The code drops and reopens the price feed when a window ends and again when the next one is listed about 10 s later (`market()` in `quoter/speedcheck.py` and `live/pspeed_live.py`). In those seconds the recorded book is stale, so a replay \"buys\" offers that were not there. Before this was cut out, the speed family looked good even 2 and 5 seconds late; after, it is gone at 2 seconds. `swing.FIRST` skips the first 12 s. `backtest/speedcheck.md` and `backtest/maker5m.md` did not skip them.",
          "- **The real bot has the same blind spot.** Of 34 real orders killed on 26 Nov, 8 had the offer at or under our limit at every book update until the exchange answered, with 16 to 247 shares showing, and nobody else bought it. All 8 were sent 0.2-6 s after a window started. The 4 orders that filled were sent 37-101 s in.",
          "- **A waiting order's fill is bad news.** It fills when the price falls through it. On minute data a waiting sell offer looks much worse than it is (the price has run far past it by the minute's end), so read the \"hopeful\" line too.",
          "- **Minute data hides the dip-and-recover.** Stops look nearly free by the minute and cost $2-3 per $100 by the second.",
          "- **Buying the other side later is the same trade as selling.** It pays the same fee and locks the money to the end, so it was not tested apart.", "",
          "## Verdict", "",
          "Dropped as a strategy: no track. The useful outcomes are (1) keep holding to the end in every bot we have, (2) the 12-second blind spot at each window start, which is a concrete thing to fix or avoid in the real speed bot.", ""]
    with open(os.path.join(HERE, "backtest", "swing.md"), "w") as fh:
        fh.write("\n".join(L))
    print("wrote backtest/swing.md", len(L), "lines")


def speed_lines(spd):
    L = ["| How late we buy | Which offers | Way out | Bets a day | Per $100, first days | Per $100, fresh days | A day at 10 shares, fresh days | Worst day | Days ahead |", "|---|---|---|---|---|---|---|---|---|"]
    nd = 10
    for r in spd["rows"]:
        if r["exit"] == "sell at +10c / stop -10c" or r["guard"].startswith("book heard"):
            continue
        L.append(f"| {r['late']} | {r['guard'].replace('...and ', 'book fresh and ')} | {r['exit']} | {r['n'] / nd:.0f} | {usd(r['per100_learn'])} | {usd(r['per100_fresh'])} | {usd(r['day_fresh'])} | {usd(r['worst_day'])} | {r['days_up']} of {nd} |")
    return L, spd["note"]

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "prep":
        prep(sys.argv[2:])
    elif cmd == "facts":
        facts(int(sys.argv[2]) if len(sys.argv) > 2 else 0)
    elif cmd == "grid":
        what = sys.argv[2] if len(sys.argv) > 2 else "btc"
        if what in ("btc", "eth", "sol"):
            grid(Data(("btc", "eth", "sol").index(what)), f"grid_{what}", (1.0,))
        elif what == "kmin":
            grid(KMin(), "grid_kmin", (0, 60))
        elif what == "ksec":
            grid(KSec(), "grid_ksec", (2,))
    elif cmd == "tables":
        report_data()
    elif cmd == "exams":
        exams()
    elif cmd == "speed":
        speed()
    elif cmd == "report":
        report()
