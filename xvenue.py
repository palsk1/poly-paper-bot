#!/usr/bin/env python3
"""Same bet, two sites: Kalshi's and Polymarket's 15-minute crypto "up or down" windows (research only).

The idea (popular on Reddit/GitHub as a "risk-free arb bot"): both sites list "is BTC higher at 10:15 than at
10:00". Buy UP on one site and DOWN on the other. If the two cost less than $1 together, one of them pays $1.

What this tool checks, on the recorder's real order books and trade tapes (releases data-YYYYMMDD):
  1. how far apart in time the recorder reads the two sites (it matters: these prices move ~1c every 5 s)
  2. what the pair really costs after both fees, read at the same second
  3. what happens if you buy every "gap", scored on the real results of both sites
  4. how often the two sites disagree on the result (they use different price feeds, so a pair can pay $0 or $2)

Fill prices: Polymarket = the recorded asks, walked for SHARES shares. Kalshi = the WORST price a real taker paid
for that side within +-HALF seconds of the Polymarket read (Kalshi books list bids only and the recorder reads
them ~17 s earlier, so the tape is the honest price at that second). Fees: Kalshi taker 7c x P x (1-P) rounded up,
Polymarket the market's own fee rate.

Usage:  python3 xvenue.py results [days]   real results of both sites -> xv_cache/results.json.gz, mismatch table
        python3 xvenue.py run              replay on the recordings, writes backtest/xvenue.md
        python3 xvenue.py all [days]       both
        python3 xvenue.py live [min] [s]   live: read both books in the same second every few seconds, re-read gaps 2 s later
        python3 xvenue.py selftest         fake data: a fair world must lose its costs, a planted gap must be found
Probe: xv_results_<days>, xv_run, xv_all_<days>, xv_live_<minutes>, xv_selftest.  XV_REC_DIR=<folder> uses already downloaded files.
"""
import bisect
import collections
import datetime as dt
import glob
import gzip
import json
import math
import os
import random
import re
import statistics as st
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import bot
import kcrypto

CACHE = os.path.join(bot.ROOT, "xv_cache")
REC_DIR = os.environ.get("XV_REC_DIR") or os.path.join(CACHE, "rec")
RES_PATH = os.path.join(CACHE, "results.json.gz")
OUT = os.path.join(bot.ROOT, "backtest", "xvenue.md")
# coin -> (Kalshi series, Polymarket slug prefix). Gold/silver are listed on both too but on different metals feeds.
PAIRS = {"BTC": ("KXBTC15M", "btc"), "ETH": ("KXETH15M", "eth"), "SOL": ("KXSOL15M", "sol"),
         "XRP": ("KXXRP15M", "xrp"), "DOGE": ("KXDOGE15M", "doge"), "BNB": ("KXBNB15M", "bnb"),
         "HYPE": ("KXHYPE15M", "hype"), "ZEC": ("KXZEC15M", "zec")}
K2COIN = {v[0]: k for k, v in PAIRS.items()}
P2COIN = {v[1]: k for k, v in PAIRS.items()}
SHARES = 10
HALF = 5            # Kalshi tape window around the Polymarket read, seconds each way
DEFAULT_PFEE = 0.07
KRE = re.compile(r"^(KX[A-Z]+15M)-")
PRE = re.compile(r"^([a-z]+)-updown-15m-(\d+)$")


def money(x):
    return f"{'-' if x < 0 else '+'}${abs(x):.2f}"


# ================================================================ results of both sites

def poly_results(prefix, starts):
    """{start: {"p": 1 Up won / 0 Down won, "fee": rate}} from gamma, 20 slugs a call."""
    out = {}

    def take(m):
        g = PRE.match(str(m.get("slug") or ""))
        if not g:
            return
        try:
            names = json.loads(m.get("outcomes") or "[]")
            prices = [float(x) for x in json.loads(m.get("outcomePrices") or "[]")]
        except Exception:
            return
        if len(names) != 2 or len(prices) != 2 or not m.get("closed") or sorted(prices) != [0.0, 1.0]:
            return
        up = [i for i, n in enumerate(names) if str(n).lower() == "up"]
        if up:
            out[int(g.group(2))] = {"p": int(prices[up[0]] == 1.0), "fee": bot.fee_rate(m)}

    def batch(chunk):
        try:
            rows = bot.envelope_rows(bot.http_json(f"{bot.GAMMA}/markets", {
                "slug": [f"{prefix}-updown-15m-{s}" for s in chunk], "closed": "true", "limit": 100}), "markets", "data")
        except Exception as e:
            print(f"  gamma batch failed: {e}")
            rows = []
        return rows

    chunks = [starts[i:i + 20] for i in range(0, len(starts), 20)]
    with ThreadPoolExecutor(6) as ex:
        for rows in ex.map(batch, chunks):
            for m in rows:
                if isinstance(m, dict):
                    take(m)
    return out


def results(days=30):
    days = int(days)
    t1 = int(time.time()) - 1800
    t0 = t1 - days * 86400
    res = kcrypto.rjson(RES_PATH, {}) or {}
    for coin, (series, prefix) in PAIRS.items():
        ks = kcrypto.list_markets(series, t0, t1)
        starts = sorted({m["close"] - 900 for m in ks if f"{coin}:{m['close']}" not in res or "p" not in res[f"{coin}:{m['close']}"]})
        ps = poly_results(prefix, starts)
        n = 0
        for m in ks:
            key = f"{coin}:{m['close']}"
            row = res.setdefault(key, {})
            row.update({"k": int(m["res"] == "yes"), "strike": m["strike"], "kvol": m["vol"]})
            p = ps.get(m["close"] - 900)
            if p:
                row.update(p)
            n += "p" in row
        print(f"{coin}: {len(ks)} Kalshi windows, {n} with a Polymarket result too")
    kcrypto.wjson(RES_PATH, res)
    for ln in mismatch_lines(res):
        print(ln)
    return res


def mismatch_lines(res, since=None):
    by = collections.defaultdict(lambda: [0, 0, 0, 0])   # both, agree, K up + P down, K down + P up
    for key, r in res.items():
        coin, close = key.split(":")
        if "k" not in r or "p" not in r or (since and int(close) < since):
            continue
        b = by[coin]
        b[0] += 1
        b[1] += r["k"] == r["p"]
        b[2] += r["k"] == 1 and r["p"] == 0
        b[3] += r["k"] == 0 and r["p"] == 1
    out = ["| Coin | Windows on both sites | Same result | Kalshi up, Polymarket down | Kalshi down, Polymarket up | Disagree, out of 1,000 |",
           "|---|---|---|---|---|---|"]
    tot = [0, 0, 0, 0]
    for coin in PAIRS:
        b = by.get(coin)
        if not b or not b[0]:
            continue
        tot = [a + c for a, c in zip(tot, b)]
        out.append(f"| {coin} | {b[0]:,} | {b[1]:,} | {b[2]} | {b[3]} | {1000 * (b[2] + b[3]) / b[0]:.0f} |")
    if tot[0]:
        out.append(f"| **All** | {tot[0]:,} | {tot[1]:,} | {tot[2]} | {tot[3]} | {1000 * (tot[2] + tot[3]) / tot[0]:.0f} |")
    return out


# ================================================================ recordings

def download_recordings():
    os.makedirs(REC_DIR, exist_ok=True)
    if os.environ.get("XV_REC_DIR"):
        return
    hdr = {"User-Agent": "xvenue", "Accept": "application/vnd.github+json"}
    if os.environ.get("GH_TOKEN"):
        hdr["Authorization"] = "Bearer " + os.environ["GH_TOKEN"]
    todo = []
    for page in range(1, 6):
        req = urllib.request.Request(f"https://api.github.com/repos/palsk1/poly-paper-bot/releases?per_page=100&page={page}", headers=hdr)
        rels = json.loads(urllib.request.urlopen(req, timeout=30).read())
        for r in rels:
            if str(r.get("tag_name", "")).startswith("data-"):
                todo += [(a["name"], a["browser_download_url"], a["size"]) for a in r.get("assets") or [] if a["name"].startswith("rec-")]
        if len(rels) < 100:
            break

    def one(a):
        path = os.path.join(REC_DIR, a[0])
        if os.path.exists(path) and os.path.getsize(path) == a[2]:
            return
        for i in range(3):
            try:
                urllib.request.urlretrieve(a[1], path + ".tmp")
                os.replace(path + ".tmp", path)
                return
            except Exception as e:
                print(f"  {a[0]}: {e}")
                time.sleep(3 + 3 * i)
    with ThreadPoolExecutor(6) as ex:
        list(ex.map(one, todo))
    print(f"recordings: {len(todo)} hour files in {REC_DIR}")


def iso_s(s):
    return dt.datetime.strptime(s[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=dt.timezone.utc).timestamp() + \
        (float("0." + s[20:].rstrip("Z")) if len(s) > 20 and s[19] == "." else 0.0)


def load_recordings():
    """win[(coin, close)] = {"kb": [(t, yes bid, yes ask)], "kt": [(time, yes price, taker side)],
                             "pb": [(t, bids, asks)], "pt": [(time, Up price)]}"""
    ktk, ptok, pcid = {}, {}, {}
    win = collections.defaultdict(lambda: {"kb": [], "kt": [], "pb": [], "pt": []})
    files = sorted(glob.glob(os.path.join(REC_DIR, "rec-*.jsonl.gz")))
    for f in files:
        try:
            with gzip.open(f, "rt") as fh:
                for ln in fh:
                    d = json.loads(ln)
                    k = d.get("k")
                    if k == "meta" and d.get("set") == "fast":
                        for m in d.get("kalshi") or []:
                            g = KRE.match(m.get("tk") or "")
                            if g and g.group(1) in K2COIN and m.get("cl"):
                                ktk[m["tk"]] = (K2COIN[g.group(1)], int(iso_s(m["cl"])))
                        for m in d.get("poly") or []:
                            g = PRE.match(m.get("slug") or "")
                            if g and g.group(1) in P2COIN:
                                key = (P2COIN[g.group(1)], int(g.group(2)) + 900)
                                ptok[m["tok"]] = key
                                pcid[m["cid"]] = key
                    elif k == "kbook" and d["tk"] in ktk and d.get("yb") and d.get("nb"):
                        win[ktk[d["tk"]]]["kb"].append((d["t"], d["yb"][0][0], round(1 - d["nb"][0][0], 4)))
                    elif k == "pbook" and d["tok"] in ptok:
                        win[ptok[d["tok"]]]["pb"].append((d["t"], d["b"][:8], d["a"][:8]))
                    elif k == "ktrade" and d.get("ticker") in ktk:
                        win[ktk[d["ticker"]]]["kt"].append((iso_s(d["created_time"]), float(d["yes_price_dollars"]), d.get("taker_side")))
                    elif k == "ptrade" and d.get("cid") in pcid and d.get("timestamp"):
                        up = str(d.get("outcome", "")).lower() == "up"
                        win[pcid[d["cid"]]]["pt"].append((float(d["timestamp"]), float(d["price"]) if up else 1 - float(d["price"])))
        except Exception as e:
            print(f"  {os.path.basename(f)}: {e}")
    for w in win.values():
        for key in ("kb", "kt", "pb", "pt"):
            w[key].sort(key=lambda r: r[0])
    return {k: w for k, w in win.items() if w["pb"] and w["kt"]}, len(files)


def read_offsets(win):
    """How many seconds after the recorder's pass time each site's book was really read: the shift at which the
    book's middle price sits closest to that site's own trades."""
    out = {}
    for name, bk, tk in (("Kalshi", "kb", "kt"), ("Polymarket", "pb", "pt")):
        err = collections.defaultdict(list)
        for (coin, close), w in win.items():
            ts = [r[0] for r in w[tk]]
            for row in w[bk]:
                t = row[0]
                if not (close - 900 < t < close - 30):
                    continue
                if bk == "kb":
                    bid, ask = row[1], row[2]
                else:
                    if not row[1] or not row[2]:
                        continue
                    bid, ask = row[1][0][0], row[2][0][0]
                if ask - bid > 0.03:
                    continue
                for d in range(-10, 61, 5):
                    i = bisect.bisect_right(ts, t + d) - 1
                    if i >= 0 and t + d - ts[i] < 3:
                        err[d].append(abs(w[tk][i][1] - (bid + ask) / 2))
        tab = {d: st.mean(v) for d, v in err.items() if len(v) >= 30}
        out[name] = (min(tab, key=tab.get) if tab else 0, tab)
    return out


def walk(levels, n):
    need, cost = n, 0.0
    for p, s in levels:
        q = min(need, s)
        cost += q * p
        need -= q
        if need <= 1e-9:
            return cost / n
    return None


def kfee(n, p):
    return math.ceil(0.07 * n * p * (1 - p) * 100 - 1e-9) / 100


def pair_reads(win, res, p_delta, k_mode, half=HALF, shares=SHARES):
    """Every moment both sites can be priced. k_mode "tape": Kalshi = worst real taker price within +-half s of the
    true Polymarket read time. k_mode "book": Kalshi = the book the recorder saved in the same pass (the naive way).
    Row: (coin, close, secs to end, combo, kalshi price, poly price, total cost a pair incl. fees, pays or None)"""
    rows = []
    for (coin, close), w in win.items():
        r = res.get(f"{coin}:{close}") or {}
        rate = r.get("fee", DEFAULT_PFEE)
        ts = [x[0] for x in w["kt"]]
        kbt = [x[0] for x in w["kb"]]
        for t, bids, asks in w["pb"]:
            if not (close - 900 <= t < close - 45):
                continue
            if k_mode == "tape":
                tr = w["kt"][bisect.bisect_left(ts, t + p_delta - half):bisect.bisect_right(ts, t + p_delta + half)]
            else:
                i = bisect.bisect_right(kbt, t) - 1
                if i < 0 or t - kbt[i] > 130:
                    continue
                kb = w["kb"][i]
            for combo in "AB":   # A: Kalshi UP + Polymarket DOWN.  B: Kalshi DOWN + Polymarket UP
                if combo == "A":
                    pa = walk([(round(1 - p, 4), s) for p, s in bids], shares)
                    kp = [x[1] for x in tr if x[2] == "yes"] if k_mode == "tape" else [kb[2]]
                else:
                    pa = walk(asks, shares)
                    kp = [1 - x[1] for x in tr if x[2] == "no"] if k_mode == "tape" else [1 - kb[1]]
                if not kp or pa is None:
                    continue
                ka = max(kp)
                if not (0.005 < ka < 0.995 and 0.005 < pa < 0.995):
                    continue
                tot = ka + pa + (kfee(shares, ka) + bot.taker_fee(shares, pa, rate)) / shares
                pays = None
                if "k" in r and "p" in r:
                    pays = (r["k"] if combo == "A" else 1 - r["k"]) + (1 - r["p"] if combo == "A" else r["p"])
                rows.append((coin, close, t - close, combo, ka, pa, tot, pays))
    return rows


def take_gaps(rows, limit):
    """Buy the first read per window and combo whose total cost is under `limit`. Returns list of (cost, pays, row)."""
    seen, out = set(), []
    for r in sorted(rows, key=lambda r: (r[1], r[2])):
        if r[6] < limit and r[7] is not None and (r[0], r[1], r[3]) not in seen:
            seen.add((r[0], r[1], r[3]))
            out.append(r)
    return out


def score(bets, shares=SHARES):
    """Money for `shares` pairs a bet. Luck range: resample whole windows (coins in one window move together)."""
    if not bets:
        return None
    pnl = [(r[7] - r[6]) * shares for r in bets]
    cost = [r[6] * shares for r in bets]
    by = collections.defaultdict(lambda: [0.0, 0.0])
    for r, p, c in zip(bets, pnl, cost):
        by[r[1]][0] += p
        by[r[1]][1] += c
    keys = list(by)
    rnd = random.Random(7)
    boots = []
    for _ in range(2000):
        pick = [by[rnd.choice(keys)] for _ in keys]
        boots.append(100 * sum(x[0] for x in pick) / max(1e-9, sum(x[1] for x in pick)))
    boots.sort()
    return {"n": len(bets), "cost": sum(cost), "pnl": sum(pnl), "per100": 100 * sum(pnl) / sum(cost),
            "lo": boots[100], "hi": boots[1899], "zero": sum(r[7] == 0 for r in bets), "two": sum(r[7] == 2 for r in bets),
            "windows": len(keys)}


def score_line(label, s):
    if not s:
        return f"| {label} | 0 | | | | | |"
    return (f"| {label} | {s['n']} | ${s['cost']:,.0f} | {money(s['pnl'])} | **{money(s['per100'])}** | "
            f"{money(s['lo'])} to {money(s['hi'])} | {s['zero']} / {s['two']} |")


def run():
    res = kcrypto.rjson(RES_PATH, {}) or {}
    download_recordings()
    win, nfiles = load_recordings()
    if not win:
        print("no paired windows in the recordings")
        return
    t_lo, t_hi = min(c for _, c in win), max(c for _, c in win)
    offs = read_offsets(win)
    k_delta, p_delta = offs["Kalshi"][0], offs["Polymarket"][0]
    naive = pair_reads(win, res, 0, "book")
    tape = {h: pair_reads(win, res, p_delta, "tape", half=h) for h in (2, 5, 8)}
    main = tape[HALF]
    L = []
    L += ["# Same bet on two sites: Kalshi vs Polymarket 15-minute crypto (xvenue.py)", "",
          f"Research only, no track. Recordings {dt.datetime.fromtimestamp(t_lo, dt.timezone.utc):%d %b %H:%M} to "
          f"{dt.datetime.fromtimestamp(t_hi, dt.timezone.utc):%d %b %H:%M} UTC ({nfiles} hour files), "
          f"{len(win)} windows listed on both sites ({', '.join(sorted({c for c, _ in win}))}). "
          f"Each bet is {SHARES} shares on each site, both fees paid.", "",
          "## 1. The recorder reads the two sites at different moments", "",
          "Each book is stamped with the minute the recorder's round started, not the second it was read. "
          "Lining each site's book up with that site's own trades shows when it was really read:", "",
          "| Seconds after the stamp | " + " | ".join(str(d) for d in range(-10, 61, 5)) + " |",
          "|---|" + "---|" * len(range(-10, 61, 5))]
    for name in ("Kalshi", "Polymarket"):
        tab = offs[name][1]
        L.append(f"| {name}: book vs its own trades, cents apart | " + " | ".join(f"{100 * tab[d]:.1f}" if d in tab else "" for d in range(-10, 61, 5)) + " |")
    L += ["", f"Best match: Kalshi at about +{k_delta} s, Polymarket at about +{p_delta} s. "
          f"So the two books in one round are about {p_delta - k_delta} seconds apart, and these prices move more than 1c every 5 seconds. "
          "Any test that compares the two books straight from one round sees gaps that were never there.", ""]

    def cost_stats(rows):
        v = [r[6] for r in rows]
        return (len(v), st.median(v), st.median([r[4] + r[5] for r in rows]), sum(a < 1 for a in v), sum(a < 0.99 for a in v), sum(a < 0.97 for a in v))
    L += ["## 2. What the pair costs", "",
          "A pair pays $1.00 when the sites agree. \"Under $1.00\" is what a bot would call a gap.", "",
          "| How the two prices are lined up | Reads | Typical cost before fees | Typical cost with fees | Under $1.00 | Under $0.99 | Under $0.97 |",
          "|---|---|---|---|---|---|---|"]
    for label, rows in [("Naive: both books from the same recorder round", naive)] + \
                       [(f"Same second: Kalshi trades within {h} s of the Polymarket read", tape[h]) for h in (2, 5, 8)]:
        if rows:
            n, med, raw, a, b, c = cost_stats(rows)
            L.append(f"| {label} | {n:,} | ${raw:.3f} | ${med:.3f} | {a} ({1000 * a / n:.0f} in 1,000) | {b} | {c} |")
    L += ["", "The stricter the line-up, the fewer gaps. That is what timing noise looks like, not free money.", "",
          "| Minutes before the end | Reads | Typical cost with fees | Under $1.00 |", "|---|---|---|---|"]
    by = collections.defaultdict(list)
    for r in main:
        by[int((-r[2] - 1) // 180) * 3].append(r[6])
    for k in sorted(by, reverse=True):
        L.append(f"| {k + 3} to {k} | {len(by[k]):,} | ${st.median(by[k]):.3f} | {sum(a < 1 for a in by[k])} |")

    L += ["", "## 3. Buying every gap, scored on the real results", "",
          "First gap per window and direction. \"Paid $0 / paid $2\" = bets where the two sites disagreed (both legs lost / both won).", "",
          "| Rule | Bets | Money in | P&L | P&L per $100 | Luck range (90 of 100) | Paid $0 / paid $2 |", "|---|---|---|---|---|---|---|"]
    scored = sum(1 for r in main if r[7] is not None)
    for label, rows in (("Naive line-up", naive), (f"Same second (+-{HALF} s)", main), ("Same second, strict (+-8 s)", tape[8])):
        for lim in (1.0, 0.99, 0.97):
            L.append(score_line(f"{label}: buy when the pair costs under ${lim:.2f}", score(take_gaps(rows, lim))))
    allp = [r for r in main if r[7] is not None]
    L.append(score_line("Control: buy the pair at every read, gap or not", score(allp)))
    L += ["", f"({scored:,} of {len(main):,} same-second reads have a result from both sites.)", ""]
    gaps = take_gaps(main, 0.99)
    if gaps:
        hot = collections.Counter(r[1] for r in gaps).most_common(3)
        L += [f"Where the {len(gaps)} under-$0.99 bets sit: " + ", ".join(
            f"{n} at {dt.datetime.fromtimestamp(c, dt.timezone.utc):%d %b %H:%M}" for c, n in hot) +
            " (several coins in the same window = one fast market move, read a few seconds apart).", ""]

    since = t_lo - 900
    L += ["## 4. How often the two sites disagree on the result", "",
          "Kalshi settles on a 60-second average of one price index, Polymarket on a single Chainlink price. "
          "When the coin ends almost exactly where it started, they can disagree. Then a pair pays $0 or $2.", ""]
    L += mismatch_lines(res)
    L += ["", "Only the days of the recordings:", ""] + mismatch_lines(res, since)
    L += ["", "## How to rerun", "", "`xv_all_30` on the probe workflow (results + replay), or `xv_run` after `xv_results_<days>`."]
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as fh:
        fh.write("\n".join(L) + "\n")
    print("\n".join(L))


# ================================================================ live check: both books in the same second

def live(minutes=120, every=3):
    """Read both sites' books within the same second, every few seconds. A pair under $1.00 is read again 2 s
    later: only gaps still there at the second read count as buyable (at the second read's prices).
    Prints one line per gap and a summary. Reads only, buys nothing, saves nothing."""
    import recorder
    minutes, every = float(minutes), float(every)
    pool = ThreadPoolExecutor(4)
    cur, cur_win, last_try = {}, None, 0

    def refresh(start):
        out = {}
        for coin, (series, prefix) in PAIRS.items():
            try:
                ks = [m for m in (kcrypto.get("/markets", {"series_ticker": series, "status": "open", "limit": 100}).get("markets") or [])
                      if kcrypto.tsec(m.get("close_time")) == start + 900]
                pm = bot.envelope_rows(bot.http_json(f"{bot.GAMMA}/markets", {"slug": f"{prefix}-updown-15m-{start}"}), "markets", "data")
                if not ks or not pm:
                    print(f"  {coin}: Kalshi {len(ks)} / Polymarket {len(pm)} markets for this window")
                if ks and pm:
                    toks = bot.market_tokens(pm[0])
                    names = [str(n).lower() for n in json.loads(pm[0].get("outcomes") or "[]")]
                    if len(toks) == 2 and names[:1] == ["up"]:
                        out[coin] = (ks[0]["ticker"], toks[0], bot.fee_rate(pm[0]))
            except Exception as e:
                print(f"  refresh {coin}: {e}")
        return out

    def read(coins):
        t0 = time.time()
        kf = {c: pool.submit(recorder.kalshi_book, cur[c][0]) for c in coins}
        pf = pool.submit(recorder.poly_books, [cur[c][1] for c in coins])
        pb = pf.result()
        out = {}
        for c in coins:
            try:
                kb = kf[c].result()
            except Exception:
                continue
            b = pb.get(cur[c][1])
            if not b or not kb["yb"] or not kb["nb"]:
                continue
            rate = cur[c][2]
            for combo in "AB":
                if combo == "A":
                    ka, pa = walk([(round(1 - p, 4), s) for p, s in kb["nb"]], SHARES), walk([(round(1 - p, 4), s) for p, s in b["b"]], SHARES)
                else:
                    ka, pa = walk([(round(1 - p, 4), s) for p, s in kb["yb"]], SHARES), walk(b["a"], SHARES)
                if ka is None or pa is None or not (0.005 < ka < 0.995 and 0.005 < pa < 0.995):
                    continue
                out[(c, combo)] = (ka, pa, ka + pa + (kfee(SHARES, ka) + bot.taker_fee(SHARES, pa, rate)) / SHARES)
        return out, time.time() - t0

    t_end = time.time() + minutes * 60
    n_reads = n_first = n_conf = 0
    costs, spans, conf, wins = [], [], [], set()
    while time.time() < t_end:
        now = time.time()
        start = int(now // 900) * 900
        left = start + 900 - now
        if start != cur_win or (len(cur) < len(PAIRS) and now - last_try > 20):
            if start != cur_win:
                cur = {}
            cur.update(refresh(start))
            cur_win, last_try = start, now
            print(f"window {dt.datetime.fromtimestamp(start, dt.timezone.utc):%H:%M}: {len(cur)} coins on both sites ({' '.join(sorted(cur))})")
        if not cur or left < 20 or left > 885:
            time.sleep(2)
            continue
        got, span = read(list(cur))
        spans.append(span)
        n_reads += len(got)
        costs += [v[2] for v in got.values()]
        wins.update((c, start) for c, _ in got)
        hits = {k: v for k, v in got.items() if v[2] < 1.0}
        if hits:
            n_first += len(hits)
            time.sleep(2)
            again, _ = read(sorted({c for c, _ in hits}))
            for k, v in hits.items():
                v2 = again.get(k)
                ok = bool(v2 and v2[2] < 1.0)
                n_conf += ok
                if ok:
                    conf.append((k[0], start, k[1], v2[2]))
                print(f"GAP {k[0]} {k[1]} {left:.0f}s left: first read K {v[0]:.3f} + P {v[1]:.3f} = ${v[2]:.3f} with fees; "
                      f"2 s later {'$%.3f' % v2[2] if v2 else 'no book'} {'STILL THERE' if ok else 'gone'}")
        time.sleep(max(0.2, every - (time.time() - now)))
    if not costs:
        print("no reads")
        return
    print(f"\nLIVE SUMMARY: {minutes:.0f} min, {len(wins)} coin-windows, {n_reads:,} pair reads, both sites read within "
          f"{st.median(spans):.1f} s (worst {max(spans):.1f} s). Typical pair cost with fees ${st.median(costs):.3f}, "
          f"cheapest ${min(costs):.3f}. Under $1.00 at the first read: {n_first}. Still under $1.00 2 s later: {n_conf}.")
    seen, total = set(), 0.0
    for c, w, combo, cost in conf:
        if (c, w, combo) not in seen:
            seen.add((c, w, combo))
            total += (1 - cost) * SHARES
    print(f"Buying each confirmed gap once per window and side ({len(seen)} bets of {SHARES} pairs): {money(total)} if the two sites agree on the result.")


# ================================================================ selftest

def selftest():
    """Fair fake world: both sites quote the true chance +-1c and always agree. Buying pairs must lose about the
    costs. Then one planted 90c pair must be found and must win."""
    rnd = random.Random(1)
    win, res = {}, {}
    for i in range(300):
        close = 1_800_000_000 + 900 * i
        p = min(0.95, max(0.05, rnd.random()))
        up = int(rnd.random() < p)
        res[f"BTC:{close}"] = {"k": up, "p": up, "fee": 0.07}
        t = close - 600
        win[("BTC", close)] = {"kb": [], "pt": [],
                               "kt": [(t + 17, round(p + 0.01, 2), "yes"), (t + 17.5, round(p - 0.01, 2), "no")],
                               "pb": [(t, [(round(p - 0.01, 2), 500)], [(round(p + 0.01, 2), 500)])]}
    rows = pair_reads(win, res, 17, "tape")
    s = score([r for r in rows if r[7] is not None])
    print(f"fair world: {s['n']} pairs, P&L per $100 {s['per100']:+.2f} (must be clearly negative), gaps under $1: {len(take_gaps(rows, 1.0))} (must be 0)")
    ok = s["per100"] < -1 and not take_gaps(rows, 1.0)
    close = 1_900_000_000
    res[f"BTC:{close}"] = {"k": 1, "p": 1, "fee": 0.07}
    win[("BTC", close)] = {"kb": [], "pt": [], "kt": [(close - 583, 0.40, "yes")], "pb": [(close - 600, [(0.50, 500)], [(0.52, 500)])]}
    g = take_gaps(pair_reads(win, res, 17, "tape"), 0.99)
    print(f"planted gap: found {len(g)} (must be 1), pays {g[0][7] if g else None} (must be 1), cost {g[0][6] if g else 0:.3f}")
    ok = ok and len(g) == 1 and g[0][7] == 1 and g[0][3] == "A"
    print("SELFTEST", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    args = sys.argv[2:]
    if cmd == "results":
        results(*args[:1])
    elif cmd == "run":
        run()
    elif cmd == "all":
        results(*args[:1])
        run()
    elif cmd == "live":
        live(*args[:2])
    elif cmd == "selftest":
        sys.exit(selftest())
    else:
        print(__doc__)
