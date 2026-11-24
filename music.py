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


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "peek"
    {"peek": do_peek, "hddpeek": do_hdd_peek}[cmd]()
