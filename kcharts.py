"""Kalshi's weekly chart markets (Spotify, Billboard, Netflix top 10 ...) vs the public daily charts. Paper research.

  python3 kcharts.py series    # probe kch_series: which chart series Kalshi runs
  python3 kcharts.py list      # probe kch_list: every settled market of those series -> bt_cache/kch/markets.json.gz
"""
import collections, datetime as dt, os, re, sys, time
from concurrent.futures import ThreadPoolExecutor

import bot, khouse, kmentions as km, yesno

ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(ROOT, "bt_cache", "kch")
MK = os.path.join(CACHE, "markets.json.gz")
kget, rj, wj = yesno.kget, khouse.rj, khouse.wj
WORDS = re.compile(r"spotify|billboard|netflix|song|album|chart|hot 100|top 10|top show|top movie|streaming|apple music|"
                   r"youtube|tiktok|rotten|box office|luminate|artist|grammy|podcast|twitch|steam|app store|imdb|metacritic|nielsen", re.I)


def chart_series():
    out, seen = [], set()
    for p in ({"category": "Entertainment"}, {"category": "Culture"}, {"category": "Music"}, {"category": "Movies"}, {"category": "TV"}, {}):
        try:
            r = kget("/series", p)
        except Exception as e:
            print(f"  /series {p} failed: {str(e)[:120]}", flush=True)
            continue
        got = r.get("series") or []
        print(f"  /series {p}: {len(got)} series, categories {collections.Counter(str(s.get('category')) for s in got).most_common(20)}", flush=True)
        for s in got:
            tk = str(s.get("ticker") or "")
            txt = f"{tk} {s.get('title') or ''} {' '.join(s.get('tags') or [])}"
            if tk and tk not in seen and (WORDS.search(txt) or str(s.get("category")) in ("Entertainment", "Culture", "Music")):
                seen.add(tk)
                out.append(s)
    return out


def do_series():
    ser = chart_series()
    print("chart-like series:", len(ser), flush=True)
    print(collections.Counter((s.get("category"), s.get("frequency")) for s in ser).most_common(30), flush=True)
    for s in sorted(ser, key=lambda s: (str(s.get("category")), str(s.get("frequency")), s["ticker"])):
        if WORDS.search(f"{s['ticker']} {s.get('title')}") or s.get("frequency") in ("weekly", "daily"):
            print(f"  {s.get('category')} | {s.get('frequency')} | {s['ticker']} | {str(s.get('title'))[:90]} | {s.get('tags')}", flush=True)


def do_list(pick=None):
    os.makedirs(CACHE, exist_ok=True)
    have = rj(MK, None) or {"series": {}, "markets": {}}
    ser = [s for s in chart_series() if (re.search(pick, s["ticker"], re.I) if pick else
                                         (s.get("frequency") in ("weekly", "daily", "monthly") and str(s.get("category")) == "Entertainment"))]
    print("series to list:", len(ser), flush=True)
    for s in ser:
        have["series"][s["ticker"]] = {"title": str(s.get("title") or "")[:120], "cat": s.get("category"), "freq": s.get("frequency"),
                                       "fee": [s.get("fee_type"), s.get("fee_multiplier")], "tags": s.get("tags"),
                                       "src": [x.get("url") for x in (s.get("settlement_sources") or []) if isinstance(x, dict)][:3]}
    with ThreadPoolExecutor(4) as ex:
        for s, ok, n in ex.map(km.series_markets, sorted(x["ticker"] for x in ser)):
            have["markets"].update(ok)
            have["series"][s]["n"] = len(ok)
    wj(MK, have)
    ms = list(have["markets"].values())
    by = collections.defaultdict(list)
    for m in ms:
        by[m["s"]].append(m)
    d = lambda t: dt.datetime.utcfromtimestamp(t).strftime("%Y-%m-%d")
    print(f"settled markets {len(ms)}, events {len({m['ev'] for m in ms})}", flush=True)
    print("\n| series | title | freq | markets | events | first | last | yes won | middle volume | total volume | middle life days | source |")
    for s, v in sorted(by.items(), key=lambda kv: -sum(m["vol"] for m in kv[1]))[:120]:
        vols = sorted(m["vol"] for m in v)
        life = sorted((m["close"] - m["open"]) / 86400 for m in v)
        i = have["series"][s]
        print(f"| {s} | {i['title'][:50]} | {i['freq']} | {len(v)} | {len({m['ev'] for m in v})} | {d(min(m['close'] for m in v))} | "
              f"{d(max(m['close'] for m in v))} | {sum(m['res'] == 'yes' for m in v)} | {vols[len(vols) // 2]:.0f} | {sum(vols):.0f} | "
              f"{life[len(life) // 2]:.1f} | {i['src']} |", flush=True)
    for s, v in sorted(by.items(), key=lambda kv: -sum(m["vol"] for m in kv[1]))[:25]:
        m = max(v, key=lambda m: m["vol"])
        print("EX", s, {k: m[k] for k in ("t", "q", "w", "res", "vol")}, "| RULE", m["rule"][:300], flush=True)


UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"


def raw(url, n=40, extra=None):
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/json,text/tab-separated-values,*/*",
                                               "Accept-Language": "en-US,en;q=0.9", **(extra or {})})
    for i in range(4):
        try:
            with urllib.request.urlopen(req, timeout=n) as r:
                return r.read().decode("utf-8", "replace")
        except Exception as e:
            if i == 3 or "HTTP Error 4" in str(e):
                raise
            time.sleep(3 + 3 * i)


def do_peek():
    """which free chart sources answer from here"""
    for u in ("https://www.netflix.com/tudum/top10/data/all-weeks-countries.tsv",
              "https://www.netflix.com/tudum/top10/data/all-weeks-global.tsv",
              "https://flixpatrol.com/top10/netflix/united-states/2026-11-05/",
              "https://flixpatrol.com/top10/netflix/united-states/",
              "https://flixpatrol.com/top10/netflix/united-states/2026-45/",
              "https://www.netflix.com/tudum/top10/united-states/tv?week=2026-11-08",
              "https://kworb.net/spotify/country/us_daily.html",
              "https://kworb.net/youtube/",
              "https://charts.youtube.com/charts/TopArtists/us/daily"):
        try:
            s = raw(u, 40)
        except Exception as e:
            print("FAIL", u, str(e)[:150], flush=True)
            continue
        print("OK", u, len(s), flush=True)
        if u.endswith(".tsv"):
            L = s.split("\n")
            print("  head", L[:3], flush=True)
            us = [x for x in L if x.startswith("United States")]
            print("  US rows", len(us), us[:12], flush=True)
            print("  last", L[-3:], flush=True)
        else:
            t = re.sub(r"\s+", " ", re.sub(r"<script.*?</script>|<style.*?</style>", " ", s, flags=re.S))
            t = re.sub(r"<[^>]+>", "|", t)
            t = re.sub(r"(\|\s*)+", "| ", t)
            i = max(0, t.find("TOP 10"))
            print("  text", t[i:i + 2500], flush=True)


def do_peek2():
    """a daily Netflix US top 10 the bot can read, today and for past days"""
    for u in ("https://www.the-numbers.com/netflix-top-10",
              "https://www.the-numbers.com/netflix-top-10/2026/11/05",
              "https://www.the-numbers.com/netflix-top-10/tv-shows/2026/11/05",
              "https://www.whats-on-netflix.com/most-popular/",
              "https://www.whats-on-netflix.com/most-popular/top-10-tv-shows-on-netflix/",
              "https://web.archive.org/web/20261105120000/https://flixpatrol.com/top10/netflix/united-states/",
              "https://archive.org/wayback/available?url=flixpatrol.com/top10/netflix/united-states/2026-11-05/&timestamp=20261106",
              "https://web.archive.org/cdx/search/cdx?url=flixpatrol.com/top10/netflix/united-states/*&from=20261001&limit=40&output=json&filter=statuscode:200",
              "https://flixpatrol.com/top10/netflix/united-states/2026-11-05/",
              "https://www.justwatch.com/us/provider/netflix?sort_by=trending_7_day",
              "https://top10.netflix.com/united-states/tv",
              "https://www.netflix.com/tudum/top10/united-states/tv"):
        try:
            s = raw(u, 50, {"Referer": "https://www.google.com/", "Accept-Encoding": "identity"})
        except Exception as e:
            print("FAIL", u, str(e)[:150], flush=True)
            continue
        print("OK", u, len(s), flush=True)
        t = re.sub(r"\s+", " ", re.sub(r"<script.*?</script>|<style.*?</style>", " ", s, flags=re.S))
        t = re.sub(r"<[^>]+>", "|", t)
        t = re.sub(r"(\|\s*)+", "| ", t)
        i = max(0, min([x for x in (t.find("Rank"), t.find("TOP 10"), t.find("Top 10")) if x >= 0] or [0]))
        print("  text", t[i:i + 1800], flush=True)


TAPE_RX = "KXNETFLIX|KXTOPSONG|KXTOPALBUM|KXALBUMDEBUT|KXYTVIEWSW|KXALBUMEQUIV"
NFX = os.path.join(CACHE, "netflix.json.gz")


def do_tapes(pick=None):
    """probe kch_tapes[-regex]: hourly bid/ask + every trade of the picked series' settled markets -> bt_cache/kch/tapes_<series>.json.gz"""
    have = (rj(MK, {}) or {}).get("markets") or {}
    rx = re.compile(pick or TAPE_RX)
    by = collections.defaultdict(list)
    for m in have.values():
        if rx.search(m["s"]) and m["vol"] >= 100:
            by[m["s"]].append(m)
    t0 = time.time()
    for s, ms in sorted(by.items(), key=lambda kv: -sum(m["vol"] for m in kv[1])):
        path = os.path.join(CACHE, f"tapes_{s}.json.gz")
        got = rj(path, {}) or {}
        todo = [m for m in ms if m["t"] not in got]
        for i in range(0, len(todo), 300):
            with ThreadPoolExecutor(8) as ex:
                for tk, d in ex.map(km.tape_one, todo[i:i + 300]):
                    got[tk] = d
            wj(path, got)
        print(f"{s}: {len(got)} of {len(ms)} markets, {sum(len(d['tr']) for d in got.values())} trades, "
              f"{sum(1 for d in got.values() if not d['c'])} without quotes, {sum(1 for d in got.values() if not d['full'])} cut short "
              f"({time.time() - t0:.0f}s)", flush=True)


def do_netflix():
    """probe kch_netflix: Netflix's own weekly top 10 lists (US by country file, plus global with hours) -> bt_cache/kch/netflix.json.gz"""
    out = {"us": [], "global": []}
    L = raw("https://www.netflix.com/tudum/top10/data/all-weeks-countries.tsv", 120).split("\n")
    for x in L[1:]:
        p = x.rstrip("\r").split("\t")
        if len(p) >= 8 and p[1] == "US":
            out["us"].append([p[2], p[3], int(p[4]), p[5], p[6], int(p[7] or 0)])
    L = raw("https://www.netflix.com/tudum/top10/data/all-weeks-global.tsv", 120).split("\n")
    for x in L[1:]:
        p = x.rstrip("\r").split("\t")
        if len(p) >= 9:
            out["global"].append([p[0], p[1], int(p[2]), p[3], p[4], int(p[5] or 0), int(p[7] or 0), int(p[8] or 0)])
    os.makedirs(CACHE, exist_ok=True)
    wj(NFX, out)
    print("US rows", len(out["us"]), "global rows", len(out["global"]), "weeks", out["us"][-1][0], "to", out["us"][0][0])


def do_peek3():
    """how does whats-on-netflix load a past day's top 10?"""
    s = raw("https://www.whats-on-netflix.com/most-popular/", 60, {"Referer": "https://www.google.com/", "Accept-Encoding": "identity"})
    print("len", len(s))
    for m in re.finditer(r"<script[^>]*src=[\"']([^\"']+)", s):
        print("SRC", m.group(1))
    for kw in ("admin-ajax", "wp-json", "fetch(", "ajaxurl", "top10", "top-10", "date", "country", "nonce", "endpoint", "api"):
        for m in list(re.finditer(re.escape(kw), s))[:6]:
            print("KW", kw, "|", re.sub(r"\s+", " ", s[max(0, m.start() - 160):m.start() + 260]))
    for m in re.finditer(r"<script(?![^>]*src)[^>]*>(.*?)</script>", s, flags=re.S):
        b = m.group(1)
        if re.search(r"top|date|fetch|ajax", b, re.I) and len(b) > 200:
            print("INLINE", len(b), "|", re.sub(r"\s+", " ", b)[:3000])


# ================================================================ analysis
HOURS = (144, 120, 96, 72, 48, 24, 12, 3)
BANDS = ((0.03, .10), (.10, .25), (.25, .50), (.50, .75), (.75, .90), (.90, .97))
fee = km.fee


def load(pick=TAPE_RX):
    """-> markets, tapes of the picked series. Repairs the hourly quotes that come 100 times too small (see kmentions.load)."""
    import glob
    rx = re.compile(pick)
    ms = {t: m for t, m in ((rj(MK, {}) or {}).get("markets") or {}).items() if rx.search(m["s"])}
    tp = {}
    for f in sorted(glob.glob(os.path.join(CACHE, "tapes_*.json.gz"))):
        for tk, v in (rj(f, {}) or {}).items():
            if tk not in ms:
                continue
            vals = [x for c in v["c"] for x in c[1:3] if x is not None]
            if vals and max(vals) <= 0.0101 and v["tr"] and max(t[1] for t in v["tr"]) > 20:
                for c in v["c"]:
                    c[1] = None if c[1] is None else round(c[1] * 100, 4)
                    c[2] = None if c[2] is None else round(c[2] * 100, 4)
            v["tr"].sort()
            tp[tk] = v
    return ms, tp


def looks(ms, tp, hours=HOURS):
    """One row per market and look time (hours before the event's FIRST close: a market's own close can leak the result).
    Each row also knows: was this title last time's winner in its series (inc), was it listed last time (old),
    is it the event's favourite at that hour (fav), and the sum of all asks in its event (book)."""
    evs = collections.defaultdict(list)
    for m in ms.values():
        evs[m["ev"]].append(m)
    first = {e: ev_close(L) for e, L in evs.items()}
    by_s = collections.defaultdict(list)
    for e, L in evs.items():
        by_s[L[0]["s"]].append(e)
    prev = {}
    for s, es in by_s.items():
        es.sort(key=lambda e: first[e])
        for a, b in zip(es, es[1:]):
            prev[b] = a
    rows = []
    for e, L in evs.items():
        p = prev.get(e)
        pw = {km.norm(m["w"]) for m in evs[p] if m["res"] == "yes"} if p else set()
        pl = {km.norm(m["w"]) for m in evs[p]} if p else set()
        for h in hours:
            t = first[e] - h * 3600
            got = []
            for m in L:
                v = tp.get(m["t"])
                if not v or not v["c"] or t < m["open"] + 3600:
                    continue
                c = None
                for x in v["c"]:
                    if x[0] > t:
                        break
                    c = x
                if not c or c[1] is None or c[2] is None or t - c[0] > 3 * 3600:
                    continue
                got.append({"tk": m["t"], "s": m["s"], "ev": e, "h": h, "t": t, "bid": c[1], "ask": c[2], "yes": m["res"] == "yes",
                            "vol": m["vol"], "w": m["w"], "inc": km.norm(m["w"]) in pw, "old": km.norm(m["w"]) in pl, "has_prev": bool(p)})
            if not got:
                continue
            top = max(got, key=lambda r: r["bid"] + r["ask"])
            book = sum(r["ask"] for r in got)
            for r in got:
                r["fav"] = r is top
                r["book"] = book
                r["n"] = len(got)
            rows += got
    return rows


def line(name, b):
    if not b:
        return f"{name:54s} none"
    b = sorted(b, key=lambda x: x["t"])
    h = len(b) // 2
    return (f"{name:54s} bets {len(b):5d} ev {len({x['ev'] for x in b}):4d} won {sum(1 for x in b if x['pay'] > 0):5d} "
            f"per100 {km.per100(b):+7.2f} halves {km.per100(b[:h]):+7.2f} {km.per100(b[h:]):+7.2f} avgpx {sum(x['p'] for x in b) / len(b):.2f}")


def run(pick="KXNETFLIX", score=False):
    ms, tp = load(pick)
    rows = [r for r in looks(ms, tp) if km.ok(r, 0.10)]
    print(f"markets {len(ms)}, with tapes {len(tp)}, events {len({m['ev'] for m in ms.values()})}, rows {len(rows)}")
    cl = collections.Counter()
    evs = collections.defaultdict(list)
    for m in ms.values():
        evs[m["ev"]].append(m["close"])
    for L in evs.values():
        cl[round((max(L) - min(L)) / 3600)] += 1
    print("hours between first and last close inside an event:", sorted(cl.items())[:12])
    tries = 0
    for ser in sorted({r["s"] for r in rows}) + ["ALL"]:
        R = [r for r in rows if ser == "ALL" or r["s"] == ser]
        print(f"\n=== {ser}")
        for h in HOURS:
            H = [r for r in R if r["h"] == h]
            print(line(f"always Yes {h}h", km.yes_bets(H)))
            print(line(f"always No  {h}h", km.no_bets(H)))
            tries += 2
        if ser != "ALL":
            continue
        for h in (120, 72, 24):
            H = [r for r in R if r["h"] == h]
            for lo, hi in BANDS:
                B = [r for r in H if lo <= (r["bid"] + r["ask"]) / 2 < hi]
                print(line(f"  {h}h Yes at {lo:.2f}-{hi:.2f}", km.yes_bets(B)))
                print(line(f"  {h}h No  at {lo:.2f}-{hi:.2f}", km.no_bets(B)))
                tries += 2
            for nm, f in (("favourite", lambda r: r["fav"]), ("not favourite", lambda r: not r["fav"]),
                          ("last winner", lambda r: r["inc"]), ("listed before, not winner", lambda r: r["old"] and not r["inc"]),
                          ("new title", lambda r: r["has_prev"] and not r["old"]),
                          ("last winner and favourite", lambda r: r["inc"] and r["fav"]),
                          ("last winner, not favourite", lambda r: r["inc"] and not r["fav"]),
                          ("new title and favourite", lambda r: r["has_prev"] and not r["old"] and r["fav"]),
                          ("asks add up to 1.10+", lambda r: r["book"] >= 1.10), ("asks add up under 1.03", lambda r: r["book"] < 1.03)):
                B = [r for r in H if f(r)]
                print(line(f"  {h}h Yes {nm}", km.yes_bets(B)))
                print(line(f"  {h}h No  {nm}", km.no_bets(B)))
                tries += 2
    print("tries", tries)
    return rows


WON = "https://www.whats-on-netflix.com/most-popular/"


def do_peek4():
    """the date form of whats-on-netflix's daily top 10, and the US block"""
    import urllib.parse, urllib.request
    H = {"Referer": WON, "Accept-Encoding": "identity"}
    s = raw(WON, 60, H)
    i = s.find('id="datepicker"')
    a = s.rfind("<form", 0, i)
    print("FORM", re.sub(r"\s+", " ", s[a if a >= 0 else max(0, i - 800):i + 900]))
    j = s.find('id="won-mp-country-US"')
    print("US BLOCK", re.sub(r"\s+", " ", s[j - 300:j + 5000]))
    names = re.findall(r'<input[^>]*name="([^"]+)"', s[a if a >= 0 else 0:i + 900])
    print("input names", names)

    def title(x):
        return re.findall(r"won-mp-chart-title\">([^<]+)", x)[:3]
    print("today:", title(s))
    for nm in set(names + ["date", "d", "won_mp_date", "chart_date"]):
        for val in ("11/05/2026", "2026-11-05"):
            u = WON + "?" + urllib.parse.urlencode({nm: val})
            try:
                print("GET", nm, val, title(raw(u, 40, H)), flush=True)
            except Exception as e:
                print("GET", nm, val, "FAIL", str(e)[:80], flush=True)
            try:
                req = urllib.request.Request(WON, data=urllib.parse.urlencode({nm: val}).encode(), headers={"User-Agent": UA, **H})
                with urllib.request.urlopen(req, timeout=40) as r:
                    print("POST", nm, val, title(r.read().decode("utf-8", "replace")), flush=True)
            except Exception as e:
                print("POST", nm, val, "FAIL", str(e)[:80], flush=True)


DAILY = os.path.join(CACHE, "daily.json.gz")


def parse_daily(s):
    """-> {"us": [[heading, [[rank, title, tv|movie], ...]], ...], "global": [...]} from one whats-on-netflix day page."""
    out = {}
    a, b = s.find("Global charts"), s.find("Most popular by country")
    u = s.find('id="won-mp-country-US"')
    v = s.find('id="won-mp-country-', u + 30) if u >= 0 else -1
    for key, x in (("global", s[a:b] if 0 <= a < b else ""), ("us", s[u:v if v > u else u + 60000] if u >= 0 else "")):
        secs = []
        for part in re.split(r'<h4 class="won-mp-chart-title"[^>]*>', x)[1:]:
            head = re.sub(r"<[^>]+>", "", part.split("</h4>")[0]).strip()
            rows = [[int(r), t, k] for r, t, k in re.findall(
                r'won-mp-rank-col">(\d+)</td>.*?data-won-mp-trend-title="([^"]*)"[^>]*?data-won-mp-trend-type="([^"]*)"', part, flags=re.S)]
            secs.append([head, rows])
        out[key] = secs
    return out


def do_daily(first="2025-01-01"):
    """probe kch_daily: Netflix's daily top 10 (US + global) for every day since `first`, from whats-on-netflix -> bt_cache/kch/daily.json.gz"""
    import html
    os.makedirs(CACHE, exist_ok=True)
    have = rj(DAILY, {}) or {}
    d, end, t0, bad = dt.date.fromisoformat(first), dt.datetime.now(dt.timezone.utc).date() - dt.timedelta(days=1), time.time(), 0
    miss = 0
    while d <= end and time.time() - t0 < 200 * 60 and bad < 60:
        k = d.isoformat()
        if k not in have:
            try:
                s = raw(f"{WON}?dateselect={d.month:02d}/{d.day:02d}/{d.year}", 60, {"Referer": WON, "Accept-Encoding": "identity"})
                want = f"{d.strftime('%b')} {d.day}"
                tt = re.findall(r"Most popular by country — ([A-Za-z]+ \d+)", s)
                p = parse_daily(html.unescape(s))
                if not tt and len(s) > 100000:
                    miss += 1                         # a real page without the country charts: the site has no list for that day
                    if miss % 20 == 1:
                        print("  no country charts on", k, len(s), [h for h, _ in p["global"]][:3], flush=True)
                elif not tt or tt[0] != want or not any(r for _, r in p["us"]):
                    bad += 1
                    print("  odd page", k, tt[:1], [(h, len(r)) for h, r in p["us"]][:4], len(s), flush=True)
                    time.sleep(90)
                else:
                    have[k] = p
            except Exception as e:
                bad += 1
                print("  failed", k, str(e)[:100], flush=True)
                time.sleep(60)
            time.sleep(2.5)
            if len(have) % 40 == 0:
                wj(DAILY, have)
                print(f"  {len(have)} days, at {k} ({time.time() - t0:.0f}s)", flush=True)
        d += dt.timedelta(days=1)
    wj(DAILY, have)
    ks = sorted(have)
    print("days", len(ks), ks[:1], ks[-1:], "odd or failed", bad, "days without country charts", miss)
    mon = collections.Counter(k[:7] for k in ks)
    print("days per month", sorted(mon.items()))
    for k in ks[-1:] + ks[:1]:
        for key in ("us", "global"):
            for h, r in have[k][key]:
                print(k, key, h, "|", r[:10])


def ev_close(L):
    """The event's planned close: the close time most of its markets share (a doubled market that Kalshi pulls closes days early)."""
    return collections.Counter(m["close"] for m in L).most_common(1)[0][0]


# ---------------------------------------------------------------- the daily top 10 as outside knowledge
DAY = 86400
KNOWN_H = 30               # a list dated D counts as readable from D + 30 hours UTC (the day after, 06:00)


def tkey(w):
    w = re.sub(r"\(.*?\)", "", str(w).lower())
    w = re.split(r":\s*(season|limited series|s\d+\b|part \d|volume|vol\.|book|chapter \d)", w)[0]
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", w.replace("&", "and"))).strip()


def day_lists(kind):
    """{date: {title key: rank}} of the US daily top 10; kind 'tv' or 'movie'."""
    out = {}
    for k, v in (rj(DAILY, {}) or {}).items():
        for h, rows in v.get("us") or []:
            if rows and (("TV" in h) == (kind == "tv")):
                out[dt.date.fromisoformat(k)] = {tkey(t): r for r, t, _ in rows}
    return out


def week_of(ev):
    """Monday of the viewing week from an event ticker like KXNETFLIXRANKSHOW-26NOV09 (list out the day after that date)."""
    d = dt.datetime.strptime(ev.rsplit("-", 1)[1], "%y%b%d").date()
    return d - dt.timedelta(days=7)


def points(lists, mon, t, lag):
    """Points per title from the week's daily lists readable at time t (10 for a day at #1 ... 1 for #10), the count of
    lists used, and the newest list's #1."""
    pts, n, top = collections.Counter(), 0, None
    for i in range(7):
        d = mon + dt.timedelta(days=i + lag)
        if dt.datetime(d.year, d.month, d.day, tzinfo=dt.timezone.utc).timestamp() + KNOWN_H * 3600 > t:
            break
        L = lists.get(d)
        if not L:
            continue
        n += 1
        for k, r in L.items():
            pts[k] += 11 - r
            if r == 1:
                top = k
    return pts, n, top


def feat(pts, n, top, k):
    """The cell a title sits in: lists so far, leader or not, how clear, and who holds today's #1."""
    order = sorted(pts.values(), reverse=True) + [0, 0]
    mine = pts.get(k, 0)
    lead = mine > 0 and mine == order[0]
    gap = (mine - (order[1] if lead else order[0])) / (10.0 * max(1, n))
    g = 0 if abs(gap) < 0.1 else 1 if abs(gap) < 0.3 else 2
    nb = 1 if n <= 2 else 2 if n <= 4 else 3 if n <= 6 else 4
    return (nb, "lead" if lead else "chase" if mine > 0 else "absent", g, top == k)


def daily_rows(pick="KXNETFLIXRANK(SHOW|MOVIE)$", lag=1, step_h=6):
    """Every `step_h` hours of every US #1 market: the Kalshi bid/ask next to the title's cell from the daily lists."""
    ms, tp = load(pick)
    evs = collections.defaultdict(list)
    for m in ms.values():
        evs[m["ev"]].append(m)
    L = {"tv": day_lists("tv"), "movie": day_lists("movie")}
    rows = []
    for e, M in evs.items():
        kind = "tv" if "SHOW" in e else "movie"
        mon, T = week_of(e), ev_close(M)
        keys = collections.Counter(tkey(m["w"]) for m in M)
        op = min(m["open"] for m in M)
        t = (op // 3600 + 2) * 3600
        while t < T - 3600:
            pts, n, top = points(L[kind], mon, t, lag)
            if n:
                for m in M:
                    k = tkey(m["w"])
                    v = tp.get(m["t"])
                    if keys[k] > 1 or not v or not v["c"] or m["close"] != T:
                        continue
                    c = None
                    for x in v["c"]:
                        if x[0] > t:
                            break
                        c = x
                    if not c or c[1] is None or c[2] is None or t - c[0] > 3 * 3600:
                        continue
                    rows.append({"tk": m["t"], "ev": e, "t": t, "bid": c[1], "ask": c[2], "yes": m["res"] == "yes", "w": m["w"],
                                 "f": feat(pts, n, top, k), "n": n, "kind": kind, "pts": pts.get(k, 0), "left": (T - t) / 3600})
            t += step_h * 3600
    return rows


def with_chance(rows, min_seen=15):
    """Walk forward: each event's chance per cell comes only from events that closed before it opened (a week earlier)."""
    evs = sorted({r["ev"] for r in rows}, key=lambda e: week_of(e))
    by = collections.defaultdict(list)
    for r in rows:
        by[r["ev"]].append(r)
    cnt, out, done = collections.defaultdict(lambda: [0, 0]), [], []
    for e in evs:
        w = week_of(e)
        while done and week_of(done[0]) < w:           # only weeks that finished before this one started
            for r in by[done.pop(0)]:
                c = cnt[r["f"]]
                c[0] += r["yes"]
                c[1] += 1
        for r in by[e]:
            y, n = cnt[r["f"]]
            if n >= min_seen:
                out.append(dict(r, q=(y + 1) / (n + 2), seen=n))
        done.append(e)
    return out


def first_bets(rows, gap=0.10, extra=0.0, side="both", lo=0.03, hi=0.97, max_gap=0.15):
    """One bet per market: the first look where the chance is `gap` above the asking price (Yes) or below the bid (No)."""
    out, used = [], set()
    for r in sorted(rows, key=lambda r: r["t"]):
        if r["tk"] in used or r["ask"] - r["bid"] > max_gap or r["bid"] < 0.005:
            continue
        b = None
        if side in ("both", "yes") and lo <= r["ask"] <= hi and r["q"] - r["ask"] >= gap:
            p = r["ask"] + extra
            b = {"cost": p + fee(p), "pay": 1.0 if r["yes"] else 0.0, "p": p, "side": "yes"}
        elif side in ("both", "no") and lo <= 1 - r["bid"] <= hi and r["bid"] - r["q"] >= gap:
            p = 1 - r["bid"] + extra
            b = {"cost": p + fee(p), "pay": 0.0 if r["yes"] else 1.0, "p": p, "side": "no"}
        if b:
            used.add(r["tk"])
            b.update(pnl=b["pay"] - b["cost"], ev=r["ev"], t=r["t"], tk=r["tk"], w=r["w"], q=r["q"], f=r["f"], kind=r["kind"], left=r["left"])
            out.append(b)
    return out


def daily_run(pick="KXNETFLIXRANK(SHOW|MOVIE)$"):
    for lag in (0, 1):
        rows = daily_rows(pick, lag)
        last = {}
        for r in rows:                                   # does the points leader of the full week win?
            if r["n"] == 7:
                last.setdefault(r["ev"], []).append(r)
        hit = sum(1 for L in last.values() if any(r["yes"] and r["f"][1] == "lead" for r in L))
        won = sum(1 for L in last.values() if any(r["yes"] for r in L))
        print(f"lag {lag}: rows {len(rows)}, events {len({r['ev'] for r in rows})}, weeks with all 7 lists {len(last)}, "
              f"winner listed {won}, winner is the points leader {hit}")
    rows = with_chance(daily_rows(pick, 1))
    print("rows with a chance", len(rows), "events", len({r["ev"] for r in rows}))
    cal = collections.defaultdict(lambda: [0, 0, 0.0, 0.0])
    for r in rows:
        c = cal[round(r["q"] * 10) / 10]
        c[0] += r["yes"]; c[1] += 1; c[2] += (r["bid"] + r["ask"]) / 2; c[3] += r["q"]
    print("how good is the chance? (chance bucket: rows, won share, model, Kalshi middle price)")
    for k in sorted(cal):
        y, n, p, q = cal[k]
        print(f"  {k:.1f}: {n:5d} won {y / n:.2f} model {q / n:.2f} price {p / n:.2f}")
    bs = lambda p, key: sum((r[key] if key == "q" else (r["bid"] + r["ask"]) / 2 - r["yes"]) ** 2 for r in rows) / len(rows)
    print("miss score (lower is better): model", round(sum((r["q"] - r["yes"]) ** 2 for r in rows) / len(rows), 4),
          "Kalshi price", round(sum(((r["bid"] + r["ask"]) / 2 - r["yes"]) ** 2 for r in rows) / len(rows), 4))
    for gap in (0.05, 0.10, 0.15, 0.25):
        for side in ("yes", "no", "both"):
            print(line(f"gap {gap} {side}", first_bets(rows, gap, side=side)))
    b = first_bets(rows, 0.10)
    for nm, f in (("tv", lambda x: x["kind"] == "tv"), ("movie", lambda x: x["kind"] == "movie"),
                  ("72h+ left", lambda x: x["left"] >= 72), ("24-72h left", lambda x: 24 <= x["left"] < 72), ("under 24h left", lambda x: x["left"] < 24),
                  ("leader", lambda x: x["f"][1] == "lead"), ("chaser", lambda x: x["f"][1] == "chase"), ("absent", lambda x: x["f"][1] == "absent")):
        print(line(f"  gap 0.10 both, {nm}", [x for x in b if f(x)]))
    print(line("gap 0.10 both +2c", first_bets(rows, 0.10, extra=0.02)))
    return rows


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "drun":
        daily_run()
        sys.exit(0)
    if len(sys.argv) > 1 and sys.argv[1].startswith("daily"):
        do_daily(sys.argv[1][6:] or "2025-01-01")
        sys.exit(0)
    if len(sys.argv) > 1 and sys.argv[1] == "peek4":
        do_peek4()
        sys.exit(0)
    if len(sys.argv) > 1 and sys.argv[1].startswith("run"):
        run(sys.argv[1][4:] or "KXNETFLIX")
        sys.exit(0)
    A1 = sys.argv[1] if len(sys.argv) > 1 else ""
    if A1.startswith("tapes"):
        do_tapes(A1[6:] or None)
        sys.exit(0)
    if A1 in ("netflix", "peek3"):
        {"netflix": do_netflix, "peek3": do_peek3}[A1]()
        sys.exit(0)
    if len(sys.argv) > 1 and sys.argv[1] == "peek2":
        do_peek2()
        sys.exit(0)
    if len(sys.argv) > 1 and sys.argv[1] == "peek":
        do_peek()
        sys.exit(0)
    a = sys.argv[1] if len(sys.argv) > 1 else "series"
    if a == "series":
        do_series()
    elif a.startswith("list"):
        do_list(a[5:] or None)
