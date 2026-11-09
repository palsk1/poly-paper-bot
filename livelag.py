#!/usr/bin/env python3
"""Live esports lag test (Jan's question, 2026-11-09): "can a fast bot see a CS2 round / LoL fight
and bet before Polymarket's odds move?"

Records only. Never trades, never touches state/.

It listens to two free Polymarket websockets at once and stamps every message with our own clock:
  sports  wss://sports-api.polymarket.com/ws        live scores of every game (no key)
  market  wss://ws-subscriptions-clob.polymarket.com/ws/market   order books + trades (no key)
Esports games are the ones whose status is lowercase (not_started / running / finished).
For every live esports game it subscribes to all markets of that Polymarket event (match winner,
map winners, ...), then for every score change it asks: when did the price move, compared with
the moment Polymarket's own score feed told us? Negative lead = the price moved first (someone has
a faster feed than the free one). It also lists every big price jump (4c+ within 3s) and the
nearest score change, and how long a message takes to reach us (server timestamp vs our clock).

Usage: python3 livelag.py scan            (30s: what's live now + esports games starting soon)
       python3 livelag.py rec [minutes]   (record + report; raw data in livelag_out/ for upload)
       python3 livelag.py selftest        (offline check of the analysis)
"""
import asyncio
import gzip
import json
import os
import sys
import time

import bot
from bot import GAMMA, http_json

SPORTS_WS = "wss://sports-api.polymarket.com/ws"
MARKET_WS = "wss://ws-subscriptions-clob.polymarket.com/ws/market"
OUT_DIR = "livelag_out"
ESPORT_STATUS = {"not_started", "running", "finished", "postponed", "canceled"}
JUMP_C = 0.04      # a "big jump": mid moves this much ...
JUMP_S = 3.0       # ... within this many seconds


def now():
    return time.time()


def jl(x):
    if isinstance(x, list):
        return x
    try:
        return json.loads(x or "[]")
    except Exception:
        return []


def is_esport(msg):
    return str(msg.get("status") or "") in ESPORT_STATUS


def event_markets(ev):
    """All open markets of one Polymarket event: [{tok, outcome, q, type, cid}]."""
    if not ev:
        return None, []
    out = []
    for m in ev.get("markets") or []:
        if m.get("closed"):
            continue
        toks = jl(m.get("clobTokenIds"))
        outs = jl(m.get("outcomes"))
        if not toks or m.get("sportsMarketType") not in ("moneyline", "child_moneyline"):
            continue  # match winner + game/map winners only
        out.append({"tok": str(toks[0]), "outcome": outs[0] if outs else "?", "q": m.get("question"),
                    "type": m.get("sportsMarketType"), "cid": m.get("conditionId")})
    return ev, out


TAGS = ["esports", "counter-strike", "cs2", "dota-2", "league-of-legends", "lol", "valorant"]
_IDX = {"t": 0, "by_gid": {}, "by_team": {}}


def game_index(force=False):
    """Open esports events on Gamma, by gameId (the sports feed has no slug). Refreshed every 10 min."""
    if not force and now() - _IDX["t"] < 600:
        return _IDX
    by_gid, by_team, seen = {}, {}, set()
    for tag in TAGS:
        for off in range(0, 2000, 500):
            try:
                evs = http_json(f"{GAMMA}/events", {"tag_slug": tag, "closed": "false", "limit": 500, "offset": off})
            except Exception as e:
                print(f"  gamma {tag}: {e}")
                break
            evs = evs if isinstance(evs, list) else []
            for ev in evs:
                if ev.get("id") in seen:
                    continue
                seen.add(ev.get("id"))
                gids = {ev.get("gameId")} | {m.get("gameId") for m in ev.get("markets") or []}
                for g in gids:
                    if g:
                        by_gid[str(g)] = ev
                by_team[(ev.get("title") or "").lower()] = ev
            if len(evs) < 500:
                break
    _IDX.update(t=now(), by_gid=by_gid, by_team=by_team)
    print(f"  gamma: {len(seen)} open esports events, {len(by_gid)} with a gameId")
    return _IDX


def find_event(msg):
    idx = game_index()
    ev = idx["by_gid"].get(str(msg.get("gameId")))
    if ev:
        return ev
    h, a = (msg.get("homeTeam") or "").lower(), (msg.get("awayTeam") or "").lower()
    if h and a:
        for title, ev in idx["by_team"].items():
            if h in title and a in title:
                return ev
    return None


class Rec:
    def __init__(self, path=None):
        os.makedirs(OUT_DIR, exist_ok=True)
        self.f = gzip.open(path or os.path.join(OUT_DIR, f"lag_{int(now())}.jsonl.gz"), "wt")
        self.games = {}       # gameId -> last sports msg
        self.changes = []     # (t, gameId, old, new)
        self.slug_of = {}     # gameId -> slug
        self.mkts = {}        # token -> market info (+ game)
        self.mids = {}        # token -> [(t, mid, bid, ask)]
        self.trades = {}      # token -> [(t, price, size, side)]
        self.lag_ms = []      # our receive time - server timestamp, market ws
        self.want = asyncio.Queue()
        self.n = {"sports": 0, "market": 0}

    def put(self, kind, obj):
        self.f.write(json.dumps({"k": kind, "t": round(now(), 3), **obj}, separators=(",", ":")) + "\n")

    # ---------- sports ----------
    def on_sport(self, msg):
        if not isinstance(msg, dict) or not is_esport(msg):
            return
        self.n["sports"] += 1
        t = now()
        gid = msg.get("gameId")
        self.put("sport", {"m": msg})
        old = self.games.get(gid)
        key = (msg.get("score"), msg.get("period"), msg.get("status"))
        if old is not None:
            okey = (old.get("score"), old.get("period"), old.get("status"))
            if okey != key:
                self.changes.append((t, gid, okey, key))
        self.games[gid] = msg
        if msg.get("live") and gid not in self.slug_of:
            self.slug_of[gid] = msg.get("slug") or f"{msg.get('leagueAbbreviation')}: {msg.get('homeTeam')} vs {msg.get('awayTeam')}"
            self.want.put_nowait(msg)

    # ---------- market ----------
    def mid_point(self, tok, bid, ask, t):
        if bid is None or ask is None:
            return
        try:
            bid, ask = float(bid), float(ask)
        except Exception:
            return
        if not (0 < bid < ask < 1) or ask - bid > 0.2:
            return
        s = self.mids.setdefault(tok, [])
        mid = round((bid + ask) / 2, 4)
        if not s or s[-1][1] != mid:
            s.append((t, mid, bid, ask))

    def on_market(self, msg):
        msgs = msg if isinstance(msg, list) else [msg]
        t = now()
        for m in msgs:
            if not isinstance(m, dict):
                continue
            self.n["market"] += 1
            et = m.get("event_type") or m.get("type")
            ts = m.get("timestamp")
            try:
                if ts:
                    self.lag_ms.append(t * 1000 - float(ts))
            except Exception:
                pass
            if et == "book":
                tok = str(m.get("asset_id"))
                bids = m.get("bids") or []
                asks = m.get("asks") or []
                bb = max((float(x["price"]) for x in bids), default=None)
                ba = min((float(x["price"]) for x in asks), default=None)
                self.put("book", {"tok": tok, "bb": bb, "ba": ba, "ts": ts,
                                  "b": [[x["price"], x["size"]] for x in sorted(bids, key=lambda x: -float(x["price"]))[:5]],
                                  "a": [[x["price"], x["size"]] for x in sorted(asks, key=lambda x: float(x["price"]))[:5]]})
                if tok in self.mkts:
                    self.mid_point(tok, bb, ba, t)
            elif et == "price_change":
                for pc in m.get("price_changes") or m.get("changes") or []:
                    tok = str(pc.get("asset_id") or m.get("asset_id"))
                    if tok not in self.mkts:
                        continue
                    self.put("pc", {"tok": tok, "p": pc.get("price"), "s": pc.get("size"), "sd": pc.get("side"),
                                    "bb": pc.get("best_bid"), "ba": pc.get("best_ask"), "ts": ts})
                    self.mid_point(tok, pc.get("best_bid"), pc.get("best_ask"), t)
            elif et == "best_bid_ask":
                tok = str(m.get("asset_id"))
                if tok in self.mkts:
                    self.put("bba", {"tok": tok, "bb": m.get("best_bid"), "ba": m.get("best_ask"), "ts": ts})
                    self.mid_point(tok, m.get("best_bid"), m.get("best_ask"), t)
            elif et == "last_trade_price":
                tok = str(m.get("asset_id"))
                self.put("trade", {"tok": tok, "p": m.get("price"), "s": m.get("size"), "sd": m.get("side"), "ts": ts})
                try:
                    self.trades.setdefault(tok, []).append((t, float(m.get("price")), float(m.get("size") or 0), m.get("side")))
                except Exception:
                    pass

    def close(self):
        self.f.close()


async def sports_loop(rec, until):
    import websockets
    while now() < until:
        try:
            async with websockets.connect(SPORTS_WS, ping_interval=None, max_size=None, open_timeout=20) as ws:
                while now() < until:
                    try:
                        raw = await asyncio.wait_for(ws.recv(), timeout=15)
                    except asyncio.TimeoutError:
                        continue
                    if raw == "ping":
                        await ws.send("pong")
                        continue
                    try:
                        msg = json.loads(raw)
                    except Exception:
                        continue
                    for x in (msg if isinstance(msg, list) else [msg]):
                        rec.on_sport(x)
        except Exception as e:
            rec.put("err", {"where": "sports", "e": str(e)[:200]})
            print(f"  sports ws error: {e}; reconnecting")
            await asyncio.sleep(3)


async def market_loop(rec, until):
    import websockets
    subscribed = set()
    while now() < until:
        try:
            async with websockets.connect(MARKET_WS, ping_interval=None, max_size=None, open_timeout=20) as ws:
                if subscribed:
                    await ws.send(json.dumps({"assets_ids": sorted(subscribed), "type": "market",
                                              "custom_feature_enabled": True}))
                last_ping = now()
                first = not subscribed
                while now() < until:
                    # new games to follow
                    while not rec.want.empty():
                        smsg = rec.want.get_nowait()
                        gid = smsg.get("gameId")
                        slug = rec.slug_of[gid]
                        ev = await asyncio.get_running_loop().run_in_executor(None, find_event, smsg)
                        ev, mk = event_markets(ev)
                        if not mk:
                            print(f"  no Polymarket markets for live game {gid} {slug}")
                            continue
                        toks = []
                        for m in mk:
                            m["game"] = gid
                            m["slug"] = slug
                            rec.mkts[m["tok"]] = m
                            toks.append(m["tok"])
                        rec.put("meta", {"game": gid, "slug": slug, "title": (ev or {}).get("title"), "markets": mk})
                        print(f"  following {slug}: {len(mk)} markets ({(ev or {}).get('title')})")
                        new = [x for x in toks if x not in subscribed]
                        subscribed.update(new)
                        if new:
                            if first:
                                await ws.send(json.dumps({"assets_ids": new, "type": "market",
                                                          "custom_feature_enabled": True}))
                                first = False
                            else:
                                await ws.send(json.dumps({"assets_ids": new, "operation": "subscribe",
                                                          "custom_feature_enabled": True}))
                    if now() - last_ping > 9:
                        await ws.send("PING")
                        last_ping = now()
                    if not subscribed:
                        await asyncio.sleep(1)
                        continue
                    try:
                        raw = await asyncio.wait_for(ws.recv(), timeout=2)
                    except asyncio.TimeoutError:
                        continue
                    if raw in ("PONG", "pong"):
                        continue
                    try:
                        rec.on_market(json.loads(raw))
                    except Exception:
                        continue
        except Exception as e:
            rec.put("err", {"where": "market", "e": str(e)[:200]})
            print(f"  market ws error: {e}; reconnecting")
            await asyncio.sleep(3)


# ---------- analysis ----------

def mid_at(series, t):
    """Last mid at or before t (None if none)."""
    lo, hi, best = 0, len(series) - 1, None
    while lo <= hi:
        k = (lo + hi) // 2
        if series[k][0] <= t:
            best = series[k][1]
            lo = k + 1
        else:
            hi = k - 1
    return best


def big_part(score):
    """'21-11|0-1|Bo3' -> '0-1' (maps won). Plain scores stay as they are."""
    parts = str(score or "").split("|")
    return parts[1] if len(parts) >= 2 else str(score)


def move_time(series, t0, before=60, after=60):
    """When, around t0, did the mid make its move? Returns (time_of_biggest_step, total_move, step)."""
    a, b = mid_at(series, t0 - before), mid_at(series, t0 + after)
    if a is None:  # recording started inside the window: use the first mid we have
        a = next((p[1] for p in series if p[0] <= t0 + after), None)
    if a is None or b is None:
        return None, None, None
    pts = [p for p in series if t0 - before < p[0] <= t0 + after]
    prev, best_t, best_step = a, None, 0.0
    for t, mid, _, _ in pts:
        step = mid - prev
        # the biggest step in the direction of the total move
        if (b - a) * step > 0 and abs(step) > abs(best_step):
            best_t, best_step = t, step
        prev = mid
    return best_t, b - a, best_step


def report(rec, minutes):
    L = [f"# Live esports lag test ({time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}, {minutes} min)", ""]
    L.append(f"Messages: {rec.n['sports']} esports score updates, {rec.n['market']} market updates, "
             f"{len(rec.mkts)} markets on {len({m['game'] for m in rec.mkts.values()})} live games.")
    if rec.lag_ms:
        xs = sorted(rec.lag_ms)
        L.append(f"Delivery lag of the market websocket to us (our clock - Polymarket's timestamp): "
                 f"median {xs[len(xs)//2]:.0f} ms, 90th pct {xs[int(len(xs)*0.9)]:.0f} ms (n={len(xs)}).")
    L.append("")
    by_game = {}
    for tok, m in rec.mkts.items():
        by_game.setdefault(m["game"], []).append(tok)
    leads = []
    L.append("## Score changes vs price moves")
    L.append("lead = when the price made its biggest step minus when Polymarket's score feed told us. "
             "Negative = the price moved first.")
    L.append("")
    small = []   # kills / rounds: (lead, move)
    for t, gid, old, new in rec.changes:
        toks = by_game.get(gid) or []
        if not toks:
            continue
        is_big = big_part(old[0]) != big_part(new[0]) or old[1] != new[1] or old[2] != new[2]
        if is_big:
            L.append(f"- {time.strftime('%H:%M:%S', time.gmtime(t))} {rec.slug_of.get(gid, gid)}: "
                     f"{old[0]} {old[1]} -> {new[0]} {new[1]} ({new[2]})")
        for tok in toks:
            s = rec.mids.get(tok) or []
            win = 60 if is_big else 15
            mt, tot, step = move_time(s, t, win, win)
            if mt is None or abs(tot) < (0.02 if is_big else 0.01):
                continue
            m = rec.mkts[tok]
            lead = mt - t
            if not is_big:
                small.append((lead, abs(step)))
                continue
            leads.append(lead)
            path = " ".join(f"{dt:+d}s:{mid_at(s, t + dt) * 100:.1f}" if mid_at(s, t + dt) is not None else f"{dt:+d}s:-"
                            for dt in (-30, -10, -3, 0, 3, 10, 30))
            L.append(f"    {m['q']} [{m['outcome']}]: moved {tot * 100:+.1f}c, biggest step {step * 100:+.1f}c "
                     f"at lead {lead:+.1f}s | mid {path}")
    if leads:
        xs = sorted(leads)
        L.append("")
        L.append(f"Map/game ends: n={len(xs)}, median lead {xs[len(xs)//2]:+.1f}s, price first in {sum(x < 0 for x in xs)}, "
                 f"feed first in {sum(x >= 0 for x in xs)}.")
    if small:
        xs = sorted(x[0] for x in small)
        q = lambda f: xs[min(len(xs) - 1, int(len(xs) * f))]
        L.append("")
        L.append(f"Kills/rounds inside a game (window +-15s, moves of 1c+): n={len(xs)}, lead 10th pct {q(0.1):+.1f}s, "
                 f"median {q(0.5):+.1f}s, 90th pct {q(0.9):+.1f}s; price first in {sum(x < 0 for x in xs)}, "
                 f"feed first in {sum(x >= 0 for x in xs)}. Big ones (3c+ step):")
        bigs = sorted(x[0] for x in small if x[1] >= 0.03)
        if bigs:
            L.append(f"    n={len(bigs)}, median lead {bigs[len(bigs)//2]:+.1f}s, price first in {sum(x < 0 for x in bigs)}")
    # how often does the free score feed update?
    gaps = {}
    for t, gid, old, new in rec.changes:
        gaps.setdefault(gid, []).append(t)
    g = sorted(b - a for ts in gaps.values() for a, b in zip(ts, ts[1:]))
    if g:
        L.append(f"\nScore feed: {len(rec.changes)} changes, median gap between updates {g[len(g)//2]:.0f}s.")
    L.append("")
    L.append(f"## Big jumps ({JUMP_C * 100:.0f}c+ within {JUMP_S:.0f}s) and the nearest score change")
    jumps = []
    for tok, s in rec.mids.items():
        j = 0
        for i in range(len(s)):
            while s[i][0] - s[j][0] > JUMP_S:
                j += 1
            if abs(s[i][1] - s[j][1]) >= JUMP_C:
                jumps.append((s[i][0], tok, s[j][1], s[i][1]))
                j = i  # don't count the same jump twice
    for t, tok, a, b in sorted(jumps):
        m = rec.mkts[tok]
        near = [c for c in rec.changes if c[1] == m["game"]]
        dt = min((c[0] - t for c in near), key=abs, default=None)
        vol = sum(x[2] for x in rec.trades.get(tok, []) if t - 5 <= x[0] <= t + 5)
        L.append(f"- {time.strftime('%H:%M:%S', time.gmtime(t))} {m['q']} [{m['outcome']}] {a * 100:.1f} -> {b * 100:.1f}c, "
                 f"trades +-5s: {vol:.0f} shares, nearest score change "
                 + (f"{dt:+.1f}s after the jump" if dt is not None else "none"))
    L.append(f"\n{len(jumps)} big jumps, {len(rec.changes)} score changes.")
    return "\n".join(L)


async def run(minutes):
    rec = Rec()
    until = now() + minutes * 60
    print(f"recording {minutes} min ...", flush=True)
    await asyncio.gather(sports_loop(rec, until), market_loop(rec, until))
    rec.close()
    txt = report(rec, minutes)
    with open(os.path.join(OUT_DIR, "report.md"), "w") as f:
        f.write(txt + "\n")
    print(txt)


async def scan():
    import websockets
    seen = {}
    t_end = now() + 30
    async with websockets.connect(SPORTS_WS, ping_interval=None, max_size=None, open_timeout=20) as ws:
        while now() < t_end:
            try:
                raw = await asyncio.wait_for(ws.recv(), timeout=5)
            except asyncio.TimeoutError:
                continue
            if raw == "ping":
                await ws.send("pong")
                continue
            try:
                msg = json.loads(raw)
            except Exception:
                continue
            for x in (msg if isinstance(msg, list) else [msg]):
                if isinstance(x, dict):
                    seen.setdefault(x.get("gameId"), []).append((now(), x))
    print(f"sports ws: {len(seen)} games in 30s")
    for gid, xs in seen.items():
        x = xs[-1][1]
        tag = "ESPORT" if is_esport(x) else "sport"
        print(f"  {tag} {x.get('leagueAbbreviation')} {x.get('slug')} | {x.get('status')} live={x.get('live')} "
              f"score={x.get('score')} period={x.get('period')} | {len(xs)} msgs | keys {sorted(x.keys())}")
    game_index(force=True)
    shown = 0
    for gid, xs in seen.items():
        x = xs[-1][1]
        if not is_esport(x):
            continue
        print(f"  {x.get('leagueAbbreviation')} {x.get('homeTeam')} vs {x.get('awayTeam')} | {x.get('score')} | gameId {gid}")
        ev, mk = event_markets(find_event(x))
        print(f"    -> {(ev or {}).get('title')} | {(ev or {}).get('slug')} | {len(mk)} markets")
        for m in mk[:12]:
            print(f"       {m['type']} | {m['q']} | {m['outcome']}")
        if ev and not shown:
            shown = 1
            print(f"       event keys: {sorted(ev.keys())[:80]}")
    # what starts soon (by gameStartTime / startTime) so we know when to record
    soon = []
    for ev in {id(e): e for e in _IDX["by_team"].values()}.values():
        st = ev.get("startTime") or next((m.get("gameStartTime") for m in ev.get("markets") or [] if m.get("gameStartTime")), None)
        if st:
            soon.append((str(st), ev.get("title"), ev.get("volume24hr") or ev.get("volume")))
    soon.sort()
    nowiso = time.strftime("%Y-%m-%dT%H", time.gmtime(now() - 3 * 3600))
    print("  starting soon (UTC):")
    for st, title, vol in [x for x in soon if x[0] >= nowiso][:40]:
        print(f"    {st} | {title} | vol {vol}")


def selftest():
    rec = Rec(path=os.path.join(OUT_DIR, "selftest.jsonl.gz"))
    _IDX["t"] = now()
    rec.mkts["A"] = {"game": 1, "q": "Team X vs Team Y", "outcome": "X", "tok": "A"}
    rec.slug_of[1] = "cs2-x-y"
    base = 1000.0
    rec.mids["A"] = [(base - 50, 0.50, .49, .51), (base - 2, 0.52, .51, .53), (base - 1.5, 0.60, .59, .61),
                     (base + 5, 0.61, .60, .62)]
    rec.changes = [(base, 1, ("1-0", "map 1", "running"), ("2-0", "map 1", "running"))]
    txt = report(rec, 0)
    rec.close()
    assert "lead -1.5s" in txt, txt
    assert "50.0 -> 60.0c" in txt or "52.0 -> 60.0c" in txt, txt
    print(txt)
    print("selftest ok")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "scan"
    if cmd == "scan":
        asyncio.run(scan())
    elif cmd == "rec":
        asyncio.run(run(float(sys.argv[2]) if len(sys.argv) > 2 else 60))
    elif cmd == "selftest":
        selftest()
    else:
        print(__doc__)
