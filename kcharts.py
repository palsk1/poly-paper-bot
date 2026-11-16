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
    with urllib.request.urlopen(req, timeout=n) as r:
        return r.read().decode("utf-8", "replace")


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


if __name__ == "__main__":
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
