#!/usr/bin/env python3
"""Player props and award futures (NBA/NFL player points, touchdowns, first scorer, MVP...) on Kalshi and Polymarket
vs sportsbook lines with the bookie's cut taken out. backtest/props.md.

PAPER ONLY. Reads public data, never trades, never writes state/.

  python3 props.py scan      (probe pp_scan: which prop / award series exist on Kalshi, Polymarket and Pinnacle)
"""
import collections
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor

import backtest as bt
import bot
import khouse
import kmentions as km
import sharp
import yesno

CACHE = os.path.join(bt.CACHE, "pp")
rj, wj = khouse.rj, khouse.wj
G = "https://gamma-api.polymarket.com"
PROP_RX = re.compile(r"point|rebound|assist|three|3-point|touchdown|\btd\b|yard|reception|passing|rushing|receiving|"
                     r"goal ?scorer|scorer|to score|strikeout|home run|hits\b|\bhr\b|shots|saves|sack|interception|"
                     r"player|mvp|most valuable|rookie|award|coach of|defensive player|heisman|cy young|"
                     r"ballon|golden boot|top scorer|leading|leader|double.double|triple.double|first basket", re.I)


def kalshi_scan():
    ser = yesno.kget("/series", {"category": "Sports"}).get("series") or []
    if not ser:
        ser = [s for s in yesno.kget("/series", {}).get("series") or [] if s.get("category") == "Sports"]
    pick = [s for s in ser if s.get("ticker") and PROP_RX.search(str(s.get("title")))]
    print(f"Kalshi sports series {len(ser)} | prop/award-looking {len(pick)}", flush=True)
    info = {s["ticker"]: s for s in pick}
    out = {}
    with ThreadPoolExecutor(6) as ex:
        for t, ok, n in ex.map(km.series_markets, sorted(info)):
            if not ok:
                continue
            v = list(ok.values())
            s = info[t]
            out[t] = {"title": str(s.get("title"))[:90], "freq": s.get("frequency"), "n": len(v),
                      "ev": len({m["ev"] for m in v}), "vol": sum(m["vol"] for m in v),
                      "yes": sum(m["res"] == "yes" for m in v),
                      "first": km_d(min(m["close"] for m in v)), "last": km_d(max(m["close"] for m in v)),
                      "ex": [(m["q"][:70], m["w"][:40], m["res"], int(m["vol"]))
                             for m in sorted(v, key=lambda m: -m["vol"])[:3]]}
    os.makedirs(CACHE, exist_ok=True)
    wj(os.path.join(CACHE, "kscan.json.gz"), out)
    print("| series | title | freq | markets | events | yes won | contracts | first close | last close |")
    for t, s in sorted(out.items(), key=lambda kv: -kv[1]["vol"]):
        print(f"| {t} | {s['title']} | {s['freq']} | {s['n']} | {s['ev']} | {s['yes']} | {s['vol']:,.0f} | {s['first']} | {s['last']} |")
    for t, s in sorted(out.items(), key=lambda kv: -kv[1]["vol"])[:40]:
        print("EX", t, s["ex"], flush=True)
    # open ones too (props are listed a day before a game and settle the same night)
    for t in [t for t, _ in sorted(out.items(), key=lambda kv: -kv[1]["vol"])[:12]]:
        try:
            r = yesno.kget("/markets", {"series_ticker": t, "status": "open", "limit": 200})
            ms = r.get("markets") or []
            print(f"OPEN {t}: {len(ms)} markets", [(m.get("ticker"), m.get("yes_sub_title"), m.get("yes_bid_dollars"),
                                                    m.get("yes_ask_dollars"), m.get("volume_fp")) for m in ms[:4]])
        except Exception as e:
            print("OPEN", t, "failed", str(e)[:100])


def km_d(t):
    import datetime as dt
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m-%d")


def poly_scan():
    sp = bot.http_json(f"{G}/sports")
    want = {s.get("sport"): s.get("series") for s in sp}
    for code in ("nba", "nfl", "nhl", "mlb", "epl", "cfb", "ncaab"):
        ser = want.get(code)
        if not ser:
            continue
        typ, vol, ex = collections.Counter(), collections.Counter(), {}
        for closed in ("true", "false"):
            for off in range(0, 400, 100):
                try:
                    evs = bot.http_json(f"{G}/events", {"series_id": ser, "closed": closed, "limit": 100, "offset": off,
                                                        "order": "startDate", "ascending": "false"})
                except Exception as e:
                    print(code, "events failed", str(e)[:100])
                    break
                if not evs:
                    break
                for ev in evs:
                    for m in ev.get("markets") or []:
                        k = (closed, str(m.get("sportsMarketType")))
                        typ[k] += 1
                        vol[k] += bot.fnum(m.get("volumeNum"), 0)
                        ex.setdefault(k, (m.get("question"), m.get("volumeNum"), m.get("bestBid"), m.get("bestAsk")))
        print(f"\n== Polymarket {code} (series {ser}), market types (closed?, type): markets, $ traded")
        for k, n in typ.most_common(40):
            print(f"  {k}: {n} markets, ${vol[k]:,.0f} | e.g. {ex[k]}")
    # award futures
    for q in ("mvp", "rookie of the year", "heisman", "golden boot", "ballon", "cy young", "defensive player"):
        try:
            r = bot.http_json(f"{G}/public-search", {"q": q, "limit_per_type": 10, "events_status": "all"})
        except Exception as e:
            print("search", q, "failed", str(e)[:80])
            continue
        evs = r.get("events") or []
        print(f"\n== Polymarket search '{q}': {len(evs)} events")
        for e in evs[:10]:
            print(f"  {e.get('slug')} | closed {e.get('closed')} | ${bot.fnum(e.get('volume'), 0):,.0f} | "
                  f"{len(e.get('markets') or [])} markets | end {e.get('endDate')}")


def pin_scan():
    for sid, lids in ((4, (487, 493)), (15, (889, 880)), (19, (1456,)), (3, (246,)), (29, (1980,))):
        try:
            mus = sharp.pin(f"/sports/{sid}/matchups")
        except Exception as e:
            print("pinnacle", sid, "failed", e)
            continue
        sp = [m for m in mus if m.get("type") == "special"]
        cats = collections.Counter(((m.get("special") or {}).get("category"), (m.get("league") or {}).get("name"))
                                   for m in sp)
        print(f"\n== Pinnacle sport {sid}: {len(mus)} matchups, {len(sp)} specials; by (category, league):")
        for k, n in cats.most_common(15):
            print("  ", k, n)
        for m in sp[:4]:
            print("   EX", json.dumps({k: m.get(k) for k in ("id", "startTime", "special", "participants", "parentId",
                                                             "units")})[:700])
        if sp:
            try:
                mks = sharp.pin(f"/sports/{sid}/markets/straight")
                ids = {m["id"] for m in sp[:200]}
                got = [x for x in mks if x.get("matchupId") in ids]
                print(f"   markets for the first 200 specials: {len(got)}; e.g.", json.dumps(got[:2])[:600])
            except Exception as e:
                print("   markets failed", e)


def scan():
    for f in (kalshi_scan, poly_scan, pin_scan):
        try:
            f()
        except Exception as e:
            print(f.__name__, "FAILED", repr(e)[:300])
        sys.stdout.flush()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "scan"
    {"scan": scan, "kalshi": kalshi_scan, "poly": poly_scan, "pin": pin_scan}[cmd]()
