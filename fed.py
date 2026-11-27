#!/usr/bin/env python3
"""Fed rate decision and CPI bets (Kalshi + Polymarket) vs what futures / options markets imply.
backtest/fed.md. PAPER ONLY: reads public data, never trades, never writes state/.

  python3 fed.py src      (probe fed_src: which free futures / options histories Actions can read, and the markets)
  python3 fed.py fetch    (probe fed_fetch: Atlanta Fed options-implied odds, Treasury bill rates, Kalshi Fed + CPI
                           markets with hourly bid/ask and trades, Polymarket fed-rates / cpi tags -> bt_cache/fed/)
"""
import datetime as dt
import json
import os
import sys
import urllib.request

import bot

K, G = bot.KALSHI, bot.GAMMA
UTC = dt.timezone.utc
BUA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
CACHE = os.path.join(bot.ROOT, "bt_cache", "fed")


def raw(url, ua=BUA, timeout=40):
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read(), r.headers.get("Content-Type")
    except urllib.error.HTTPError as e:
        try:
            body = e.read()[:300]
        except Exception:
            body = b""
        return e.code, body, None
    except Exception as e:
        return None, f"{type(e).__name__}: {e}".encode(), None


YH = "https://query{}.finance.yahoo.com/v8/finance/chart/{}?period1={}&period2={}&interval=1d"


def src():
    now = int(dt.datetime.now(UTC).timestamp())
    tries = {}
    for sym in ("ZQ=F", "ZQZ26.CBT", "ZQF27.CBT", "ZQZ25.CBT", "ZQU25.CBT", "ZQH24.CBT", "SR3=F", "SR3Z26.CME"):
        tries[f"yahoo {sym}"] = YH.format(1, sym, now - 3 * 365 * 86400, now)
    tries.update({
        "yahoo2 ZQZ25.CBT": YH.format(2, "ZQZ25.CBT", now - 3 * 365 * 86400, now),
        "stooq zq.f": "https://stooq.com/q/d/l/?s=zq.f&i=d",
        "stooq zqz25.f": "https://stooq.com/q/d/l/?s=zqz25.f&i=d",
        "atlanta MPT xlsx": "https://www.atlantafed.org/-/media/Project/Atlanta/FRBA/Documents/research-and-data/data/market-probability-tracker/mpt_histdata.xlsx",
        "fred DFF": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DFF",
        "fred DTB4WK": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DTB4WK",
        "fred DGS1MO": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS1MO",
        "fred SOFR": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=SOFR",
        "fred T5YIE": "https://fred.stlouisfed.org/graph/fredgraph.csv?id=T5YIE",
        "treasury bills daily": "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/2025/all?type=daily_treasury_bill_rates&field_tdr_date_value=2025&page&_format=csv",
        "cme fedwatch page": "https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html",
        "cme zq quotes": "https://www.cmegroup.com/CmeWS/mvc/Quotes/Future/305/G",
        "rateprobability latest": "https://rateprobability.com/api/latest",
        "investing zq": "https://www.investing.com/rates-bonds/30-day-fed-fund-futures-historical-data",
        "barchart zq": "https://www.barchart.com/futures/quotes/ZQZ25/price-history/historical",
        "nyfed sofr api": "https://markets.newyorkfed.org/api/rates/secured/sofr/last/5.json",
    })
    for name, url in tries.items():
        code, body, ct = raw(url)
        head = body[:260].decode("utf-8", "replace").replace("\n", " | ")
        extra = ""
        if name.startswith("yahoo") and code == 200:
            try:
                j = json.loads(body)
                r = j["chart"]["result"][0]
                ts = r.get("timestamp") or []
                cl = r["indicators"]["quote"][0].get("close") or []
                extra = f" ROWS {len(ts)} first {dt.datetime.utcfromtimestamp(ts[0]).date() if ts else '-'} last " \
                        f"{dt.datetime.utcfromtimestamp(ts[-1]).date() if ts else '-'} close[-3:] {cl[-3:]}"
            except Exception as e:
                extra = f" parse {e}"
        print(f"== {name}: HTTP {code} {ct} {len(body)} bytes{extra}\n   {head[:260]}", flush=True)
    # Kalshi: every series about the Fed, rates or inflation
    try:
        ser = bot.http_json(f"{K}/series", {}).get("series") or []
        words = ("fed", "fomc", "rate", "cpi", "inflation", "pce", "powell", "cut", "hike")
        hit = [s for s in ser if any(w in (str(s.get("title")) + " " + str(s.get("ticker"))).lower() for w in words)]
        print(f"\nKalshi series {len(ser)}, matching {len(hit)}")
        for s in hit:
            print("KS", s.get("ticker"), "|", s.get("category"), "|", s.get("frequency"), "|", str(s.get("title"))[:90])
    except Exception as e:
        print("kalshi series failed", e)
    for t in ("KXFED", "KXFEDDECISION", "FED", "FEDDECISION", "KXRATECUT", "KXCPI"):
        try:
            r = bot.http_json(f"{K}/markets", {"series_ticker": t, "limit": 5, "status": "settled"})
            ms = r.get("markets") or []
            print("\nKM", t, len(ms))
            for m in ms[:5]:
                print("   ", m.get("ticker"), "|", str(m.get("title"))[:80], "|", m.get("yes_sub_title"), "|",
                      m.get("result"), "| vol", m.get("volume_fp") or m.get("volume"), "| close", m.get("close_time"))
            r = bot.http_json(f"{K}/historical/markets", {"series_ticker": t, "limit": 3})
            for m in (r.get("markets") or [])[:3]:
                print("   hist", m.get("ticker"), "|", str(m.get("title"))[:80], "|", m.get("result"), "|", m.get("close_time"))
        except Exception as e:
            print("KM", t, "failed", str(e)[:120])
    # Polymarket: Fed and CPI events
    for slug in ("fed-rates", "fed", "economic-policy", "inflation", "cpi", "economy"):
        try:
            tg = bot.http_json(f"{G}/tags/slug/{slug}")
            tid = tg.get("id")
            r = bot.http_json(f"{G}/events", {"tag_id": tid, "closed": "true", "limit": 100, "order": "volume",
                                              "ascending": "false"})
            ev = bot.envelope_rows(r, "events", "data")
            print(f"\nPM tag {slug} id {tid}: {len(ev)} closed events (top by volume)")
            for e in ev[:25]:
                print("   ", e.get("slug"), "| $", int(float(e.get("volume") or 0)), "| end", str(e.get("endDate"))[:10],
                      "| mk", len(e.get("markets") or []))
        except Exception as e:
            print("PM tag", slug, "failed", str(e)[:120])


MPT_URL = ("https://www.atlantafed.org/-/media/Project/Atlanta/FRBA/Documents/research-and-data/data/"
           "market-probability-tracker/mpt_histdata.xlsx")
BILLS = ("https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/"
         "{y}/all?type=daily_treasury_bill_rates&field_tdr_date_value={y}&page&_format=csv")
K_SERIES = ("KXFEDDECISION", "KXFED", "FEDDECISION", "FED", "KXCPI", "KXCPIYOY", "KXCPICORE")
P_TAGS = ("fed-rates", "cpi")


def fetch():
    import csv
    import io
    import time
    from concurrent.futures import ThreadPoolExecutor
    import khouse
    import kmentions as km
    import dates
    os.makedirs(CACHE, exist_ok=True)
    rj, wj = khouse.rj, khouse.wj
    xl = os.path.join(CACHE, "mpt_histdata.xlsx")
    if not os.path.exists(xl):
        code, body, _ = raw(MPT_URL, timeout=120)
        print("MPT", code, len(body), flush=True)
        if code == 200:
            open(xl, "wb").write(body)
    if os.path.exists(xl):
        import openpyxl
        wb = openpyxl.load_workbook(xl, read_only=True)
        for ws in wb.worksheets:
            print(f"\nSHEET {ws.title} dims {ws.max_row}x{ws.max_column}")
            for i, row in enumerate(ws.iter_rows(values_only=True)):
                print("  ", [str(v)[:22] for v in row[:16]])
                if i >= 7:
                    break
    bp = os.path.join(CACHE, "bills.json.gz")
    bills = rj(bp, {}) or {}
    for y in range(2021, 2027):
        if str(y) in bills and y < 2026:
            continue
        code, body, _ = raw(BILLS.format(y=y), timeout=60)
        if code == 200:
            rows = list(csv.DictReader(io.StringIO(body.decode("utf-8", "replace"))))
            bills[str(y)] = rows
            print("bills", y, len(rows), flush=True)
    wj(bp, bills)
    mk = os.path.join(CACHE, "kmarkets.json.gz")
    have = rj(mk, {}) or {}
    for s in K_SERIES:
        if s in have and s not in ("KXFEDDECISION", "KXFED"):
            continue
        _, ok, n = km.series_markets(s)
        have[s] = ok
        print("kalshi", s, len(ok), "settled", flush=True)
        wj(mk, have)
    t0 = time.time()
    for s in K_SERIES:
        ms = [m for m in have.get(s, {}).values() if m["vol"] >= 500]
        path = os.path.join(CACHE, f"tapes_{s}.json.gz")
        got = rj(path, {}) or {}
        todo = [m for m in ms if m["t"] not in got]
        for i in range(0, len(todo), 120):
            with ThreadPoolExecutor(6) as ex:
                for tk, dd in ex.map(dates.tape_one, todo[i:i + 120]):
                    got[tk] = dd
            wj(path, got)
            print(f"  {s}: {len(got)} of {len(ms)} ({time.time() - t0:.0f}s)", flush=True)
            if time.time() - t0 > 3.5 * 3600:
                print("time's up, run again", flush=True)
                return
    import families
    families.fetch(",".join(P_TAGS))


# ---------------------------------------------------------------- the test
import re
import math
import collections
DAY = 86400
LOOKS = (1, 2, 4, 7, 14, 21, 28)       # days before the decision, each at 15:00 UTC (US markets open)
PKL = os.path.join(CACHE, "mpt.pkl")


def d10(t):
    return dt.datetime.fromtimestamp(t, UTC).strftime("%Y-%m-%d")


def k_fee(p):
    return math.ceil(7 * p * (1 - p) - 1e-9) / 100


def mpt():
    """{(obs day, quarter start): {"cur": current lower bound (bps), "p": {lower bound: chance}}} from the Atlanta Fed
    file (CME 3-month SOFR options). Chances under 2 in 100 are left out of the file, so we scale the rest to 1."""
    import pandas as pd
    if os.path.exists(PKL):
        return pd.read_pickle(PKL)
    d = pd.read_excel(os.path.join(CACHE, "mpt_histdata.xlsx"), sheet_name="DATA")
    d = d[d.field.str.match(r"Prob: \d")]
    out = {}
    for (day, rs, cur), g in d.groupby(["date", "reference_start", "target_range"]):
        lo = int(str(cur).split("bps")[0])
        pr = {int(f.split()[1].replace("bps", "")): v / 100 for f, v in zip(g.field, g.value)}
        tot = sum(pr.values())
        out[(str(day)[:10], str(rs)[:10])] = {"cur": lo, "p": {k: v / tot for k, v in pr.items()}}
    pd.to_pickle(out, PKL)
    return out


def implied(M, day, meet):
    """Options-implied chance of each move (in 25bp steps) at the meeting on `meet`, seen with the file of `day`.
    Only for meetings that sit on a quarter's first day (the March / June / September / December meetings, the
    December one up to 8 days early): the quarter that starts there is mostly the rate set at that meeting.
    The next meeting, about 6 weeks into the quarter, blurs it a bit (said in the report)."""
    md = dt.date.fromisoformat(meet)
    for k in range(0, 9):
        r = M.get((day, (md + dt.timedelta(days=k)).isoformat()))
        if r:
            out = collections.defaultdict(float)
            for lo, p in r["p"].items():
                out[round((lo - r["cur"]) / 25)] += p
            return dict(out), r["cur"]
    return None, None


def obs_day(M_days, t):
    """Newest file day strictly before the day of t (the file for day D comes out the next morning)."""
    d = d10(t)
    best = None
    for x in M_days:
        if x < d:
            best = x
        else:
            break
    return best


K_OUT = {"H26": lambda k: k >= 2, "H25": lambda k: k == 1, "H0": lambda k: k == 0, "C25": lambda k: k == -1,
         "C26": lambda k: k <= -2}


def p_rule(item):
    s = str(item).lower().strip()
    if "no change" in s:
        return lambda k: k == 0
    m = re.match(r"(\d+)(\+?) bps (decrease|increase)", s)
    if not m:
        return None
    n, plus, way = int(m.group(1)) // 25, m.group(2) == "+", m.group(3)
    n = -n if way == "decrease" else n
    if plus:
        return (lambda k, n=n: k <= n) if n < 0 else (lambda k, n=n: k >= n)
    return lambda k, n=n: k == n


def k_quote(cs, t):
    best = None
    for c in cs:
        if c[0] <= t:
            best = c
        else:
            break
    if not best or best[0] < t - 12 * 3600 or best[1] is None or best[2] is None:
        return None
    return best[1], best[2]


def points():
    """One row per market per look: options-implied chance, market price, result."""
    import families
    import khouse
    M = mpt()
    days = sorted({k[0] for k in M})
    rows = []
    km = khouse.rj(os.path.join(CACHE, "kmarkets.json.gz"))
    tp = khouse.rj(os.path.join(CACHE, "tapes_KXFEDDECISION.json.gz"))
    tpf = khouse.rj(os.path.join(CACHE, "tapes_KXFED.json.gz"))
    for v in list(tp.values()) + list(tpf.values()):     # Kalshi's 100-times-too-small quote trap (dates.load)
        vals = [x for c in v["c"] for x in c[1:3] if x is not None]
        if vals and max(vals) <= 0.0101 and v["tr"] and max(t[1] for t in v["tr"]) > 20:
            for c in v["c"]:
                c[1] = None if c[1] is None else round(c[1] * 100, 4)
                c[2] = None if c[2] is None else round(c[2] * 100, 4)
    for s, tapes in (("KXFEDDECISION", tp), ("KXFED", tpf)):
        for tk, m in km[s].items():
            meet = d10(m["close"])
            if tk not in tapes:
                continue
            cs = sorted(tapes[tk]["c"])
            for L in LOOKS:
                t = int(dt.datetime.fromisoformat(meet).replace(tzinfo=UTC).timestamp()) - L * DAY + 15 * 3600
                if t < m["open"]:
                    continue
                od = obs_day(days, t)
                P, cur = implied(M, od, meet) if od else (None, None)
                if P is None:
                    continue
                if s == "KXFEDDECISION":
                    f = K_OUT.get(tk.split("-")[-1])
                else:
                    x = re.search(r"-T(\d+\.\d+)$", tk)
                    lvl = round(float(x.group(1)) * 100) if x else None
                    f = (lambda k, lvl=lvl, cur=cur: cur + 25 + 25 * k > lvl) if lvl else None
                if not f:
                    continue
                q = k_quote(cs, t)
                if not q:
                    continue
                pi = sum(v for k, v in P.items() if f(k))
                rows.append({"site": "kalshi", "s": s, "ev": m["ev"], "meet": meet, "L": L, "t": t, "id": tk,
                             "imp": pi, "bid": q[0], "ask": q[1], "won": m["res"] == "yes"})
    ms, tpp = families.load("fed-rates")
    for mid, m in ms.items():
        if not re.match(r"fed-(interest-rates|decision-in)", m["ev_slug"]) or mid not in tpp:
            continue
        f = p_rule(m.get("item"))
        if not f or not m.get("closed_t"):
            continue
        meet = d10(m["closed_t"] - 6 * 3600)
        b = tpp[mid]["b"]
        for L in LOOKS:
            t = int(dt.datetime.fromisoformat(meet).replace(tzinfo=UTC).timestamp()) - L * DAY + 15 * 3600
            od = obs_day(days, t)
            P, cur = implied(M, od, meet) if od else (None, None)
            if P is None:
                continue
            nxt = [x for x in b if t <= x[0] < t + 7200]
            prv = [x for x in b if t - 6 * 3600 <= x[0] < t]
            if not nxt or not prv:
                continue
            rows.append({"site": "poly", "s": "PM", "ev": m["ev_slug"], "meet": meet, "L": L, "t": t, "id": mid,
                         "imp": sum(v for k, v in P.items() if f(k)), "last": prv[-1][4],
                         "hi": max(x[4] for x in nxt), "lo": min(x[3] for x in nxt), "fee": m.get("fee") or 0.0,
                         "won": m["final"][0] == 1.0})
    return rows


def cost(r, yes, extra=0.0):
    """$ paid for one $1 share at the real price (+extra), fee included, or None if not buyable at 1-97c."""
    if r["site"] == "kalshi":
        px = r["ask"] if yes else 1 - r["bid"]
        if not 0.01 <= px <= 0.97:
            return None
        px = min(0.99, px + extra)
        return px + k_fee(px)
    px = r["hi"] if yes else 1 - r["lo"]
    if not 0.01 <= px <= 0.97:
        return None
    px = min(0.99, px + extra)
    return px + px * (1 - px) * r["fee"]


def mid(r):
    return (r["bid"] + r["ask"]) / 2 if r["site"] == "kalshi" else r["last"]


def run():
    import exam
    rows = points()
    meets = collections.Counter((r["site"], r["meet"]) for r in rows)
    print(f"points {len(rows)}; meetings: {sorted(meets)}")
    print("\n## Who guesses better? (lower is better)\n")
    print("| Site | Days before | Points | Meetings | Options score | Market score |")
    print("|---|---|---|---|---|---|")
    for site in ("kalshi", "poly"):
        for L in LOOKS:
            rr = [r for r in rows if r["site"] == site and r["L"] == L]
            if not rr:
                continue
            bi = sum((r["imp"] - r["won"]) ** 2 for r in rr) / len(rr)
            bm = sum((mid(r) - r["won"]) ** 2 for r in rr) / len(rr)
            print(f"| {site} | {L} | {len(rr)} | {len({r['meet'] for r in rr})} | {bi:.4f} | {bm:.4f} |")
    print("\n## Biggest disagreements (options minus market, 7 days or less before)\n")
    for r in sorted((r for r in rows if r["L"] <= 7), key=lambda r: -abs(r["imp"] - mid(r)))[:25]:
        print(f"- {r['site']} {r['id']} {r['L']}d: options {r['imp']:.2f}, market {mid(r):.2f}, won {r['won']}")
    bets_all = {}
    for thr in (0.05, 0.10, 0.20):
        for site in ("kalshi", "poly", "both"):
            bets = []
            seen = set()
            for r in sorted(rows, key=lambda r: -r["L"]):
                if site != "both" and r["site"] != site:
                    continue
                for yes in (True, False):
                    c = cost(r, yes)
                    if c is None:
                        continue
                    fair = r["imp"] if yes else 1 - r["imp"]
                    if fair - c < thr:
                        continue
                    key = (r["id"], yes)
                    if key in seen:          # one bet per market and side: the earliest look that qualifies
                        continue
                    seen.add(key)
                    win = r["won"] == yes
                    sh = 25 / c
                    bets.append({"ev": r["meet"], "t": r["t"], "cost": 25.0, "pay": sh if win else 0.0,
                                 "id": r["id"], "yes": yes, "c": c, "fair": fair, "site": r["site"]})
            bets_all[(thr, site)] = bets
            exam.score(bets, f"Fed decisions vs options odds ({site}, {int(thr * 100)}c+)", tries=12,
                       src="fed.py run", log=(thr == 0.10 and site == "both"), status="dropped")
    for b in bets_all[(0.10, "both")]:
        print(f"  BET {b['site']} {b['id']} {'Yes' if b['yes'] else 'No'} cost {b['c']:.2f} options {b['fair']:.2f} "
              f"-> {'won' if b['pay'] else 'lost'}")
    return rows


# ---------------------------------------------------------------- one site against the other
KS = range(-4, 5)
MON = ("january", "february", "march", "april", "may", "june", "july", "august", "september", "october",
       "november", "december")


def k_tapes(series):
    import khouse
    tp = khouse.rj(os.path.join(CACHE, f"tapes_{series}.json.gz"), {}) or {}
    for v in tp.values():
        vals = [x for c in v["c"] for x in c[1:3] if x is not None]
        if vals and max(vals) <= 0.0101 and v["tr"] and max(t[1] for t in v["tr"]) > 20:
            for c in v["c"]:
                c[1] = None if c[1] is None else round(c[1] * 100, 4)
                c[2] = None if c[2] is None else round(c[2] * 100, 4)
        v["c"].sort()
    return tp


def pm_now(b, t, window=7200):
    """Polymarket at t: last real trade of the 6 hours before, and the worst Yes / No price of the next 2 hours."""
    prv = [x for x in b if t - 6 * 3600 <= x[0] < t]
    nxt = [x for x in b if t <= x[0] < t + window]
    if not prv or not nxt:
        return None
    return prv[-1][4], max(x[4] for x in nxt), min(x[3] for x in nxt)


def cross_bets(pairs, gap, step=6 * 3600, span=28 * DAY):
    """pairs: [(ev, t_end, kalshi fair fn(t) -> (bid, ask) or None, pm market, pm trades, won)].
    Two rules, one bet per market and side, earliest moment that fits:
      buy on Polymarket when its real price is `gap`+ cheaper than Kalshi's (Kalshi's bid for Yes, ask for No);
      buy on Kalshi when Kalshi's real ask is `gap`+ under Polymarket's last trade."""
    pmb, kb = [], []
    for ev, t_end, kq, m, b, won, kfee in pairs:
        seen = set()
        t = t_end - span
        while t < t_end - 3600:
            q, p = kq(t), pm_now(b, t)
            t += step
            if not q or not p:
                continue
            bid, ask = q
            last, hi, lo = p
            fee = m.get("fee") or 0.0
            for yes in (True, False):
                px = hi if yes else 1 - lo
                fair = bid if yes else 1 - ask
                if ("p", yes) not in seen and 0.02 <= px <= 0.97 and fair - (px + px * (1 - px) * fee) >= gap:
                    seen.add(("p", yes))
                    c = px + px * (1 - px) * fee
                    pmb.append({"ev": ev, "t": t, "cost": 25.0, "pay": 25 / c if won == yes else 0.0})
                kpx = ask if yes else 1 - bid
                pfair = last if yes else 1 - last
                if kfee and ("k", yes) not in seen and 0.02 <= kpx <= 0.97 and pfair - (kpx + k_fee(kpx)) >= gap:
                    seen.add(("k", yes))
                    c = kpx + k_fee(kpx)
                    kb.append({"ev": ev, "t": t, "cost": 25.0, "pay": 25 / c if won == yes else 0.0})
    return pmb, kb


def fed_pairs():
    import families
    import khouse
    km = khouse.rj(os.path.join(CACHE, "kmarkets.json.gz"))
    tp = k_tapes("KXFEDDECISION")
    kby = {}
    for tk, m in km["KXFEDDECISION"].items():
        f = K_OUT.get(tk.split("-")[-1])
        if f and tk in tp:
            kby[(d10(m["close"]), frozenset(k for k in KS if f(k)))] = (tk, tp[tk]["c"])
    ms, tpp = families.load("fed-rates")
    pairs = []
    for mid, m in ms.items():
        if not re.match(r"fed-(interest-rates|decision-in)", m["ev_slug"]) or mid not in tpp or not m.get("closed_t"):
            continue
        f = p_rule(m.get("item"))
        if not f:
            continue
        meet = d10(m["closed_t"] - 6 * 3600)
        hit = kby.get((meet, frozenset(k for k in KS if f(k))))
        if not hit:
            continue
        t_end = int(dt.datetime.fromisoformat(meet).replace(tzinfo=UTC).timestamp()) + 18 * 3600
        pairs.append((meet, t_end, (lambda cs: lambda t: k_quote(cs, t))(hit[1]), m, tpp[mid]["b"],
                      m["final"][0] == 1.0, True))
    return pairs


def cpi_pairs():
    """Polymarket US CPI brackets ("0.3%", "<=0.1%", ">=0.8%") vs the same bracket built from Kalshi's
    "above X" ladder: bracket x = above(x - 0.1) minus above(x); Kalshi bid/ask of the bracket from both rungs."""
    import families
    import khouse
    km = khouse.rj(os.path.join(CACHE, "kmarkets.json.gz"))
    fams = {"KXCPI": r"^(\w+)-inflation-us-monthly", "KXCPIYOY": r"^(\w+)-inflation-us-annual",
            "KXCPICORE": r"^core-cpi-(?:ex-food-and-energy-)?mom-(\w+)"}
    ms, tpp = families.load("cpi")
    pairs = []
    for ser, rx in fams.items():
        tp = k_tapes(ser)
        lad = collections.defaultdict(dict)
        for tk, m in km[ser].items():
            x = re.search(r"-(\d\d)([A-Z]{3})-T(-?\d+\.\d+)$", tk)
            if x and tk in tp:
                lad[(2000 + int(x.group(1)), x.group(2))][round(float(x.group(3)), 1)] = tp[tk]["c"]
        for mid, m in ms.items():
            g = re.match(rx, m["ev_slug"])
            if not g or g.group(1) not in MON or mid not in tpp or not m.get("end"):
                continue
            mon = MON.index(g.group(1)) + 1
            y = int(d10(m["end"])[:4]) - (1 if mon == 12 and d10(m["end"])[5:7] == "01" else 0)
            L = lad.get((y, MON[mon - 1][:3].upper()))
            it = str(m.get("item") or "").replace("%", "").strip()
            v = re.match(r"^(≤|≥|<=|>=)?\s*(-?\d+\.\d)$", it)
            if not L or not v:
                continue
            x = float(v.group(2))
            if v.group(1) in ("≤", "<="):
                rungs = [(round(x, 1), -1)]                  # 1 - above(x)
            elif v.group(1) in ("≥", ">="):
                rungs = [(round(x - 0.1, 1), +1)]            # above(x - 0.1)
            else:
                rungs = [(round(x - 0.1, 1), +1), (round(x, 1), -1)]
            if any(r not in L for r, _ in rungs):
                continue

            def kq(t, L=L, rungs=rungs):
                bid = ask = 1.0 if rungs[0][1] == -1 and len(rungs) == 1 else 0.0
                for r, sg in rungs:
                    q = k_quote(L[r], t)
                    if not q:
                        return None
                    if sg > 0:
                        bid += q[0]
                        ask += q[1]
                    else:
                        bid -= q[1]
                        ask -= q[0]
                return (max(0.0, bid), min(1.0, ask)) if ask - bid <= 0.10 else None
            pairs.append((m["ev_slug"], m["end"], kq, m, tpp[mid]["b"], m["final"][0] == 1.0, len(rungs) == 1))
    return pairs


def cross():
    import exam
    for name, pairs in (("Fed decisions", fed_pairs()), ("US CPI", cpi_pairs())):
        print(f"\n## {name}: {len(pairs)} Polymarket markets with a Kalshi twin, {len({p[0] for p in pairs})} events")
        for gap in (0.03, 0.05, 0.10):
            pmb, kb = cross_bets(pairs, gap)
            exam.score(pmb, f"{name}: buy on Polymarket {int(gap * 100)}c+ under Kalshi", tries=12, src="fed.py cross",
                       log=gap in (0.05, 0.10), status="dropped")
            exam.score(kb, f"{name}: buy on Kalshi {int(gap * 100)}c+ under Polymarket", tries=12, src="fed.py cross",
                       log=gap == 0.05, status="dropped")
        if name == "US CPI":            # read the 10c+ Polymarket bets one by one (they are the only ones ahead)
            for ev, t_end, kq, m, b, won, one in pairs:
                t, seen = t_end - 28 * DAY, set()
                while t < t_end - 3600:
                    q, p = kq(t), pm_now(b, t)
                    t0, t = t, t + 6 * 3600
                    if not q or not p:
                        continue
                    for yes in (True, False):
                        px = p[1] if yes else 1 - p[2]
                        fair = q[0] if yes else 1 - q[1]
                        if yes not in seen and 0.02 <= px <= 0.97 and fair - px >= 0.10:
                            seen.add(yes)
                            usd = sum(x[5] for x in b if t0 <= x[0] < t0 + 7200)
                            print(f"  CPI BET {ev[:42]} {m.get('item')} {'Yes' if yes else 'No'}: paid {px:.2f}, Kalshi "
                                  f"{fair:.2f}, {(t_end - t0) / DAY:.0f} days before, ${usd:,.0f} traded in those 2 hours, "
                                  f"{'won' if won == yes else 'lost'}")


# ---------------------------------------------------------------- backward look: what did winners have in common?
def backward():
    """Every Fed decision market on both sites (all meetings, not only quarter-start ones) at 1-28 days before:
    how often each price band won, then the two sides the table points to (favourites, No on long shots)."""
    import exam
    import families
    import khouse
    km = khouse.rj(os.path.join(CACHE, "kmarkets.json.gz"))
    tp = k_tapes("KXFEDDECISION")
    rows = []
    for tk, m in km["KXFEDDECISION"].items():
        if tk not in tp:
            continue
        meet = d10(m["close"])
        T = int(dt.datetime.fromisoformat(meet).replace(tzinfo=UTC).timestamp())
        for L in (1, 3, 7, 14, 28):
            q = k_quote(tp[tk]["c"], T - L * DAY + 15 * 3600)
            if q:
                rows.append(dict(site="kalshi", ev=meet, L=L, t=T - L * DAY, bid=q[0], ask=q[1], won=m["res"] == "yes"))
    ms, tpp = families.load("fed-rates")
    for mid_, m in ms.items():
        if not re.match(r"fed-(interest-rates|decision-in)", m["ev_slug"]) or mid_ not in tpp or not m.get("closed_t"):
            continue
        meet = d10(m["closed_t"] - 6 * 3600)
        T = int(dt.datetime.fromisoformat(meet).replace(tzinfo=UTC).timestamp())
        for L in (1, 3, 7, 14, 28):
            p = pm_now(tpp[mid_]["b"], T - L * DAY + 15 * 3600)
            if p:
                rows.append(dict(site="poly", ev=meet, L=L, t=T - L * DAY, last=p[0], hi=p[1], lo=p[2],
                                 fee=m.get("fee") or 0, won=m["final"][0] == 1.0))
    print(f"\n## Backward look: {len(rows)} looks, {len({(r['site'], r['ev']) for r in rows})} site-meetings\n")
    print("| Site | Price band | Looks | Average price | Share that won | Meetings |")
    print("|---|---|---|---|---|---|")
    for site in ("kalshi", "poly"):
        for lo, hi in ((0.02, 0.10), (0.10, 0.30), (0.30, 0.70), (0.70, 0.90), (0.90, 0.98)):
            rr = [r for r in rows if r["site"] == site and lo <= mid(r) < hi]
            if rr:
                print(f"| {site} | {int(lo * 100)}-{int(hi * 100)}c | {len(rr)} | {sum(mid(r) for r in rr) / len(rr):.2f} | "
                      f"{sum(r['won'] for r in rr) / len(rr):.2f} | {len({r['ev'] for r in rr})} |")
    for name, sel, yes in (("Fed: buy the favourite at 85-97c", lambda r: 0.85 <= mid(r) < 0.97, True),
                           ("Fed: buy No on long shots at 3-15c", lambda r: 0.03 <= mid(r) < 0.15, False)):
        for L in (1, 7, 28):
            bets = []
            for r in rows:
                if r["L"] != L or not sel(r):
                    continue
                c = cost(r, yes)
                if c is not None:
                    bets.append(dict(ev=r["ev"], t=r["t"], cost=25.0, pay=25 / c if r["won"] == yes else 0.0))
            exam.score(bets, f"{name}, {L} days before (both sites)", tries=12, src="fed.py backward", log=(L == 7),
                       status="dropped")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "src"
    {"src": src, "fetch": fetch, "run": run, "cross": cross, "backward": backward, "all": lambda: (run(), cross(), backward())}[cmd]()
