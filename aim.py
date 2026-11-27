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
d10 = lambda t: dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m-%d")


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
# usage bets: a lab's share of the week's tokens on OpenRouter, daily shares on Vercel's AI Gateway, app downloads
USE_K = "^KX([A-Z]+SHARE|TOKENUSEM?|TOPUSAGEAI|[A-Z]+VSPEND|[A-Z]+VREQ|OSSPEND|[A-Z]+APP|AIAPPARRAY)$"
APP_K = "^KXAPPRANK(FREE|FREE2|FREE3|FREESECOND|PAID)$"     # daily "#1 free app in the US App Store" (appstore.py)
SPACE_K = "^KX(SPACEXCOUNT|SPACEXSTARSHIP|LAUNCHES|LAUNCHCOUNTM|RKLBCOUNT|OTHERLAUNCH)$"   # rocket launch counts (spacex.py)
PICKS = {"use": USE_K, "arena": ARENA_K, "app": APP_K, "space": SPACE_K}


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
LB_SUBSETS = ("text", "text_style_control", "webdev", "vision", "text_to_image", "search", "text_to_video", "image_to_video", "image_edit", "video_edit", "agent", "document")
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


# ================================================================ Polymarket leaderboard markets -> what they ask
norm = lambda x: re.sub(r"[^a-z0-9]", "", str(x or "").lower())
ORG = {"zai": "zai", "zhipu": "zai", "zhipuai": "zai", "xai": "xai", "moonshot": "moonshot", "moonshotai": "moonshot", "metaai": "meta",
       "alibabacloud": "alibaba", "qwen": "alibaba", "googledeepmind": "google", "deepmind": "google", "bytedanceseed": "bytedance",
       "amazonnova": "amazon", "mistralai": "mistral", "nvidiaai": "nvidia", "microsoftai": "microsoft", "tencenthunyuan": "tencent"}
org = lambda x: ORG.get(norm(x), norm(x))
CHINA = {"alibaba", "moonshot", "baidu", "zai", "xiaomi", "deepseek", "bytedance", "minimax", "meituan", "tencent", "stepfun", "01ai",
         "sensetime", "iflytek", "kuaishou", "shengshu", "baichuan", "zhipu", "manus", "unitree"}
BOARDS = (("text-to-video", "text_to_video", "overall"), ("text to video", "text_to_video", "overall"),
          ("image-to-video", "image_to_video", "overall"), ("image to video", "image_to_video", "overall"),
          ("text-to-image", "text_to_image", "overall"), ("text to image", "text_to_image", "overall"),
          ("image edit", "image_edit", "overall"), ("image-edit", "image_edit", "overall"), ("video edit", "video_edit", "overall"),
          ("webdev", "webdev", "overall"), ("code arena", "webdev", "overall"), ("ai agent", "agent", "overall"), ("agent arena", "agent", "overall"),
          ("search", "search", "overall"), ("vision", "vision", "overall"), ("document", "document", "overall"),
          ("math", "text", "math"), ("coding", "text", "coding"), ("for coding", "text", "coding"))


def parse(m):
    """One Polymarket market -> {sub, cat, pos, unit, who, china} when it asks who stands where on an Arena board at its end time."""
    q, d, title = m["q"], m.get("desc") or "", m.get("title") or ""
    low = (q + " " + title).lower()
    if not re.search(r"arena", d, re.I) or not m.get("item"):
        return None
    if re.search(r"released|debut|reach|first hit|score on|trading competition|will have a #1|have a #1|parlay|before |remain", low):
        return None
    if not re.search(r"(best|top|#\d|second|third)", low) or not re.search(r"end of|on [a-z]+ \d", low):
        return None
    pos = 2 if re.search(r"second|#2|2nd", low) else 3 if re.search(r"third|#3|3rd", low) else 1
    sub, cat = "text", "overall"
    for key, s_, c_ in BOARDS:
        if key in low:
            sub, cat = s_, c_
            break
    if sub == "text" and re.search(r"style control on", low + " " + d[:900].lower()) and not re.search(r"style control off", low):
        sub = "text_style_control"
    lab = bool(re.search(r"\blab\b", low))
    model_unit = not re.search(r"company|lab|companies", low)
    return {"sub": sub, "cat": cat, "pos": pos, "unit": "model" if model_unit else ("lab" if lab else "company"),
            "who": m["item"], "china": "chinese" in low}


_LB = {}


def lb(sub):
    if sub not in _LB:
        _LB[sub] = rj(lb_path(sub), {}) or {}
    return _LB[sub]


def board(sub, cat, day, lag=1):
    """The newest board published at least `lag` days before `day` (YYYY-MM-DD) -> (publish day, rows) or None."""
    days = (lb(sub).get(cat) or {})
    cut = (dt.date.fromisoformat(day) - dt.timedelta(days=lag)).isoformat()
    ok = [x for x in days if x <= cut]
    if not ok:
        return None
    x = max(ok)
    return x, days[x]


def standing(rows, P):
    """Who holds place P['pos'] on these rows, the way the market counts it. Rows are already in rank, score order."""
    rows = [r for r in rows if r[2] is not None]
    rows.sort(key=lambda r: (r[6] if r[6] is not None else 9e9, -r[2]))
    if P["china"]:
        rows = [r for r in rows if org(r[1]) in CHINA]
    if P["unit"] == "model":
        seq = [norm(r[0]) for r in rows]
    elif P["unit"] == "lab" or P["china"]:
        seq = []
        for r in rows:
            if org(r[1]) not in seq:
                seq.append(org(r[1]))
    else:
        seq = [org(r[1]) for r in rows]
    return seq, (seq[P["pos"] - 1] if len(seq) >= P["pos"] else None)


def who_key(P):
    return norm(P["who"]) if P["unit"] == "model" else org(P["who"])


def lb_markets():
    """Finished Polymarket leaderboard markets with what they ask. -> ({id: market + 'P'}, tapes)"""
    import families
    ms, tp = families.load("ai")
    out = {}
    for k, m in ms.items():
        P = parse(m)
        if P and lb(P["sub"]).get(P["cat"]):
            m["P"] = P
            out[k] = m
    return out, tp


def check():
    """Does the board the day before the end already name the winner? Also shows how often our reading of the rules is right."""
    ms, tp = lb_markets()
    print(len(ms), "leaderboard markets,", len({m["ev_slug"] for m in ms.values()}), "events,", sum(1 for k in ms if k in tp), "with real trades")
    by = collections.defaultdict(lambda: [0, 0, 0, 0])
    bad = []
    for k, m in ms.items():
        P = m["P"]
        end_day = d10(m["end"])
        for lag, col in ((0, 0), (7, 2)):
            b = board(P["sub"], P["cat"], end_day, lag)
            if not b:
                continue
            seq, holder = standing(list(b[1]), P)
            pred = holder == who_key(P)
            won = m["final"][0] == 1.0
            key = (P["sub"], P["cat"], P["pos"], P["unit"], P["china"])
            by[key][col] += pred == won
            by[key][col + 1] += 1
            if lag == 0 and pred != won and len(bad) < 40:
                bad.append((m["ev_slug"][:60], P["who"], "we say", holder, "won" if won else "lost", b[0], seq[:4]))
    print("| board | part | place | unit | Chinese only | board on the end day says the result | board a week before |")
    for key, v in sorted(by.items(), key=lambda kv: -kv[1][1]):
        print("|", " | ".join(str(x) for x in key), f"| {v[0]} of {v[1]} | {v[2]} of {v[3]} |")
    for x in bad:
        print("  MISS", x)
    return ms, tp


LAG = 3                       # a board dated D is only used from day D+3 on: the date on a board can be 1-2 days before it went public
FIRST_END = "2025-07-01"      # before this the dataset's old boards do not reproduce the results (style control default changed May 2025)


def place_of(rows, P):
    """(place of the market's own name now or None, score gap: its best score minus the best score of the name that holds / chases the place)."""
    seq, holder = standing(list(rows), P)
    me = who_key(P)
    best = {}
    for r in rows:
        if r[2] is None or (P["china"] and org(r[1]) not in CHINA):
            continue
        k = norm(r[0]) if P["unit"] == "model" else org(r[1])
        best[k] = max(best.get(k, -9e9), r[2])
    place = seq.index(me) + 1 if me in seq else None
    if P["unit"] == "company" and not P["china"]:      # literal model order: a company can hold several places
        place = P["pos"] if holder == me else place
    mine = best.get(me)
    gap = None
    if mine is not None and holder is not None:
        if holder == me:
            rest = sorted((v for k, v in best.items() if k != me), reverse=True)
            gap = mine - rest[0] if rest else None
        else:
            gap = mine - best.get(holder, mine)
    return place, holder, gap


def looks_lb(ms, tp, step=6 * 3600, fresh=12 * 3600, lag=LAG):
    """Every leaderboard market every 6 hours: dict rows with the last real price and where its name stands on the newest board
    published on an earlier day."""
    import stocks
    R = []
    for k, m in ms.items():
        b = (tp.get(k) or {}).get("b")
        if not b or not m.get("start") or d10(m["end"]) < FIRST_END:
            continue
        P = m["P"]
        t = max(m["start"], b[0][0]) + 3600
        t -= t % step
        last_day, st = None, None
        while t < m["end"] - 1800:
            pp = stocks._price(b, t, fresh=fresh)
            if pp is not None:
                day = d10(t)
                if day != last_day:
                    bd = board(P["sub"], P["cat"], day, lag)
                    st = (place_of(bd[1], P) + (bd[0],)) if bd else None
                    last_day = day
                if st:
                    R.append({"k": k, "t": t, "h": (m["end"] - t) / 3600, "pp": pp, "place": st[0], "holds": st[1] == who_key(P),
                              "gap": st[2], "bday": st[3], "won": m["final"][0] == 1.0})
            t += step
    return R


def buy(m, b, t, yes, extra=0.02, stake=10.0, lo=0.03, hi=0.97, window=7200, pp=None):
    """$10 at the worst price anyone paid in the next 2 hours (never better than the price we saw) + 2c + the market's own fee."""
    nxt = [x for x in b if t <= x[0] < min(t + window, m["end"] - 1800)]
    if not nxt:
        return None
    px = max(x[4] for x in nxt) if yes else 1 - min(x[3] for x in nxt)
    if pp is not None:
        px = max(px, pp if yes else 1 - pp)
    if not lo <= px <= hi:
        return None
    c = min(0.99, px + extra)
    sh = stake / c
    win = (m["final"][0] == 1.0) == yes
    return {"ev": m["ev_slug"], "t": nxt[0][0], "cost": stake + bot.taker_fee(sh, c, m.get("fee") or 0.0), "pay": sh if win else 0.0,
            "sh": sh, "px": px, "yes": yes, "id": m["id"], "ques": m["q"]}


def first_bets(ms, tp, R, sel, yes, **kw):
    """One bet per market: the first look where sel(row) holds."""
    out, seen = [], set()
    for r in R:
        if r["k"] in seen or not sel(r):
            continue
        x = buy(ms[r["k"]], tp[r["k"]]["b"], r["t"], yes, pp=r["pp"], **kw)
        seen.add(r["k"])
        if x:
            x.update(h=r["h"], pp=r["pp"], gap=r["gap"], place=r["place"])
            out.append(x)
    return out


HB = ((0, 24, "last day"), (24, 72, "1-3 days"), (72, 168, "3-7 days"), (168, 336, "1-2 weeks"), (336, 9e9, "2+ weeks"))
PB = ((0.03, .10), (.10, .25), (.25, .50), (.50, .75), (.75, .90), (.90, .97))


def cell(b, n=12):
    import earn
    return f"{earn.usd(earn.per100(b))} ({len(b)}, {sum(1 for x in b if x['pay'] > 0)} won)" if len(b) >= n else f"- ({len(b)})"


def comb(ms, tp, R, title="all leaderboard markets"):
    print(f"\n### {title}: {len({r['k'] for r in R})} markets with a price and a board\n")
    for holds in (True, False):
        print(f"\n{'Its name HOLDS the place on the newest board' if holds else 'Its name does NOT hold the place'}\n")
        print("| time left | side | " + " | ".join(f"Yes at {a * 100:.0f}-{b * 100:.0f}c" for a, b in PB) + " |")
        print("|---|---|" + "---|" * len(PB))
        for h0, h1, nm in HB:
            for yes in (True, False):
                print(f"| {nm} | {'Yes' if yes else 'No'} | " + " | ".join(
                    cell(first_bets(ms, tp, R, lambda r, a=a, b=b: r["holds"] == holds and h0 <= r["h"] < h1 and a <= r["pp"] < b, yes))
                    for a, b in PB) + " |")


# ================================================================ the outside number: how often a place changes hands, from the boards themselves
BASE_BOARDS = (("text", "overall"), ("text_style_control", "overall"), ("text", "math"), ("text", "coding"), ("webdev", "overall"),
               ("text_to_image", "overall"), ("text", "hard_prompts"), ("text", "creative_writing"), ("text", "instruction_following"),
               ("text", "longer_query"), ("text", "multi_turn"), ("text_style_control", "math"), ("text_style_control", "coding"),
               ("vision", "overall"), ("search", "overall"))
HZ = (3, 7, 14, 30, 400)
GAPS = (3, 8, 15, 1e9)


def hz_bucket(days):
    for i, x in enumerate(HZ):
        if days <= x:
            return i
    return len(HZ) - 1


def gap_bucket(g):
    g = abs(g or 0)
    for i, x in enumerate(GAPS):
        if g < x:
            return i
    return len(GAPS) - 1


class Base:
    """For every past pair of boards (start, the board in force `days` later): did the name that held place P still hold it,
    and did a name that did not hold it take it? Looked up walk-forward: only pairs that ENDED before the day asked about."""

    def __init__(self, first="2024-06-01"):
        import bisect
        self.bisect = bisect
        S = collections.defaultdict(list)
        for sub, cat in BASE_BOARDS:
            days = lb(sub).get(cat) or {}
            ds = sorted(d for d in days if d >= first)
            for unit in ("company", "lab", "model"):
                for pos in (1, 2, 3):
                    P0 = {"pos": pos, "unit": unit, "china": False}
                    st = {}
                    for d in ds:
                        st[d] = self._names(days[d], P0)
                    for i, d0 in enumerate(ds):
                        a = dt.date.fromisoformat(d0)
                        seen_h = set()
                        for d1 in ds[i + 1:]:
                            n = (dt.date.fromisoformat(d1) - a).days
                            if n > 60:
                                break
                            hb = hz_bucket(n)
                            if (hb, n // 2) in seen_h:        # thin out near-identical pairs
                                continue
                            seen_h.add((hb, n // 2))
                            h0, names0 = st[d0]
                            h1, _ = st[d1]
                            for nm, (place, gap) in names0.items():
                                holds = nm == h0
                                if not holds and (place is None or place > pos + 3):
                                    continue
                                S[(unit, pos, hb, holds, gap_bucket(gap))].append((d1, 1 if h1 == nm else 0))
                                S[(unit, pos, hb, holds, -1)].append((d1, 1 if h1 == nm else 0))
        self.S = {}
        for k, v in S.items():
            v.sort()
            pre = [0]
            for _, y in v:
                pre.append(pre[-1] + y)
            self.S[k] = ([d for d, _ in v], pre)

    @staticmethod
    def _names(rows, P0):
        seq, holder = standing(list(rows), P0)
        out = {}
        for nm in dict.fromkeys(seq[:8]):
            place, _, gap = place_of(rows, dict(P0, who=nm))
            out[nm] = (place, gap)
        return holder, out

    def chance(self, unit, pos, days, holds, gap, before, need=40):
        hb = hz_bucket(days)
        for gb in (gap_bucket(gap), -1):
            v = self.S.get((unit, pos, hb, holds, gb))
            if not v:
                continue
            i = self.bisect.bisect_left(v[0], before)
            if i >= need:
                return (v[1][i] + 1) / (i + 2), i
        return None, 0


def with_chance(ms, R, B=None):
    """Adds r['pm'] = the boards' own record for this kind of place, time left and score gap (walk-forward)."""
    B = B or Base()
    out = []
    for r in R:
        m = ms[r["k"]]
        P = m["P"]
        if P["china"]:
            continue
        days = (dt.date.fromisoformat(d10(m["end"])) - dt.date.fromisoformat(r["bday"])).days
        if not r["holds"] and (r["place"] is None or r["place"] > P["pos"] + 3):
            pm, n = 0.01, 999
        else:
            pm, n = B.chance(P["unit"], P["pos"], days, r["holds"], r["gap"], d10(r["t"]))
        if pm is None:
            continue
        r = dict(r, pm=pm, n=n)
        out.append(r)
    return out


def brier(R):
    import statistics
    f = lambda key: statistics.mean((r[key] - r["won"]) ** 2 for r in R) if R else None
    return f("pm"), f("pp")


def model_report(ms, tp, R):
    import earn
    print(f"\n### The boards' own record against the price: {len(R)} looks at {len({r['k'] for r in R})} markets\n")
    print("| time left | looks | miss score, the record | miss score, the price | (lower is better) |")
    print("|---|---|---|---|---|")
    for h0, h1, nm in HB:
        v = [r for r in R if h0 <= r["h"] < h1]
        if v:
            a, b = brier(v)
            print(f"| {nm} | {len(v)} | {a:.4f} | {b:.4f} | {'record' if a < b else 'price'} |")
    print("\n| rule | bets | won | per $100 | first half | second half |")
    print("|---|---|---|---|---|---|")
    out = {}
    for nm, sel, yes in (("Yes where the record is 10c+ above the price", lambda r: r["pm"] - r["pp"] >= 0.10, True),
                         ("No where the record is 10c+ below the price", lambda r: r["pp"] - r["pm"] >= 0.10, False),
                         ("Yes, 10c+, its name holds the place", lambda r: r["pm"] - r["pp"] >= 0.10 and r["holds"], True),
                         ("Yes, 10c+, its name does not hold the place", lambda r: r["pm"] - r["pp"] >= 0.10 and not r["holds"], True),
                         ("No, 10c+, its name holds the place", lambda r: r["pp"] - r["pm"] >= 0.10 and r["holds"], False),
                         ("No, 10c+, its name does not hold the place", lambda r: r["pp"] - r["pm"] >= 0.10 and not r["holds"], False),
                         ("Yes where the record is 20c+ above the price", lambda r: r["pm"] - r["pp"] >= 0.20, True),
                         ("No where the record is 20c+ below the price", lambda r: r["pp"] - r["pm"] >= 0.20, False)):
        b = sorted(first_bets(ms, tp, R, sel, yes), key=lambda x: x["t"])
        out[nm] = b
        h = len(b) // 2
        print(f"| {nm} | {len(b)} | {sum(1 for x in b if x['pay'] > 0)} | {earn.usd(earn.per100(b))} | {earn.usd(earn.per100(b[:h]))} | {earn.usd(earn.per100(b[h:]))} |")
    return out


# ================================================================ Kalshi: the same boards, real asking prices
BRAND = {"claude": "anthropic", "gemini": "google", "chatgpt": "openai", "gpt": "openai", "grok": "xai", "muse": "meta", "llama": "meta",
         "dola": "bytedance", "doubao": "bytedance", "qwen": "alibaba", "kimi": "moonshot", "glm": "zai", "mimo": "xiaomi",
         "amazonnova": "amazon", "nova": "amazon", "ernie": "baidu", "hunyuan": "tencent", "copilot": "microsoft", "mai": "microsoft",
         "longcat": "meituan", "step": "stepfun"}
K_SERIES = {"KXLLM1": ("text", "overall", "lab", False), "KXTOPMODEL": ("text", "overall", "model", False),
            "KXTECHRANKLISTAICODE": ("webdev", "overall", "lab", False), "KXCHINAAI": ("text", "overall", "lab", True),
            "KXMATHAI": ("text", "math", "lab", False)}


def k_parse(m):
    if m["s"] not in K_SERIES:
        return None
    sub, cat, unit, china = K_SERIES[m["s"]]
    who = m["w"]
    if unit == "lab":
        x = re.match(r"If (.+?) (?:has|is) ", m["rule"] or "")
        nm = norm(x.group(1)) if x else norm(who)
        who = BRAND.get(nm, BRAND.get(norm(m["w"]), org(nm)))
    return {"sub": sub, "cat": cat, "pos": 1, "unit": unit, "who": who, "china": china}


def k_load():
    """Settled Kalshi leaderboard markets + hourly real bid/ask and trades (the 100-times-too-small quote trap repaired)."""
    import glob
    ms = {}
    for t, m in ((rj(MK, {}) or {}).get("markets") or {}).items():
        P = k_parse(m)
        if P and lb(P["sub"]).get(P["cat"]):
            m["P"] = P
            ms[t] = m
    tp = {}
    for f in sorted(glob.glob(os.path.join(CACHE, "ktapes_*.json.gz"))):
        for tk, v in (rj(f, {}) or {}).items():
            if tk not in ms:
                continue
            vals = [x for c in v["c"] for x in c[1:3] if x is not None]
            if vals and max(vals) <= 0.0101 and v["tr"] and max(t[1] for t in v["tr"]) > 20:
                for c in v["c"]:
                    c[1] = None if c[1] is None else round(c[1] * 100, 4)
                    c[2] = None if c[2] is None else round(c[2] * 100, 4)
            tp[tk] = v
    return ms, tp


def k_fee(p):
    import math
    return math.ceil(7 * p * (1 - p) - 1e-9) / 100        # Kalshi's fee per contract, to the cent, for a small order


def k_check():
    ms, tp = k_load()
    by = collections.defaultdict(lambda: [0, 0])
    miss = []
    for t, m in ms.items():
        if d10(m["close"]) < FIRST_END:
            continue
        b = board(m["P"]["sub"], m["P"]["cat"], d10(m["close"]), 0)
        if not b:
            continue
        seq, holder = standing(list(b[1]), m["P"])
        ok = (holder == who_key(m["P"])) == (m["res"] == "yes")
        by[m["s"]][0] += ok
        by[m["s"]][1] += 1
        if not ok and len(miss) < 25:
            miss.append((t, m["w"], m["P"]["who"], "we say", holder, m["res"], b[0], seq[:3]))
    print({k: f"{v[0]} of {v[1]}" for k, v in by.items()})
    for x in miss:
        print("  MISS", x)


def k_looks(ms, tp, lag=LAG):
    """Every market every hour with a real two-sided quote: where its name stands + the real asking prices."""
    R = []
    for t, m in ms.items():
        v = tp.get(t)
        if not v or d10(m["close"]) < FIRST_END:
            continue
        P = m["P"]
        last_day, st = None, None
        for c in v["c"]:
            ts, bid, ask = c[0], c[1], c[2]
            if bid is None or ask is None or ts >= m["close"] - 1800 or not 0 < ask < 1 or ask <= bid:
                continue
            day = d10(ts)
            if day != last_day:
                bd = board(P["sub"], P["cat"], day, lag)
                st = (place_of(bd[1], P) + (bd[0],)) if bd else None
                last_day = day
            if st:
                R.append({"k": t, "t": ts, "h": (m["close"] - ts) / 3600, "bid": bid, "ask": ask, "pp": (bid + ask) / 2,
                          "holds": st[1] == who_key(P), "gap": st[2], "place": st[0], "bday": st[3], "won": m["res"] == "yes"})
    return R


def k_bets(ms, R, sel, yes, stake=10.0, max_gap=0.15):
    """One bet per market at the first hour sel(row) holds: the real asking price + Kalshi's fee."""
    out, seen = [], set()
    for r in R:
        if r["k"] in seen or not sel(r) or r["ask"] - r["bid"] > max_gap:
            continue
        seen.add(r["k"])
        px = r["ask"] if yes else 1 - r["bid"]
        if not 0.02 <= px <= 0.98:
            continue
        m = ms[r["k"]]
        n = stake / (px + k_fee(px))
        out.append({"ev": m["ev"], "t": r["t"], "cost": stake, "pay": n if (m["res"] == "yes") == yes else 0.0, "sh": n, "px": px,
                    "yes": yes, "id": r["k"], "h": r["h"], "gap": r["gap"], "s": m["s"]})
    return sorted(out, key=lambda x: x["t"])


# ================================================================ usage numbers: Vercel AI Gateway and OpenRouter (free, public)
VERCEL = "https://vercel.com/api/ai/leaderboard-export"
ORX = "https://openrouter.ai/api/v1/datasets/exports/rankings-daily"


def _try(url, params=None):
    try:
        return bot.http_json(url, params, retries=2)
    except Exception as e:
        print("  FAILED", url[:110], str(e)[:160], flush=True)
        return None


def usrc():
    """probe aim_usrc: the public usage numbers the usage bets settle on -> bt_cache/aim/vercel_<set>.json.gz, openrouter_daily.json.gz"""
    os.makedirs(CACHE, exist_ok=True)
    today = dt.datetime.now(dt.timezone.utc).date()
    for ds in ("labs", "models"):
        rows, a = [], dt.date(2025, 10, 1)
        while a <= today:
            b = min(today, a + dt.timedelta(days=59))
            r = _try(VERCEL, {"dataset": ds, "from": a.isoformat(), "to": b.isoformat()})
            got = (r or {}).get("rows") or []
            if r and not rows:
                print("vercel", ds, {k: v for k, v in r.items() if k != "rows"}, got[:3], flush=True)
            rows += got
            a = b + dt.timedelta(days=1)
        print("vercel", ds, len(rows), "rows", collections.Counter((x.get("metric"), x.get("modality")) for x in rows).most_common(12), flush=True)
        if rows:
            wj(os.path.join(CACHE, f"vercel_{ds}.json.gz"), rows)
    # OpenRouter: one public file per snapshot day, each holding the 30 days before it. Keep every snapshot's view of every day
    # ("first" = the first time a day was seen, "last" = the newest), so restated numbers can be told apart.
    path = os.path.join(CACHE, "openrouter_daily.json.gz")
    have = rj(path, None) or {"snaps": [], "first": {}, "last": {}}
    d, miss = today, 0
    while miss < 12 and d >= dt.date(2025, 1, 1):
        ds = d.isoformat()
        if ds not in have["snaps"]:
            r = _try(f"{ORX}/{ds}.json")
            if r and r.get("rows"):
                miss = 0
                have["snaps"].append(ds)
                for x in r["rows"]:
                    k = x["date"]
                    row = [x["model_permaslug"], x["total_tokens"]]
                    have["first"].setdefault(k, {})          # filled below, oldest snapshot wins
                    have["last"].setdefault(k, {"snap": "", "rows": []})
                    if ds >= have["last"][k]["snap"]:
                        if ds > have["last"][k]["snap"]:
                            have["last"][k] = {"snap": ds, "rows": []}
                        have["last"][k]["rows"].append(row)
                    f = have["first"][k]
                    if not f or ds <= f["snap"]:
                        if not f or ds < f["snap"]:
                            have["first"][k] = f = {"snap": ds, "rows": []}
                        f["rows"].append(row)
            else:
                miss += 1
        d -= dt.timedelta(days=1)
    wj(path, have)
    print("openrouter snapshots", len(have["snaps"]), min(have["snaps"] or ["-"]), max(have["snaps"] or ["-"]),
          "days", len(have["last"]), min(have["last"] or ["-"]), max(have["last"] or ["-"]), flush=True)
    for k in sorted(have["last"])[-2:]:
        print(" ", k, have["last"][k]["snap"], have["last"][k]["rows"][:4], "| first seen", have["first"][k]["snap"], have["first"][k]["rows"][:2], flush=True)
    # other places that keep the weekly page as it looked each day
    for u in ("https://openrouter.ai/api/v1/datasets/exports/index.json",
              "https://api.github.com/repos/lyll23/OpenRouter-OS-Rankings-f/contents/data/datasets"):
        try:
            import urllib.request
            with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "paper-bot"}), timeout=25) as r:
                t = r.read().decode("utf-8", "replace")
            print("OK", u, len(t), t[:6000].replace("\n", " "), flush=True)
        except Exception as e:
            print("FAILED", u, str(e)[:120], flush=True)


def orfind():
    """probe aim_orfind: where does Kalshi's 'OpenRouter text market share by model author' come from? Reads Kalshi's rules for the
    share series, the OpenRouter rankings page and the API paths its scripts call, and prints what answers."""
    import urllib.request
    def get(u, n=400000):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 paper-bot", "Accept": "*/*"}), timeout=30) as r:
                return r.status, r.read(n).decode("utf-8", "replace")
        except Exception as e:
            return str(e)[:80], ""
    for s in ("KXGOOGSHARE", "KXOPENSHARE", "KXANTHSHARE"):
        r = _try(f"{bot.KALSHI}/series/{s}") or {}
        se = r.get("series") or {}
        print(s, bot.json.dumps({k: se.get(k) for k in ("title", "settlement_sources", "contract_url", "contract_terms_url", "frequency")})[:900], flush=True)
        r = _try(f"{bot.KALSHI}/markets", {"series_ticker": s, "limit": 1, "status": "settled"}) or {}
        for m in (r.get("markets") or [])[:1]:
            print("  rules:", (m.get("rules_primary") or "")[:600], "|", (m.get("rules_secondary") or "")[:900], flush=True)
    st, html = get("https://openrouter.ai/rankings")
    print("rankings page", st, len(html), flush=True)
    paths = sorted(set(re.findall(r'["\'](/api/[A-Za-z0-9_\-/\.?=&]+)', html)))
    print("api paths in page:", paths[:80], flush=True)
    for k in ("market share", "marketShare", "market_share", "author"):
        i = html.find(k)
        print(" ctx", k, html[max(0, i - 300):i + 300].replace("\n", " ") if i >= 0 else "-", flush=True)
    js = sorted(set(re.findall(r'(/_next/static/[^"\']+?\.js)', html)))
    print("scripts", len(js), flush=True)
    found = set()
    for u in js[:120]:
        st2, t = get("https://openrouter.ai" + u, 3000000)
        for x in re.findall(r'["\'`](/api/(?:frontend|v1)/[A-Za-z0-9_\-/\.${}]+)', t):
            if any(w in x.lower() for w in ("rank", "stat", "share", "author", "usage", "dataset", "token")):
                found.add(x)
    print("api paths in scripts:", sorted(found)[:150], flush=True)
    tries = ["/api/frontend/stats/market-share", "/api/frontend/stats/author-share", "/api/frontend/rankings",
             "/api/frontend/stats/rankings", "/api/v1/datasets/exports/index.json",
             "/api/v1/datasets/exports/rankings-weekly/2026-11-16.json", "/api/v1/datasets/exports/market-share-daily/2026-11-20.json",
             "/api/v1/datasets/exports/author-share-daily/2026-11-20.json"] + sorted(found)[:60]
    for x in tries:
        if "$" in x or "{" in x:
            continue
        st3, t = get("https://openrouter.ai" + x, 200000)
        print("TRY", x, st3, len(t), t[:700].replace("\n", " "), flush=True)


ORF = "https://openrouter.ai/api/frontend/v1/public/stats/rankings"


def orshare():
    """probe aim_orshare: OpenRouter's own rankings-page data (the chart Kalshi's share bets settle on) -> bt_cache/aim/or_*.json.gz.
    Keeps every snapshot, so a day seen twice shows whether OpenRouter restates its numbers."""
    import urllib.request
    os.makedirs(CACHE, exist_ok=True)
    def get(u, n=20000000):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 paper-bot", "Accept": "*/*"}), timeout=40) as r:
                return r.status, r.read(n).decode("utf-8", "replace")
        except Exception as e:
            return str(e)[:80], ""
    # what parameters do the page's scripts send with these two calls?
    st, html = get("https://openrouter.ai/rankings", 3000000)
    i = html.find("Market share by model author, as text")
    print("text summary:", re.sub(r"<[^>]+>", " ", html[i:i + 4000]) if i >= 0 else "-", flush=True)
    for u in sorted(set(re.findall(r'(/_next/static/[^"\']+?\.js)', html)))[:120]:
        _, t = get("https://openrouter.ai" + u, 4000000)
        for k in ("author-market-share", "rankings/models", "model-rankings-chart"):
            for mm in re.finditer(re.escape(k), t):
                print("JS", k, u[-40:], t[max(0, mm.start() - 500):mm.start() + 700].replace("\n", " "), flush=True)
    snap = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M")
    for name, q in (("authorshare", "author-market-share"), ("authorshare_req", "author-market-share?metric=requests"),
                    ("models", "models"), ("models_week", "models?view=week"), ("models_month", "models?view=month"),
                    ("modelchart", "model-rankings-chart")):
        st, t = get(f"{ORF}/{q}")
        print("GET", q, st, len(t), t[:300], flush=True)
        if not t:
            continue
        try:
            js = bot.json.loads(t)
        except Exception:
            continue
        path = os.path.join(CACHE, f"or_{name}.json.gz")
        have = rj(path, None) or {"snaps": {}}
        have["snaps"][snap] = js
        wj(path, have)
        d = js.get("data")
        if isinstance(d, dict) and "data" in d:
            d = d["data"]
        if isinstance(d, list) and d and isinstance(d[0], dict) and "x" in d[0]:
            print("  weeks", len(d), d[0]["x"], d[-1]["x"], flush=True)
            for w in d[-4:]:
                tot = sum(w["ys"].values())
                print("  ", w["x"], {k: round(100 * v / tot, 1) for k, v in sorted(w["ys"].items(), key=lambda kv: -kv[1])}, flush=True)
        elif isinstance(d, list):
            print("  rows", len(d), collections.Counter(str(r.get("date"))[:10] for r in d if isinstance(r, dict)).most_common(40), flush=True)


def orparams():
    """probe aim_orparams: which query parameters make author-market-share match the page's own text summary."""
    import urllib.request
    def get(u, n=8000000):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 paper-bot", "Accept": "*/*"}), timeout=40) as r:
                return r.status, r.read(n).decode("utf-8", "replace")
        except Exception as e:
            return str(e)[:80], ""
    st, html = get("https://openrouter.ai/rankings", 3000000)
    for u in sorted(set(re.findall(r'(/_next/static/[^"\']+?\.js)', html)))[:150]:
        _, t = get("https://openrouter.ai" + u)
        for k in ("authorMarketShare", "Market share by model author", "market-share", "Share of text requests", "metric:"):
            for mm in list(re.finditer(re.escape(k), t))[:6]:
                print("JS", k, u[-30:], t[max(0, mm.start() - 400):mm.start() + 500].replace("\n", " "), flush=True)
    import itertools
    combos = [""]
    for k, vs in (("metric", ["requests", "tokens", "count", "request_count"]), ("modality", ["text", "text->text"]),
                  ("inputModality", ["text"]), ("outputModality", ["text"]), ("category", ["text"]), ("type", ["text"]),
                  ("view", ["week"])):
        combos += [f"{k}={v}" for v in vs]
    combos += ["metric=requests&modality=text", "metric=requests&outputModality=text", "metric=requests&inputModality=text",
               "metric=requests&outputModality=text&inputModality=text", "metric=requests&type=text", "metric=requests&category=text"]
    for q in combos:
        st, t = get(f"{ORF}/author-market-share" + ("?" + q if q else ""))
        try:
            d = bot.json.loads(t)["data"]["data"]
            w = [x for x in d if x["x"] == "2026-11-16"][0]["ys"]
            tot = sum(w.values())
            print("Q", q or "-", st, {k: round(100 * v / tot, 1) for k, v in sorted(w.items(), key=lambda kv: -kv[1])[:8]}, flush=True)
        except Exception as e:
            print("Q", q or "-", st, str(e)[:60], t[:200], flush=True)


ORQ = "metric=requests&modality=text"          # the settings that reproduce the page's own "Market share by model author" text


def orday():
    """probe aim_orday: save the share chart Kalshi settles on (requests, text) and look for a by-day version of it."""
    import urllib.request
    def get(u):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 paper-bot", "Accept": "*/*"}), timeout=40) as r:
                return r.status, r.read().decode("utf-8", "replace")
        except Exception as e:
            return str(e)[:80], ""
    snap = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M")
    for extra in ["", "&granularity=day", "&interval=day", "&period=day", "&timeframe=day", "&bucket=day", "&view=day",
                  "&range=day", "&groupBy=day", "&resolution=day", "&window=day", "&period=daily", "&interval=daily",
                  "&granularity=daily", "&view=month", "&period=month", "&timeframe=month", "&range=month",
                  "&from=2026-11-01&to=2026-11-20", "&startDate=2026-11-01&endDate=2026-11-20", "&date=2026-11-20", "&week=2026-11-09"]:
        st, t = get(f"{ORF}/author-market-share?{ORQ}{extra}")
        try:
            js = bot.json.loads(t)
            d = js["data"]["data"]
            xs = [w["x"] for w in d]
            print("D", extra or "-", st, len(d), xs[:2], xs[-3:], f"{sum(d[-1]['ys'].values()):.3e}", flush=True)
            if not extra:
                path = os.path.join(CACHE, "or_share_text_req.json.gz")
                have = rj(path, None) or {"snaps": {}}
                have["snaps"][snap] = js
                wj(path, have)
        except Exception as e:
            print("D", extra or "-", st, str(e)[:60], t[:150], flush=True)


ORLAB = {"KXGOOGSHARE": "google", "KXOPENSHARE": "openai", "KXANTHSHARE": "anthropic", "KXDEEPSHARE": "deepseek",
         "KXZAISHARE": "z-ai", "KXTENCENTSHARE": "tencent", "KXXIAOMISHARE": "xiaomi", "KXBABASHARE": "qwen",
         "KXMETASHARE": "meta-llama", "KXMISTRALSHARE": "mistralai", "KXSTEALTHSHARE": "stealth", "KXMOONSHARE": "moonshotai",
         "KXXAISHARE": "x-ai", "KXMINIMAXSHARE": "minimax", "KXNVIDIASHARE": "nvidia"}


def orlive():
    """probe aim_orlive: the running week on OpenRouter's share chart next to Kalshi's open share ladders, right now.
    Appends to bt_cache/aim/or_live.json.gz so repeated looks build a record of price vs the running number."""
    import urllib.request
    with urllib.request.urlopen(urllib.request.Request(f"{ORF}/author-market-share?{ORQ}", headers={"User-Agent": "Mozilla/5.0 paper-bot"}), timeout=40) as r:
        js = bot.json.loads(r.read().decode())
    d = js["data"]["data"]
    cur = d[-1]
    tot = sum(cur["ys"].values())
    share = {k: 100 * v / tot for k, v in cur["ys"].items()}
    prev = {k: 100 * v / sum(d[-2]["ys"].values()) for k, v in d[-2]["ys"].items()}
    now = time.time()
    wk0 = dt.datetime.fromisoformat(cur["x"]).replace(tzinfo=dt.timezone.utc).timestamp()
    print("week", cur["x"], "days done", round((now - wk0) / 86400, 2), {k: round(v, 1) for k, v in sorted(share.items(), key=lambda kv: -kv[1])}, flush=True)
    rows = []
    for s, a in ORLAB.items():
        r = _try(f"{bot.KALSHI}/markets", {"series_ticker": s, "status": "open", "limit": 200}) or {}
        for m in r.get("markets") or []:
            x = re.search(r"bove \$?([0-9.]+)", m.get("yes_sub_title") or m.get("subtitle") or "") or re.search(r"-([0-9.]+)$", m["ticker"])
            if not x:
                continue
            def px(k):
                v = m.get(k + "_dollars")
                v = float(v) if v not in (None, "") else (m.get(k) or 0) / 100
                return v
            rows.append({"s": s, "a": a, "t": m["ticker"], "X": float(x.group(1)), "bid": px("yes_bid"), "ask": px("yes_ask"),
                         "close": m.get("close_time"), "rule": (m.get("rules_primary") or "")[-60:], "share": share.get(a), "prev": prev.get(a)})
    for r in sorted(rows, key=lambda r: (r["s"], r["close"] or "", r["X"])):
        print(f"{r['s']:16} {r['t']:28} X {r['X']:5}  run {r['share'] if r['share'] is None else round(r['share'], 2)}  last wk {r['prev'] if r['prev'] is None else round(r['prev'], 1)}  bid {r['bid']:.2f} ask {r['ask']:.2f}  close {r['close']}  {r['rule']}", flush=True)
    path = os.path.join(CACHE, "or_live.json.gz")
    have = rj(path, None) or []
    have.append({"t": now, "week": cur["x"], "share": share, "rows": rows})
    wj(path, have)


# ================================================================ usage bets on Kalshi: ladders ("above X") on a public usage number
def use_fam(s):
    if re.search(r"V(SPEND|REQ)$|^KXOSSPEND$|^KXOPENSOURCESHARE$", s):
        return "vercel"                      # daily shares on Vercel's AI Gateway
    if re.search(r"SHARE$", s) and s not in ("KXRFKSHARE", "KXMLABELSHARE"):
        return "orshare"                     # a lab's share of the week on OpenRouter
    if s.startswith("KXTOKENUSE"):
        return "tokens"                      # OpenRouter's token total of the week / month
    if re.search(r"APP$|APPARRAY$", s) and "APPSTORE" not in s and s != "KXTAXAPP":
        return "apps"                        # monthly app downloads
    return None


def use_load():
    """Settled usage ladders + tapes (100-times-too-small quotes repaired) + what each event ended at, read off its own ladder."""
    import statistics
    ms = {}
    for t, m in ((rj(MK, {}) or {}).get("markets") or {}).items():
        x = re.search(r"bove \$?([0-9.]+)", m["w"])
        if re.search(USE_K, m["s"]) and use_fam(m["s"]) and x:
            m["X"], m["fam"] = float(x.group(1)), use_fam(m["s"])
            ms[t] = m
    tp = {}
    for s in {m["s"] for m in ms.values()}:
        for tk, v in (rj(os.path.join(CACHE, f"ktapes_{s}.json.gz"), {}) or {}).items():
            if tk in ms:
                vals = [x for c in v["c"] for x in c[1:3] if x is not None]
                if vals and max(vals) <= 0.0101 and v["tr"] and max(t[1] for t in v["tr"]) > 20:
                    for c in v["c"]:
                        c[1] = None if c[1] is None else c[1] * 100
                        c[2] = None if c[2] is None else c[2] * 100
                tp[tk] = v
    evs = collections.defaultdict(list)
    for m in ms.values():
        evs[m["ev"]].append(m)
    E = {}
    for ev, v in evs.items():
        yes, no = [m["X"] for m in v if m["res"] == "yes"], [m["X"] for m in v if m["res"] == "no"]
        xs = sorted(m["X"] for m in v)
        step = statistics.median([b - a for a, b in zip(xs, xs[1:])] or [0.01 * xs[0]])
        val = (max(yes) + min(no)) / 2 if yes and no else (min(no) - step / 2 if no else max(yes) + step / 2)
        E[ev] = {"s": v[0]["s"], "fam": v[0]["fam"], "close": v[0]["close"], "val": val,
                 "known": max(m["exp"] for m in v) if v[0]["fam"] == "vercel" else v[0]["close"] + 6 * 3600}
    return ms, tp, E


def use_rows(ms, tp, E):
    """Every market every hour with a real two-sided quote + a chance from 'the last result plus the usual change'."""
    import math
    bys = collections.defaultdict(list)
    for ev, e in E.items():
        bys[e["s"]].append((e["close"], ev))
    pairs = collections.defaultdict(list)          # family -> (time the later result was known, days apart, log change)
    for s, L in bys.items():
        L.sort()
        for i, (ca, a) in enumerate(L):
            for cb, b in L[i + 1:i + 8]:
                if E[a]["val"] > 0 and E[b]["val"] > 0:
                    pairs[E[a]["fam"]].append((E[b]["known"], round((cb - ca) / 86400), math.log(E[b]["val"] / E[a]["val"])))
    R = []
    for t, m in ms.items():
        v = tp.get(t)
        if not v or m["ev"] not in E:
            continue
        L = bys[m["s"]]
        for c in v["c"]:
            ts, bid, ask = c[0], c[1], c[2]
            if bid is None or ask is None or not (0 < ask < 1 and ask > bid) or ts >= m["close"] - 1800:
                continue
            prev = [(cl, ev) for cl, ev in L if E[ev]["known"] <= ts and cl < m["close"]]
            pm = v1 = None
            if prev and E[prev[-1][1]]["val"] > 0:
                v1 = E[prev[-1][1]]["val"]
                lag = round((m["close"] - prev[-1][0]) / 86400)
                pool = [x[2] for x in pairs[m["fam"]] if x[0] <= ts and x[1] == lag]
                if len(pool) >= 25:
                    need = math.log(m["X"] / v1)
                    pm = (sum(1 for x in pool if x > need) + 0.5) / (len(pool) + 1)
            R.append({"k": t, "t": ts, "h": (m["close"] - ts) / 3600, "bid": bid, "ask": ask, "pp": (bid + ask) / 2, "pm": pm,
                      "won": m["res"] == "yes", "holds": True, "gap": 0, "place": 0, "fam": m["fam"], "s": m["s"], "X": m["X"], "v1": v1})
    return R


def tokens_rows(ms, tp):
    """KXTOKENUSE: chance from OpenRouter's public daily token totals (day D is public from D+1 03:00 UTC):
    days known so far + the rest of the week scaled from last week, misses measured on every earlier 7-day window."""
    import math
    O = rj(os.path.join(CACHE, "openrouter_daily.json.gz"), {}) or {"first": {}}
    D = {day: sum(r[1] for r in v["rows"]) / 1e12 for day, v in O["first"].items()}
    if not D:
        return [], D
    d0 = dt.date.fromisoformat(min(D))

    def tot(start, k0, k1):
        xs = [D.get((start + dt.timedelta(days=k)).isoformat()) for k in range(k0, k1)]
        return None if None in xs else sum(xs)

    def point(start, n):
        prev = tot(start - dt.timedelta(days=7), 0, 7)
        if prev is None:
            return None
        if n == 0:
            pp = tot(start - dt.timedelta(days=14), 0, 7)
            return prev * (prev / pp if pp else 1.0)
        known, pk = tot(start, 0, n), tot(start - dt.timedelta(days=7), 0, n)
        return None if known is None or not pk else known + (prev - pk) * known / pk

    def errs(before, n, memo={}):
        if (before, n) not in memo:
            out, s = [], d0 + dt.timedelta(days=14)
            while s + dt.timedelta(days=7) <= before:
                p, a = point(s, n), tot(s, 0, 7)
                if p and a:
                    out.append(math.log(a / p))
                s += dt.timedelta(days=1)
            memo[(before, n)] = out
        return memo[(before, n)]
    R = []
    for t, m in ms.items():
        v = tp.get(t)
        if m["s"] != "KXTOKENUSE" or not v:
            continue
        start = dt.datetime.fromtimestamp(m["close"], dt.timezone.utc).date() - dt.timedelta(days=7)
        for c in v["c"]:
            ts, bid, ask = c[0], c[1], c[2]
            if bid is None or ask is None or not (0 < ask < 1 and ask > bid) or ts >= m["close"] - 1800:
                continue
            asof = (dt.datetime.fromtimestamp(ts, dt.timezone.utc) - dt.timedelta(hours=3)).date()
            n = max(0, min(7, (asof - start).days))
            p = point(start, n)
            e = errs(asof, n)
            if p is None or (n < 7 and len(e) < 10):
                continue
            need = math.log(m["X"] / p)
            pm = (1.0 if p > m["X"] else 0.0) if n >= 7 else (sum(1 for x in e if x > need) + 0.5) / (len(e) + 1)
            R.append({"k": t, "t": ts, "h": (m["close"] - ts) / 3600, "bid": bid, "ask": ask, "pp": (bid + ask) / 2, "pm": pm, "n": n,
                      "won": m["res"] == "yes", "holds": True, "gap": 0, "place": 0, "fam": "tokens", "s": m["s"], "X": m["X"]})
    return R, D


USE_TRIES = 150
USE_NAMES = {"vercel": "Vercel AI Gateway daily shares", "orshare": "OpenRouter weekly share of a lab",
             "tokens": "OpenRouter weekly token total", "apps": "monthly app downloads"}


def use_report(log=False):
    import statistics
    ms, tp, E = use_load()
    R = use_rows(ms, tp, E)
    print(f"## Kalshi usage ladders: {len(ms)} settled markets, {len(E)} events, {len(R)} hourly looks with a real two-sided quote\n")
    print("| kind | series | markets | events | first close | last close | middle gap between buy and sell price |\n|---|---|---|---|---|---|---|")
    for fam, nm in USE_NAMES.items():
        v = [m for m in ms.values() if m["fam"] == fam]
        g = [r["ask"] - r["bid"] for r in R if r["fam"] == fam]
        print(f"| {nm} | {len({m['s'] for m in v})} | {len(v)} | {len({m['ev'] for m in v})} | {d10(min(m['close'] for m in v))} | "
              f"{d10(max(m['close'] for m in v))} | {statistics.median(g) * 100:.0f}c |")
    KB = lambda sel, yes, mg=0.15: k_bets(ms, R, sel, yes, max_gap=mg)
    wk = lambda x: d10(ms[x["id"]]["close"])
    week = lambda b: [dict(x, ev=wk(x)) for x in b]       # one separate bet per week or day: labs in it are linked
    print("\n### The last result plus the usual change, against the price\n")
    print("| kind | time left | looks | miss score, last result | miss score, the price |\n|---|---|---|---|---|")
    for fam, nm in USE_NAMES.items():
        for h0, h1, lab in ((0, 24, "last day"), (24, 72, "1-3 days"), (72, 9e9, "3+ days")):
            v = [r for r in R if r["fam"] == fam and r["pm"] is not None and h0 <= r["h"] < h1]
            if len(v) >= 200:
                print(f"| {nm} | {lab} | {len(v)} | {statistics.mean((r['pm'] - r['won']) ** 2 for r in v):.4f} | "
                      f"{statistics.mean((r['pp'] - r['won']) ** 2 for r in v):.4f} |")
    TR, D = tokens_rows(ms, tp)
    print(f"\n### OpenRouter's public daily token totals ({len(D)} days, {min(D or ['-'])} to {max(D or ['-'])}) against the weekly token bets\n")
    print("| days of the week already public | looks | miss score, the count | miss score, the price |\n|---|---|---|---|")
    for n in range(8):
        v = [r for r in TR if r["n"] == n]
        if v:
            print(f"| {n} | {len(v)} | {statistics.mean((r['pm'] - r['won']) ** 2 for r in v):.4f} | {statistics.mean((r['pp'] - r['won']) ** 2 for r in v):.4f} |")
    print("\n### The exam\n\nReal asking price + Kalshi's fee, $10 a bet, first hour that fits, gap between buy and sell price at most 15c. "
          "Separate bets = weeks or days, because the answers inside one are linked.\n\n" + HEAD)
    TB = lambda sel, yes: k_bets(ms, TR, sel, yes)
    _line("OpenRouter weekly token total (Kalshi): Yes where the public daily count says 15c+ more than the ask",
          week(TB(lambda r: r["pm"] - r["ask"] >= .15, True)), USE_TRIES, log)
    _line("OpenRouter weekly token total (Kalshi): No where the public daily count says 15c+ less than the bid",
          week(TB(lambda r: r["bid"] - r["pm"] >= .15, False)), USE_TRIES, log)
    for fam, nm in USE_NAMES.items():
        F = lambda r: r["fam"] == fam and r["pm"] is not None
        if any(F(r) for r in R):
            _line(f"{nm}: Yes where the last result says 15c+ more than the ask", week(KB(lambda r: F(r) and r["pm"] - r["ask"] >= .15, True)), USE_TRIES)
            _line(f"{nm}: No where the last result says 15c+ less than the bid", week(KB(lambda r: F(r) and r["bid"] - r["pm"] >= .15, False)), USE_TRIES)
    for fam, nm in USE_NAMES.items():
        F = lambda r: r["fam"] == fam
        _line(f"Usage ladders (Kalshi), {nm}: always Yes at 3-97c, first look", week(KB(lambda r: F(r) and .03 <= r["ask"] <= .97, True)), USE_TRIES, log)
        _line(f"Usage ladders (Kalshi), {nm}: always No, Yes at 3-97c, first look", week(KB(lambda r: F(r) and .03 <= r["bid"] <= .97, False)), USE_TRIES, log)
        _line(f"{nm}: No on long shots, Yes at 3-15c", week(KB(lambda r: F(r) and .03 <= r["bid"] < .15, False)), USE_TRIES)
        _line(f"{nm}: Yes on near-sure things, 85-97c", week(KB(lambda r: F(r) and .85 <= r["ask"] <= .97, True)), USE_TRIES)
    print("\n### Backward look: the OpenRouter share bets on the first day of the week\n\n" + HEAD)
    O = lambda r: r["fam"] == "orshare"
    D1 = lambda r: O(r) and r["h"] >= 144
    lead = KB(lambda r: D1(r) and .15 <= r["ask"] <= .85, True)
    _line("OpenRouter lab share (Kalshi): Yes at 15-85c on the first day of the week", week(lead), USE_TRIES, log)
    _line("same, No instead of Yes", week(KB(lambda r: D1(r) and .15 <= r["bid"] <= .85, False)), USE_TRIES)
    _line("same, Yes, the 4 big labs only", week(KB(lambda r: D1(r) and r["s"] in ("KXOPENSHARE", "KXGOOGSHARE", "KXDEEPSHARE", "KXANTHSHARE")
                                                  and .15 <= r["ask"] <= .85, True)), USE_TRIES)
    _line("same, Yes at 15-50c", week(KB(lambda r: D1(r) and .15 <= r["ask"] <= .50, True)), USE_TRIES)
    _line("same, Yes at 50-85c", week(KB(lambda r: D1(r) and .50 < r["ask"] <= .85, True)), USE_TRIES)
    _line("same, strike at or below last week's result", week(KB(lambda r: D1(r) and r["v1"] and r["X"] <= r["v1"] and .15 <= r["ask"] <= .85, True)), USE_TRIES)
    _line("same, strike above last week's result", week(KB(lambda r: D1(r) and r["v1"] and r["X"] > r["v1"] and .15 <= r["ask"] <= .85, True)), USE_TRIES)
    for a, b, lab in ((120, 144, "second day"), (72, 120, "days 3-4"), (24, 72, "days 5-6"), (0, 24, "last day")):
        _line(f"Yes at 15-85c, {lab}", week(KB(lambda r: O(r) and a <= r["h"] < b and .15 <= r["ask"] <= .85, True)), USE_TRIES)
    _line("Vercel daily shares: Yes at 15-85c on the first day", week(KB(lambda r: r["fam"] == "vercel" and r["h"] >= 96 and .15 <= r["ask"] <= .85, True)), USE_TRIES)
    c = collections.defaultdict(list)
    for x in lead:
        c[wk(x)].append(x)
    print("\nThe first-day Yes rule week by week (week's end, bets, won, dollars): " + ", ".join(
        f"{k} {len(v)} / {sum(1 for y in v if y['pay'] > 0)} / {sum(y['pay'] - y['cost'] for y in v):+.0f}" for k, v in sorted(c.items(), key=lambda kv: kv[1][0]["t"])))
    c = collections.defaultdict(list)
    for x in lead:
        c[x["s"]].append(x)
    print("\nBy lab: " + ", ".join(f"{k} {len(v)} / {sum(1 for y in v if y['pay'] > 0)} / {sum(y['pay'] - y['cost'] for y in v):+.0f}" for k, v in sorted(c.items())))


# ================================================================ the whole report
def _line(name, b, tries, log=False, status="dropped", prereg=False):
    import exam, earn
    b = sorted(b, key=lambda x: x["t"])
    c = exam.score(b, name, tries=tries, prereg=prereg, log=log, quiet=True, status=status, src="aim.py, backtest/aim.md")
    h = len(b) // 2
    print(f"| {name} | {len(b)} | {sum(1 for x in b if x['pay'] > 0)} | {earn.usd(earn.per100(b)) if b else '-'} | "
          f"{earn.usd(earn.per100(b[:h])) if h else '-'} / {earn.usd(earn.per100(b[h:])) if h else '-'} | "
          f"{c.get('lo100')} to {c.get('hi100')} | {c.get('floor100')} | {c.get('verdict')} |")
    return b, c


HEAD = "| rule | bets | won | per $100 | first half / second half | luck range per $100 | worst case per $100 | exam verdict |\n|---|---|---|---|---|---|---|---|"
TRIES = 150           # cuts looked at on the leaderboard markets (comb tables + the model + the backward look)


def report(log=False):
    import families
    ms, tp = lb_markets()
    R = looks_lb(ms, tp)
    print(f"## Polymarket: {len(ms)} leaderboard markets, {len({m['ev_slug'] for m in ms.values()})} events, {len(R)} looks\n")
    comb(ms, tp, R)
    out = model_report(ms, tp, with_chance(ms, R))
    print("\n### The exam\n\n" + HEAD)
    _line("Arena leaderboard bets (Polymarket): Yes where the boards' own change record is 10c+ above the price",
          out["Yes where the record is 10c+ above the price"], TRIES, log)
    _line("Arena leaderboard bets (Polymarket): No where the boards' own change record is 10c+ below the price",
          out["No where the record is 10c+ below the price"], TRIES, log)
    H = lambda h, lo, hi: (lambda r: r["holds"] and r["h"] < h and lo <= r["pp"] < hi)
    fb = lambda sel, yes=True, **kw: first_bets(ms, tp, R, sel, yes, **kw)
    _line("late holder, 50-90c, last 3 days", fb(H(72, .5, .9)), TRIES)
    _line("Arena leaderboard bets (Polymarket): Yes on the name already holding the place, 50-97c, last 3 days", fb(H(72, .5, .97)), TRIES, log)
    _line("late holder, 50-97c, last 3 days, 4c extra", fb(H(72, .5, .97), extra=0.04), TRIES)
    _line("late holder, 50-97c, last 3 days, 6c extra", fb(H(72, .5, .97), extra=0.06), TRIES)
    b5, _ = _line("late holder, 50-97c, last 5 days", fb(H(120, .5, .97)), TRIES)
    _line("late holder, 50-97c, last 7 days", fb(H(168, .5, .97)), TRIES)
    _line("holder, 50-97c, days 3 to 7 only", fb(lambda r: r["holds"] and 72 <= r["h"] < 168 and .5 <= r["pp"] < .97), TRIES)
    _line("blind: any name at 50-97c, last 3 days", fb(lambda r: r["h"] < 72 and .5 <= r["pp"] < .97), TRIES)
    _line("a favourite that does NOT hold the place, last 3 days", fb(lambda r: not r["holds"] and r["h"] < 72 and .5 <= r["pp"] < .97), TRIES)
    _line("Arena leaderboard bets (Polymarket): Yes on the holder priced 3-50c with 2+ weeks left",
          fb(lambda r: r["holds"] and r["h"] >= 336 and .03 <= r["pp"] < .50), TRIES, log)
    print("\nThe 5-day rule by kind of bet (bets, won):")
    for key in ("unit", "pos", "sub"):
        c = collections.defaultdict(list)
        for x in b5:
            c[ms[x["id"]]["P"][key]].append(x)
        print(f"- {key}: " + ", ".join(f"{k} {len(v)} / {sum(1 for y in v if y['pay'] > 0)}" for k, v in sorted(c.items(), key=str)))
    print("\n### Backward look: every time the holder lost inside the last 7 days\n")
    for x in sorted(fb(H(168, .5, .97)), key=lambda x: x["t"]):
        if x["pay"] == 0:
            m = ms[x["id"]]
            P = m["P"]
            e1 = board(P["sub"], P["cat"], d10(m["end"]), 0)
            print(f"- {d10(x['t'])}, {x['h']:.0f} hours left, paid {x['px'] * 100:.0f}c: {m['q'][:90]} -> ended {[r[0][:24] for r in e1[1][:3]]}")

    # ---- Kalshi: the fresh check (rule written down before these prices were opened)
    km, kt = k_load()
    KR = k_looks(km, kt)
    print(f"\n## Kalshi, the fresh check: {len(km)} settled markets ({', '.join(sorted({m['s'] for m in km.values()}))}), "
          f"{len(KR)} hourly looks with a real two-sided quote\n")
    print("Bought at the real asking price + Kalshi's fee, $10 a bet, first hour that fits, buy-sell gap at most 15c.\n\n" + HEAD)
    KH = lambda h, lo, hi: (lambda r: r["holds"] and r["h"] <= h and lo <= r["ask"] <= hi)
    k3, _ = _line("Arena leaderboard bets (Kalshi, fresh check): Yes on the name already holding first place, ask 50-97c, last 3 days",
                  k_bets(km, KR, KH(72, .5, .97), True), 2, log, prereg=True)
    _line("Kalshi: same, last 5 days", k_bets(km, KR, KH(120, .5, .97), True), 2, prereg=True)
    _line("Kalshi: same, ask 50-90c, last 3 days", k_bets(km, KR, KH(72, .5, .9), True), TRIES)
    _line("Kalshi: same, last day only", k_bets(km, KR, KH(24, .5, .97), True), TRIES)
    _line("Kalshi: any name at 50-97c, last 3 days", k_bets(km, KR, lambda r: r["h"] <= 72 and .5 <= r["ask"] <= .97, True), TRIES)
    _line("Kalshi: holder priced 3-50c, last 7 days", k_bets(km, KR, KH(168, .03, .5), True), TRIES)
    _line("Kalshi: always Yes, 3-97c, first look", k_bets(km, KR, lambda r: .03 <= r["ask"] <= .97, True), TRIES)
    _line("Kalshi: always No, Yes at 3-97c, first look", k_bets(km, KR, lambda r: .03 <= r["bid"] <= .97, False), TRIES)
    _line("Kalshi: No on a name that does not hold the place, Yes 3-50c, last 3 days",
          k_bets(km, KR, lambda r: not r["holds"] and r["h"] <= 72 and .03 <= r["bid"] <= .5, False), TRIES)
    by = collections.defaultdict(list)
    for x in k3:
        by[x["s"]].append(x)
    print("\nThe 3-day rule by Kalshi series (bets, won, dollars): " + ", ".join(
        f"{k} {len(v)} / {sum(1 for y in v if y['pay'] > 0)} / {sum(y['pay'] - y['cost'] for y in v):+.2f}" for k, v in sorted(by.items())))
    print("\nIts losses:")
    for x in k3:
        if x["pay"] == 0:
            m = km[x["id"]]
            e1 = board(m["P"]["sub"], m["P"]["cat"], d10(m["close"]), 0)
            print(f"- {x['id']}, paid {x['px'] * 100:.0f}c, {x['h']:.0f} hours left, lead then {x['gap']:.1f} points -> ended {[r[0][:24] for r in e1[1][:3]]}")

    # ---- release-day bets ("will X be released on <day>"), prices alone
    am, at = families.load("ai")
    rel = lambda m: bool(re.search(r"released|release |announce|launch", (m["q"] + " " + m["ev_slug"]).lower())) and not parse(m)
    on = {k: m for k, m in am.items() if rel(m) and not re.search(r"\bby\b|before", m["q"].lower())}
    S = families.looks(on, at)

    def rb(sel, **kw):
        o = []
        for k, rows in S.items():
            for t, f, h, pp in rows:
                if sel(f, h, pp):
                    x = buy(on[k], at[k]["b"], t, False, pp=pp, **kw)
                    if x:
                        o.append(x)
                    break
        return o
    print(f"\n## Polymarket release-day bets: {len(S)} markets in {len({on[k]['ev_slug'] for k in S})} events\n\n" + HEAD)
    _line("AI release-day bets (Polymarket): No where Yes is 10-50c after the first third of the market's life",
          rb(lambda f, h, pp: f >= .33 and h > 24 and .10 <= pp < .50), 260, log)
    _line("release-day No, same, 4c extra", rb(lambda f, h, pp: f >= .33 and h > 24 and .10 <= pp < .50, extra=0.04), 260)
    _line("release-day No, Yes 3-10c, any time", rb(lambda f, h, pp: h > 24 and .03 <= pp < .10), 260)


if __name__ == "__main__":
    a = sys.argv[1] if len(sys.argv) > 1 else ""
    cmd, _, arg = a.partition("-")
    if cmd == "kscan":
        kscan()
    elif cmd == "lb":
        lb_fetch()
    elif cmd == "check":
        check()
    elif cmd == "comb":
        ms, tp = lb_markets()
        R = looks_lb(ms, tp, lag=int(arg or LAG))
        comb(ms, tp, R, f"all leaderboard markets, boards dated {int(arg or LAG)}+ days before the look")
    elif cmd == "model":
        ms, tp = lb_markets()
        R = with_chance(ms, looks_lb(ms, tp, lag=int(arg or LAG)))
        model_report(ms, tp, R)
    elif cmd == "report":
        report(log=len(sys.argv) > 2 and sys.argv[2] == "log")
    elif cmd == "kcheck":
        k_check()
    elif cmd == "use":
        use_report(log=len(sys.argv) > 2 and sys.argv[2] == "log")
    elif cmd == "usrc":
        usrc()
    elif cmd == "orfind":
        orfind()
    elif cmd == "orshare":
        orshare()
    elif cmd == "orparams":
        orparams()
    elif cmd == "orday":
        orday()
    elif cmd == "orlive":
        orlive()
    elif cmd == "klist":
        klist(PICKS.get(arg, arg) or ARENA_K)
    elif cmd == "ktapes":
        ktapes(PICKS.get(arg, arg) or ARENA_K)
    elif cmd == "kall":
        klist(PICKS.get(arg, arg) or ARENA_K)
        ktapes(PICKS.get(arg, arg) or ARENA_K)
    else:
        print(__doc__)
