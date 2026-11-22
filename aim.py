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


if __name__ == "__main__":
    a = sys.argv[1] if len(sys.argv) > 1 else ""
    cmd, _, arg = a.partition("-")
    if cmd == "kscan":
        kscan()
    else:
        print(__doc__)
