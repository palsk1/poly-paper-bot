#!/usr/bin/env python3
"""Live tennis dig (22 Nov 2026): do Polymarket / Kalshi tennis prices over- or under-react after a break of serve
or a lost set, against a simple point-based win model? Research only. PAPER ONLY, never trades, never writes state/.

    python3 tennis.py scout      (probe `ten_scout`: what tennis markets exist, which free score feeds Actions can read)
"""
import collections
import datetime as dt
import gzip
import json
import os
import re
import sys
import time
import urllib.request

import bot
import yesno

G, D, K = bot.GAMMA, bot.DATA, bot.KALSHI
CACHE = os.path.join("bt_cache", "ten")
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"


def raw(url, timeout=25, headers=None):
    h = {"User-Agent": UA, "Accept": "*/*"}
    h.update(headers or {})
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def short(x, n=500):
    s = json.dumps(x, default=str) if not isinstance(x, str) else x
    return s[:n]


def jl(x):
    if isinstance(x, list):
        return x
    try:
        return json.loads(x or "[]")
    except Exception:
        return []


def scout():
    print("=== A. feeds reachable from here ===", flush=True)
    for name, url in (
            ("sackmann slam pbp files", "https://api.github.com/repos/JeffSackmann/tennis_slam_pointbypoint/contents/"),
            ("sackmann pbp files", "https://api.github.com/repos/JeffSackmann/tennis_pointbypoint/contents/"),
            ("sackmann atp files", "https://api.github.com/repos/JeffSackmann/tennis_atp/contents/"),
            ("sackmann charting", "https://api.github.com/repos/JeffSackmann/tennis_MatchChartingProject/contents/"),
            ("sofascore live", "https://api.sofascore.com/api/v1/sport/tennis/events/live"),
            ("sofascore www", "https://www.sofascore.com/api/v1/sport/tennis/events/live"),
            ("espn atp", "https://site.api.espn.com/apis/site/v2/sports/tennis/atp/scoreboard"),
            ("livescore", "https://prod-public-api.livescore.com/v1/api/app/live/tennis/0"),
            ("flashscore feed", "https://www.flashscore.com/tennis/"),
            ("tennis-data 2026", "http://www.tennis-data.co.uk/2026/2026.xlsx"),
            ("api-tennis", "https://api.api-tennis.com/tennis/?method=get_livescore"),
            ("365scores", "https://webws.365scores.com/web/games/current/?appTypeId=5&langId=1&sports=3"),
            ("aiscore", "https://api.aiscore.com/v1/web/api/match/live?sport_id=3"),
            ("wta live", "https://api.wtatennis.com/tennis/tournaments/?page=0&pageSize=5&excludeLevels=ITF&from=2026-11-15&to=2026-11-30"),
            ("atp live", "https://app.atptour.com/api/v2/gateway/livematches/website?scoringTournamentLevel=tour"),
            ("atp chall", "https://app.atptour.com/api/v2/gateway/livematches/website?scoringTournamentLevel=challenger"),
            ("itf live", "https://www.itftennis.com/tennis/api/LiveScores/GetLiveScores"),
    ):
        try:
            b = raw(url)
            txt = b[:4000].decode("utf-8", "replace")
            if "api.github.com" in url:
                js = json.loads(b)
                txt = " ".join(f"{x['name']}" for x in js)[-900:] + f"  ({len(js)} files)"
            print(f"  OK   {name}: {len(b)} bytes: {txt[:900]}", flush=True)
        except Exception as e:
            print(f"  FAIL {name}: {str(e)[:120]}", flush=True)

    print("\n=== B. Polymarket tennis ===", flush=True)
    for slug in ("tennis", "atp", "wta"):
        try:
            tg = bot.http_json(f"{G}/tags/slug/{slug}")
            print(f"  tag {slug}: id {tg.get('id')}", flush=True)
        except Exception as e:
            print(f"  tag {slug}: {str(e)[:80]}")
            continue
        for closed in ("false", "true"):
            cur, n, months, shown = None, 0, collections.Counter(), 0
            vols = []
            for _ in range(40 if closed == "true" else 8):
                p = {"tag_id": tg["id"], "closed": closed, "limit": 50}
                if cur:
                    p["after_cursor"] = cur
                try:
                    r = bot.http_json(f"{G}/events/keyset", p)
                except Exception as e:
                    print("   page failed", str(e)[:100])
                    break
                rows = [e for e in bot.envelope_rows(r, "events", "data") if isinstance(e, dict)]
                for e in rows:
                    n += 1
                    months[str(e.get("endDate") or e.get("startDate") or "")[:7]] += 1
                    vols.append(bot.fnum(e.get("volume"), 0))
                    if shown < 3 and bot.fnum(e.get("volume"), 0) > 20000:
                        shown += 1
                        ms = e.get("markets") or []
                        print(f"   EVENT {closed}: {short({k: e.get(k) for k in ('id', 'slug', 'title', 'startDate', 'endDate', 'startTime', 'gameId', 'volume', 'live', 'ended', 'score', 'period', 'elapsed', 'eventDate', 'seriesSlug')}, 700)}")
                        print(f"     tags {[t.get('slug') for t in e.get('tags') or []]}")
                        for m in ms[:6]:
                            print(f"     MKT {short({k: m.get(k) for k in ('question', 'sportsMarketType', 'conditionId', 'gameStartTime', 'volume', 'outcomes', 'outcomePrices', 'closedTime', 'feesEnabled', 'feeSchedule', 'takerBaseFee', 'makerBaseFee', 'orderMinSize', 'orderPriceMinTickSize', 'secondsDelay', 'bestBid', 'bestAsk', 'line')}, 900)}")
                cur = r.get("next_cursor") if isinstance(r, dict) else None
                if not rows or not cur:
                    break
            vols.sort()
            print(f"  tag {slug} closed={closed}: {n} events (more: {bool(cur)}), months {dict(sorted(months.items()))}, "
                  f"volume median ${vols[len(vols) // 2] if vols else 0:,.0f}, top tenth ${vols[int(len(vols) * .9)] if vols else 0:,.0f}", flush=True)

    # one finished match: how dense is the trade list during play?
    print("\n=== B2. one finished match tape ===", flush=True)
    try:
        import informed
        tg = bot.http_json(f"{G}/tags/slug/tennis")
        r = bot.http_json(f"{G}/events/keyset", {"tag_id": tg["id"], "closed": "true", "limit": 50})
        evs = [e for e in bot.envelope_rows(r, "events", "data") if isinstance(e, dict)]
        evs.sort(key=lambda e: -bot.fnum(e.get("volume"), 0))
        for e in evs[:3]:
            for m in (e.get("markets") or []):
                if m.get("sportsMarketType") not in ("moneyline", None):
                    continue
                rows, more = informed.tape(m["conditionId"], 60)
                ts = sorted(int(bot.fnum(bot.pick(x, "timestamp", "time"))) for x in rows)
                gs = m.get("gameStartTime")
                print(f"  {e.get('title')} | {m.get('question')} vol ${bot.fnum(m.get('volume'), 0):,.0f} start {gs} closed {m.get('closedTime')}: {len(rows)} trades (more {more}) "
                      f"{dt.datetime.utcfromtimestamp(ts[0]) if ts else ''} .. {dt.datetime.utcfromtimestamp(ts[-1]) if ts else ''}")
                if rows:
                    print("   row", short(rows[0], 700))
                    g0 = bot.parse_iso(str(gs).replace(" ", "T").replace("+00", "+00:00")) if gs else None
                    if g0:
                        g0 = g0.timestamp()
                        inplay = [t for t in ts if t >= g0]
                        per = collections.Counter((t - int(g0)) // 600 for t in inplay)
                        print(f"   in play: {len(inplay)} trades; per 10 min: {[per[i] for i in range(0, 18)]}")
                break
    except Exception as e:
        print("  tape failed", str(e)[:200])

    print("\n=== C. Kalshi tennis ===", flush=True)
    try:
        ser, cur = [], None
        for _ in range(30):
            p = {"category": "Sports", "limit": 1000}
            if cur:
                p["cursor"] = cur
            r = yesno.kget("/series", p)
            ser += r.get("series") or []
            cur = r.get("cursor")
            if not cur:
                break
        ten = [s for s in ser if re.search(r"tennis|\batp\b|\bwta\b|wimbledon|roland|us open|australian open|challenger|davis", f"{s.get('title')} {s.get('ticker')} {s.get('tags')}", re.I)]
        print(f"  {len(ser)} sports series, {len(ten)} tennis-looking")
        for s in ten[:80]:
            print(f"   {s.get('ticker')}: {s.get('title')} | {s.get('frequency')} | fee {s.get('fee_type')} x{s.get('fee_multiplier')} | tags {s.get('tags')}")
        now = int(time.time())
        for s in ten:
            tk = s.get("ticker")
            if not re.search(r"MATCH|GAME$", tk or ""):
                continue
            try:
                r = yesno.kget("/markets", {"series_ticker": tk, "status": "settled", "limit": 1000, "min_close_ts": now - 30 * 86400})
                ms = r.get("markets") or []
                r2 = yesno.kget("/markets", {"series_ticker": tk, "status": "open", "limit": 200})
                mo = r2.get("markets") or []
            except Exception as e:
                print(f"   {tk}: {str(e)[:80]}")
                continue
            vs = sorted(bot.fnum(m.get("volume_fp") or m.get("volume"), 0) for m in ms)
            print(f"   {tk}: {len(ms)} settled in 30 days (more {bool(r.get('cursor'))}), {len(mo)} open; contracts median {vs[len(vs) // 2] if vs else 0:,.0f} top tenth {vs[int(len(vs) * .9)] if vs else 0:,.0f}", flush=True)
            if ms:
                m = max(ms, key=lambda m: bot.fnum(m.get("volume_fp") or m.get("volume"), 0))
                print("    busiest:", short({k: m.get(k) for k in ("ticker", "event_ticker", "title", "yes_sub_title", "open_time", "close_time", "expected_expiration_time", "result", "volume_fp", "volume", "rules_primary", "can_close_early", "tick_size", "price_level_structure")}, 900))
                c0 = bot.parse_iso(m.get("close_time")).timestamp()
                for iv in (1, 60):
                    try:
                        cr = yesno.kget(f"/series/{tk}/markets/{m['ticker']}/candlesticks", {"start_ts": int(c0 - 5 * 3600), "end_ts": int(c0), "period_interval": iv})
                        cs = cr.get("candlesticks") or []
                        print(f"    candles every {iv} min: {len(cs)}; sample {short(cs[len(cs) // 2] if cs else None, 500)}")
                    except Exception as e:
                        print(f"    candles {iv}: {str(e)[:100]}")
                try:
                    tr = yesno.kget("/markets/trades", {"ticker": m["ticker"], "limit": 1000})
                    tt = tr.get("trades") or []
                    print(f"    trades page: {len(tt)} (more {bool(tr.get('cursor'))}); sample {short(tt[0] if tt else None, 400)}")
                except Exception as e:
                    print(f"    trades: {str(e)[:100]}")
            if mo:
                m = mo[0]
                print("    open sample:", short({k: m.get(k) for k in ("ticker", "title", "yes_sub_title", "yes_bid_dollars", "yes_ask_dollars", "close_time", "expected_expiration_time", "volume_fp")}, 500))
        try:
            ml = yesno.kget("/milestones", {"limit": 100, "minimum_start_date": dt.datetime.utcnow().strftime("%Y-%m-%dT00:00:00Z"), "category": "Sports"})
            mm = [x for x in ml.get("milestones") or [] if re.search("tennis|atp|wta", json.dumps(x), re.I)]
            print(f"  milestones: {len(ml.get('milestones') or [])}, tennis {len(mm)}; sample {short(mm[0] if mm else (ml.get('milestones') or [None])[0], 900)}")
            if mm:
                ld = yesno.kget(f"/live_data/{mm[0].get('type')}/milestone/{mm[0].get('id')}")
                print("  live_data:", short(ld, 1200))
        except Exception as e:
            print("  milestones failed", str(e)[:150])
    except Exception as e:
        print("  kalshi failed", str(e)[:200])

    print("\n=== D. Polymarket sports websocket, 45 s: tennis messages ===", flush=True)
    try:
        import asyncio
        import websockets

        async def listen():
            seen, by_league = [], collections.Counter()
            end = time.time() + 45
            async with websockets.connect("wss://sports-api.polymarket.com/ws", ping_interval=None, max_size=None, open_timeout=20) as ws:
                while time.time() < end:
                    try:
                        rawm = await asyncio.wait_for(ws.recv(), timeout=10)
                    except asyncio.TimeoutError:
                        continue
                    if rawm == "ping":
                        await ws.send("pong")
                        continue
                    try:
                        msg = json.loads(rawm)
                    except Exception:
                        continue
                    for x in (msg if isinstance(msg, list) else [msg]):
                        if isinstance(x, dict):
                            by_league[str(x.get("leagueAbbreviation"))] += 1
                            if re.search("atp|wta|tennis|itf|chall", str(x.get("leagueAbbreviation")) + str(x.get("slug")), re.I):
                                seen.append((round(time.time(), 2), x))
            print("  messages by league:", dict(by_league.most_common(40)))
            print(f"  tennis messages: {len(seen)}")
            for t, x in seen[:25]:
                print("   ", t, short(x, 600))
        asyncio.run(listen())
    except Exception as e:
        print("  ws failed", str(e)[:200])



# ================================================================ the point-based win model
# Each player wins a fixed share of the points on their own serve (pa, pb). Everything else follows by counting:
# points -> game -> set (tiebreak at 6-6) -> match. The pre-match price fixes the gap between pa and pb.
from functools import lru_cache


def p_game(p, a=0, b=0):
    """Chance the server wins the game from points a-b (0..3 = 0/15/30/40, deuce handled)."""
    if a >= 4 and a - b >= 2:
        return 1.0
    if b >= 4 and b - a >= 2:
        return 0.0
    if a >= 3 and b >= 3:
        d = p * p / (p * p + (1 - p) * (1 - p))
        return d if a == b else (p + (1 - p) * d if a > b else p * d)
    return p * p_game(p, a + 1, b) + (1 - p) * p_game(p, a, b + 1)


@lru_cache(maxsize=None)
def _tb(pa, pb, a, b, srv, to):
    """Chance A wins a tiebreak to `to` from a-b; srv = 0 if A serves the NEXT point."""
    if a >= to and a - b >= 2:
        return 1.0
    if b >= to and b - a >= 2:
        return 0.0
    if a >= to - 1 and b >= to - 1 and a == b:      # two points, one on each serve
        wa, wb = pa, 1 - pb
        return wa * wb / (wa * wb + (1 - wa) * (1 - wb))
    w = pa if srv == 0 else 1 - pb
    n = a + b + 1                                   # points played after this one
    nxt = srv if n % 2 == 0 else 1 - srv            # serve changes after odd points (1, 3, 5, ...)
    return w * _tb(pa, pb, a + 1, b, nxt, to) + (1 - w) * _tb(pa, pb, a, b + 1, nxt, to)


@lru_cache(maxsize=None)
def _set(pa, pb, ga, gb, srv):
    """Chance A wins the set from games ga-gb, srv = 0 if A serves the next game (start of a game)."""
    if ga >= 6 and ga - gb >= 2:
        return 1.0
    if gb >= 6 and gb - ga >= 2:
        return 0.0
    if ga == 6 and gb == 6:
        return _tb(pa, pb, 0, 0, srv, 7)
    h = p_game(pa) if srv == 0 else 1 - p_game(pb)
    return h * _set(pa, pb, ga + 1, gb, 1 - srv) + (1 - h) * _set(pa, pb, ga, gb + 1, 1 - srv)


@lru_cache(maxsize=None)
def _match(pa, pb, sa, sb, best):
    """Chance A wins the match at the START of a set with sets sa-sb. Who serves first in a set barely matters."""
    need = best // 2 + 1
    if sa >= need:
        return 1.0
    if sb >= need:
        return 0.0
    s = (_set(pa, pb, 0, 0, 0) + _set(pa, pb, 0, 0, 1)) / 2
    return s * _match(pa, pb, sa + 1, sb, best) + (1 - s) * _match(pa, pb, sa, sb + 1, best)


def p_match(pa, pb, sa=0, sb=0, ga=0, gb=0, srv=None, pts=None, best=3):
    """Chance A wins the match from any score. srv: 0 = A serves this game, 1 = B, None = unknown (average).
    pts = (server's points, receiver's points) inside the current game, or tiebreak points (a, b) at 6-6."""
    pa, pb = round(pa, 4), round(pb, 4)
    need = best // 2 + 1
    if sa >= need:
        return 1.0
    if sb >= need:
        return 0.0
    if srv is None:
        return (p_match(pa, pb, sa, sb, ga, gb, 0, None, best) + p_match(pa, pb, sa, sb, ga, gb, 1, None, best)) / 2
    w_set, l_set = _match(pa, pb, sa + 1, sb, best), _match(pa, pb, sa, sb + 1, best)
    if ga == 6 and gb == 6:
        a, b = pts or (0, 0)
        first = srv if (a + b) % 4 in (0, 3) else 1 - srv   # srv = who served the first tiebreak point
        s = _tb(pa, pb, a, b, first if pts else srv, 7)
    else:
        if pts:
            g = p_game(pa if srv == 0 else pb, pts[0], pts[1])
            h = g if srv == 0 else 1 - g
        else:
            h = p_game(pa) if srv == 0 else 1 - p_game(pb)
        s = h * _set(pa, pb, ga + 1, gb, 1 - srv) + (1 - h) * _set(pa, pb, ga, gb + 1, 1 - srv)
    return s * w_set + (1 - s) * l_set


def fit_gap(p0, base=0.62, best=3):
    """Serve shares (pa, pb) around `base` whose pre-match chance for A equals the pre-match price p0."""
    lo, hi = -0.3, 0.3
    for _ in range(40):
        mid = (lo + hi) / 2
        if p_match(base + mid, base - mid, best=best) < p0:
            lo = mid
        else:
            hi = mid
    d = (lo + hi) / 2
    return round(base + d, 4), round(base - d, 4)


def model_selftest():
    assert abs(p_game(0.5) - 0.5) < 1e-9 and abs(p_game(0.6) - 0.7357) < 1e-3, p_game(0.6)
    assert abs(p_match(0.62, 0.62) - 0.5) < 1e-9
    assert abs(p_match(0.65, 0.60) + p_match(0.60, 0.65) - 1) < 1e-9
    a, b = fit_gap(0.7)
    assert abs(p_match(a, b) - 0.7) < 1e-3, (a, b)
    even_down_set = p_match(0.62, 0.62, 0, 1)
    assert abs(even_down_set - 0.25) < 1e-9, even_down_set
    brk = p_match(0.62, 0.62, 0, 0, 2, 1, 0)        # a break up, serving
    assert 0.6 < brk < 0.8, brk
    assert p_match(0.62, 0.62, 0, 0, 0, 0, 0, (3, 0)) > p_match(0.62, 0.62, 0, 0, 0, 0, 0, (0, 3))
    print(f"model ok: even match, a set down {even_down_set:.2f}; a break up at 2-1 {brk:.3f}; "
          f"70c favourite a set down {p_match(a, b, 0, 1):.3f}, a set up {p_match(a, b, 1, 0):.3f}")



def keys_tree(x, depth=3, pre=""):
    """Compact shape of a JSON thing."""
    if isinstance(x, dict):
        if depth <= 0:
            return "{..}"
        return "{" + ", ".join(f"{k}: {keys_tree(v, depth - 1)}" for k, v in list(x.items())[:40]) + "}"
    if isinstance(x, list):
        return f"[{len(x)}x {keys_tree(x[0], depth - 1) if x else ''}]"
    return short(str(x), 40)


def scout2():
    print("=== feeds: shapes ===", flush=True)
    try:
        j = json.loads(raw("https://site.api.espn.com/apis/site/v2/sports/tennis/atp/scoreboard"))
        evs = j.get("events") or []
        print("espn events", len(evs), [e.get("name") for e in evs][:5])
        for e in evs[:2]:
            for g in (e.get("groupings") or [])[:2]:
                cs = g.get("competitions") or []
                print("  grouping", (g.get("grouping") or {}).get("slug"), len(cs))
                live = [c for c in cs if ((c.get("status") or {}).get("type") or {}).get("state") == "in"] or cs[-1:]
                for c in live[:2]:
                    print("   comp", short({"id": c.get("id"), "date": c.get("date"), "status": (c.get("status") or {}).get("type"), "period": (c.get("status") or {}).get("period"),
                                             "players": [[(x.get("athlete") or {}).get("displayName"), x.get("linescores"), x.get("possession"), x.get("winner")] for x in c.get("competitors") or []]}, 900))
    except Exception as e:
        print("espn failed", str(e)[:150])
    try:
        j = json.loads(raw("https://webws.365scores.com/web/games/current/?appTypeId=5&langId=1&sports=3"))
        gs = j.get("games") or []
        print("365 games", len(gs), "live", sum(1 for g in gs if g.get("statusGroup") == 3))
        lv = [g for g in gs if g.get("statusGroup") == 3] or gs[:1]
        for g in lv[:2]:
            print("  365 game:", short(g, 2500))
    except Exception as e:
        print("365 failed", str(e)[:150])
    try:
        j = json.loads(raw("https://prod-public-api.livescore.com/v1/api/app/live/tennis/0"))
        for st in (j.get("Stages") or [])[:3]:
            for e in (st.get("Events") or [])[:1]:
                print("  livescore event:", st.get("Snm"), short(e, 1500))
    except Exception as e:
        print("livescore failed", str(e)[:150])

    print("\n=== Kalshi tennis series (all) ===", flush=True)
    ser, cur = [], None
    for _ in range(30):
        p = {"category": "Sports", "limit": 1000}
        if cur:
            p["cursor"] = cur
        r = yesno.kget("/series", p)
        ser += r.get("series") or []
        cur = r.get("cursor")
        if not cur:
            break
    ten = [s for s in ser if "Tennis" in (s.get("tags") or [])]
    print(len(ten), "series:", "; ".join(f"{s['ticker']}={s.get('title')}" for s in ten))
    now = int(time.time())
    for s in ten:
        tk = s["ticker"]
        if not re.search(r"SET|GAME|GWIN|TOTAL|EXACT|S\dG", tk):
            continue
        try:
            r = yesno.kget("/markets", {"series_ticker": tk, "status": "settled", "limit": 1000, "min_close_ts": now - 14 * 86400})
        except Exception as e:
            print(" ", tk, str(e)[:60])
            continue
        ms = r.get("markets") or []
        if not ms:
            continue
        vs = sorted(bot.fnum(m.get("volume_fp"), 0) for m in ms)
        evs = collections.defaultdict(list)
        for m in ms:
            evs[m.get("event_ticker")].append(m)
        ev, mm = max(evs.items(), key=lambda kv: len(kv[1]))
        print(f"  {tk}: {len(ms)} settled in 14 days (more {bool(r.get('cursor'))}), {len(evs)} events, contracts median {vs[len(vs) // 2]:,.0f}")
        for m in sorted(mm, key=lambda m: m.get("close_time") or "")[:14]:
            print(f"     {m['ticker']} | {m.get('title')} | {m.get('yes_sub_title')} | close {m.get('close_time')} | res {m.get('result')} | vol {m.get('volume_fp')}")
    # tennis milestones + live data
    try:
        seen = 0
        cur = None
        for _ in range(8):
            p = {"limit": 500, "minimum_start_date": time.strftime("%Y-%m-%dT00:00:00Z", time.gmtime(now - 86400)), "category": "Sports"}
            if cur:
                p["cursor"] = cur
            ml = yesno.kget("/milestones", p)
            for x in ml.get("milestones") or []:
                if x.get("type") == "tennis_match" or "tennis" in str(x.get("type")) and "table" not in str(x.get("type")):
                    seen += 1
                    if seen <= 4:
                        print("  milestone:", short(x, 700))
                        try:
                            print("   live_data:", short(yesno.kget(f"/live_data/{x.get('type')}/milestone/{x.get('id')}"), 1500))
                        except Exception as e:
                            print("   live_data failed", str(e)[:120])
            cur = ml.get("cursor")
            if not cur:
                break
        print("  tennis milestones:", seen)
    except Exception as e:
        print("  milestones failed", str(e)[:150])

    print("\n=== Polymarket tennis matches ===", flush=True)
    for q in ({"series_slug": "atp"}, {"tag_slug": "tennis", "order": "startDate", "ascending": "false"}):
        try:
            r = bot.http_json(f"{G}/events", dict(q, closed="true", limit=50))
            r = bot.envelope_rows(r, "events", "data")
            print(" query", q, "->", len(r), [(e.get("slug"), str(e.get("startDate"))[:10]) for e in r[:4]])
        except Exception as e:
            print(" query", q, "failed", str(e)[:100])
    try:
        srs = bot.http_json(f"{G}/series", {"slug": "atp"})
        srs = bot.envelope_rows(srs, "series", "data")
        for sr in srs[:2]:
            print(" series atp:", short({k: v for k, v in sr.items() if k != "events"}, 500), "events", len(sr.get("events") or []))
    except Exception as e:
        print(" series failed", str(e)[:100])
    # recent matches: set markets' closed times against the trades
    try:
        import informed
        r = bot.http_json(f"{G}/events", {"tag_slug": "tennis", "closed": "true", "limit": 50, "order": "startDate", "ascending": "false"})
        evs = [e for e in bot.envelope_rows(r, "events", "data") if e.get("gameId")]
        evs.sort(key=lambda e: -bot.fnum(e.get("volume"), 0))
        for e in evs[:3]:
            print(f" MATCH {e.get('title')} | score {e.get('score')} | start {e.get('startTime')} | vol ${bot.fnum(e.get('volume'), 0):,.0f} | {len(e.get('markets') or [])} markets")
            g0 = bot.parse_iso(e.get("startTime")).timestamp()
            for m in e.get("markets") or []:
                typ = m.get("sportsMarketType")
                if typ not in ("moneyline", "tennis_first_set_winner", "tennis_set_winner"):
                    continue
                rows, more = informed.tape(m["conditionId"], 40)
                tt = sorted((int(bot.fnum(x.get("timestamp"))), x.get("outcome_index"), x.get("side"), bot.fnum(x.get("price")), bot.fnum(x.get("size"))) for x in rows)
                ct = bot.parse_iso(str(m.get("closedTime")).replace(" ", "T").replace("+00", "+00:00"))
                ct = ct.timestamp() if ct else 0
                inplay = [x for x in tt if x[0] >= g0]
                print(f"   {typ} line {m.get('line')} | {m.get('question')} | prices {m.get('outcomePrices')} | closed +{(ct - g0) / 60:.1f} min after start | {len(tt)} trades (more {more}), {len(inplay)} in play, "
                      f"$ in play {sum(x[3] * x[4] for x in inplay):,.0f}, umaEnd {m.get('umaEndDate')} resolvedBy {str(m.get('resolvedBy'))[:12]} automaticallyResolved {m.get('automaticallyResolved')}")
                last = [x for x in tt if x[0] <= ct][-6:]
                print("      last trades before close (sec before close, outcome, side, price, size):", [(int(ct - x[0]), x[1], x[2], x[3], round(x[4])) for x in last])
                if typ == "moneyline":
                    per = collections.Counter(int(x[0] - g0) // 600 for x in inplay)
                    print("      trades per 10 min in play:", [per[i] for i in range(0, 20)])
                    o0 = [(x[0], x[3] if x[1] == 0 else 1 - x[3]) for x in tt]
                    pth = []
                    for k in range(-2, 40):
                        c = [p for t, p in o0 if t <= g0 + k * 300]
                        pth.append(round(c[-1], 2) if c else None)
                    print("      player-1 price every 5 min from 10 min before start:", pth)
    except Exception as e:
        import traceback
        traceback.print_exc()


# ================================================================ live recorder (probe `ten_live_<minutes>`)
# Records, with our own clock: Polymarket's free score feed (one update a game), the best bid / ask and every trade of
# each live match-winner market, Kalshi's quotes and Kalshi's own live score (who serves, points) for the same
# matches, and 365scores' live score. Raw lines go to ten_cache/live/ (shared store), so the test can be redone offline.
LIVE_DIR = os.path.join("ten_cache", "live")
K_SERIES = ("KXATPMATCH", "KXWTAMATCH", "KXATPCHALLENGERMATCH", "KXWTACHALLENGERMATCH", "KXITFMATCH", "KXITFWMATCH")
TEN_LEAGUES = {"atp", "wta", "itf", "challenger", "wtachallenger", "atpchallenger", "tennis"}


def is_tennis(msg):
    return str(msg.get("leagueAbbreviation") or "").lower() in TEN_LEAGUES


def ten_index(force=False):
    import livelag
    idx = livelag._IDX
    if not force and time.time() - idx["t"] < 300:
        return idx
    by_gid, by_team, n = {}, {}, 0
    for off in range(0, 4000, 50):
        try:
            evs = bot.http_json(f"{G}/events", {"tag_slug": "tennis", "closed": "false", "limit": 50, "offset": off})
        except Exception as e:
            print(f"  gamma tennis page {off}: {str(e)[:80]}")
            break
        evs = evs if isinstance(evs, list) else []
        for ev in evs:
            n += 1
            for g in {ev.get("gameId")} | {m.get("gameId") for m in ev.get("markets") or []}:
                if g:
                    by_gid[str(g)] = ev
            by_team[(ev.get("title") or "").lower()] = ev
        if len(evs) < 50:
            break
    idx.update(t=time.time(), by_gid=by_gid, by_team=by_team)
    print(f"  gamma: {n} open tennis events, {len(by_gid)} with a gameId", flush=True)
    return idx


def make_rec():
    import threading
    import livelag

    class TRec(livelag.Rec):
        def __init__(self, path):
            super().__init__(path)
            self.lock = threading.Lock()
            self.lastq = {}
            self.n.update(q=0, trade=0, kq=0, kl=0, s365=0)

        def put(self, kind, obj):
            with self.lock:
                self.f.write(json.dumps({"k": kind, "t": round(time.time(), 3), **obj}, separators=(",", ":")) + "\n")

        def quote(self, tok, bb, ba, ts):
            if tok not in self.mkts or (bb, ba) == self.lastq.get(tok):
                return
            self.lastq[tok] = (bb, ba)
            self.n["q"] += 1
            self.put("q", {"tok": tok, "bb": bb, "ba": ba, "ts": ts})
            self.mid_point(tok, bb, ba, time.time())

        def on_market(self, msg):
            for m in (msg if isinstance(msg, list) else [msg]):
                if not isinstance(m, dict):
                    continue
                self.n["market"] += 1
                et = m.get("event_type") or m.get("type")
                ts = m.get("timestamp")
                try:
                    if ts:
                        self.lag_ms.append(time.time() * 1000 - float(ts))
                except Exception:
                    pass
                if et == "book":
                    tok = str(m.get("asset_id"))
                    if tok not in self.mkts:
                        continue
                    bids = sorted(m.get("bids") or [], key=lambda x: -float(x["price"]))[:3]
                    asks = sorted(m.get("asks") or [], key=lambda x: float(x["price"]))[:3]
                    self.put("book", {"tok": tok, "ts": ts, "b": [[x["price"], x["size"]] for x in bids], "a": [[x["price"], x["size"]] for x in asks]})
                    self.quote(tok, bids[0]["price"] if bids else None, asks[0]["price"] if asks else None, ts)
                elif et == "price_change":
                    for pc in m.get("price_changes") or m.get("changes") or []:
                        self.quote(str(pc.get("asset_id") or m.get("asset_id")), pc.get("best_bid"), pc.get("best_ask"), ts)
                elif et == "best_bid_ask":
                    self.quote(str(m.get("asset_id")), m.get("best_bid"), m.get("best_ask"), ts)
                elif et == "last_trade_price":
                    tok = str(m.get("asset_id"))
                    if tok in self.mkts:
                        self.n["trade"] += 1
                        self.put("trade", {"tok": tok, "p": m.get("price"), "s": m.get("size"), "sd": m.get("side"), "ts": ts})
    os.makedirs(LIVE_DIR, exist_ok=True)
    return TRec(os.path.join(LIVE_DIR, f"rec_{time.strftime('%Y%m%d_%H%M', time.gmtime())}.jsonl.gz"))


def kalshi_poll(rec, until):
    """Thread: Kalshi quotes + Kalshi's live score for matches in play, about every 2 s."""
    evs, last_ref, lastq, lastl, batch_ok = {}, 0, {}, {}, True
    while time.time() < until:
        t0 = time.time()
        try:
            if t0 - last_ref > 600:
                new = {}
                for sr in K_SERIES:
                    cur = None
                    for _ in range(5):
                        p = {"series_ticker": sr, "status": "open", "limit": 1000}
                        if cur:
                            p["cursor"] = cur
                        r = yesno.kget("/markets", p)
                        for m in r.get("markets") or []:
                            e = new.setdefault(m["event_ticker"], {"tks": [], "names": [], "exp": m.get("expected_expiration_time")})
                            e["tks"].append(m["ticker"])
                            e["names"].append(m.get("yes_sub_title"))
                        cur = r.get("cursor")
                        if not cur:
                            break
                cur = None
                for _ in range(10):
                    p = {"limit": 500, "category": "Sports", "minimum_start_date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t0 - 8 * 3600))}
                    if cur:
                        p["cursor"] = cur
                    r = yesno.kget("/milestones", p)
                    for x in r.get("milestones") or []:
                        if not str(x.get("type")).startswith("tennis"):
                            continue
                        for et in x.get("primary_event_tickers") or []:
                            if et in new:
                                new[et].update(ms=x.get("id"), typ=x.get("type"), start=bot.parse_iso(x.get("start_date")).timestamp() if x.get("start_date") else None)
                    cur = r.get("cursor")
                    if not cur:
                        break
                for et, e in new.items():
                    if et not in evs:
                        rec.put("kmeta", {"ev": et, **e})
                evs, last_ref = new, t0
                print(f"  kalshi: {len(evs)} open tennis events, {sum(1 for e in evs.values() if e.get('ms'))} with a live-score id", flush=True)
            live = {et: e for et, e in evs.items() if e.get("start") and e["start"] - 900 <= t0 <= e["start"] + 6 * 3600}
            tks = [sorted(e["tks"])[0] for e in live.values()]
            for i in range(0, len(tks), 60):
                r = yesno.kget("/markets", {"tickers": ",".join(tks[i:i + 60]), "limit": 100})
                for m in r.get("markets") or []:
                    sig = (m.get("yes_bid_dollars"), m.get("yes_ask_dollars"), m.get("status"))
                    if lastq.get(m["ticker"]) != sig:
                        lastq[m["ticker"]] = sig
                        rec.n["kq"] += 1
                        rec.put("kq", {"tk": m["ticker"], "yb": sig[0], "ya": sig[1], "st": sig[2], "v": m.get("volume_fp"),
                                       "bs": m.get("yes_bid_size_fp"), "as": m.get("yes_ask_size_fp")})
            ids = [(et, e) for et, e in live.items() if e.get("ms")]
            got = []
            if batch_ok and ids:
                try:
                    for i in range(0, len(ids), 50):
                        r = yesno.kget("/live_data/batch", {"milestone_ids": [e["ms"] for _, e in ids[i:i + 50]]})
                        got += r.get("live_datas") or r.get("live_data") or []
                except Exception as ex:
                    batch_ok = False
                    print("  kalshi live_data batch not available:", str(ex)[:100], flush=True)
            if not batch_ok:
                for et, e in ids[:40]:
                    try:
                        got.append(yesno.kget(f"/live_data/{e['typ']}/milestone/{e['ms']}").get("live_data"))
                    except Exception:
                        pass
            by_ms = {e["ms"]: et for et, e in ids}
            for ld in got:
                if not isinstance(ld, dict):
                    continue
                d = ld.get("details") or {}
                sig = json.dumps([d.get(k) for k in ("competitor1_round_scores", "competitor2_round_scores", "competitor1_current_round_score", "competitor2_current_round_score",
                                                     "server", "advantage", "status", "match_status", "competitor1_overall_score", "competitor2_overall_score")], default=str)
                mid = ld.get("milestone_id")
                if lastl.get(mid) != sig:
                    lastl[mid] = sig
                    rec.n["kl"] += 1
                    rec.put("kl", {"ev": by_ms.get(mid), "c1": d.get("competitor1_id"), "srv": d.get("server"), "adv": d.get("advantage"),
                                   "r1": [x.get("score") for x in d.get("competitor1_round_scores") or []], "r2": [x.get("score") for x in d.get("competitor2_round_scores") or []],
                                   "g1": d.get("competitor1_current_round_score"), "g2": d.get("competitor2_current_round_score"),
                                   "p1": d.get("competitor1_current_game_score", d.get("competitor1_game_score")), "p2": d.get("competitor2_current_game_score", d.get("competitor2_game_score")),
                                   "st": d.get("status"), "ms": d.get("match_status"), "raw": d if rec.n["kl"] <= 3 else None})
        except Exception as ex:
            print("  kalshi poll error:", str(ex)[:150], flush=True)
            time.sleep(5)
        time.sleep(max(0.2, 2.0 - (time.time() - t0)))


def s365_poll(rec, until):
    last = {}
    while time.time() < until:
        t0 = time.time()
        try:
            j = json.loads(raw("https://webws.365scores.com/web/games/current/?appTypeId=5&langId=1&sports=3", timeout=15))
            for g in j.get("games") or []:
                if g.get("statusGroup") != 3:
                    continue
                st = [[x.get("id"), x.get("homeCompetitorScore"), x.get("awayCompetitorScore")] for x in g.get("stages") or [] if x.get("homeCompetitorScore", -1) != -1]
                srv = 1 if (g.get("homeCompetitor") or {}).get("inPossession") else 2 if (g.get("awayCompetitor") or {}).get("inPossession") else 0
                sig = json.dumps([st, srv])
                if last.get(g["id"]) != sig:
                    last[g["id"]] = sig
                    rec.n["s365"] += 1
                    rec.put("s365", {"id": g["id"], "h": (g.get("homeCompetitor") or {}).get("name"), "a": (g.get("awayCompetitor") or {}).get("name"),
                                     "comp": g.get("competitionDisplayName"), "start": g.get("startTime"), "st": st, "srv": srv})
        except Exception as ex:
            print("  365 poll error:", str(ex)[:120], flush=True)
        time.sleep(max(0.5, 5.0 - (time.time() - t0)))


def live(minutes):
    import asyncio
    import threading
    import livelag
    livelag.is_esport = is_tennis
    livelag.game_index = ten_index
    rec = make_rec()
    until = time.time() + minutes * 60
    print(f"recording live tennis for {minutes:.0f} min -> {rec.f.name}", flush=True)
    for fn in (kalshi_poll, s365_poll):
        threading.Thread(target=fn, args=(rec, until), daemon=True).start()

    async def beat():
        while time.time() < until:
            await asyncio.sleep(max(1, min(600, until - time.time())))
            print(f"  {time.strftime('%H:%M', time.gmtime())} {dict(rec.n)} games followed {len(rec.slug_of)} markets {len(rec.mkts)}", flush=True)

    async def go():
        await asyncio.gather(livelag.sports_loop(rec, until), livelag.market_loop(rec, until), beat())
    asyncio.run(go())
    time.sleep(3)
    path = rec.f.name
    rec.close()
    print(f"done: {dict(rec.n)}; file {os.path.getsize(path) / 1e6:.1f} MB", flush=True)
    live_report([path])


def live_rows(paths):
    for p in paths:
        with gzip.open(p, "rt") as f:
            for line in f:
                try:
                    yield json.loads(line)
                except Exception:
                    continue


def live_report(paths):
    """How late is the free score feed? For every game end the feed reported: where was the price before and after."""
    import bisect
    meta, mids, changes, lastsc = {}, collections.defaultdict(list), [], {}
    for r in live_rows(paths):
        k = r["k"]
        if k == "meta":
            for m in r["markets"]:
                if m.get("type") == "moneyline":
                    meta[m["tok"]] = {"game": r["game"], "title": r.get("title"), "q": m.get("q")}
        elif k == "q":
            try:
                bb, ba = float(r["bb"]), float(r["ba"])
            except Exception:
                continue
            if 0 < bb < ba < 1 and ba - bb <= 0.1:
                mids[r["tok"]].append((r["t"], (bb + ba) / 2, bb, ba))
        elif k == "sport":
            m = r["m"]
            g = m.get("gameId")
            key = (m.get("score"), m.get("period"))
            if g in lastsc and lastsc[g] != key and m.get("live"):
                changes.append((r["t"], g, lastsc[g], key))
            lastsc[g] = key
    tok_of = {v["game"]: t for t, v in meta.items()}
    print(f"\n=== feed delay: {len(changes)} score changes on {len({c[1] for c in changes})} matches, {len(meta)} match-winner markets ===")

    def at(s, t):
        i = bisect.bisect_right(s, (t, 9, 9, 9)) - 1
        return s[i][1] if i >= 0 else None
    rows = []
    for t, g, old, new in changes:
        s = mids.get(tok_of.get(g))
        if not s:
            continue
        a, b = at(s, t - 90), at(s, t + 60)
        if a is None or b is None or abs(b - a) < 0.03:
            continue
        done = {d: (at(s, t + d) - a) / (b - a) for d in (-30, -10, -5, 0, 5, 10, 20)}
        rows.append((t, g, old, new, a, b, done))
    if not rows:
        print("no game ends with a 3c+ move yet")
        return
    for d in (-30, -10, -5, 0, 5, 10, 20):
        xs = sorted(r[6][d] for r in rows)
        print(f"  share of the price move already done {d:+d} s from the feed's update: median {xs[len(xs) // 2]:.2f}, a quarter of cases under {xs[len(xs) // 4]:.2f}")
    print(f"  ({len(rows)} game ends where the match price moved 3c+ between 90 s before and 60 s after)")
    for t, g, old, new, a, b, done in rows[:12]:
        print(f"   {time.strftime('%H:%M:%S', time.gmtime(t))} {meta[tok_of[g]]['title'][:40]} {old} -> {new}: {a * 100:.0f}c -> {b * 100:.0f}c, done at feed time {done[0]:.2f}")


def scout3():
    """365scores: does it keep finished matches with set lengths and point by point?"""
    for name, url in (
            ("allscores day", "https://webws.365scores.com/web/games/allscores/?appTypeId=5&langId=1&sports=3&startDate=15/11/2026&endDate=15/11/2026&showOdds=false&onlyMajorGames=false"),
            ("results", "https://webws.365scores.com/web/games/results/?appTypeId=5&langId=1&sports=3"),
    ):
        try:
            j = json.loads(raw(url))
            gs = j.get("games") or []
            print(f"{name}: {len(gs)} games; paging {j.get('paging')}; comps {collections.Counter(str(g.get('competitionDisplayName'))[:25] for g in gs).most_common(12)}")
            fin = [g for g in gs if g.get("statusGroup") == 4]
            for g in fin[:2]:
                print("  game:", short({k: g.get(k) for k in ("id", "competitionDisplayName", "startTime", "statusText", "stages", "hasPointByPoint", "winner")}, 1200))
            if fin:
                gid = fin[0]["id"]
                for u in (f"https://webws.365scores.com/web/game/?appTypeId=5&langId=1&gameId={gid}",
                          f"https://webws.365scores.com/web/game/pointByPoint/?appTypeId=5&langId=1&gameId={gid}",
                          f"https://webws.365scores.com/web/game/stats/?appTypeId=5&langId=1&games={gid}"):
                    try:
                        d = json.loads(raw(u))
                        print("  detail", u.split("/web/")[1][:40], "->", keys_tree(d, 4)[:1800])
                        gm = d.get("game") or {}
                        for kk in ("pointByPoint", "playByPlay", "events", "chartEvents"):
                            if gm.get(kk) or d.get(kk):
                                print(f"   {kk}:", short(gm.get(kk) or d.get(kk), 1500))
                    except Exception as e:
                        print("  detail", u.split("/web/")[1][:40], "failed", str(e)[:100])
        except Exception as e:
            print(name, "failed", str(e)[:150])
    # Kalshi: do the set-winner markets close right at the end of the set? compare with the match market's 1-minute candles
    try:
        now = int(time.time())
        r = yesno.kget("/markets", {"series_ticker": "KXATPSETWINNER", "status": "settled", "limit": 1000, "min_close_ts": now - 14 * 86400})
        ms = r.get("markets") or []
        evs = collections.defaultdict(list)
        for m in ms:
            evs[m["event_ticker"]].append(m)
        print("kalshi set-winner events:", len(evs), "sets listed:", collections.Counter(m["ticker"].split("-")[-2] for m in ms))
        for ev, mm in list(evs.items())[:4]:
            mt = ev.replace("KXATPSETWINNER", "KXATPMATCH")
            try:
                mk = yesno.kget("/markets", {"event_ticker": mt}).get("markets") or []
            except Exception:
                mk = []
            print(" ", ev, [(m["ticker"].split("-", 2)[-1], m.get("open_time"), m.get("close_time"), m.get("result")) for m in mm], "| match:", [(m["ticker"].split("-")[-1], m.get("close_time"), m.get("result"), m.get("settlement_ts")) for m in mk])
    except Exception as e:
        print("kalshi set check failed", str(e)[:150])


# ================================================================ history: Kalshi minute prices + 365scores set times
S365_DIR = os.path.join("ten_cache", "s365")
KT_DIR = os.path.join("ten_cache", "kalshi")
DAY = 86400


def rj(path, default=None):
    try:
        with gzip.open(path, "rt") as f:
            return json.load(f)
    except Exception:
        return default


def wj(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with gzip.open(path + ".tmp", "wt") as f:
        json.dump(obj, f, separators=(",", ":"))
    os.replace(path + ".tmp", path)


def s365_day(d0):
    """Finished tennis matches of one UTC day from 365scores: start time and minutes per set."""
    d = time.strftime("%d/%m/%Y", time.gmtime(d0))
    j = json.loads(raw(f"https://webws.365scores.com/web/games/allscores/?appTypeId=5&langId=1&sports=3&startDate={d}&endDate={d}&showOdds=false&onlyMajorGames=false", timeout=30))
    out = []
    for g in j.get("games") or []:
        if g.get("statusGroup") != 4:
            continue
        sets = []
        for x in g.get("stages") or []:
            if str(x.get("name", "")).startswith("Set ") and x.get("homeCompetitorScore", -1) >= 0:
                mm = re.sub(r"\D", "", str(x.get("time") or ""))
                sets.append([int(x["homeCompetitorScore"]), int(x["awayCompetitorScore"]), int(mm) if mm else None])
        h, a = g.get("homeCompetitor") or {}, g.get("awayCompetitor") or {}
        out.append({"id": g["id"], "comp": g.get("competitionDisplayName"), "start": g.get("startTime"), "status": g.get("statusText"),
                    "h": h.get("name"), "a": a.get("name"), "hs": h.get("score"), "as": a.get("score"), "sets": sets})
    return out


def k_settled(series, t0, t1):
    rows = []
    for path in ("/markets", "/historical/markets"):
        cur = None
        for _ in range(200):
            p = {"series_ticker": series, "min_close_ts": int(t0), "max_close_ts": int(t1), "limit": 1000}
            if path == "/markets":
                p["status"] = "settled"
            if cur:
                p["cursor"] = cur
            try:
                r = yesno.kget(path, p)
            except Exception as e:
                print(f"  list {series} {path}: {str(e)[:90]}", flush=True)
                break
            got = r.get("markets") or []
            rows += got
            cur = r.get("cursor")
            if not cur or not got:
                break
    seen, out = set(), []
    for m in rows:
        if m["ticker"] in seen or str(m.get("result")) not in ("yes", "no"):
            continue
        seen.add(m["ticker"])
        out.append({"t": m["ticker"], "ev": m["event_ticker"], "name": m.get("yes_sub_title"), "title": m.get("title"), "rules": str(m.get("rules_primary") or "")[:260],
                    "open": m.get("open_time"), "close": m.get("close_time"), "exp": m.get("expected_expiration_time"), "res": m.get("result"),
                    "vol": bot.fnum(m.get("volume_fp") or m.get("volume"), 0)})
    return out


def k_minutes(series, tk, a, b):
    """[[minute end, bid, ask, contracts]] in cents, from 1-minute candles."""
    out = []
    for path in (f"/series/{series}/markets/{tk}/candlesticks", f"/historical/markets/{tk}/candlesticks"):
        try:
            x = a
            while x < b:
                r = yesno.kget(path, {"start_ts": int(x), "end_ts": int(min(b, x + 4000 * 60)), "period_interval": 1})
                for c in r.get("candlesticks") or []:
                    def px(blk, key="close_dollars"):
                        v = (c.get(blk) or {}).get(key)
                        return None if v in (None, "") else round(float(v) * 100, 1)
                    out.append([int(c.get("end_period_ts") or 0), px("yes_bid"), px("yes_ask"), round(bot.fnum(c.get("volume_fp"), 0)),
                                px("yes_bid", "low_dollars"), px("yes_ask", "high_dollars")])
                x += 4000 * 60
        except Exception:
            out = []
            continue
        if out:
            break
    return out


def fetch(days=45):
    """probe `ten_fetch_<days>`: 365scores set times + Kalshi minute prices of every settled tennis match. Resumable."""
    from concurrent.futures import ThreadPoolExecutor
    T0 = time.time()
    today = int(time.time()) // DAY * DAY
    n365 = 0
    for d0 in range(today - days * DAY, today, DAY):
        path = os.path.join(S365_DIR, time.strftime("%Y%m%d", time.gmtime(d0)) + ".json.gz")
        if os.path.exists(path):
            continue
        try:
            got = s365_day(d0)
        except Exception as e:
            print("  365 day failed", time.strftime("%Y-%m-%d", time.gmtime(d0)), str(e)[:100], flush=True)
            time.sleep(3)
            continue
        if got or d0 < today - 2 * DAY:
            wj(path, got)
        n365 += len(got)
        time.sleep(0.7)
    print(f"365scores: {n365} new finished matches, {len(os.listdir(S365_DIR)) if os.path.isdir(S365_DIR) else 0} day files ({time.time() - T0:.0f} s)", flush=True)
    for sr in K_SERIES:
        mpath = os.path.join(KT_DIR, f"markets_{sr}.json.gz")
        have = {m["t"]: m for m in rj(mpath, [])}
        new = k_settled(sr, today - days * DAY, today + DAY)
        for m in new:
            have.setdefault(m["t"], m)
        wj(mpath, list(have.values()))
        evs = collections.defaultdict(list)
        for m in have.values():
            evs[m["ev"]].append(m)
        print(f"{sr}: {len(have)} settled markets, {len(evs)} matches; closes {min((m['close'] for m in have.values()), default='')[:10]} .. {max((m['close'] for m in have.values()), default='')[:10]}", flush=True)
        todo = []
        for ev, mm in sorted(evs.items()):
            m = sorted(mm, key=lambda m: m["t"])[0]
            todo.append(m)
        n_sh = (len(todo) + 199) // 200
        for i in range(n_sh):
            tp = os.path.join(KT_DIR, f"min_{sr}_{i:03d}.json.gz")
            old = rj(tp, {})
            chunk = [m for m in todo[i * 200:(i + 1) * 200] if m["t"] not in old]
            if not chunk:
                continue
            if time.time() - T0 > 250 * 60:
                print("  out of time, run again to continue", flush=True)
                return

            def one(m):
                c = bot.parse_iso(m["close"]).timestamp()
                return m["t"], k_minutes(sr, m["t"], c - 8 * 3600, c + 60)
            with ThreadPoolExecutor(6) as ex:
                for tk, rows in ex.map(one, chunk):
                    old[tk] = rows
            wj(tp, old)
            print(f"  {sr} minutes file {i + 1}/{n_sh}: {sum(1 for v in old.values() if v)}/{len(old)} with prices ({(time.time() - T0) / 60:.0f} min)", flush=True)

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "scout"
    if cmd == "scout":
        scout()
    elif cmd == "scout2":
        scout2()
    elif cmd == "scout3":
        scout3()
    elif cmd == "live":
        live(float(sys.argv[2]) if len(sys.argv) > 2 else 60)
    elif cmd == "livereport":
        import glob
        live_report(sorted(glob.glob(os.path.join(LIVE_DIR, "*.jsonl.gz"))))
    elif cmd == "fetch":
        fetch(int(sys.argv[2]) if len(sys.argv) > 2 else 45)
    elif cmd == "selftest":
        model_selftest()
    else:
        print(__doc__)

