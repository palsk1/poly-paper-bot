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


if __name__ == "__main__":
    a = sys.argv[1] if len(sys.argv) > 1 else "peek"
    {"peek": do_peek}[a]()
