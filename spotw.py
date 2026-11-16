"""Spotify's weekly #1 song bets (Polymarket now, Kalshi until July 2026) vs the real daily play counts. Paper research.

  python3 spotw.py peek      # probe spw_peek: where the daily play counts per song can be read
"""
import collections, datetime as dt, os, re, sys, time

import kcharts as K

ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(ROOT, "bt_cache", "spw")
rj, wj, raw = K.rj, K.wj, K.raw


def text(s, n=1500, start=("Pos", "Streams")):
    t = re.sub(r"\s+", " ", re.sub(r"<script.*?</script>|<style.*?</style>", " ", s, flags=re.S))
    t = re.sub(r"(\|\s*)+", "| ", re.sub(r"<[^>]+>", "|", t))
    i = max(0, min([x for x in (t.find(k) for k in start) if x >= 0] or [0]))
    return t[i:i + n]


def do_peek():
    s = ""
    for u in ("https://kworb.net/spotify/country/us_daily.html",
              "https://kworb.net/spotify/country/us_weekly.html",
              "https://kworb.net/spotify/country/global_daily.html",
              "https://kworb.net/spotify/country/global_weekly.html",
              "https://kworb.net/spotify/country/us_daily_totals.html",
              "https://web.archive.org/web/20260615120000/https://kworb.net/spotify/country/us_daily.html",
              "https://web.archive.org/web/20250615120000/https://kworb.net/spotify/country/us_daily.html",
              "https://web.archive.org/web/20260615120000/https://kworb.net/spotify/country/us_weekly.html",
              "https://web.archive.org/web/20260615120000/https://kworb.net/spotify/country/global_daily.html",
              "https://archive.org/wayback/available?url=kworb.net/spotify/country/us_daily.html&timestamp=20260301",
              "https://charts-spotify-com-service.spotify.com/public/v0/charts",
              "https://charts.spotify.com/charts/view/regional-us-daily/2026-06-15"):
        try:
            x = raw(u, 50, {"Accept-Encoding": "identity"})
        except Exception as e:
            print("FAIL", u, str(e)[:120], flush=True)
            continue
        print("OK", u, len(x), flush=True)
        print("  links", re.findall(r'href="([^"]*track/[^"]+)"', x)[:3], re.findall(r"captures|\d+ captures", x)[:2], flush=True)
        print("  text", text(x, 900), flush=True)
        if u.endswith("us_daily.html") and "web.archive" not in u:
            s = x
    ids = re.findall(r'href="\.\./track/([A-Za-z0-9]+)\.html"', s)[:2]
    for i in ids:
        for u in (f"https://kworb.net/spotify/track/{i}.html",):
            try:
                x = raw(u, 50, {"Accept-Encoding": "identity"})
                print("OK", u, len(x), flush=True)
                print("  text", text(x, 2500, ("Date", "Peak", "Total")), flush=True)
                j = x.find("US")
                print("  raw", re.sub(r"\s+", " ", x[max(0, x.find("<table")):][:1800]), flush=True)
            except Exception as e:
                print("FAIL", u, str(e)[:120], flush=True)


def do_peek2():
    x = raw("https://kworb.net/spotify/track/7scFxt9VhL4FJwuPSfRlfN.html", 50, {"Accept-Encoding": "identity"})
    print(len(x), [(m.start(), x[m.start() - 60:m.start() + 120].replace("\n", " ")) for m in re.finditer(r"(?i)daily", x)][:12], flush=True)
    print("tables", [m.start() for m in re.finditer("<table", x)], re.findall(r'<div class="[^"]+"', x)[:40], flush=True)
    for m in list(re.finditer("<table", x))[1:3]:
        print("  T", re.sub(r"\s+", " ", x[m.start():m.start() + 1500]), flush=True)
    print("tail", text(x[-6000:], 3000, ("zzz",)), flush=True)
    for u in ("https://web.archive.org/cdx/search/cdx?url=kworb.net/spotify/country/us_daily.html&from=20241001&output=json&filter=statuscode:200&collapse=timestamp:8&fl=timestamp",
              "https://web.archive.org/cdx/search/cdx?url=kworb.net/spotify/country/global_daily.html&from=20241001&output=json&filter=statuscode:200&collapse=timestamp:8&fl=timestamp",
              "https://web.archive.org/cdx/search/cdx?url=kworb.net/spotify/country/us_weekly.html&from=20241001&output=json&filter=statuscode:200&collapse=timestamp:8&fl=timestamp",
              "https://charts-spotify-com-service.spotify.com/public/v0/charts/regional-us-daily/2026-06-15",
              "https://charts-spotify-com-service.spotify.com/public/v0/charts/regional-us-daily/latest",
              "https://charts-spotify-com-service.spotify.com/auth/v0/charts/regional-us-daily/2026-06-15"):
        for k in range(3):
            try:
                y = raw(u, 90, {"Accept-Encoding": "identity"})
                n = y.count("\n")
                print("OK", u[:110], len(y), n, y[:300].replace("\n", " "), "...", y[-200:].replace("\n", " "), flush=True)
                break
            except Exception as e:
                print("FAIL", u[:110], str(e)[:120], flush=True)
                time.sleep(20)


if __name__ == "__main__":
    a = sys.argv[1] if len(sys.argv) > 1 else "peek"
    {"peek": do_peek, "peek2": do_peek2}[a]()
