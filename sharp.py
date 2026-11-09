#!/usr/bin/env python3
"""Sharp-bookmaker fair price: buy on Polymarket when a game outcome is cheaper than Pinnacle's odds say it is worth.

PAPER ONLY. Reads public data, never trades.

Pinnacle is the bookmaker the pros bet with: it takes big bets, so its odds move to where the money says. Its odds
include its margin (all outcomes add up to a bit over 100 per 100), so we remove that first ("de-vig"). Two ways of
removing it give slightly different answers; we always use the one that is LESS favorable to the side we buy.

Odds come from Pinnacle's own public website feed (guest.api.arcadia.pinnacle.com, the same JSON its site shows,
no key or account). Its official API closed to the public in July 2025.

    python3 sharp.py scan     # live: match today's Polymarket games to Pinnacle, print the gaps (no trades)
    python3 sharp.py probe*   # raw API shapes (debugging)
    python3 sharp.py selftest # offline checks of the de-vig and the name matching
"""
import csv
import datetime as dt
import difflib
import io
import json
import re
import sys
import unicodedata
import urllib.error
import urllib.request

import bot

G = bot.GAMMA

SOURCES = {
    "football-data (free CSV, Pinnacle closing odds)": "https://www.football-data.co.uk/mmz4281/2627/E0.csv",
    "football-data last season": "https://www.football-data.co.uk/mmz4281/2526/E0.csv",
    "the-odds-api (no key: expect 401)": "https://api.the-odds-api.com/v4/sports/soccer_epl/odds?regions=eu&bookmakers=pinnacle",
    "oddspapi (no key: expect 401)": "https://api.oddspapi.io/v4/sports",
    "pinnacle guest site api": "https://guest.api.arcadia.pinnacle.com/0.1/sports/29/leagues?all=false",
    "pinnodds": "https://pinnodds.com/",
}


def raw(url):
    req = urllib.request.Request(url, headers={"User-Agent": bot.UA})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:300]
    except Exception as e:
        return None, f"{type(e).__name__}: {e}".encode()


def probe():
    print("== odds sources")
    for name, url in SOURCES.items():
        st, body = raw(url)
        print(f"{name}: HTTP {st}, {len(body)} bytes")
        if url.endswith(".csv") and st == 200:
            rows = list(csv.DictReader(io.StringIO(body.decode("utf-8-sig", "replace"))))
            cols = list(rows[0].keys()) if rows else []
            print("  columns:", ",".join(cols))
            for r in rows[-3:]:
                print("  ", {k: r.get(k) for k in ("Date", "Time", "HomeTeam", "AwayTeam", "FTR", "PSH", "PSD", "PSA",
                                                   "PSCH", "PSCD", "PSCA", "AvgCH", "MaxCH", "B365CH")})
        else:
            print("  ", body[:200])
    print("\n== polymarket sports list")
    try:
        sp = bot.http_json(f"{G}/sports")
        for s in sp[:80] if isinstance(sp, list) else []:
            print("  ", {k: s.get(k) for k in ("sport", "series", "tags", "resolution")})
    except Exception as e:
        print("  /sports failed:", e)
    print("\n== a few EPL game events (closed and open)")
    for closed in ("true", "false"):
        try:
            evs = bot.http_json(f"{G}/events", {"tag_slug": "epl", "closed": closed, "limit": 5, "order": "endDate",
                                                "ascending": "false"})
        except Exception as e:
            print("  events failed:", e)
            continue
        for ev in evs[:3]:
            print(f"\n  EVENT {ev.get('slug')} | {ev.get('title')} | start {ev.get('startTime')} end {ev.get('endDate')}"
                  f" | gameId {ev.get('gameId')} | keys {sorted(ev.keys())[:60]}")
            for m in (ev.get("markets") or [])[:4]:
                print("    ", {k: m.get(k) for k in ("question", "slug", "sportsMarketType", "gameStartTime", "outcomes",
                                                    "outcomePrices", "feesEnabled", "feeSchedule", "volumeNum",
                                                    "bestAsk", "bestBid", "closed", "groupItemTitle")})


PIN = "https://guest.api.arcadia.pinnacle.com/0.1"


def pin(path, params=None):
    return bot.http_json(f"{PIN}{path}", params)


def probe2():
    print("== polymarket sport codes")
    sp = bot.http_json(f"{G}/sports")
    print(" ".join(f"{s.get('sport')}:{s.get('series')}" for s in sp))
    want = {s.get("sport"): s.get("series") for s in sp}
    for code in ("epl", "nba", "nfl", "nhl", "atp"):
        ser = want.get(code)
        if not ser:
            continue
        for closed in ("true", "false"):
            try:
                evs = bot.http_json(f"{G}/events", {"series_id": ser, "closed": closed, "limit": 3, "order": "startDate",
                                                    "ascending": "false"})
            except Exception as e:
                print(code, "events failed", e)
                continue
            for ev in evs[:2]:
                print(f"\n  {code} EVENT {ev.get('slug')} | {ev.get('title')} | startTime {ev.get('startTime')} "
                      f"| gameId {ev.get('gameId')} | eventMetadata {ev.get('eventMetadata')}")
                for m in (ev.get("markets") or [])[:5]:
                    print("    ", {k: m.get(k) for k in ("question", "sportsMarketType", "gameStartTime", "outcomes",
                                                        "outcomePrices", "feeSchedule", "volumeNum", "bestAsk",
                                                        "bestBid", "line", "groupItemTitle", "umaResolutionStatus")})
    print("\n== pinnacle guest api")
    for path in ("/leagues/1980/matchups", "/leagues/1980/markets/straight", "/sports/29/markets/straight?primaryOnly=true",
                 "/leagues/487/matchups"):
        st, body = raw(PIN + path)
        print(path, "HTTP", st, len(body), "bytes")
        try:
            js = json.loads(body)
        except Exception:
            print("  ", body[:300])
            continue
        rows = js if isinstance(js, list) else [js]
        print("   rows", len(rows))
        for r in rows[:3]:
            print("   ", json.dumps(r)[:900])


def probe3():
    """Raw shapes needed for matching: Pinnacle matchups + moneyline prices; Polymarket game events in the next 2 days."""
    for sid in (29, 4):
        mus = pin(f"/sports/{sid}/matchups")
        mks = pin(f"/sports/{sid}/markets/straight", {"primaryOnly": "true"})
        print(f"\n== pinnacle sport {sid}: {len(mus)} matchups, {len(mks)} markets; types",
              sorted({(m.get('type'), m.get('key')) for m in mks})[:12])
        reg = [m for m in mus if m.get("type") == "matchup" and not m.get("isLive")][:2]
        for m in reg:
            print("  MATCHUP", json.dumps({k: m.get(k) for k in ("id", "type", "startTime", "isLive", "parentId", "units",
                                                               "participants", "status")})[:700],
                  "| league", (m.get("league") or {}).get("name"))
            for mk in mks:
                if mk.get("matchupId") == m.get("id") and mk.get("type") == "moneyline":
                    print("    ML", json.dumps(mk)[:500])
    now = bot.now()
    import datetime as dt
    evs = bot.gamma_events({"tag_id": 100639, "closed": "false", "end_date_min": bot.iso(now),
                            "end_date_max": bot.iso(now + dt.timedelta(days=2))}, max_pages=3)
    print(f"\n== polymarket game events ending within 2 days: {len(evs)}")
    soc = [e for e in evs if any("win on" in str(m.get("question", "")) for m in e.get("markets") or [])][:2]
    for e in evs[:2] + soc:
        print(f"  EVENT {e.get('slug')} | {e.get('title')} | startTime {e.get('startTime')} | series "
              f"{[s.get('slug') for s in e.get('series') or []]} | tags {[t.get('slug') for t in e.get('tags') or []][:6]}")
        for m in (e.get("markets") or []):
            if m.get("sportsMarketType") == "moneyline":
                print("    ", {k: m.get(k) for k in ("question", "outcomes", "outcomePrices", "bestAsk", "bestBid",
                                                    "gameStartTime", "groupItemTitle", "liquidityNum", "feeSchedule")})


# ================================================================ core: odds, de-vig, matching

PIN_SPORTS = {29: "soccer", 4: "basketball", 19: "hockey", 15: "football", 3: "baseball", 33: "tennis", 22: "mma",
              12: "esports"}


def american_to_prob(a):
    """Pinnacle's American odds -> implied chance (still includes the margin). -150 -> 0.6, +200 -> 0.333."""
    a = float(a)
    return (-a) / (-a + 100) if a < 0 else 100 / (a + 100)


def devig(qs):
    """Implied chances (summing to a bit over 1) -> two fair estimates per outcome: (multiplicative, power).
    Multiplicative scales every outcome down by the same factor. Power raises each to the k that makes them sum to 1,
    which takes more margin off longshots (bookies pad longshots more). Returns [(mult, power), ...]."""
    tot = sum(qs)
    mult = [q / tot for q in qs]
    lo, hi = 1.0, 3.0
    for _ in range(60):
        k = (lo + hi) / 2
        if sum(q ** k for q in qs) > 1:
            lo = k
        else:
            hi = k
    k = (lo + hi) / 2 if tot > 1 else 1.0
    pw = [q ** k for q in qs]
    z = sum(pw)
    return [(m, p / z) for m, p in zip(mult, pw)]


STOP = {"fc", "cf", "afc", "sc", "cd", "sd", "ud", "ac", "as", "ss", "us", "club", "de", "la", "the", "fk", "sk", "bk",
        "if", "cp", "rc", "rcd", "sv", "vfl", "vfb", "tsg", "calcio", "cfc", "bc", "ca", "se", "ec", "and", "vs", "v"}
ALIAS = {"utd": "united", "st": "saint", "man": "manchester", "intl": "international", "nottm": "nottingham",
         "wolves": "wolverhampton"}


def norm_name(x):
    x = unicodedata.normalize("NFKD", str(x)).encode("ascii", "ignore").decode().lower()
    x = re.sub(r"\(.*?\)", " ", x)
    toks = [ALIAS.get(t, t) for t in re.findall(r"[a-z0-9]+", x)]
    return [t for t in toks if t not in STOP] or toks


def name_score(a, b):
    """0..1: how sure we are that two team/player names are the same side."""
    ta, tb = norm_name(a), norm_name(b)
    if not ta or not tb:
        return 0.0
    sa, sb = set(ta), set(tb)
    contain = len(sa & sb) / min(len(sa), len(sb))
    ratio = difflib.SequenceMatcher(None, " ".join(ta), " ".join(tb)).ratio()
    return max(contain, ratio)


def pinnacle_board(sports=None):
    """Pre-game full-game moneylines from Pinnacle: [{id, sport, league, start, names {home, away}, prob {home, away,
    draw?}, limit, version}]. Live (in-play) games and specials are left out."""
    out = []
    for sid in sports or PIN_SPORTS:
        try:
            mus = pin(f"/sports/{sid}/matchups")
            mks = pin(f"/sports/{sid}/markets/straight", {"primaryOnly": "true"})
        except Exception as e:
            print(f"pinnacle sport {sid} failed: {e}")
            continue
        ml = {}
        for mk in mks:
            if mk.get("type") == "moneyline" and mk.get("key") == "s;0;m" and mk.get("status") == "open" \
                    and not mk.get("isAlternate"):
                ml[mk.get("matchupId")] = mk
        for m in mus:
            mk = ml.get(m.get("id"))
            if not mk or m.get("type") != "matchup" or m.get("isLive") or m.get("parentId") \
                    or str(m.get("units") or "Regular") != "Regular":
                continue
            names = {p.get("alignment"): p.get("name") for p in m.get("participants") or []}
            prices = {p.get("designation"): p.get("price") for p in mk.get("prices") or []}
            if not names.get("home") or not names.get("away") or prices.get("home") is None or prices.get("away") is None:
                continue
            keys = ["home", "away"] + (["draw"] if prices.get("draw") is not None else [])
            fair = devig([american_to_prob(prices[k]) for k in keys])
            lim = max([bot.fnum(x.get("amount")) for x in mk.get("limits") or []] or [0])
            out.append({"id": m.get("id"), "sport": PIN_SPORTS[sid], "league": (m.get("league") or {}).get("name"),
                        "start": bot.parse_iso(m.get("startTime")), "names": names,
                        "prob": dict(zip(keys, fair)), "limit": lim, "version": mk.get("version"),
                        "overround": round(sum(american_to_prob(prices[k]) for k in keys) - 1, 4)})
    return out


def poly_games(hours=36):
    """Open Polymarket game events starting within `hours`, with their full-game winner markets."""
    t0 = bot.now()
    evs = bot.gamma_events({"tag_id": 100639, "closed": "false", "end_date_min": bot.iso(t0),
                            "end_date_max": bot.iso(t0 + dt.timedelta(hours=hours + 24))}, max_pages=15)
    out = []
    for e in evs:
        mls = [m for m in e.get("markets") or [] if m.get("sportsMarketType") == "moneyline" and not m.get("closed")
               and m.get("acceptingOrders") is not False and len(bot.market_tokens(m)) == 2]
        if not mls:
            continue
        start = bot.parse_iso(str(mls[0].get("gameStartTime") or e.get("startTime") or "").replace(" ", "T")
                              .replace("+00", "Z").replace("ZZ", "Z"))
        if not start or not (t0 < start < t0 + dt.timedelta(hours=hours)):
            continue
        out.append({"event": e, "start": start, "markets": mls})
    return out


def side_names(g):
    """Polymarket game -> the outcomes we can buy, each tied to a side name or 'draw':
    [(market, outcome index, side name, is_yes_no)]. Two-team markets ('Rangers' vs 'Oilers') give both outcomes.
    Soccer gives one Yes/No market per team plus a draw market."""
    out = []
    for m in g["markets"]:
        outs = [str(o) for o in bot.jlist(m.get("outcomes"))]
        if [o.lower() for o in outs] == ["yes", "no"]:
            git = str(m.get("groupItemTitle") or "")
            q = str(m.get("question") or "")
            if git.lower().startswith("draw") or "end in a draw" in q.lower():
                out.append((m, None, "draw", True))
            else:
                nm = git or re.sub(r"^will (.*?) win.*$", r"\1", q, flags=re.I)
                out.append((m, None, nm, True))
        elif len(outs) == 2:
            out.append((m, 0, outs[0], False))
            out.append((m, 1, outs[1], False))
    return out


def match_game(g, board, max_gap_min=75, min_score=0.6):
    """The Pinnacle matchup for a Polymarket game, and side -> Pinnacle key ('home'/'away'/'draw'), or (None, None).
    Needs the start times within max_gap_min and BOTH team names to match clearly (best beats runner-up)."""
    sides = side_names(g)
    teams = sorted({nm for _, _, nm, _ in sides if nm != "draw"})
    has_draw = any(nm == "draw" for _, _, nm, _ in sides)
    if len(teams) != 2:
        return None, None
    best, second = None, 0.0
    for b in board:
        if abs((b["start"] - g["start"]).total_seconds()) > max_gap_min * 60 or ("draw" in b["prob"]) != has_draw:
            continue
        s1 = min(name_score(teams[0], b["names"]["home"]), name_score(teams[1], b["names"]["away"]))
        s2 = min(name_score(teams[0], b["names"]["away"]), name_score(teams[1], b["names"]["home"]))
        sc, amap = (s1, {teams[0]: "home", teams[1]: "away"}) if s1 >= s2 else (s2, {teams[0]: "away", teams[1]: "home"})
        if best is None or sc > best[0]:
            second = best[0] if best else second
            best = (sc, b, amap)
        elif sc > second:
            second = sc
    if not best or best[0] < min_score or best[0] - second < 0.15:
        return None, None
    amap = best[2]
    amap["draw"] = "draw"
    return best[1], amap


def fair_for(b, key, yes):
    """Conservative fair chance of what we'd buy: the lower of the two de-vig estimates.
    yes=True: the outcome happens. yes=False (a 'No' share): it doesn't."""
    m, p = b["prob"][key]
    return min(m, p) if yes else 1 - max(m, p)


def offers(g, b, amap):
    """Every buyable side of a matched game with its listed ask and conservative fair chance:
    [(market, token index, label, ask, fair)]. Asks are from Gamma's bestAsk/bestBid; the bot re-prices on the book."""
    out = []
    for m, idx, nm, yn in side_names(g):
        key = amap.get(nm)
        if key is None:
            continue
        ask, bid = bot.fnum(m.get("bestAsk"), None), bot.fnum(m.get("bestBid"), None)
        outs = [str(o) for o in bot.jlist(m.get("outcomes"))]
        if yn:
            label = "draw" if key == "draw" else nm
            out.append((m, 0, f"{label}: Yes", ask, fair_for(b, key, True)))
            out.append((m, 1, f"{label}: No", (1 - bid) if bid else None, fair_for(b, key, False)))
        else:
            a = ask if idx == 0 else ((1 - bid) if bid else None)
            out.append((m, idx, outs[idx], a, fair_for(b, key, True)))
    return [o for o in out if o[3] and 0 < o[3] < 1]


def sharp_candidates(names):
    """For bot.run_fast: {track name: [candidate, ...]} sorted by edge. The bot then re-prices every candidate on
    the real order book (5 shares) and only buys if the edge survives the real ask and the fee."""
    rs = {n: bot.rules_for(n) for n in names}
    hours = max(r.get("max_hours_to_start", 24) for r in rs.values())
    board = pinnacle_board([s for s, nm in PIN_SPORTS.items() if any(nm in r.get("sports", list(PIN_SPORTS.values()))
                                                                     for r in rs.values())])
    games = poly_games(hours)
    print(f"sharp: {len(board)} Pinnacle games, {len(games)} Polymarket games in the next {hours}h")
    out = {n: [] for n in names}
    matched = 0
    for g in games:
        b, amap = match_game(g, board)
        if not b:
            continue
        matched += 1
        mins = (g["start"] - bot.now()).total_seconds() / 60
        for n, r in rs.items():
            if b["sport"] not in r.get("sports", [b["sport"]]) or b["limit"] < r.get("min_pinnacle_limit", 0) \
                    or mins < r.get("min_minutes_to_start", 10) or mins > r.get("max_hours_to_start", 24) * 60:
                continue
            for m, i, label, ask, fair in offers(g, b, amap):
                if not (r["min_price"] <= ask <= r["max_price"]):
                    continue
                edge = fair - ask - bot.fee_rate(m) * ask * (1 - ask)
                if edge < r["min_model_edge"] or edge > r.get("max_model_edge", 1):
                    continue
                mm = {**m, "events": [{"id": g["event"].get("id"), "slug": g["event"].get("slug")}]}
                c = bot.candidate(mm, i, max(mins / 1440, 0.01), bot.fnum(bot.pick(m, "liquidityNum", "liquidity")),
                                  {"model_p": round(fair, 4), "model_edge": round(edge, 4),
                                   "signal": f"Pinnacle {b['league']} fair {fair * 100:.1f} (limit {b['limit']:.0f})"})
                c["outcome"] = label
                c["theme"] = b["sport"]
                out[n].append(c)
    print(f"sharp: matched {matched} of {len(games)} Polymarket games to Pinnacle")
    for n in out:
        out[n].sort(key=lambda c: -c["model_edge"])
    return out


def scan():
    """Live look, no trades: how close Polymarket's listed asks sit to Pinnacle's fair price."""
    board = pinnacle_board()
    games = poly_games(36)
    print(f"Pinnacle pre-game moneylines: {len(board)} | Polymarket games starting within 36h: {len(games)}")
    by_sport, rows, unmatched = {}, [], []
    for g in games:
        b, amap = match_game(g, board)
        if not b:
            unmatched.append(g["event"].get("title"))
            continue
        by_sport[b["sport"]] = by_sport.get(b["sport"], 0) + 1
        for m, i, label, ask, fair in offers(g, b, amap):
            fee = bot.fee_rate(m) * ask * (1 - ask)
            rows.append({"sport": b["sport"], "league": b["league"], "title": g["event"].get("title"), "side": label,
                         "ask": ask, "fair": fair, "edge": fair - ask - fee, "limit": b["limit"],
                         "liq": bot.fnum(bot.pick(m, "liquidityNum", "liquidity")), "over": b["overround"],
                         "pin": f"{b['names']['home']} v {b['names']['away']}",
                         "hrs": (g["start"] - bot.now()).total_seconds() / 3600})
    print(f"matched games by sport: {by_sport}; unmatched {len(unmatched)}, e.g. {unmatched[:12]}")
    if not rows:
        return
    import statistics as stx
    print(f"\nbuyable sides: {len(rows)}. Listed ask minus fair price (positive = Polymarket dearer):")
    for sp in sorted({r['sport'] for r in rows}):
        rr = [r for r in rows if r["sport"] == sp]
        gaps = [r["ask"] - r["fair"] for r in rr]
        print(f"  {sp:10s} n={len(rr):4d} median {stx.median(gaps) * 100:+.1f}c, "
              f"edge>=1c: {sum(r['edge'] >= 0.01 for r in rr)}, >=3c: {sum(r['edge'] >= 0.03 for r in rr)}, "
              f">=5c: {sum(r['edge'] >= 0.05 for r in rr)}")
    print("\nPinnacle limit (max bet $) on matched games:", sorted(stx.quantiles([r["limit"] for r in rows], n=4)))
    print("\nbest 40 sides by edge after the fee (listed ask; real fills come from the book):")
    for r in sorted(rows, key=lambda r: -r["edge"])[:40]:
        print(f"  {r['edge'] * 100:+5.1f}c  ask {r['ask'] * 100:5.1f} fair {r['fair'] * 100:5.1f} | {r['sport']}/{r['league']} "
              f"| {r['title'][:45]} -> {r['side'][:28]} | pin {r['pin'][:40]} lim {r['limit']:.0f} liq {r['liq']:.0f} "
              f"in {r['hrs']:.1f}h")


def selftest():
    f = devig([american_to_prob(-150), american_to_prob(130)])
    assert abs(sum(x[0] for x in f) - 1) < 1e-9 and abs(sum(x[1] for x in f) - 1) < 1e-6, f
    assert f[1][1] < f[1][0], "power de-vig should trim the longshot more"
    assert abs(american_to_prob(-150) - 0.6) < 1e-9 and abs(american_to_prob(200) - 1 / 3) < 1e-9
    assert name_score("Oilers", "Edmonton Oilers") == 1.0
    assert name_score("Deportivo Alavés", "Deportivo Alaves") > 0.9
    assert name_score("Man United", "Manchester United") == 1.0
    assert name_score("Arsenal", "Chelsea") < 0.5
    t = bot.now() + dt.timedelta(hours=5)
    board = [{"id": 1, "sport": "hockey", "league": "NHL", "start": t, "names": {"home": "Edmonton Oilers",
              "away": "New York Rangers"}, "prob": {"home": (0.6, 0.6), "away": (0.4, 0.4)}, "limit": 1000,
              "overround": 0.02},
             {"id": 2, "sport": "hockey", "league": "NHL", "start": t, "names": {"home": "Vancouver Canucks",
              "away": "Philadelphia Flyers"}, "prob": {"home": (0.45, 0.45), "away": (0.55, 0.55)}, "limit": 1000,
              "overround": 0.02}]
    g = {"start": t, "event": {"id": "e", "slug": "nhl-nyr-edm", "title": "Rangers vs. Oilers"},
         "markets": [{"question": "Rangers vs. Oilers", "outcomes": '["Rangers", "Oilers"]', "bestAsk": 0.35,
                      "bestBid": 0.34, "clobTokenIds": '["1", "2"]', "outcomePrices": '["0.345", "0.655"]'}]}
    b, amap = match_game(g, board)
    assert b and b["id"] == 1 and amap["Rangers"] == "away", (b, amap)
    o = offers(g, b, amap)
    assert [(x[2], round(x[3], 2), x[4]) for x in o] == [("Rangers", 0.35, 0.4), ("Oilers", 0.66, 0.6)], o
    sg = {"start": t, "event": {"id": "s", "title": "CD Pamplona vs. SD Eibar"}, "markets": [
        {"question": "Will CD Pamplona win on 2026-10-28?", "groupItemTitle": "CD Pamplona", "outcomes": '["Yes","No"]',
         "bestAsk": 0.2, "bestBid": 0.1, "clobTokenIds": '["a","b"]'},
        {"question": "Will CD Pamplona vs. SD Eibar end in a draw?", "groupItemTitle": "Draw (CD Pamplona vs. SD Eibar)",
         "outcomes": '["Yes","No"]', "bestAsk": 0.25, "bestBid": 0.2, "clobTokenIds": '["c","d"]'},
        {"question": "Will SD Eibar win on 2026-10-28?", "groupItemTitle": "SD Eibar", "outcomes": '["Yes","No"]',
         "bestAsk": 0.6, "bestBid": 0.55, "clobTokenIds": '["e","f"]'}]}
    sboard = [{"id": 3, "sport": "soccer", "league": "Spain - Copa del Rey", "start": t + dt.timedelta(minutes=30),
               "names": {"home": "Pamplona", "away": "Eibar"}, "prob": {"home": (0.15, 0.14), "away": (0.6, 0.61),
               "draw": (0.25, 0.25)}, "limit": 500, "overround": 0.03}] + board
    b, amap = match_game(sg, sboard)
    assert b and b["id"] == 3 and amap["CD Pamplona"] == "home" and amap["SD Eibar"] == "away", (b, amap)
    o = {x[2]: (round(x[3], 4), round(x[4], 4)) for x in offers(sg, b, amap)}
    assert o["SD Eibar: Yes"] == (0.6, 0.6) and o["SD Eibar: No"] == (0.45, 0.39) and o["draw: No"][1] == 0.75, o
    print("sharp selftest ok")


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "scan"
    {"probe": probe, "probe2": probe2, "probe3": probe3, "scan": scan, "selftest": selftest}[what]()
