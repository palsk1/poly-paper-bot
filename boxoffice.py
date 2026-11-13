#!/usr/bin/env python3
"""Box office markets ("Will 'Movie' 3rd weekend box office be between 20m and 25m?") vs the daily ticket numbers.

  python3 boxoffice.py peek     can we read the daily numbers (Box Office Mojo / The Numbers) from here?
  python3 boxoffice.py fetch    every finished box office market + real trades, and the daily numbers -> bt_cache/bo/
  python3 boxoffice.py run      the test -> backtest/boxoffice.md
"""
import collections
import concurrent.futures as cf
import datetime as dt
import gzip
import hashlib
import html
import math
import os
import re
import sys
import time
import urllib.request

import backtest as bt
import bot

G = bt.G
CACHE = os.path.join(bt.CACHE, "bo")
TAG = 51                      # Gamma tag "Box Office"
SHARD = 400
T0 = time.time()
BROWSER = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"


def raw(url, ua=BROWSER):
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept": "text/html,*/*", "Accept-Language": "en-US,en;q=0.8",
                                               "Accept-Encoding": "gzip"})
    with urllib.request.urlopen(req, timeout=40) as r:
        b = r.read()
        if r.headers.get("Content-Encoding") == "gzip":
            b = gzip.decompress(b)
        return b.decode("utf-8", "replace")


def money(s):
    s = re.sub(r"[^0-9.]", "", s or "")
    return float(s) if s else None


def mojo_day(day):
    """Box Office Mojo's table for one day: [(title, dollars that day, theaters, dollars so far, days out)]."""
    t = raw(f"https://www.boxofficemojo.com/date/{day}/")
    rows = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", t, re.S):
        td = [html.unescape(re.sub(r"<[^>]+>", "", x)).strip() for x in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
        if len(td) >= 10 and td[3].startswith("$"):
            rows.append([td[2], money(td[3]), money(td[6]), money(td[8]), money(td[9])])
    return rows


def peek():
    for u in ("https://www.boxofficemojo.com/date/2026-10-10/", "https://www.boxofficemojo.com/weekend/2026W41/",
              "https://www.the-numbers.com/box-office-chart/daily/2026/10/10", "https://www.the-numbers.com/movie/Avatar-Fire-and-Ash-(2025)#tab=box-office"):
        for ua in (BROWSER, bot.UA):
            try:
                t = raw(u, ua)
                print(f"\n== {u} [{ua[:12]}] {len(t)} chars, tables {t.count('<table')}, rows {t.count('<tr')}", flush=True)
                txt = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>|<style.*?</style>", " ", t, flags=re.S))))
                i = txt.find("Daily")
                print("   ", txt[max(0, i - 100):i + 900])
                break
            except Exception as e:
                print(f"\n== {u} [{ua[:12]}] FAILED {str(e)[:150]}", flush=True)
    try:
        r = mojo_day("2026-10-10")
        print("\nmojo_day rows", len(r), r[:8])
    except Exception as e:
        print("mojo_day failed", str(e)[:200])


def pages(closed="true"):
    out, cur = [], None
    for _ in range(400):
        p = {"tag_id": TAG, "closed": closed, "limit": 50}
        if cur:
            p["after_cursor"] = cur
        r = bot.http_json(f"{G}/events/keyset", p)
        rows = [e for e in bot.envelope_rows(r, "events", "data") if isinstance(e, dict)]
        out += rows
        cur = r.get("next_cursor") if isinstance(r, dict) else None
        if not rows or not cur:
            break
    return out


def slim(e, m):
    m = dict(m)
    m.setdefault("events", [{"id": e.get("id"), "slug": e.get("slug")}])
    s = bt.slim_market(m)
    s["cid"] = m.get("conditionId")
    s["title"] = e.get("title")
    s["desc"] = str(m.get("description") or "")[:1500]
    s["item"] = m.get("groupItemTitle")
    return s


def fetch():
    import btcheck
    import optfair
    os.makedirs(CACHE, exist_ok=True)
    ms = {}
    for e in pages():
        for m in e.get("markets") or []:
            if isinstance(m, dict):
                s = slim(e, m)
                if len(s["toks"]) == 2 and s["end"] and s.get("cid"):
                    ms[s["id"]] = s
    cut = btcheck.T(btcheck.HOLDOUT_FROM)
    n_all = len(ms)
    ms = {k: m for k, m in ms.items() if m["end"] < cut}          # the holdout stays unseen until 21 Dec
    bt.wjson(os.path.join(CACHE, "markets.json.gz"), ms)
    print(f"box office markets {n_all}, before the holdout {len(ms)}, events {len({m['ev_slug'] for m in ms.values()})}", flush=True)
    want = sorted((m for m in ms.values() if m.get("closed") and (m.get("vol") or 0) >= 200),
                  key=lambda m: hashlib.md5(("bo" + m["ev_slug"]).encode()).hexdigest())
    n_sh = (len(want) + SHARD - 1) // SHARD
    for i in range(n_sh):
        path = os.path.join(CACHE, f"tapes_{i:02d}.json.gz")
        if os.path.exists(path):
            continue
        chunk = want[i * SHARD:(i + 1) * SHARD]
        out = {}
        with cf.ThreadPoolExecutor(8) as ex:
            for mid, r in ex.map(optfair.fetch_tape, [(m, m["cid"]) for m in chunk]):
                if r is not None:
                    out[mid] = r
        bt.wjson(path, out)
        print(f"  tapes file {i + 1}/{n_sh}: {len(out)}/{len(chunk)} ({(time.time() - T0) / 60:.0f} min), cut short {sum(1 for r in out.values() if r['cut'])}", flush=True)
    # the daily ticket numbers, every day from a year before the first market
    dpath = os.path.join(CACHE, "daily.json.gz")
    days = bt.rjson(dpath, {}) or {}
    first = min(m["end"] for m in ms.values() if m["end"] > 1700000000)
    d = dt.date.fromtimestamp(max(first, time.time() - 900 * 86400)) - dt.timedelta(days=400)
    todo = []
    while d < dt.date.today() - dt.timedelta(days=2):
        if d.isoformat() not in days:
            todo.append(d.isoformat())
        d += dt.timedelta(days=1)
    print(f"daily numbers: have {len(days)} days, need {len(todo)} more", flush=True)
    bad = 0
    todo.sort(reverse=True)                                       # newest first: those are the days the markets need
    with cf.ThreadPoolExecutor(1) as ex:
        def one(day):
            time.sleep(0.7)                                       # Box Office Mojo answers 503 when asked faster
            for k in range(3):
                try:
                    return day, mojo_day(day)
                except Exception as e:
                    err = e
                    time.sleep(5 + 10 * k)
            return day, str(err)[:100]
        for n, (day, rows) in enumerate(ex.map(one, todo)):
            if isinstance(rows, str) or not rows:
                bad += 1
                if bad <= 5:
                    print("   day failed", day, rows)
                continue
            days[day] = rows
            if n % 200 == 199:
                bt.wjson(dpath, days)
                print(f"   {n + 1}/{len(todo)} days ({(time.time() - T0) / 60:.0f} min), failed {bad}", flush=True)
    bt.wjson(dpath, days)
    print(f"daily numbers: {len(days)} days saved, {bad} failed")


# ================================================================ the test
OUT = "backtest/boxoffice.md"
TRIES = 45


def load():
    ms = bt.rjson(os.path.join(CACHE, "markets.json.gz"), {}) or {}
    tp = {}
    i = 0
    while os.path.exists(os.path.join(CACHE, f"tapes_{i:02d}.json.gz")):
        tp.update(bt.rjson(os.path.join(CACHE, f"tapes_{i:02d}.json.gz"), {}) or {})
        i += 1
    # weekend markets: they all close for betting Monday 12:00 UTC, after a Friday-Sunday weekend
    ms = {k: m for k, m in ms.items() if m.get("final") in ([1.0, 0.0], [0.0, 1.0]) and (tp.get(k) or {}).get("b")
          and re.search(r"weekend|opening", m.get("title") or "", re.I) and time.gmtime(m["end"]).tm_hour == 12}
    return ms, tp


def forecast_check():
    """How well can ticket sales be forecast from the public daily numbers? Wide releases (2,000+ theaters), 2nd weekend
    or later. Fit on weekends before Oct 2025, checked on the ones after. Returns [(what we know, typical miss, 9-in-10 miss, n)]."""
    import numpy as np
    D = bt.rjson(os.path.join(CACHE, "daily.json.gz"), {}) or {}
    mov = collections.defaultdict(dict)
    for day, rows in D.items():
        for title, g, th, tot, days in rows:
            if g and g > 0:
                mov[title][day] = (g, th or 0)
    sh = lambda s_, k: str(dt.date.fromisoformat(s_) + dt.timedelta(days=k))
    S = []
    for title, g in mov.items():
        for day in g:
            if dt.date.fromisoformat(day).weekday() != 4:
                continue
            w, pw, wk = [g.get(sh(day, k)) for k in (0, 1, 2)], [g.get(sh(day, k)) for k in (-7, -6, -5)], [g.get(sh(day, k)) for k in (-4, -3, -2, -1)]
            if not all(w) or not all(pw) or not all(wk[:3]) or w[0][1] < 2000 or pw[0][1] < 2000 or sum(x[0] for x in pw) < 3e6:
                continue
            L = math.log
            S.append({"day": day, "W": L(sum(x[0] for x in w)), "PW": L(sum(x[0] for x in pw)), "MTW": L(sum(x[0] for x in wk[:3])),
                      "TH": L(w[0][1] / pw[0][1]), "FRI": L(w[0][0]), "THU": L(wk[3][0]) if wk[3] else None})
    out = []
    for cols, nm in ((("PW", "MTW", "TH"), "last weekend + Monday-Wednesday + theater count (known Thursday)"),
                     (("PW", "MTW", "TH", "THU"), "the same + Thursday's number (known Friday)"),
                     (("FRI", "PW"), "Friday's number (known Saturday)")):
        rows = [r for r in S if all(r[c] is not None for c in cols)]
        tr, te = [r for r in rows if r["day"] < "2025-10-01"], [r for r in rows if r["day"] >= "2025-10-01"]
        if len(tr) < 30 or len(te) < 30:
            continue
        X = np.array([[1.0] + [r[c] for c in cols] for r in tr])
        b = np.linalg.lstsq(X, np.array([r["W"] for r in tr]), rcond=None)[0]
        res = np.array([abs(r["W"] - (b[0] + sum(b[i + 1] * r[c] for i, c in enumerate(cols)))) for r in te])
        out.append((nm, (math.exp(float(np.percentile(res, 50))) - 1) * 100, (math.exp(float(np.percentile(res, 90))) - 1) * 100, len(te)))
    return out, len(D)


FAMILIES = """| family (Polymarket tag) | finished events / markets | traded per market (middle one) | settles on | verdict |
|---|---|---|---|---|
| Box office (`box-office`, id 51) | 305 / 1,593 | $14,500 | the-numbers.com, boxofficemojo.com | **tested here** |
| Earnings beats (`earnings`, id 1013) | 1,602 / 1,606 | $5,200 | company reports | tested 13 Nov (`earn.md`): fair |
| Mentions (`mention-markets`, id 100343) | 1,356 / 24,228 | small | video / transcript | tested 13 Nov (`mentions.md`): track `word_no` |
| YouTube (`youtube`, id 146) | 412 / 3,725 | $2,400 | youtube.com view counts | mostly MrBeast video views (about 170 events) and podcast mentions; **untested**, views need a counter we don't have history for |
| Rotten Tomatoes (`rotten-tomatoes`, id 101453) | 93 / 576 | $1,500 | rottentomatoes.com | untested, few events |
| Billboard (`billboard`, id 103077) | 101 / 1,478 | $330 | billboard.com | untested, thin |
| Spotify (`spotify`, id 102851) | 175 / 3,099 | $0 | Spotify charts | most markets never trade |
| Netflix (`netflix`, id 100407) | 431 / 7,657 | $0 | Netflix top 10 | most markets never trade |
| Awards (`awards`, id 18) | 756 / 14,898 | $0 | award shows | most markets never trade; census said about fair |
| Airdrops / token value (`airdrops`, `fdv`) | 50 / 260 and 109 / 800 | $109,000 and $42,500 | token prices | big money, one-off events, no repeating number to keep score of |
| AI (`ai`, id 439) / OpenAI (`openai`) | 785 / 8,372 and 315 / 2,477 | $1,500 / $1,300 | leaderboards, company news | mixed bag, a dig of its own (census: leaderboard underdogs, 64 events) |
| Google Search (`google-search`) | 15 / 566 | $0 | Google Trends | too few |"""


def run():
    import json
    import btcheck
    import earn
    import exam
    ms, tp = load()
    L = []
    P = L.append
    kind = lambda m: "opening" if re.search("opening", m["title"], re.I) else "later"
    P("# Box office markets, and a sweep of repeating market families (boxoffice.py, families.py)\n")
    P(f"Generated {bot.iso()}. Paper only. The holdout from {btcheck.HOLDOUT_FROM} is not in here.\n")
    P("## 1. The sweep: which families repeat, trade real money and settle on a public number?\n")
    P("Looked up by Polymarket tag (`python3 families.py peek <tags>`, probe `fam_<tags>`), 13 Nov 2026.\n")
    P(FAMILIES)
    P("\nBox office was the best fit: every weekend, real money, and it settles on daily ticket numbers anyone can read.\n")
    P("## 2. Box office: can the public ticket numbers out-forecast the market?\n")
    fc, n_days = forecast_check()
    P(f"Daily ticket sales of every movie from Box Office Mojo ({n_days} days saved). A simple forecast of a movie's 2nd or "
      "later weekend, built on weekends before October 2025 and checked on the ones after:\n")
    P("| what the forecast knows | half the time it misses by less than | 9 times in 10 by less than | weekends checked |")
    P("|---|---|---|---|")
    for nm, a, b, n in fc:
        P(f"| {nm} | {a:.0f} in 100 | {b:.0f} in 100 | {n} |")
    P("\nPolymarket's brackets are about 10 in 100 wide (\"between 20m and 23m\"). A forecast that is usually off by 15-20 in "
      "100 before the weekend can't pick a bracket, and even with Friday's number in hand it is off by about a bracket. "
      "The people trading these read the same numbers hours earlier from the trade press. No model bet was run: it would "
      "only be noise.\n")
    P(f"## 3. Is the price itself fair? ({len(ms)} weekend markets in {len({m['ev_slug'] for m in ms.values()})} events)\n")
    P("Markets close Monday 12:00 UTC after a Friday-Sunday weekend. How often Yes won, by price, at four moments:\n")
    looks = ((96, "Thursday noon, before the weekend"), (60, "Saturday 00:00, previews known"), (40, "Saturday 20:00, Friday known"),
             (16, "Sunday 20:00, estimate out"))
    P("| Yes price | " + " | ".join(nm for _, nm in looks) + " |")
    P("|---|" + "---|" * len(looks))
    for lo, hi in ((0.02, .10), (.10, .25), (.25, .45), (.45, .65), (.65, .85), (.85, .98)):
        cells = []
        for H, _ in looks:
            r = [(earn.last_before(tp[k]["b"], m["end"] - H * 3600), m["final"][0]) for k, m in ms.items()]
            r = [y for p, y in r if p is not None and lo <= p < hi]
            cells.append(f"{sum(r) / max(1, len(r)) * 100:.0f} in 100 ({len(r)})")
        P(f"| {lo * 100:.0f}-{hi * 100:.0f}c | " + " | ".join(cells) + " |")
    P("\nFair, give or take. The one soft spot: brackets priced 65-85c before the weekend won more often than their price, on "
      "a few dozen markets. Bets, $10 each, bought at the worst price of the next 2 hours + 1c + today's fee:\n")
    P(earn.HEAD)
    b_fav = earn.blind(ms, tp, True, hours=96, plo=.65) + earn.blind(ms, tp, True, hours=60, plo=.65, sel=lambda k, m: earn.last_before(tp[k]["b"], m["end"] - 96 * 3600) is None)
    b_cheap = earn.blind(ms, tp, True, hours=96, phi=.25)
    b_no = earn.blind(ms, tp, False, hours=96, phi=.25)
    b_fade = earn.moved(ms, tp, looks=(96, 72, 40, 30), back=24)
    b_follow = earn.moved(ms, tp, looks=(96, 72, 40, 30), back=24, fade=False)
    P(earn.line("Yes at 65c+ before the weekend", b_fav))
    P(earn.line("Yes under 25c before the weekend", b_cheap))
    P(earn.line("No where Yes is under 25c", b_no))
    P(earn.line("Yes at 25-65c before the weekend", earn.blind(ms, tp, True, hours=96, plo=.25, phi=.65)))
    P(earn.line("Yes at 65c+ on Saturday evening (Friday known)", earn.blind(ms, tp, True, hours=40, plo=.65)))
    P(earn.line("bet against an 8c+ jump within a day", b_fade))
    P(earn.line("follow an 8c+ jump within a day", b_follow))
    P("\nUnlike the earnings markets, a late jump here is usually real news (a ticket number came out): betting against it "
      "loses badly, and following it is too late.\n")
    P("## The exam\n")
    for name, bb in (("Box office: buy Yes on brackets at 65c+ before the weekend", b_fav), ("Box office: buy Yes on brackets under 25c before the weekend", b_cheap),
                     ("Box office: buy No where Yes is under 25c before the weekend", b_no), ("Box office: bet against an 8c+ jump within a day", b_fade),
                     ("Box office: follow an 8c+ jump within a day", b_follow)):
        card = exam.score(bb, name, tries=TRIES, src="boxoffice.py, backtest/boxoffice.md", status="dropped", quiet=True)
        print("LEDGER ROW " + json.dumps(card))
        P(f"- **{name}**: {card['bets']} bets in {card.get('groups')} separate groups, {earn.usd(card.get('per100'))} per $100, "
          f"luck range {earn.usd(card.get('lo100'))} to {earn.usd(card.get('hi100'))}, worst case {earn.usd(card.get('floor100'))} per $100, "
          f"verdict **{card.get('verdict')}**.")
    P("\n**Verdict: dropped, no track.** The market reads the ticket numbers better and sooner than a simple model, and the "
      "prices are fair. The favorite-bracket lean rests on too few bets to act on.\n")
    open(OUT, "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "peek"
    {"peek": peek, "fetch": fetch, "run": run}[cmd]()
