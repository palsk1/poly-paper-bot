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

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "scout"
    if cmd == "scout":
        scout()
    elif cmd == "scout2":
        scout2()
    elif cmd == "selftest":
        model_selftest()
    else:
        print(__doc__)

