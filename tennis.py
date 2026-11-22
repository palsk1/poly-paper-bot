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


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "scout"
    if cmd == "scout":
        scout()
    else:
        print(__doc__)
