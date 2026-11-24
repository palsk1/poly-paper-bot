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



# ================================================================ live: Pinnacle props vs Kalshi props, right now
import datetime as dt
import math
import time

LIVE = os.path.join(CACHE, "live.json.gz")
# Pinnacle "special" description ending -> (Kalshi series, sport)
PMAP = [(4, r"total points$", "KXNBAPTS"), (4, r"total rebounds$", "KXNBAREB"), (4, r"total assists$", "KXNBAAST"),
        (4, r"(three|3).?point.*made$|total 3.?pt", "KXNBA3PT"), (4, r"pts.?\+.?rebs.?\+.?asts|points.?\+.?rebounds.?\+.?assists", "KXNBAPRA"),
        (15, r"receiving yards$", "KXNFLRECYDS"), (15, r"rushing yards$", "KXNFLRSHYDS"), (15, r"passing yards$", "KXNFLPASSYDS"),
        (15, r"total receptions$", "KXNFLREC"), (15, r"passing touchdowns$|passing tds$", "KXNFLPASSTDS"),
        (15, r"touchdowns?$|anytime td|to score a (td|touchdown)", "KXNFLTD"), (15, r"rushing attempts$", "KXNFLRSHATT"),
        (15, r"interceptions?$", "KXNFLPASSINT"),
        (19, r"total goals$|to score", "KXNHLGOAL"), (19, r"total points$", "KXNHLPTS"), (19, r"total assists$", "KXNHLAST")]


def pin_props():
    """[{sport, series, player, line (Kalshi 'N+' threshold), fair_over (mult, power), limit, start, desc}]"""
    out, miss = [], collections.Counter()
    for sid in (4, 15, 19):
        try:
            mus = sharp.pin(f"/sports/{sid}/matchups")
            mks = sharp.pin(f"/sports/{sid}/markets/straight")
        except Exception as e:
            print("pinnacle", sid, "failed", e)
            continue
        by = collections.defaultdict(list)
        for mk in mks:
            if mk.get("status", "open") == "open" and mk.get("period", 0) == 0:
                by[mk.get("matchupId")].append(mk)
        for m in mus:
            sp = m.get("special") or {}
            if m.get("type") != "special" or sp.get("category") != "Player Props" or m.get("isLive"):
                continue
            desc = str(sp.get("description") or "")
            ser = next((k for s_, rx, k in PMAP if s_ == sid and re.search(rx, desc.strip(), re.I)), None)
            if not ser:
                miss[(sid, re.sub(r"^.*?(total|to|anytime)", r"\1", desc, flags=re.I)[:40])] += 1
                continue
            parts = {p.get("id"): str(p.get("name")) for p in m.get("participants") or []}
            player = re.split(r"\s+(total|to score|anytime|\()", desc, flags=re.I)[0].strip()
            for mk in by.get(m.get("id"), []):
                pr = mk.get("prices") or []
                if len(pr) != 2:
                    continue
                nm = [parts.get(x.get("participantId"), "") for x in pr]
                if mk.get("type") == "total" and {"Over", "Under"} == set(nm):
                    o = pr[nm.index("Over")]
                    u = pr[nm.index("Under")]
                    pts = bot.fnum(o.get("points"), None)
                    if pts is None or abs(pts - math.floor(pts) - 0.5) > 1e-6:
                        continue              # whole-number lines can push; Kalshi "N+" has no push
                    line = int(pts + 0.5)
                    qo, qu = sharp.american_to_prob(o["price"]), sharp.american_to_prob(u["price"])
                elif {"Yes", "No"} == set(nm):
                    line = 1
                    qo = sharp.american_to_prob(pr[nm.index("Yes")]["price"])
                    qu = sharp.american_to_prob(pr[nm.index("No")]["price"])
                else:
                    continue
                f = sharp.devig([qo, qu])
                lim = max([bot.fnum(x.get("amount")) for x in mk.get("limits") or []] or [0])
                out.append({"sport": sid, "series": ser, "player": player, "line": line, "fair": [f[0][0], f[0][1]],
                            "over_round": round(qo + qu - 1, 4), "limit": lim, "start": m.get("startTime"),
                            "desc": desc, "alt": bool(mk.get("isAlternate"))})
    print(f"pinnacle player props usable: {len(out)}; unmatched kinds: {miss.most_common(25)}")
    return out


def k_open(series):
    rows, cur = [], None
    for _ in range(30):
        p = {"series_ticker": series, "status": "open", "limit": 1000}
        if cur:
            p["cursor"] = cur
        try:
            r = yesno.kget("/markets", p)
        except Exception as e:
            print("kalshi open", series, "failed", str(e)[:80])
            break
        rows += r.get("markets") or []
        cur = r.get("cursor")
        if not cur or not r.get("markets"):
            break
    out = []
    for m in rows:
        w = str(m.get("yes_sub_title") or "")
        mm = re.match(r"^(.*?):\s*(\d+)\+\s*$", w)
        if not mm:
            continue
        out.append({"t": m.get("ticker"), "ev": m.get("event_ticker"), "player": mm.group(1).strip(),
                    "line": int(mm.group(2)), "bid": bot.fnum(m.get("yes_bid_dollars"), None),
                    "ask": bot.fnum(m.get("yes_ask_dollars"), None), "vol": bot.fnum(m.get("volume_fp"), 0),
                    "oi": bot.fnum(m.get("open_interest_fp"), 0), "liq": bot.fnum(m.get("liquidity_dollars"), 0)})
    return out


def kfee(p, n=25.0):
    """Kalshi taker fee per contract for an order of ~$n at price p (rounded up to the cent per order)."""
    c = max(1, int(n / max(p, 0.01)))
    return bot.kalshi_fee(c, p) / c


def snapshot():
    pp = pin_props()
    kk = {}
    for ser in sorted({x["series"] for x in pp}):
        kk[ser] = k_open(ser)
    rows = []
    for x in pp:
        best, bs = None, 0.0
        for k in kk.get(x["series"], []):
            if k["line"] != x["line"]:
                continue
            sc = sharp.name_score(x["player"], k["player"])
            if sc > bs:
                best, bs = k, sc
        if not best or bs < 0.85:
            continue
        fo = min(x["fair"])           # the less favourable of the two de-vig methods, per side
        fo_hi = max(x["fair"])
        r = dict(x, kt=best["t"], kplayer=best["player"], bid=best["bid"], ask=best["ask"], vol=best["vol"], oi=best["oi"])
        # cheap Yes: fair_over (low estimate) minus Kalshi Yes ask minus fee; cheap No: (1 - fair_over high) - No ask - fee
        if best["ask"] and 0 < best["ask"] < 1:
            r["yes_gap"] = round(fo - best["ask"] - kfee(best["ask"]), 4)
        if best["bid"] and 0 < best["bid"] < 1:
            na = 1 - best["bid"]
            r["no_gap"] = round((1 - fo_hi) - na - kfee(na), 4)
        if best["bid"] and best["ask"]:
            r["mid_gap"] = round((best["bid"] + best["ask"]) / 2 - (fo + fo_hi) / 2, 4)
        rows.append(r)
    return rows, len(pp)


def live(minutes="0", every="15"):
    """One snapshot, or one every `every` minutes for `minutes`; all kept in bt_cache/pp/live.json.gz for scoring."""
    os.makedirs(CACHE, exist_ok=True)
    store = rj(LIVE, {"snaps": []}) or {"snaps": []}
    t_end = time.time() + float(minutes) * 60
    while True:
        rows, n = snapshot()
        now = int(time.time())
        store["snaps"].append({"t": now, "rows": rows})
        wj(LIVE, store)
        mg = sorted(r["mid_gap"] for r in rows if "mid_gap" in r)
        yg = [r for r in rows if r.get("yes_gap", -1) >= 0.03]
        ng = [r for r in rows if r.get("no_gap", -1) >= 0.03]
        print(f"\n== snapshot {dt.datetime.utcfromtimestamp(now):%Y-%m-%d %H:%M} UTC: pinnacle {n}, matched to Kalshi {len(rows)}")
        if mg:
            q = lambda f: mg[min(len(mg) - 1, int(f * len(mg)))]
            print(f"  Kalshi middle minus Pinnacle fair: median {q(.5):+.3f}, 10th {q(.1):+.3f}, 90th {q(.9):+.3f}")
            sprd = sorted(r["ask"] - r["bid"] for r in rows if r.get("bid") and r.get("ask"))
            print(f"  Kalshi buy/sell gap median {sprd[len(sprd)//2]:.2f}; Pinnacle margin median "
                  f"{sorted(r['over_round'] for r in rows)[len(rows)//2]:.3f}")
            for ser in sorted({r["series"] for r in rows}):
                g = sorted(r["mid_gap"] for r in rows if r["series"] == ser and "mid_gap" in r)
                if g:
                    print(f"   {ser}: {len(g)} matched, median middle gap {g[len(g)//2]:+.3f}, "
                          f"yes cheap 3c+ after fee {sum(r.get('yes_gap', -1) >= .03 for r in rows if r['series'] == ser)}, "
                          f"no cheap 3c+ {sum(r.get('no_gap', -1) >= .03 for r in rows if r['series'] == ser)}")
        print(f"  cheap 3c+ after fee: Yes {len(yg)}, No {len(ng)}")
        for r in sorted(yg + ng, key=lambda r: -max(r.get('yes_gap', -1), r.get('no_gap', -1)))[:15]:
            print(f"   {r['kt']} | {r['desc']} {r['line']}+ | pin fair {r['fair'][0]:.3f}/{r['fair'][1]:.3f} lim ${r['limit']:.0f} "
                  f"| kalshi {r['bid']}/{r['ask']} vol {r['vol']:.0f} | yes {r.get('yes_gap')} no {r.get('no_gap')}")
        sys.stdout.flush()
        if time.time() + float(every) * 60 > t_end:
            break
        time.sleep(float(every) * 60)


def live_score():
    """Settle every saved snapshot through Kalshi's results: would 'buy the side 3c+ cheap vs Pinnacle' have won?"""
    store = rj(LIVE, {"snaps": []}) or {"snaps": []}
    tks = sorted({r["kt"] for s in store["snaps"] for r in s["rows"]})
    res = {}

    def one(t):
        try:
            m = yesno.kget(f"/markets/{t}").get("market") or {}
            return t, str(m.get("result") or "")
        except Exception:
            return t, ""
    with ThreadPoolExecutor(8) as ex:
        for t, r in ex.map(one, tks):
            res[t] = r
    print(f"snapshots {len(store['snaps'])}, markets {len(tks)}, settled {sum(v in ('yes', 'no') for v in res.values())}")
    import exam
    for gap in (0.0, 0.02, 0.03, 0.05):
        bets, seen = [], set()
        for s in store["snaps"]:
            for r in s["rows"]:
                rr = res.get(r["kt"])
                if rr not in ("yes", "no") or r["kt"] in seen:
                    continue
                for side, g in (("yes", r.get("yes_gap")), ("no", r.get("no_gap"))):
                    if g is None or g < gap:
                        continue
                    px = r["ask"] if side == "yes" else 1 - r["bid"]
                    n = max(1, int(25 / px))
                    cost = n * px + bot.kalshi_fee(n, px)
                    bets.append({"ev": r["kt"].rsplit("-", 2)[0], "t": s["t"], "cost": cost, "pay": n * (rr == side),
                                 "side": side})
                    seen.add(r["kt"])
                    break
        if bets:
            exam.score(bets, f"props: Kalshi side {int(gap*100)}c+ cheaper than Pinnacle fair (live snaps)", tries=8,
                       src="props.py live_score", log=False)
        else:
            print("no bets at gap", gap)
    # calibration: Pinnacle fair vs Kalshi middle, which is closer to the result (Brier)
    bp = bk = n = 0
    for s in store["snaps"][-1:] + store["snaps"][:1]:
        for r in s["rows"]:
            rr = res.get(r["kt"])
            if rr not in ("yes", "no") or not r.get("bid") or not r.get("ask"):
                continue
            y = rr == "yes"
            bp += (sum(r["fair"]) / 2 - y) ** 2
            bk += ((r["bid"] + r["ask"]) / 2 - y) ** 2
            n += 1
    if n:
        print(f"forecast error (lower is better) on {n}: Pinnacle fair {bp/n:.4f}, Kalshi middle {bk/n:.4f}")


# ================================================================ history: Kalshi prop ladders, every real quote
import random

SER = ["KXNBAPTS", "KXNBAREB", "KXNBAAST", "KXNBA3PT", "KXNFLTD", "KXNFLANYTD", "KXNFLFIRSTTD", "KXNFLRECYDS",
       "KXNFLRSHYDS", "KXNFLPASSYDS", "KXNFLREC", "KXMLBHR", "KXMLBKS", "KXMLBHIT", "KXNHLGOAL", "KXNHLPTS",
       "KXWNBAPTS", "KXEPLGOAL", "KXUCLGOAL", "KXLALIGAGOAL"]
MKS = os.path.join(CACHE, "markets.json.gz")
STARTS = os.path.join(CACHE, "starts.json.gz")
PER = int(os.environ.get("PP_N", "1500"))      # markets taped per series (random, fixed seed)
MINV = 300                                    # contracts traded, at least
SPAN = 4 * 86400                              # quotes and trades of the last 4 days before close
T0 = time.time()
BUDGET = float(os.environ.get("PP_MIN", "250")) * 60


def game_key(ev):
    """'KXNBAPTS-26NOV24MEMSAC' -> '26NOV24MEMSAC' (the same game in every series)."""
    return ev.split("-", 1)[1] if "-" in ev else ev


def starts():
    """{game key: start unix} from Kalshi's schedule, back to Nov 2025."""
    have = rj(STARTS, {}) or {}
    cur, n = None, 0
    t0 = "2025-10-01T00:00:00Z"
    for _ in range(4000):
        p = {"limit": 500, "minimum_start_date": t0, "category": "Sports"}
        if cur:
            p["cursor"] = cur
        try:
            r = yesno.kget("/milestones", p)
        except Exception as e:
            print("milestones failed", str(e)[:120])
            break
        rows = r.get("milestones") or []
        for ms in rows:
            st = khouse.its(ms.get("start_date"))
            if not st:
                continue
            for ev in (ms.get("related_event_tickers") or []) + (ms.get("primary_event_tickers") or []):
                k = game_key(ev)
                if k not in have or st < have[k]:
                    have[k] = st
        n += len(rows)
        cur = r.get("cursor")
        if not cur or not rows:
            break
    print(f"milestones read {n}, games with a start time {len(have)}", flush=True)
    wj(STARTS, have)
    return have


def tape(m):
    a, b = max(m["open"], m["close"] - SPAN), m["close"]
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
    tr, done, path = khouse.trades_span(m["t"], a, b, 3)
    tr.sort()
    return m["t"], {"c": cs, "tr": tr, "full": done}


def fetch(part="0", parts="1"):
    part, parts = int(part), int(parts)
    os.makedirs(CACHE, exist_ok=True)
    if part == 0:
        starts()
    allm = rj(MKS, {}) or {}
    for i, ser in enumerate(SER):
        if i % parts != part:
            continue
        if time.time() - T0 > BUDGET:
            print("time budget used, run again to resume")
            break
        sp = os.path.join(CACHE, f"tapes_{ser}.json.gz")
        got = rj(sp, {}) or {}
        _, ok, n = km.series_markets(ser)
        v = [m for m in ok.values() if m["vol"] >= MINV]
        for m in v:
            mm = re.match(r"^(.*?):\s*(\d+)\+\s*$", m["w"])
            m["player"], m["line"] = (mm.group(1).strip(), int(mm.group(2))) if mm else (m["w"], None)
        wj(os.path.join(CACHE, f"mk_{ser}.json.gz"), {m["t"]: m for m in v})
        random.Random(7).shuffle(v)
        todo = [m for m in v[:PER] if m["t"] not in got]
        print(f"{ser}: {n} listed, {len(ok)} settled, {len(v)} with {MINV}+ traded, taping {len(todo)} more "
              f"(have {len(got)})", flush=True)
        with ThreadPoolExecutor(8) as ex:
            for k, (tk, d) in enumerate(ex.map(tape, todo)):
                got[tk] = d
                if k % 500 == 499:
                    wj(sp, got)
                if time.time() - T0 > BUDGET:
                    break
        wj(sp, got)
        print(f"  {ser}: {len(got)} taped, {sum(1 for d in got.values() if not d['c'])} without quotes, "
              f"{sum(len(d['tr']) for d in got.values())} trades ({time.time() - T0:.0f}s)", flush=True)


def scan():
    for f in (kalshi_scan, poly_scan, pin_scan):
        try:
            f()
        except Exception as e:
            print(f.__name__, "FAILED", repr(e)[:300])
        sys.stdout.flush()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "scan"
    {"scan": scan, "kalshi": kalshi_scan, "poly": poly_scan, "pin": pin_scan, "live": live, "livescore": live_score,
     "fetch": lambda *a: fetch(*a), "report": lambda *a: report(*a)}[cmd](*sys.argv[2:])
