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


def norm(x):
    x = (x or "").lower().replace("’", "'")
    x = re.sub(r"\((feat|with|w/|from)[^)]*\)|\[[^\]]*\]| - (from|feat|with|remaster|single|radio|bonus|spotify)[^|]*$| ft\. .*$| feat\. .*$", "", x)
    return re.sub(r"[^a-z0-9]+", "", x)


def totals(which):
    """Every song that ever charted on kworb's daily list: [id, artist, title, days, peak]."""
    x = raw(f"https://kworb.net/spotify/country/{which}_daily_totals.html", 120, {"Accept-Encoding": "identity"})
    out = []
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", x, flags=re.S):
        m = re.search(r'track/([A-Za-z0-9]+)\.html">(.*?)</a>', row)
        if not m:
            continue
        tds = [re.sub(r"<[^>]+>", "", c).strip() for c in re.findall(r"<td[^>]*>(.*?)</td>", row, flags=re.S)]
        art = re.search(r'artist/[A-Za-z0-9]+\.html">(.*?)</a>', row)
        nums = [c for c in tds[1:] if re.fullmatch(r"[\d,]+", c)]
        import html as H
        out.append([m.group(1), H.unescape(art.group(1)) if art else "", H.unescape(m.group(2)),
                    int(nums[0].replace(",", "")) if nums else 0, int(nums[2].replace(",", "")) if len(nums) > 2 else 999])
    return out


def wanted_names():
    """Song titles named in the bets on both sites (normalised)."""
    import families as F
    w = collections.Counter()
    ms, _ = F.load("spotify")
    for m in ms.values():
        it = (m.get("item") or "").strip().strip('"')
        if "song" not in (m.get("q") or "").lower() or not it:
            continue
        t = re.split(r" - | by ", it)[0]
        w[norm(t)] += 1
    L = rj(os.path.join(K.CACHE, "markets.json.gz"))["markets"]
    for m in L.values():
        if re.match(r"KXSPOTIFY(W|D|GLOBALD|2D|NUM1USA)$|KXSPOTSTREAMSUSA|KXRANKLISTSONGSPOT", m["s"]):
            w[norm(m.get("w"))] += 1
    w.pop("", None)
    return w


def parse_track(x, first="2024-09-01"):
    i = x.find('<div class="daily">')
    if i < 0:
        return None
    t = x[i:]
    t = t[:t.find("</table>")]
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", t, flags=re.S)
    head = re.findall(r"<th>(.*?)</th>", rows[0])
    gi = head.index("Global") if "Global" in head else -1
    ui = head.index("US") if "US" in head else -1
    d = {}
    for r in rows[1:]:
        c = [re.sub(r"<[^>]+>", "", y).strip() for y in re.findall(r"<td[^>]*>(.*?)</td>", r, flags=re.S)]
        if not c or not re.fullmatch(r"\d{4}/\d\d/\d\d", c[0]):
            continue
        day = c[0].replace("/", "-")
        if day < first:
            continue
        v = []
        for j in (gi, ui):
            m = re.match(r"(\d+)\s*\(\s*([\d,]+)", c[j]) if 0 <= j < len(c) else None
            v += [int(m.group(1)), int(m.group(2).replace(",", ""))] if m else [0, 0]
        if v[1] or v[3]:
            d[day] = v
    return d


def do_fetch(maxpeak=3):
    os.makedirs(CACHE, exist_ok=True)
    f = os.path.join(CACHE, "tracks.json.gz")
    T = rj(f) if os.path.exists(f) else {}
    names = wanted_names()
    tot = {"us": totals("us"), "global": totals("global")}
    print("names in bets", len(names), "totals", {k: len(v) for k, v in tot.items()}, tot["us"][:3], flush=True)
    want, hit = {}, set()
    for which, rows in tot.items():
        for i, a, t, days, pk in rows:
            n = norm(t)
            if (n in names and pk <= 50) or pk <= maxpeak:
                want[i] = [a, t]
                if n in names:
                    hit.add(n)
    miss = [n for n in names if n not in hit]
    print("want", len(want), "have", len(T), "names without a song", len(miss), sorted(miss, key=lambda n: -names[n])[:60], flush=True)
    t0, n, bad = time.time(), 0, 0
    for i, (a, t) in want.items():
        if i in T or time.time() - t0 > 3.2 * 3600:
            continue
        try:
            d = parse_track(raw(f"https://kworb.net/spotify/track/{i}.html", 60, {"Accept-Encoding": "identity"}))
        except Exception as e:
            bad += 1
            print("FAIL", i, t, str(e)[:80], flush=True)
            if bad > 40:
                break
            time.sleep(10)
            continue
        T[i] = {"a": a, "t": t, "d": d or {}}
        n += 1
        if n % 100 == 0:
            print(n, "fetched", a, "-", t, len(d or {}), flush=True)
            wj(f, T)
        time.sleep(0.7)
    wj(f, T)
    print("done", len(T), "of", len(want), "failed", bad, "with days", sum(1 for v in T.values() if v["d"]), flush=True)


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
    {"peek": do_peek, "peek2": do_peek2, "fetch": do_fetch}[a]()
