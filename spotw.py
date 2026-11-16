"""Spotify's weekly #1 song bets (Polymarket now, Kalshi until July 2026) vs the real daily play counts. Paper research.

  python3 spotw.py peek | peek2   # probes spw_peek, spw_peek2: where the daily play counts per song can be read
  python3 spotw.py fetch          # probe spw_fetch: kworb's song pages (last ~31 chart days per song) -> bt_cache/spw/tracks.json.gz
  python3 spotw.py usdaily        # US daily top 50 with play counts since 2019 -> bt_cache/spw/us.json.gz
  python3 spotw.py run            # the play-count record against Kalshi's and Polymarket's prices
  python3 spotw.py report         # shared-exam lines; write-up in backtest/spotify.md
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


US_SRC = "https://raw.githubusercontent.com/sdevarajan2006/spotify-chart-markov-chain/main/data/spotify_us_daily_top200_2017_2026.csv.gz"


def do_usdaily(first="2019-01-01", top=50):
    """Spotify's US daily top 50 per day with play counts -> bt_cache/spw/us.json.gz  {day: [[spotify id, title, plays], ...]}
    Until 17 Sep 2026 from a public GitHub copy of Spotify's own daily charts, the newest month from kworb's song pages (do_fetch)."""
    import csv, gzip, io, urllib.request
    os.makedirs(CACHE, exist_ok=True)
    raw_gz = urllib.request.urlopen(urllib.request.Request(US_SRC, headers={"User-Agent": "Mozilla/5.0"}), timeout=120).read()
    out = {}
    for r in csv.DictReader(io.TextIOWrapper(gzip.GzipFile(fileobj=io.BytesIO(raw_gz)), encoding="utf-8")):
        if r["chart_date"] >= first and int(r["rank"]) <= top:
            out.setdefault(r["chart_date"], []).append([r["track_uri"].split(":")[-1], r["track_name"], int(r["streams"])])
    last = max(out)
    f = os.path.join(CACHE, "tracks.json.gz")
    add = 0
    for i, v in (rj(f) if os.path.exists(f) else {}).items():
        for day, (gp, gs, up, us) in v["d"].items():
            if day > last and us and up <= top:
                out.setdefault(day, []).append([i, v["t"], us])
                add += 1
    for L in out.values():
        L.sort(key=lambda x: -x[2])
    wj(os.path.join(CACHE, "us.json.gz"), out)
    ds = sorted(out)
    print("days", len(ds), ds[0], ds[-1], "GitHub copy ends", last, "rows from kworb", add,
          "days with under 5 songs", [d for d in ds if len(out[d]) < 5][:20], flush=True)


EDGES = (-0.30, -0.15, -0.08, -0.04, -0.02, 0.0, 0.02, 0.04, 0.08, 0.15, 0.30)


def weeks(lag_h=24):
    """One row per Spotify week (Friday to Thursday), known days k = 1..6 and song near the top:
    plays so far + the last known day repeated for the days left, and how far that is from the best other song."""
    U = rj(os.path.join(CACHE, "us.json.gz"))
    ds = sorted(U)
    d = dt.date.fromisoformat(ds[0])
    d += dt.timedelta(days=(4 - d.weekday()) % 7)
    out = {}
    prev_ids = set()
    while d + dt.timedelta(6) <= dt.date.fromisoformat(ds[-1]):
        days = [(d + dt.timedelta(i)).isoformat() for i in range(7)]
        if all(len(U.get(x, [])) >= 20 for x in days):
            tot, name = collections.Counter(), {}
            per = []
            for x in days:
                c = {i: n for i, t, n in U[x]}
                name.update({i: t for i, t, n in U[x]})
                per.append(c)
                tot.update(c)
            win = tot.most_common(2)
            wk = {"d0": d, "win": win[0][0], "margin": (win[0][1] - win[1][1]) / win[0][1], "name": name, "tot": tot, "per": per, "k": {}}
            for k in range(1, 7):
                S = collections.Counter()
                for c in per[:k]:
                    S.update(c)
                P = {i: S[i] + (7 - k) * per[k - 1].get(i, 0) for i in S}
                top = sorted(P, key=lambda i: -P[i])[:8]
                rows = {}
                for i in top:
                    o = max(P[j] for j in top if j != i)
                    g = (P[i] - o) / max(P[i], o)
                    new = i not in prev_ids and not per[0].get(i, 0) < 1 and all(i not in c for c in per[:0])
                    rows[i] = {"g": g, "f": (k, sum(1 for e in EDGES if g >= e), bool(i not in prev_ids)), "yes": i == win[0][0], "rank": top.index(i)}
                wk["k"][k] = rows
            out[d] = wk
            prev_ids = set(tot)
        else:
            prev_ids = set()
        d += dt.timedelta(7)
    return out


def chance(W, d0, f, min_seen=20):
    """Walk forward: how often a song in this cell won, counting only weeks that ended before week d0 began."""
    y = n = 0
    for d, wk in W.items():
        if d + dt.timedelta(7) > d0:
            continue
        r = [x for x in wk["k"][f[0]].values() if x["f"] == f]
        n += len(r)
        y += sum(x["yes"] for x in r)
    return (y + 1) / (n + 2) if n >= min_seen else None


def find(wk, title):
    n = norm(title)
    hit = [i for i, t in wk["name"].items() if norm(t) == n]
    return max(hit, key=lambda i: wk["tot"][i]) if hit else None


def k_rows(W, lag_h=24):
    """Kalshi's weekly 'top song USA' markets at the hour each new day's count is surely public (the day's end + lag_h, UTC)."""
    ms, tp = K.load("KXSPOTIFYW$")
    evs = collections.defaultdict(list)
    for m in ms.values():
        evs[m["ev"]].append(m)
    rows, chk = [], [0, 0, 0]
    for e, L in evs.items():
        close = K.ev_close(L)
        d0 = dt.datetime.fromtimestamp(close - 5 * 3600, dt.timezone.utc).date() - dt.timedelta(6)
        wk = W.get(d0)
        if not wk:
            chk[2] += 1
            continue
        yes = [m for m in L if m["res"] == "yes"]
        if yes:
            chk[0] += 1
            chk[1] += find(wk, yes[0]["w"]) == wk["win"]
        for k in range(1, 7):
            t = int(dt.datetime.combine(d0 + dt.timedelta(k), dt.time(0), dt.timezone.utc).timestamp()) + lag_h * 3600
            if t >= close - 1800:
                continue
            for m in L:
                v = tp.get(m["t"])
                i = find(wk, m["w"])
                if not v or not v["c"] or t < m["open"] + 3600:
                    continue
                c = None
                for x in v["c"]:
                    if x[0] > t:
                        break
                    c = x
                if not c or c[1] is None or c[2] is None or t - c[0] > 3 * 3600:
                    continue
                r = wk["k"][k].get(i) if i else None
                f = r["f"] if r else (k, 0, False)
                q = chance(W, d0, f)
                if q is None:
                    continue
                rows.append({"tk": m["t"], "ev": e, "t": t, "bid": c[1], "ask": c[2], "yes": m["res"] == "yes", "w": m["w"], "f": f, "q": q,
                             "kind": "k", "left": (close - t) / 3600, "k": k, "g": r["g"] if r else -1, "d0": d0})
    print("Kalshi: events", len(evs), "no play counts for the week", chk[2], "winner = most plays in", chk[1], "of", chk[0], flush=True)
    return rows


def p_rows(W, lag_h=24):
    """Polymarket's '#1 song on US Spotify this week' markets, same look hours, last real trade (12 hours fresh) as the price."""
    import families as F
    import stocks
    ms, tp = F.load("spotify")
    evs = collections.defaultdict(list)
    for k, m in ms.items():
        q = m.get("q") or ""
        if re.search(r"#1 (song on US Spotify|US song) this week", q) and m.get("end") and m.get("final"):
            evs[m["ev"]].append((k, m))
    rows, chk = [], [0, 0, 0]
    for e, M in evs.items():
        end = collections.Counter(m["end"] for _, m in M).most_common(1)[0][0]
        d0 = None
        for back in (6, 7, 8, 5):           # find the week whose most-played song is the market's winner
            c = dt.datetime.fromtimestamp(end - 12 * 3600, dt.timezone.utc).date() - dt.timedelta(back)
            c -= dt.timedelta((c.weekday() - 4) % 7)
            if c in W:
                d0 = c
                break
        if d0 is None:
            chk[2] += 1
            continue
        wk = W[d0]
        yes = [m for _, m in M if m["final"][0] == 1.0]
        if yes:
            chk[0] += 1
            chk[1] += find(wk, re.split(r" - | by ", yes[0]["item"].strip('"'))[0]) == wk["win"]
        for k in range(1, 7):
            t = int(dt.datetime.combine(d0 + dt.timedelta(k), dt.time(0), dt.timezone.utc).timestamp()) + lag_h * 3600
            if t >= end - 1800:
                continue
            for key, m in M:
                b = (tp.get(key) or {}).get("b")
                if not b or t < m["start"] + 3600:
                    continue
                pp = stocks._price(b, t, fresh=12 * 3600)
                if pp is None:
                    continue
                i = find(wk, re.split(r" - | by ", m["item"].strip('"'))[0])
                r = wk["k"][k].get(i) if i else None
                f = r["f"] if r else (k, 0, False)
                q = chance(W, d0, f)
                if q is None:
                    continue
                rows.append({"tk": key, "ev": e, "t": t, "bid": pp, "ask": pp, "yes": m["final"][0] == 1.0, "w": m["item"], "f": f, "q": q,
                             "kind": "p", "left": (end - t) / 3600, "k": k, "g": r["g"] if r else -1, "d0": d0})
    print("Polymarket US: events", len(evs), "no play counts for the week", chk[2], "winner = most plays in", chk[1], "of", chk[0], flush=True)
    return rows, ms, tp


def p_bets(rows, ms, tp, gap, side="both", extra=0.02):
    import stocks
    out, used = [], set()
    for r in sorted(rows, key=lambda r: r["t"]):
        yes = r["q"] - r["ask"] >= gap
        if r["tk"] in used or not (yes or r["bid"] - r["q"] >= gap) or (side != "both" and (side == "yes") != yes):
            continue
        x = stocks.buy(ms[r["tk"]], tp[r["tk"]]["b"], r["t"], yes, extra, lo=0.03, hi=0.97, window=3600)
        if x and abs(x["px"] - (r["ask"] if yes else 1 - r["bid"])) <= 0.15:
            used.add(r["tk"])
            x.update(ev=r["ev"], pnl=x["pay"] - x["cost"], p=x["px"], w=r["w"], q=r["q"], kind="p", k=r["k"], side="yes" if yes else "no")
            out.append(x)
    return out


def miss(rows):
    n = max(1, len(rows))
    return round(sum((r["q"] - r["yes"]) ** 2 for r in rows) / n, 4), round(sum(((r["bid"] + r["ask"]) / 2 - r["yes"]) ** 2 for r in rows) / n, 4)


def do_run(lag_h=24):
    W = weeks()
    ds = sorted(W)
    print("weeks", len(W), ds[0], ds[-1], flush=True)
    for k in range(1, 7):                   # how often the song ahead after k days ends the week on top
        a = [wk for wk in W.values()]
        lead = sum(1 for wk in a if any(r["rank"] == 0 and r["yes"] for r in wk["k"][k].values()))
        print(f"  after {k} days: the song ahead on our count wins the week in {lead} of {len(a)}", flush=True)
    kr = k_rows(W, lag_h)
    print("Kalshi rows", len(kr), "events", len({r["ev"] for r in kr}), "miss score model, price", miss(kr), flush=True)
    for k in range(1, 7):
        x = [r for r in kr if r["k"] == k]
        print("   k", k, len(x), miss(x))
    for g in (0.05, 0.10, 0.15, 0.25):
        for side in ("yes", "no", "both"):
            print(K.line(f"Kalshi gap {g} {side}", K.first_bets(kr, g, 0.0, side)), flush=True)
    pr, ms, tp = p_rows(W, lag_h)
    print("Polymarket rows", len(pr), "events", len({r["ev"] for r in pr}), "miss score model, price", miss(pr), flush=True)
    for g in (0.05, 0.10, 0.15, 0.25):
        for side in ("yes", "no", "both"):
            print(K.line(f"PM gap {g} {side}", p_bets(pr, ms, tp, g, side)), flush=True)


TRIES = 60


def do_report():
    """The two shared-exam lines (both dropped). The write-up is backtest/spotify.md."""
    import exam
    W = weeks()
    kr = k_rows(W)
    pr, ms, tp = p_rows(W)
    src = "spotw.py, backtest/spotify.md"
    kb = K.first_bets(kr, 0.10, 0.0, "both")
    pb = p_bets(pr, ms, tp, 0.10, "both")
    for b in kb + pb:
        b.setdefault("group", b["ev"])
    print(exam.score(kb, "Kalshi Spotify weekly #1 song (US): buy where the daily play counts are 10c+ away from the price", tries=TRIES, src=src, status="dropped", quiet=True))
    print(exam.score(pb, "Polymarket Spotify weekly #1 song (US): buy where the daily play counts are 10c+ away from the price", tries=TRIES, src=src, status="dropped", quiet=True))


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
    {"peek": do_peek, "peek2": do_peek2, "fetch": do_fetch, "usdaily": do_usdaily, "run": do_run, "report": do_report}[a]()
