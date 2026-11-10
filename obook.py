#!/usr/bin/env python3
"""Order book shape test (2026-11-10, research only, no track).

Question: does the shape of the order book (one side much thicker, big orders pulled, spread widening,
time of day, recent taker flow) predict the next price move well enough to beat the spread and fees?

Data: the recorder's hourly files on GitHub releases data-YYYYMMDD (recorder.py, PR #12): every-minute
books of Kalshi/Polymarket markets closing within 3 h, 5-minute books of the tracks' open positions,
and the full Kalshi trade tape for those tickers.

How each idea is scored (backtest/PROTOCOL.md rules where they fit):
  taker   buy at the recorded ask (or the NO side at 1 - bid) with >= 10 shares at the top, sell at the
          bid 1/5/15/60 minutes later, Kalshi fee 0.07 x p x (1-p) each way, Polymarket fee 0 (kind to us)
  hold    same entry, held to the Kalshi result (last trade in the final 2 minutes >= 90c or <= 10c)
  maker   rest a bid at the best price at the back of the queue; filled only when the real Kalshi tape
          trades through everything queued ahead plus our 10; exits: mid 15 min later (a mark, not
          money), taker 15 min later, a resting exit (maker both ways), or the result
Controls: thresholds picked on one time half and scored on the other; "random side" = every minute,
both sides (what the costs alone do); event-clustered bootstrap bands; the share of cells that pass
both halves is compared with what chance gives.

Usage:
  python3 obook.py fetch [tag ...]   download recorder releases into bt_cache/ob/rec (needs gh + token)
  python3 obook.py run               parse + grid + every test, writes backtest/obook.md
  python3 obook.py recheck           the pre-registered re-check, only on hours recorded after
                                     CUTOFF (see backtest/obook.md); run it once from ~2026-12-01
"""
import collections
import datetime as dt
import glob
import gzip
import json
import os
import pickle
import subprocess
import sys

import numpy as np

DIR = "bt_cache/ob"
REC = f"{DIR}/rec"
REPO = "palsk1/poly-paper-bot"
CUTOFF = "rec-20261110-08"   # files up to here were looked at on 2026-11-10; the re-check uses later ones only
OUT = "backtest/obook.md"
HS = (1, 5, 15, 60)
LINES = []


def say(s=""):
    print(s)
    LINES.append(s)


# ---------- data ----------

def fetch(tags=None):
    os.makedirs(REC, exist_ok=True)
    if not tags:
        rel = json.loads(subprocess.run(["gh", "api", f"repos/{REPO}/releases?per_page=100"],
                                        capture_output=True, text=True, check=True).stdout)
        tags = [r["tag_name"] for r in rel if r["tag_name"].startswith("data-")]
    for tag in tags:
        rel = json.loads(subprocess.run(["gh", "api", f"repos/{REPO}/releases/tags/{tag}"],
                                        capture_output=True, text=True, check=True).stdout)
        for a in rel.get("assets") or []:
            path = f"{REC}/{a['name']}"
            if os.path.exists(path) and os.path.getsize(path) == a["size"]:
                continue
            with open(path, "wb") as f:
                subprocess.run(["gh", "api", "-H", "Accept: application/octet-stream",
                                f"repos/{REPO}/releases/assets/{a['id']}"], stdout=f, check=True)
            print("got", a["name"])


def _iso(s):
    try:
        return dt.datetime.fromisoformat(str(s).replace("Z", "+00:00")).timestamp()
    except Exception:
        return None


def _feats(bids, asks):
    """best bid, best ask, size at best, size within 3c and 10c of best, levels."""
    if not bids or not asks:
        return None
    bb, ba = bids[0][0], asks[0][0]
    if ba <= bb:
        return None
    d = lambda rows, best, w, sg: sum(s for p, s in rows if sg * (best - p) <= w + 1e-9)
    return (bb, ba, bids[0][1], asks[0][1], d(bids, bb, .03, 1), d(asks, ba, .03, -1),
            d(bids, bb, .10, 1), d(asks, ba, .10, -1), len(bids), len(asks))


def parse(files):
    series, trades, meta, seen = collections.defaultdict(list), collections.defaultdict(list), {}, set()
    for fn in files:
        for line in gzip.open(fn, "rt"):
            try:
                d = json.loads(line)
            except Exception:
                continue
            k, t = d.get("k"), d.get("t")
            if k == "kbook":
                fe = _feats(d.get("yb") or [], [[round(1 - p, 4), s] for p, s in d.get("nb") or []])
                if fe:
                    series["K:" + d["tk"]].append((t,) + fe)
                if d.get("cl"):
                    meta.setdefault("K:" + d["tk"], {})["cl"] = d["cl"]
            elif k == "pbook":
                fe = _feats(d.get("b") or [], d.get("a") or [])
                if fe:
                    series["P:" + d["tok"]].append((t,) + fe)
            elif k == "ktrade" and "ticker" in d:
                if d.get("trade_id") in seen:
                    continue
                seen.add(d.get("trade_id"))
                try:
                    trades["K:" + d["ticker"]].append((_iso(d["created_time"]), float(d["yes_price_dollars"]),
                                                       float(d["count_fp"]), 1 if d["taker_side"] == "yes" else 0))
                except Exception:
                    pass
            elif k == "meta":
                for m in d.get("kalshi") or []:
                    meta.setdefault("K:" + m["tk"], {}).update({"cl": m.get("cl"), "ev": m.get("ev")})
                for m in d.get("poly") or []:
                    if "tok" in m:
                        meta.setdefault("P:" + m["tok"], {}).update({"end": m.get("end"), "set": d.get("set")})
            elif k == "spot":
                series["SPOT"].append((t, None))
    for v in list(series.values()) + list(trades.values()):
        v.sort(key=lambda x: x[0])
    return dict(series), dict(trades), meta


def family(key, meta):
    if key.startswith("K:"):
        s = key[2:].split("-")[0]
        if s.endswith("15M"):
            return "K_15m"
        if s.startswith(("KXTEMP", "KXHIGH", "KXLOW")):
            return "K_weather"
        if s in ("KXNASDAQ100U", "KXINXU", "KXINX", "KXNASDAQ100"):
            return "K_index"
        if s[:5] in ("KXBTC", "KXETH", "KXSOL", "KXXRP", "KXBNB", "KXDOG"):
            return "K_crypto_other"
        return "K_other"
    return "P_fast" if meta.get(key, {}).get("set") == "fast" else "P_wide"


def grid(series, trades, meta):
    """One row per market per minute (5 min for P_wide), books forward-filled, past-only features."""
    import pandas as pd
    alive = {int(t // 60) for t, _ in series.get("SPOT", [])}  # minutes the recorder was running
    rows = []
    for key, ser in series.items():
        if key == "SPOT" or len(ser) < 3:
            continue
        fam = family(key, meta)
        step = 300 if fam == "P_wide" else 60
        ts = np.array([x[0] for x in ser])
        A = np.array([x[1:] for x in ser], float)
        cl = _iso(meta.get(key, {}).get("cl") or meta.get(key, {}).get("end") or "")
        t1 = int(ts[-1])
        if key.startswith("K:") and cl:
            t1 = min(t1, int(cl) - 60)
        g = np.array([x for x in range(int(ts[0] // 60 * 60) + 60, t1 + 1, step) if x // 60 in alive])
        if len(g) < 6:
            continue
        idx = np.searchsorted(ts, g, side="right") - 1
        G = A[idx]
        tr = trades.get(key)
        flow = fvol = np.full(len(g), np.nan)
        res = np.nan
        if tr:
            tt = np.array([x[0] for x in tr])
            cs = np.concatenate([[0], np.cumsum([x[2] * (1 if x[3] else -1) for x in tr])])
            cv = np.concatenate([[0], np.cumsum([x[2] for x in tr])])
            a, b = np.searchsorted(tt, g - 300), np.searchsorted(tt, g)
            flow, fvol = cs[b] - cs[a], cv[b] - cv[a]
            if key.startswith("K:") and cl:
                late = [x[1] for x in tr if cl - 120 <= x[0] <= cl]
                if late:
                    res = 1.0 if late[-1] >= .9 else (0.0 if late[-1] <= .1 else np.nan)
        pos = {int(x): i for i, x in enumerate(g)}
        at = lambda x: G[pos[int(x)]] if int(x) in pos else None
        for i, x in enumerate(g):
            bid, ask = G[i, 0], G[i, 1]
            mid = (bid + ask) / 2
            if not .05 <= mid <= .95:
                continue
            p1, p5 = at(x - step), at(x - 300)
            r = dict(key=key, fam=fam, t=int(x), bid=bid, ask=ask, bsz1=G[i, 2], asz1=G[i, 3], bd3=G[i, 4],
                     ad3=G[i, 5], bd10=G[i, 6], ad10=G[i, 7], flow=flow[i], fvol=fvol[i], res=res, cl=cl or np.nan,
                     pbid=p1[0] if p1 is not None else np.nan, pask=p1[1] if p1 is not None else np.nan,
                     pbd3=p1[4] if p1 is not None else np.nan, pad3=p1[5] if p1 is not None else np.nan,
                     s5=(p5[1] - p5[0]) if p5 is not None else np.nan,
                     m5=((p5[1] + p5[0]) / 2) if p5 is not None else np.nan)
            for h in HS:
                q = at(x + h * 60)
                r[f"fb{h}"], r[f"fa{h}"] = (q[0], q[1]) if q is not None else (np.nan, np.nan)
            rows.append(r)
    df = pd.DataFrame(rows)
    e = 1e-9
    df["mid"], df["spr"] = (df.bid + df.ask) / 2, df.ask - df.bid
    df["I1"] = (df.bsz1 - df.asz1) / (df.bsz1 + df.asz1 + e)       # top of book: YES bids vs YES asks
    df["I3"] = (df.bd3 - df.ad3) / (df.bd3 + df.ad3 + e)           # within 3c of the best price
    df["I10"] = (df.bd10 - df.ad10) / (df.bd10 + df.ad10 + e)      # within 10c
    df["dspr"] = df.spr - df.s5                                    # spread now vs 5 min ago
    df["pullB"] = (((df.bid == df.pbid) & (df.bd3 < .5 * df.pbd3)).astype(float)
                   - ((df.ask == df.pask) & (df.ad3 < .5 * df.pad3)).astype(float))  # +1 bids pulled, -1 asks pulled
    df["flowr"] = df.flow / (df.fvol + e)                          # Kalshi taker YES minus NO, last 5 min
    df["mom5"] = df.mid - df.m5                                    # price move last 5 min (control idea)
    df["ev"] = df.key.str.replace(r"-[^-]+$", "", regex=True)
    kal = df.key.str.startswith("K:").values
    fee = lambda p: np.where(kal, .07, 0.0) * p * (1 - p)
    for h in HS:
        fb, fa = df[f"fb{h}"], df[f"fa{h}"]
        df[f"dm{h}"] = (fb + fa) / 2 - df.mid
        df[f"L{h}"] = np.where(df.asz1 >= 10, (fb - df.ask - fee(df.ask) - fee(fb)) / df.ask, np.nan)
        df[f"S{h}"] = np.where(df.bsz1 >= 10, (df.bid - fa - fee(1 - df.bid) - fee(1 - fa)) / (1 - df.bid), np.nan)
    ok = df.res.notna()
    df["Lend"] = np.where(ok & (df.asz1 >= 10), (df.res - df.ask - fee(df.ask)) / df.ask, np.nan)
    df["Send"] = np.where(ok & (df.bsz1 >= 10), (df.bid - df.res - fee(1 - df.bid)) / (1 - df.bid), np.nan)
    df["half"] = np.where(df.t < df.t.median(), "A", "B")
    return df


# ---------- tests ----------

FEATS = ["I1", "I3", "I10", "pullB", "dspr", "flowr", "mom5"]
HZ = ["1", "5", "15", "60", "end"]
rng = np.random.default_rng(1)


def p100(x):
    x = np.asarray(x, float)
    return 100 * np.nanmean(x) if np.isfinite(x).sum() else np.nan


def pick(g, feat, lo, hi, side, hz):
    up, dn = g[g[feat] >= hi], g[g[feat] <= lo]
    a, b = (up[f"L{hz}"], dn[f"S{hz}"]) if side == "follow" else (up[f"S{hz}"], dn[f"L{hz}"])
    return np.concatenate([a.values, b.values]), np.concatenate([up.ev.values, dn.ev.values])


def band(pn, ev, n=1000):
    m = np.isfinite(pn)
    pn, ev = pn[m], ev[m]
    if not len(pn):
        return np.nan, np.nan, np.nan, 0
    import pandas as pd
    gs = pd.DataFrame({"p": pn, "e": ev}).groupby("e").p.agg(["sum", "count"])
    s, c = gs["sum"].values, gs["count"].values
    bs = [s[i].sum() / c[i].sum() for i in (rng.integers(0, len(s), len(s)) for _ in range(n))]
    return 100 * pn.mean(), 100 * np.percentile(bs, 5), 100 * np.percentile(bs, 95), len(s)


def sweep(df):
    """Every feature x horizon x tail x follow/fade, thresholds from the other half."""
    import pandas as pd
    out = []
    for fam, g in df.groupby("fam"):
        for hz in HZ:
            if g[f"L{hz}"].notna().sum() < 300:
                continue
            rand = p100(np.concatenate([g[f"L{hz}"].values, g[f"S{hz}"].values]))
            for feat in FEATS:
                if g[feat].notna().sum() < 500 or g[feat].nunique() < 3:
                    continue
                for tail in (.1, .02):
                    for side in ("follow", "fade"):
                        r = dict(fam=fam, hz=hz, feat=feat, tail=tail, side=side, rand=rand)
                        for hv in ("A", "B"):
                            other = g[g.half != hv]
                            lo, hi = other[feat].quantile(tail), other[feat].quantile(1 - tail)
                            pn, _ = pick(g[g.half == hv], feat, lo, hi, side, hz) if hi > lo else (np.array([]), None)
                            r[hv], r["n" + hv] = p100(pn), int(np.isfinite(pn).sum())
                        out.append(r)
    return pd.DataFrame(out)


def maker(df, trades, Q=10, win=300):
    """Kalshi only: rest at the best bid/ask behind the queue, fill from the tape."""
    import pandas as pd
    k = df[df.key.str.startswith("K:")].copy()
    tt = {key: tuple(np.array([x[j] for x in v]) for j in range(4)) for key, v in trades.items() if key.startswith("K:")}
    fb, fa = [], []
    for r in k.itertuples():
        if r.key not in tt:
            fb.append(False); fa.append(False); continue
        t_, p_, s_, y_ = tt[r.key]
        a, b = np.searchsorted(t_, r.t), np.searchsorted(t_, r.t + win)
        P, S, Y = p_[a:b], s_[a:b], y_[a:b]
        fb.append(S[(Y == 0) & (P <= r.bid + 1e-9)].sum() > r.bsz1 + Q)
        fa.append(S[(Y == 1) & (P >= r.ask - 1e-9)].sum() > r.asz1 + Q)
    k["fillB"], k["fillA"] = fb, fa
    fee = lambda p: .07 * p * (1 - p)
    mid15 = (k.fb15 + k.fa15) / 2
    k["vB_mark"], k["vA_mark"] = (mid15 - k.bid) / k.bid, (k.ask - mid15) / (1 - k.ask)
    k["vB_exit"], k["vA_exit"] = (k.fb15 - k.bid - fee(k.fb15)) / k.bid, (k.ask - k.fa15 - fee(1 - k.fa15)) / (1 - k.ask)
    k["vB_end"], k["vA_end"] = (k.res - k.bid) / k.bid, (k.ask - k.res) / (1 - k.ask)
    rows = []
    for fam, g in k.groupby("fam"):
        lo, hi = g.I3.quantile(.2), g.I3.quantile(.8)
        for lab, mB, mA in [("always, both sides", np.ones(len(g), bool), np.ones(len(g), bool)),
                            ("lean with the thick side", (g.I3 >= hi).values, (g.I3 <= lo).values),
                            ("lean against it", (g.I3 <= lo).values, (g.I3 >= hi).values)]:
            for hv in ("A", "B"):
                hm = (g.half == hv).values
                B, A = g[mB & hm & g.fillB.values], g[mA & hm & g.fillA.values]
                cat = lambda c: np.concatenate([B["vB_" + c].values, A["vA_" + c].values])
                rows.append(dict(fam=fam, rule=lab, half=hv, fills=len(B) + len(A), mark15=p100(cat("mark")),
                                 taker_exit15=p100(cat("exit")), held=p100(cat("end"))))
    return pd.DataFrame(rows)


def md(t):
    """Plain markdown table (no tabulate dependency)."""
    f = lambda v: f"{v:.2f}" if isinstance(v, float) else str(v)
    cols = [str(c) for c in t.columns]
    rows = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    rows += ["| " + " | ".join(f(v) for v in r) + " |" for r in t.itertuples(index=False)]
    return "\n".join(rows)


def run(files, title):
    series, trades, meta = parse(files)
    df = grid(series, trades, meta)
    hours = len(files)
    say(f"# {title}\n")
    say(f"Data: {hours} recorder hours ({os.path.basename(files[0])} .. {os.path.basename(files[-1])}), "
        f"{df.key.nunique()} markets, {len(df):,} market-minutes with a price between 5c and 95c.\n")
    say("Families: " + ", ".join(f"{k} {v:,}" for k, v in df.fam.value_counts().items()) + "\n")
    say("## 1. Does the book shape move the price at all? (mid move in cents, top 10% vs bottom 10%)\n")
    say("| family | YES side thicker: mid move 5 min | YES side thinner | bids pulled | asks pulled | typical spread |")
    say("|---|---|---|---|---|---|")
    for fam, g in df.groupby("fam"):
        lo, hi = g.I3.quantile(.1), g.I3.quantile(.9)
        c = lambda x: f"{100 * np.nanmean(x):+.2f}c"
        say(f"| {fam} | {c(g[g.I3 >= hi].dm5)} | {c(g[g.I3 <= lo].dm5)} | {c(g[g.pullB == 1].dm5)} | "
            f"{c(g[g.pullB == -1].dm5)} | {100 * g.spr.median():.1f}c |")
    R = sweep(df)
    say("\n## 2. Trading it as a taker (buy at the ask, sell at the bid later, fees in)\n")
    say("What doing nothing clever costs (every minute, random side), $ per $100:\n")
    say(md(R.groupby(["fam", "hz"]).rand.first().unstack().reset_index()))
    say("\nCells ahead in BOTH halves (thresholds picked on the other half):\n")
    for hz in HZ:
        r = R[R.hz == hz]
        say(f"- hold {hz}{'' if hz == 'end' else ' min'}: {len(r)} cells, {int(((r.A > 0) & (r.B > 0)).sum())} ahead in both halves, "
            f"{int(((r.A > r.rand) & (r.B > r.rand)).sum())} beat the random side in both")
    R["worst_half"] = R[["A", "B"]].min(axis=1)
    say("\nBest 15 by the worse half:\n")
    say(md(R.sort_values("worst_half", ascending=False).head(15).round(2)))
    say("\n## 3. Leads checked harder (event-clustered 90% band, all data)\n")
    for fam, feat, tail, side, hz in PREREG + [("P_fast", "I3", .1, "follow", "5"), ("K_15m", "mom5", .1, "fade", "5")]:
        g = df[df.fam == fam]
        if not len(g):
            continue
        pn, ev = pick(g, feat, g[feat].quantile(tail), g[feat].quantile(1 - tail), side, hz)
        m, lo, hi, ne = band(pn, ev)
        cost = None
        say(f"- {fam} {feat} {side}, hold {hz}: ${m:+.2f} per $100 (band {lo:+.1f} to {hi:+.1f}), "
            f"{int(np.isfinite(pn).sum())} bets, {ne} events")
    say("\n## 4. As a maker on Kalshi (rest at the best price, back of the queue, fills from the real tape)\n")
    say(md(maker(df, trades).round(2)))
    return df


# Pre-registered on 2026-11-10 (the two hold-to-end curiosities). Re-check ONCE on hours after CUTOFF.
PREREG = [("K_crypto_other", "flowr", .1, "follow", "end"), ("K_other", "I10", .1, "follow", "end")]


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "fetch":
        return fetch(sys.argv[2:])
    files = sorted(glob.glob(f"{REC}/rec-*.jsonl.gz"))
    if cmd == "run":
        files = [f for f in files if os.path.basename(f) < CUTOFF]
        run(files, "Order book shapes vs the next price move")
        with open(OUT, "w") as f:
            f.write("\n".join(LINES) + "\n")
    elif cmd == "recheck":
        files = [f for f in files if os.path.basename(f) >= CUTOFF]
        if len(files) < 24 * 14:
            sys.exit(f"only {len(files)} fresh hours; wait for two weeks of new recordings")
        run(files, "Pre-registered re-check on fresh recordings")
        with open("backtest/obook_recheck.md", "w") as f:
            f.write("\n".join(LINES) + "\n")


if __name__ == "__main__":
    main()
