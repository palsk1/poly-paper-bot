#!/usr/bin/env python3
"""AI and tech bets (22 Nov 2026): "which company has the best AI model at the end of the month", "top model on LMArena",
"will X release model Y by ..." on Polymarket AND Kalshi, against free public numbers (the LMArena leaderboard's own
history). Research only, PAPER ONLY. Reads data, never trades, never writes state/.

  python3 aim.py kscan            # probe aim_kscan: every Kalshi series that smells of AI / tech, with its size
"""
import collections
import datetime as dt
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import backtest as bt
import bot
import yesno
import khouse
import kmentions as km

rj, wj = khouse.rj, khouse.wj
G = bt.G
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bt_cache", "aim")
MK = os.path.join(CACHE, "kmarkets.json.gz")
AI_RX = re.compile(r"\bA\.?I\.?\b|LLM|OPENAI|GPT|ANTHROPIC|CLAUDE|GEMINI|GROK|XAI|DEEPSEEK|LMARENA|ARENA|MODEL|AGI\b|NVIDIA|"
                   r"LLAMA|MISTRAL|CHATBOT|ALTMAN|BENCHMARK|FRONTIER|SUPERINTEL|ROBOTAXI|WAYMO|APPLE|IPHONE|TESLA|SPACEX|"
                   r"STARSHIP|APP ?STORE|APPRANK|TOPAPP", re.I)
d10 = lambda t: dt.datetime.utcfromtimestamp(t).strftime("%Y-%m-%d")


def kscan():
    ser = yesno.kget("/series", {}).get("series") or []
    print("Kalshi series", len(ser), collections.Counter(s.get("category") for s in ser).most_common(30), flush=True)
    pick = [s for s in ser if s.get("ticker") and (s.get("category") == "Science and Technology" or
            AI_RX.search(str(s.get("title")) + " " + s["ticker"]))
            and s.get("category") not in ("Sports", "Mentions", "Crypto", "Climate and Weather")]
    print("picked", len(pick), collections.Counter(s.get("category") for s in pick).most_common(20), flush=True)
    info = {s["ticker"]: s for s in pick}
    out = {}
    with ThreadPoolExecutor(4) as ex:
        for t, ok, n in ex.map(km.series_markets, sorted(info)):
            out[t] = ok
    rows = []
    for t, ok in out.items():
        v = list(ok.values())
        s = info[t]
        src = [y.get("url") for y in (s.get("settlement_sources") or []) if isinstance(y, dict)][:2]
        if not v:
            rows.append((0, f"| {t} | {s.get('category')} | {s.get('frequency')} | {str(s.get('title'))[:70]} | 0 | | | | | | {src} |"))
            continue
        vols = sorted(m["vol"] for m in v)
        life = sorted((m["close"] - m["open"]) / 86400 for m in v)
        rows.append((sum(vols), f"| {t} | {s.get('category')} | {s.get('frequency')} | {str(s.get('title'))[:70]} | {len(v)} | {len({m['ev'] for m in v})} | "
                     f"{d10(min(m['close'] for m in v))} | {d10(max(m['close'] for m in v))} | {sum(m['res'] == 'yes' for m in v)} | "
                     f"{vols[len(vols) // 2]:.0f} / {sum(vols):.0f} / {life[len(life) // 2]:.0f}d | {src} |"))
    print("| series | category | freq | title | settled markets | events | first close | last close | yes won | middle vol / total vol / middle life | source |")
    for _, r in sorted(rows, key=lambda x: -x[0]):
        print(r, flush=True)
    for t, ok in sorted(out.items(), key=lambda kv: -sum(m["vol"] for m in kv[1].values()))[:60]:
        if ok:
            m = max(ok.values(), key=lambda m: m["vol"])
            print("EX", t, {k: m[k] for k in ("t", "q", "w", "res", "vol")}, "| RULE", m["rule"][:300], flush=True)


ARENA_K = "^(KXLLM1|KXTOPMODEL|KXTOPAI|KXTECHRANKLISTAICODE|KXCHINAAI|KXMATHAI|KXARENASCORE|KXCODEAI)$"
K_LIFE = 50 * 86400


def klist(pick=ARENA_K):
    """probe aim_klist: every settled market of Kalshi's leaderboard series -> bt_cache/aim/kmarkets.json.gz"""
    os.makedirs(CACHE, exist_ok=True)
    have = rj(MK, None) or {"series": {}, "markets": {}}
    ser = [x for x in (yesno.kget("/series", {}).get("series") or []) if x.get("ticker") and re.search(pick, x["ticker"])]
    for x in ser:
        have["series"][x["ticker"]] = {"title": str(x.get("title") or "")[:120], "freq": x.get("frequency"),
                                       "fee": [x.get("fee_type"), x.get("fee_multiplier")],
                                       "src": [y.get("url") for y in (x.get("settlement_sources") or []) if isinstance(y, dict)][:3]}
    for x in ser:
        t, ok, n = km.series_markets(x["ticker"])
        have["markets"].update(ok)
        print(t, len(ok), "settled markets", have["series"][t], flush=True)
        evs = collections.defaultdict(list)
        for m in ok.values():
            evs[m["ev"]].append(m)
        for ev, v in sorted(evs.items(), key=lambda kv: kv[1][0]["close"])[-4:]:
            print("   ", ev, d10(v[0]["open"]), d10(v[0]["close"]), [(m["w"], m["res"], int(m["vol"])) for m in sorted(v, key=lambda m: -m["vol"])[:6]], flush=True)
        if ok:
            print("    RULE", max(ok.values(), key=lambda m: m["vol"])["rule"], flush=True)
    wj(MK, have)


def ktape_one(m):
    a, b = max(m["open"], m["close"] - K_LIFE), m["close"]
    cs = []
    for path in (f"/series/{m['s']}/markets/{m['t']}/candlesticks", f"/historical/markets/{m['t']}/candlesticks"):
        try:
            r = yesno.kget(path, {"start_ts": a - 3600, "end_ts": b, "period_interval": 60})
        except Exception:
            continue
        got = r.get("candlesticks") if isinstance(r, dict) else None
        if got:
            for c in got:
                t, bid, ask = yesno.k_candle(c)
                cs.append([t, bid, ask, bot.fnum(c.get("volume_fp") or c.get("volume"), 0)])
            break
    tr, done, path = khouse.trades_span(m["t"], a, b, 6)
    tr.sort()
    return m["t"], {"c": cs, "tr": tr, "full": done, "p": path}


def ktapes(pick=ARENA_K):
    """probe aim_ktapes: hourly bid/ask + trades of each market's whole life (at most 50 days) -> bt_cache/aim/ktapes_<series>.json.gz"""
    have = (rj(MK, {}) or {}).get("markets") or {}
    by = collections.defaultdict(list)
    for m in have.values():
        if re.search(pick, m["s"]) and m["vol"] >= 20:
            by[m["s"]].append(m)
    t0 = time.time()
    for t, ms in sorted(by.items()):
        path = os.path.join(CACHE, f"ktapes_{t}.json.gz")
        got = rj(path, {}) or {}
        todo = [m for m in ms if m["t"] not in got]
        for i in range(0, len(todo), 200):
            with ThreadPoolExecutor(6) as ex:
                for tk, dd in ex.map(ktape_one, todo[i:i + 200]):
                    got[tk] = dd
            wj(path, got)
        nc = sum(len(x["c"]) for x in got.values())
        print(f"{t}: {len(got)} of {len(ms)} markets, {nc} hourly quotes, {sum(len(x['tr']) for x in got.values())} trades, "
              f"not complete {sum(1 for x in got.values() if not x['full'])} ({time.time() - t0:.0f}s)", flush=True)


HF = "https://huggingface.co/api/datasets/lmarena-ai/leaderboard-dataset/parquet"
LB_SUBSETS = ("text", "text_style_control", "webdev", "vision", "text_to_image", "search")
LB_TOP = 30


def lb_path(sub):
    return os.path.join(CACHE, f"lb_{sub}.json.gz")


def lb_fetch():
    """probe aims_lb: Arena's own leaderboard history (Hugging Face dataset lmarena-ai/leaderboard-dataset, free, no key):
    the top 30 of every published board -> bt_cache/aim/lb_<subset>.json.gz = {category: {publish day: [[model, org, score, low, high, votes, rank]]}}"""
    import io
    import urllib.request
    import pyarrow.parquet as pq
    os.makedirs(CACHE, exist_ok=True)
    for sub in LB_SUBSETS:
        try:
            req = urllib.request.Request(f"{HF}/{sub}/full/0.parquet", headers={"User-Agent": "Mozilla/5.0"})
            raw = urllib.request.urlopen(req, timeout=300).read()
            t = pq.read_table(io.BytesIO(raw)).to_pydict()
        except Exception as e:
            print(f"{sub}: failed {str(e)[:200]}", flush=True)
            continue
        cols = list(t)
        n = len(t[cols[0]])
        out = collections.defaultdict(lambda: collections.defaultdict(list))
        for i in range(n):
            out[str(t["category"][i])][str(t["leaderboard_publish_date"][i])[:10]].append(
                [t["model_name"][i], t["organization"][i], t["rating"][i], t["rating_lower"][i], t["rating_upper"][i],
                 t["vote_count"][i], t["rank"][i]])
        slim = {}
        for c, days in out.items():
            slim[c] = {}
            for d, rows in days.items():
                rows.sort(key=lambda r: (r[6] if r[6] is not None else 9e9, -(r[2] or 0)))
                slim[c][d] = [[r[0], r[1], None if r[2] is None else round(r[2], 3), None if r[3] is None else round(r[3], 2),
                               None if r[4] is None else round(r[4], 2), r[5], r[6]] for r in rows[:LB_TOP]]
        wj(lb_path(sub), slim)
        ov = slim.get("overall") or slim.get(sorted(slim)[0])
        ds = sorted(ov)
        print(f"{sub}: {n} rows, columns {cols}, categories {len(slim)} {sorted(slim)[:40]}, overall days {len(ds)} {ds[0]}..{ds[-1]}", flush=True)
        by_year = collections.Counter(d[:7] for d in ds)
        print("   boards a month:", sorted(by_year.items())[-24:], flush=True)
        for d in ds[-3:]:
            print("  ", d, [(r[0], r[1], r[2], r[6]) for r in ov[d][:5]], flush=True)


if __name__ == "__main__":
    a = sys.argv[1] if len(sys.argv) > 1 else ""
    cmd, _, arg = a.partition("-")
    if cmd == "kscan":
        kscan()
    elif cmd == "lb":
        lb_fetch()
    elif cmd == "klist":
        klist(arg or ARENA_K)
    elif cmd == "ktapes":
        ktapes(arg or ARENA_K)
    elif cmd == "kall":
        klist()
        ktapes()
    else:
        print(__doc__)
