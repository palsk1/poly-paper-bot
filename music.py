#!/usr/bin/env python3
"""Music chart bets (Billboard Hot 100 / Billboard 200 #1, first-week album units) vs outside chart data. Paper research.

  python3 music.py peek        # probe mus_peek: which outside music sources answer from GitHub Actions
  python3 music.py run         # the tables (see backtest/music.md)
"""
import collections, datetime as dt, json, os, re, sys, time

import kcharts as K

ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(ROOT, "bt_cache", "mus")
rj, wj, raw = K.rj, K.wj, K.raw


def get(url, n=60):
    """like kcharts.raw, but unpacks gzip bodies (Wayback passes the stored gzip through on id_ snapshots)."""
    import gzip as gz, urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": K.UA, "Accept": "text/html,application/json,*/*", "Accept-Language": "en-US,en;q=0.9"})
    for i in range(4):
        try:
            with urllib.request.urlopen(req, timeout=n) as r:
                b = r.read()
            if b[:2] == b"\x1f\x8b":
                b = gz.decompress(b)
            return b.decode("utf-8", "replace")
        except Exception as e:
            if i == 3 or "HTTP Error 4" in str(e):
                raise
            time.sleep(3 + 3 * i)


def text(s, n=1500, start=None):
    t = re.sub(r"\s+", " ", re.sub(r"<script.*?</script>|<style.*?</style>", " ", s, flags=re.S))
    t = re.sub(r"(\|\s*)+", "| ", re.sub(r"<[^>]+>", "|", t))
    i = max(0, t.find(start)) if start else 0
    return t[i:i + n]


def do_peek():
    for u, st in (("https://hitsdailydouble.com/sales_plus_streaming", "Building"),
                  ("https://hitsdailydouble.com/", "Building"),
                  ("https://hitsdailydouble.com/upcoming_releases", None),
                  ("http://web.archive.org/cdx/search/cdx?url=hitsdailydouble.com/sales_plus_streaming&from=2025&output=json&limit=40&filter=statuscode:200", None),
                  ("http://web.archive.org/cdx/search/cdx?url=hitsdailydouble.com/&from=2026&output=json&limit=40&filter=statuscode:200", None),
                  ("https://www.billboard.com/charts/hot-100/2026-11-14/", "1"),
                  ("https://www.billboard.com/charts/billboard-200/2026-11-14/", "1"),
                  ("https://kworb.net/itunes/", None),
                  ("https://kworb.net/spotify/country/us_daily.html", "Pos"),
                  ("https://rss.applemarketingtools.com/api/v2/us/music/most-played/50/songs.json", None),
                  ("https://rss.applemarketingtools.com/api/v2/us/music/most-played/50/albums.json", None),
                  ("https://kworb.net/aww/", None),
                  ("https://kworb.net/radio/", None)):
        try:
            s = raw(u, 40)
        except Exception as e:
            print("FAIL", u, str(e)[:150], flush=True)
            continue
        print("OK", u, len(s), flush=True)
        print("  ", text(s, 2500, st) if "cdx" not in u and "json" not in u else s[:2500], flush=True)
    for p in ({"tag_slug": "billboard", "closed": "false"}, {"tag_slug": "music", "closed": "false"}):
        try:
            s = raw("https://gamma-api.polymarket.com/events?limit=100&" + "&".join(f"{a}={b}" for a, b in p.items()), 40)
            ev = json.loads(s)
            print("POLY", p, len(ev), flush=True)
            for e in ev[:60]:
                print("   ", e.get("endDate"), round(float(e.get("volume") or 0)), e.get("slug"), flush=True)
        except Exception as e:
            print("FAIL poly", p, str(e)[:150], flush=True)


def do_hdd_peek():
    s = raw("https://hitsdailydouble.com/sales_plus_streaming", 60)
    hrefs = sorted(set(re.findall(r'href="([^"]+)"', s)))
    print("HREFS", [h for h in hrefs if re.search(r"chart|midweek|ytd|top|week", h, re.I)][:80], flush=True)
    i = s.find("Midweek")
    print("AROUND MIDWEEK", s[max(0, i - 600):i + 400], flush=True)
    for h in hrefs:
        if re.search(r"midweek", h, re.I):
            u = h if h.startswith("http") else "https://hitsdailydouble.com" + h
            try:
                t = raw(u, 60)
                print("MID OK", u, len(t), text(t, 3000, "Week"), flush=True)
            except Exception as e:
                print("MID FAIL", u, str(e)[:120], flush=True)
    for u in ("hitsdailydouble.com/sales_plus_streaming", "hitsdailydouble.com/midweek", "hitsdailydouble.com/midweek_20",
              "hitsdailydouble.com/chart/midweek", "hitsdailydouble.com/sales_plus_streaming*"):
        try:
            c = raw("http://web.archive.org/cdx/search/cdx?url=" + u + "&from=2024&output=json&collapse=digest&filter=statuscode:200&limit=3000", 120)
            rows = json.loads(c)[1:] if c.strip() else []
            print("CDX", u, len(rows), "first", rows[:1], "last", rows[-3:], flush=True)
            by = collections.Counter(r[1][:6] for r in rows)
            print("   per month", sorted(by.items()), flush=True)
            if "*" in u:
                print("   urls", collections.Counter(r[2] for r in rows).most_common(30), flush=True)
        except Exception as e:
            print("CDX FAIL", u, str(e)[:150], flush=True)
    for ts in ("20250110000505", "20250601000000", "20260301000000", "20260901000000"):
        try:
            t = raw(f"http://web.archive.org/web/{ts}id_/https://hitsdailydouble.com/sales_plus_streaming", 120)
            print("SNAP", ts, len(t), text(t, 1500, "Week Ending"), flush=True)
        except Exception as e:
            print("SNAP FAIL", ts, str(e)[:150], flush=True)


HITS = os.path.join(CACHE, "hits.json.gz")
CLICK = "Click to see if a preview of the song is available.|"


def parse_hits(html):
    """HITS chart page -> (week ending 'YYYY-MM-DD' or None, [[rank, artist, album, label, activity, albums, tea, sea]]).
    Midweek pages have only activity and albums (tea, sea = None)."""
    t = text(html, 10 ** 7)
    we = None
    m = re.search(r"Week Ending\| ([A-Z][a-z]+ \d{1,2}, \d{4})", t)
    if m:
        we = dt.datetime.strptime(m.group(1), "%B %d, %Y").date().isoformat()
    rows = []
    parts = t.split(CLICK)
    for k, ch in enumerate(parts[1:], 1):
        if "Activity|" in ch[:400]:
            break
        f = [x.strip() for x in ch.split("|")]
        f = [x for x in f if x != ""]
        if len(f) < 5:
            continue
        artist, album, label = f[0], f[1], f[2]
        nums = []
        for x in f[3:]:
            if re.fullmatch(r"[\d,]+", x):
                nums.append(int(x.replace(",", "")))
            elif re.fullmatch(r"--|-?\d+%|New|RE|\+?\d+%", x):
                nums.append(None)
            else:
                break
        pv = [x.strip() for x in parts[k - 1].split("|") if x.strip()]
        rank = int(pv[-1]) if pv and pv[-1].isdigit() else None
        vals = [x for x in nums]
        if len(vals) >= 5:      # activity, +/-, albums, tea, sea
            act, alb, tea, sea = vals[0], vals[2], vals[3], vals[4]
        elif len(vals) >= 2:
            act, alb, tea, sea = vals[0], vals[1], None, None
        else:
            continue
        rows.append([rank, artist, album, label, act, alb, tea, sea])
    return we, rows


def do_hits(first="2024-11-07"):
    """probe mus_hits: HITS final weekly top 50 and the midweek top 20 for every week (by week-ending Thursday) -> bt_cache/mus/hits.json.gz"""
    os.makedirs(CACHE, exist_ok=True)
    have = rj(HITS, None) or {"final": {}, "mid": {}, "snaps": {}}
    d = dt.date.fromisoformat(first)
    today = dt.date.today()
    while d <= today:
        for kind, path in (("final", "hits-top-50"), ("mid", "midweek-20")):
            k = d.isoformat()
            if k in have[kind] and have[kind][k][1]:
                continue
            try:
                h = get(f"https://hitsdailydouble.com/charts/{path}/{k}", 60)
                we, rows = parse_hits(h)
                have[kind][k] = [we, rows]
                print(kind, k, "page says", we, len(rows), "rows", rows[:2], flush=True)
            except Exception as e:
                print(kind, k, "FAIL", str(e)[:100], flush=True)
            time.sleep(0.5)
        d += dt.timedelta(days=7)
    wj(HITS, have)
    # when did each page change? Wayback snapshot times of the live pages, with the week each one showed
    for kind, path in (("final", "hits-top-50"), ("mid", "midweek-20")):
        try:
            c = raw(f"http://web.archive.org/cdx/search/cdx?url=hitsdailydouble.com/charts/{path}&from=2025&output=json&filter=statuscode:200&limit=5000", 120)
            rows = json.loads(c)[1:] if c.strip() else []
        except Exception as e:
            print("CDX FAIL", path, str(e)[:120], flush=True)
            rows = []
        print("CDX", path, len(rows), flush=True)
        got = have["snaps"].setdefault(kind, {})
        last = (None, None)
        for r in rows:
            ts, dig = r[1], r[5]
            if ts in got:
                last = (dig, got[ts])
                continue
            if dig == last[0]:
                got[ts] = last[1]
                continue
            try:
                h = get(f"http://web.archive.org/web/{ts}id_/https://hitsdailydouble.com/charts/{path}", 90)
                we, rr = parse_hits(h)
                got[ts] = [we, rr[:5]]
                print("  snap", kind, ts, we, rr[:1], flush=True)
            except Exception as e:
                print("  snap FAIL", ts, str(e)[:100], flush=True)
                got[ts] = None
            last = (dig, got[ts])
            time.sleep(0.3)
        wj(HITS, have)


# ================================================================ analysis (offline, on the price store)
MON = {m: i + 1 for i, m in enumerate("JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split())}
fee = lambda p: 0.07 * p * (1 - p)                                         # Kalshi taker fee per contract
TRIES = 70        # versions looked at in this dig (hours x price bands x sides, HITS-model variants, Spotify ranks)


def norm(x):
    import spotw
    return spotw.norm(x)


def quote(tp, tk, t, stale=3 * 3600):
    """(yes bid, yes ask) of the last hourly candle at or before t, None if older than `stale`."""
    v, c = tp.get(tk), None
    if not v:
        return None
    for x in v["c"]:
        if x[0] > t:
            break
        c = x
    if not c or c[1] is None or c[2] is None or t - c[0] > stale:
        return None
    return c[1], c[2]


def rung(m):
    """the 'above X' number of a Kalshi album-units market"""
    x = re.search(r"above ([\d,\.]+)\s*(K)?", m["q"])
    if not x:
        return None
    v = float(x.group(1).replace(",", ""))
    return v * 1000 if x.group(2) else v


def week_end(ev):
    """KXALBUMEQUIV-FRE26NOV12 -> date(2026, 11, 12), the Thursday the tracking week ends"""
    mm = re.search(r"(\d\d)([A-Z]{3})(\d\d)$", ev)
    return dt.date(2000 + int(mm.group(1)), MON[mm.group(2)], int(mm.group(3))) if mm else None


def hits_row(rows, album, artist):
    a = norm(album)
    for r in rows:
        b = norm(r[2])
        if b == a or (len(a) > 5 and (b.startswith(a) or a.startswith(b)) and norm(artist)[:5] in norm(r[1])):
            return r
    return None


def album_events(series=("KXALBUMEQUIV", "KXPUREALBUMS")):
    """Kalshi album ladders with the HITS midweek and final number of the same album and week."""
    ms, tp = K.load("|".join(series))
    h = rj(HITS, {}) or {"final": {}, "mid": {}}
    ev = collections.defaultdict(list)
    for m in ms.values():
        ev[(m["s"], m["ev"])].append(m)
    out = []
    for (s, e), L in ev.items():
        wd = week_end(e)
        x = re.match(r"Will (.*) by (.*?) have above", L[0]["q"])
        if not wd or not x:
            continue
        col = 4 if s == "KXALBUMEQUIV" else 5                     # activity (all units) or albums (pure sales)
        M = (h["mid"].get(wd.isoformat()) or [None, []])[1]
        F = (h["final"].get(wd.isoformat()) or [None, []])[1]
        mr, fr = hits_row(M, x.group(1), x.group(2)), hits_row(F, x.group(1), x.group(2))
        ys = [rung(m) for m in L if m["res"] == "yes" and rung(m)]
        ns = [rung(m) for m in L if m["res"] == "no" and rung(m)]
        out.append(dict(s=s, e=e, we=wd, L=L, close=min(m["close"] for m in L), mid=mr[col] if mr else None,
                        fin=fr[col] if fr else None, lo=max(ys) if ys else 0, hi=min(ns) if ns else None))
    return out, ms, tp


def mid_model(E, tp, look_h=30):
    """HITS midweek number x (Luminate / HITS ratio of the OTHER albums) -> chance per rung, vs Kalshi's price.
    Signal time: Friday 06:00 UTC after the tracking week (the midweek page was up by Thursday ~23:00-Fri 03:00 UTC
    in every Wayback copy we have)."""
    import math
    def ratios(skip, s):
        return [math.log(math.sqrt(x["lo"] * x["hi"]) / x["mid"]) for x in E
                if x["e"] != skip and x["s"] == s and x["mid"] and x["hi"] and x["lo"] > 0]
    bets, sq = [], collections.defaultdict(lambda: [0, 0.0, 0.0])
    for x in E:
        if not x["mid"]:
            continue
        rs = ratios(x["e"], x["s"])
        if len(rs) < 8:
            continue
        t = dt.datetime(x["we"].year, x["we"].month, x["we"].day, tzinfo=dt.timezone.utc).timestamp() + look_h * 3600
        for m in x["L"]:
            T = rung(m)
            p = quote(tp, m["t"], t) if T else None
            if not p:
                continue
            y = m["res"] == "yes"
            pr = sum(1 for r in rs if x["mid"] * math.exp(r) > T) / len(rs)
            a = sq[x["s"]]
            a[0] += 1; a[1] += (pr - y) ** 2; a[2] += ((p[0] + p[1]) / 2 - y) ** 2
            if pr - p[1] >= 0.10 and 0.03 <= p[1] <= 0.97:
                bets.append(dict(ev=x["e"], t=t, cost=p[1] + fee(p[1]), pay=1.0 * y, s=x["s"]))
            elif p[0] - pr >= 0.10 and 0.03 <= 1 - p[0] <= 0.97:
                bets.append(dict(ev=x["e"], t=t, cost=1 - p[0] + fee(1 - p[0]), pay=1.0 * (not y), s=x["s"]))
    return bets, {k: (v[0], v[1] / v[0], v[2] / v[0]) for k, v in sq.items() if v[0]}


def filled(tp, tk, t, px, win=7200):
    """contracts that really traded at or under our price in the next `win` seconds (trade prices are in 1/1000 $)"""
    return sum(tr[2] for tr in tp[tk]["tr"] if t <= tr[0] < t + win and tr[1] / 1000 <= px + 1e-9)


def band_rule(E, tp, H, lo=0.10, hi=0.90, need_fill=True, series="KXALBUMEQUIV"):
    """THE LEAD: H hours before the ladder closes, buy Yes on every rung whose mid price is lo-hi (ask <= 97c,
    bid-ask gap <= 15c) at the hourly ask + fee; with need_fill, only where someone really traded at or under that
    price in the next 2 hours."""
    out = []
    for x in E:
        if x["s"] != series:
            continue
        t = x["close"] - H * 3600
        for m in x["L"]:
            p = quote(tp, m["t"], t)
            if not p or p[1] - p[0] > 0.15:
                continue
            mid = (p[0] + p[1]) / 2
            if not (lo <= mid < hi and p[1] <= 0.97):
                continue
            sz = filled(tp, m["t"], t, p[1]) if need_fill else 1
            if sz <= 0:
                continue
            out.append(dict(ev=x["e"], t=t, cost=p[1] + fee(p[1]), pay=1.0 * (m["res"] == "yes"), px=p[1], sz=sz,
                            tk=m["t"], w=m["q"][5:70], T=rung(m), mid_hits=x["mid"]))
    return sorted(out, key=lambda b: b["t"])


def hot100_spotify(look_h=(110, 60, 30, 12)):
    """Kalshi Hot 100 #1: buy Yes on the song with the most US Spotify plays in the tracking week (days known by then)."""
    import gzip
    ms, tp = K.load("KXTOPSONG$")
    us = json.load(gzip.open(os.path.join(ROOT, "bt_cache", "spw", "us.json.gz")))
    ev = collections.defaultdict(list)
    for m in ms.values():
        ev[m["ev"]].append(m)
    res = {}
    for off in look_h:
        bets = []
        for e, L in ev.items():
            c = min(m["close"] for m in L)
            chart = dt.datetime.fromtimestamp(c, dt.timezone.utc).date() + dt.timedelta(days=5)   # chart date (Saturday)
            t0, tl = chart - dt.timedelta(days=15), c - off * 3600                                # tracking week Fri-Thu
            tot, nm = collections.Counter(), {}
            for i in range(7):
                d = t0 + dt.timedelta(days=i)
                if dt.datetime(d.year, d.month, d.day, tzinfo=dt.timezone.utc).timestamp() + 42 * 3600 > tl:
                    continue                                      # a day's chart is readable ~18:00 UTC the day after
                for sid, tt, pl in us.get(d.isoformat(), []):
                    tot[sid] += pl
                    nm[sid] = tt
            if not tot:
                continue
            lead = nm[tot.most_common(1)[0][0]]
            for m in L:
                if norm(m["w"])[:10] != norm(lead)[:10]:
                    continue
                p = quote(tp, m["t"], tl, 4 * 3600)
                if p and 0.05 <= p[1] <= 0.90:
                    bets.append(dict(ev=e, t=tl, cost=p[1] + fee(p[1]), pay=1.0 * (m["res"] == "yes")))
        res[off] = bets
    return res


def per100(B):
    return 100 * sum(x["pay"] - x["cost"] for x in B) / sum(x["cost"] for x in B) if B else None


def do_run():
    E, ms, tp = album_events()
    print("album ladders", len(E), "with a HITS midweek number", sum(1 for x in E if x["mid"]))
    b, sq = mid_model(E, tp)
    print("HITS midweek model vs price (n, model miss score, market miss score; lower is better):", sq)
    print("  bets", len(b), "per $100", per100(b))
    for H in (96, 72, 60, 48, 42, 36, 30, 24, 12):
        B = band_rule(E, tp, H)
        hh = len(B) // 2
        print(f"Yes at 10-90c, {H}h before close: bets {len(B)} albums {len({x['ev'] for x in B})} "
              f"per $100 {per100(B)} halves {per100(B[:hh])} / {per100(B[hh:])}")
    for off, B in hot100_spotify().items():
        print(f"Hot 100 #1 = Spotify leader, {off}h before close: bets {len(B)} per $100 {per100(B)}")


def do_report():
    import exam
    E, ms, tp = album_events()
    src = "music.py, backtest/music.md"
    B = band_rule(E, tp, 36)
    print(exam.score(B, "Kalshi album first-week units ladders: Yes on a rung priced 10-90c, 36 hours before close (Sat ~02:00 UTC)",
                     tries=TRIES, src=src, status="lead, no track", quiet=True))
    b, sq = mid_model(E, tp)
    print(exam.score(b, "Kalshi album first-week units: buy where HITS's midweek forecast is 10c+ away from the price (Fri 06:00 UTC)",
                     tries=4, src=src, status="dropped", quiet=True))
    hs = hot100_spotify()[110]
    print(exam.score(hs, "Kalshi Billboard Hot 100 #1: Yes on the song with the most US Spotify plays in the tracking week",
                     tries=8, src=src, status="dropped", quiet=True))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "peek"
    {"peek": do_peek, "hddpeek": do_hdd_peek, "hits": do_hits, "run": do_run, "report": do_report}[cmd]()
