#!/usr/bin/env python3
"""Earnings markets ("Will Nvidia beat quarterly earnings?"): each company's own record vs Polymarket's price.

  python3 earn.py peek     how Polymarket tags these markets, how many there are
  python3 earn.py fetch    every finished earnings market + real trades -> bt_cache/ern/
  python3 earn.py run      the test -> backtest/earn.md
"""
import collections
import concurrent.futures as cf
import hashlib
import os
import re
import sys
import time

import backtest as bt
import bot

G = bt.G
CACHE = os.path.join(bt.CACHE, "ern")
TAG = 1013                    # Gamma tag "Earnings"
SHARD = 400
T0 = time.time()
BUDGET_MIN = float(os.environ.get("ERN_BUDGET_MIN", "150"))


def pages(closed="true", extra=None):
    out, cur = [], None
    for _ in range(2000):
        p = dict(extra or {}, tag_id=TAG, closed=closed, limit=50)
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
    """One 'will X beat quarterly earnings' market. The slug carries the ticker, GAAP or not, the day and the estimate:
    xom-quarterly-earnings-nongaap-eps-05-01-2026-1pt00, mrna-...-gaap-eps-05-01-2026-neg2pt67."""
    m = dict(m)
    m.setdefault("events", [{"id": e.get("id"), "slug": e.get("slug")}])
    s = bt.slim_market(m)
    s["cid"] = m.get("conditionId")
    s["title"] = e.get("title")
    s["series"] = [x.get("slug") for x in e.get("series") or [] if isinstance(x, dict)]
    s["desc"] = str(m.get("description") or "")[:900]
    slug = str(e.get("slug") or "")
    x = re.match(r"([a-z0-9]+)-quarterly-earnings-(nongaap|gaap)-eps-(\d\d)-(\d\d)-(\d{4})-(neg)?(\d+)pt(\d+)", slug)
    y = re.match(r"will-([a-z0-9]+)-beat-earnings-estimate-(\d{4})-(\d\d)-(\d\d)-(neg)?(\d+)pt(\d+)", slug)
    if x:
        s["tick"], s["gaap"] = x.group(1), x.group(2) == "gaap"
        s["day"] = f"{x.group(5)}-{x.group(3)}-{x.group(4)}"
        s["est"] = (-1 if x.group(6) else 1) * float(f"{x.group(7)}.{x.group(8)}")
    elif y:
        s["tick"], s["gaap"] = y.group(1), "non-GAAP" not in s["desc"]
        s["day"] = f"{y.group(2)}-{y.group(3)}-{y.group(4)}"
        s["est"] = (-1 if y.group(5) else 1) * float(f"{y.group(6)}.{y.group(7)}")
    return s


def fetch():
    """Every finished 'beat quarterly earnings' market before the holdout, and every real trade of each."""
    import btcheck
    import optfair
    os.makedirs(CACHE, exist_ok=True)
    ms = {}
    odd = 0
    for e in pages():
        for m in e.get("markets") or []:
            if not isinstance(m, dict):
                continue
            s = slim(e, m)
            if "tick" not in s:
                odd += 1
                continue
            if len(s["toks"]) == 2 and s["end"] and s.get("cid"):
                ms[s["id"]] = s
    cut = btcheck.T(btcheck.HOLDOUT_FROM)
    n_all = len(ms)
    ms = {k: m for k, m in ms.items() if m["end"] < cut}          # the holdout stays unseen until 21 Dec
    bt.wjson(os.path.join(CACHE, "markets.json.gz"), ms)
    res = collections.Counter(tuple(m["final"]) for m in ms.values())
    print(f"earnings markets {n_all} ({odd} other shapes skipped), before the holdout {len(ms)}, results {res.most_common(4)}, "
          f"companies {len({m['tick'] for m in ms.values()})}", flush=True)
    want = sorted((m for m in ms.values() if m.get("closed")), key=lambda m: hashlib.md5(("ern" + m["ev_slug"]).encode()).hexdigest())
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
        print(f"  tapes file {i + 1}/{n_sh}: {len(out)}/{len(chunk)} ({(time.time() - T0) / 60:.0f} min), "
              f"cut short {sum(1 for r in out.values() if r['cut'])}", flush=True)
        if (time.time() - T0) / 60 > BUDGET_MIN:
            print("time budget used, run again to continue")
            break


def peek():
    for slug in ("earnings", "earnings-calls", "earnings-beat", "stocks", "equities", "finance", "business", "ipos", "fed", "economy"):
        try:
            t = bot.http_json(f"{G}/tags/slug/{slug}")
            print(f"tag {slug}: id {t.get('id')} label {t.get('label')}", flush=True)
        except Exception as e:
            print(f"tag {slug}: none ({str(e)[:60]})", flush=True)
            continue
        if slug not in ("earnings", "earnings-calls", "earnings-beat"):
            continue
        for closed in ("true", "false"):
            out, cur = [], None
            for _ in range(400):
                p = {"tag_id": t.get("id"), "closed": closed, "limit": 50}
                if cur:
                    p["after_cursor"] = cur
                try:
                    r = bot.http_json(f"{G}/events/keyset", p)
                except Exception as e:
                    print("   page failed", str(e)[:100])
                    break
                rows = [e for e in bot.envelope_rows(r, "events", "data") if isinstance(e, dict)]
                out += rows
                cur = r.get("next_cursor") if isinstance(r, dict) else None
                if not rows or not cur:
                    break
            nm = sum(len(e.get("markets") or []) for e in out)
            ends = sorted(str(e.get("endDate"))[:10] for e in out)
            print(f"  closed={closed}: {len(out)} events, {nm} markets, ends {ends[0] if ends else '-'} .. {ends[-1] if ends else '-'}", flush=True)
            fam, qfam, months, tags = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()
            vol = []
            for e in out:
                fam[re.sub(r"[-0-9]+$", "", re.sub(r"\d+", "", str(e.get("slug"))))[:45]] += 1
                months[str(e.get("endDate"))[:7]] += 1
                for x in e.get("tags") or []:
                    tags[x.get("slug")] += 1
                for m in e.get("markets") or []:
                    q = str(m.get("question") or "")
                    qfam[re.sub(r"\(.*?\)|\$?\d[\d.,]*[a-zA-Z%]*", "#", re.sub(r"^Will [A-Z][\w&.'’-]*( [A-Z][\w&.'’-]*)*", "Will X", q))[:70]] += 1
                    vol.append(bot.fnum(bot.pick(m, "volumeNum", "volume")))
            vol.sort()
            print("   by month:", sorted(months.items()))
            print("   slug families:", fam.most_common(25))
            print("   question shapes:", qfam.most_common(40))
            print("   other tags:", tags.most_common(20))
            if vol:
                print(f"   traded per market: median ${vol[len(vol) // 2]:.0f}, top tenth ${vol[int(len(vol) * 0.9)]:.0f}, $200+ {sum(1 for v in vol if v >= 200)}")
            for e in out[:3] + out[len(out) // 2:len(out) // 2 + 3] + out[-3:]:
                print("    ", e.get("slug"), e.get("endDate"), "|", e.get("title"), "| series", [s.get("slug") for s in e.get("series") or []])
                for m in (e.get("markets") or [])[:3]:
                    print("        ", m.get("question"), m.get("outcomes"), m.get("outcomePrices"), m.get("volumeNum"), m.get("groupItemTitle"), m.get("endDate"), m.get("closedTime"))
                for m in (e.get("markets") or [])[:1]:
                    print("         desc:", str(m.get("description"))[:500].replace("\n", " "))


# ================================================================ the test
OUT = "backtest/earn.md"
TRIES = 60                    # versions looked at in this dig
FEE = 0.05                    # today's fee, charged on every bet (half of these markets were still free)


def load():
    ms = bt.rjson(os.path.join(CACHE, "markets.json.gz"), {}) or {}
    tp = {}
    i = 0
    while os.path.exists(os.path.join(CACHE, f"tapes_{i:02d}.json.gz")):
        tp.update(bt.rjson(os.path.join(CACHE, f"tapes_{i:02d}.json.gz"), {}) or {})
        i += 1
    ms = {k: m for k, m in ms.items() if m.get("final") in ([1.0, 0.0], [0.0, 1.0]) and (tp.get(k) or {}).get("b")}
    return ms, tp


def last_before(b, t):
    """Last real trade price (Yes) in a 5-minute step that had fully ended by t."""
    p = None
    for x in b:
        if x[0] + 300 <= t:
            p = x[2]
        else:
            break
    return p


def record(ms):
    """For each market: the company's earlier results on Polymarket (only markets finished a day or more before)."""
    hist, out = collections.defaultdict(list), {}
    for mid, m in sorted(ms.items(), key=lambda kv: kv[1]["end"]):
        out[mid] = [y for (t, y) in hist[m["tick"]] if t < m["end"] - 86400]
        hist[m["tick"]].append((m["closed_t"] or m["end"], m["final"][0]))
    return out


def buy(m, b, t, yes, extra, stake=10.0, lo=0.10, hi=0.90, window=7200):
    """Buy after t at the worst price anyone paid over the next `window` seconds of trades, + extra + fee.
    Why a whole window: these markets are thin with wide gaps between buyers and sellers. One sale to a waiting buyer
    makes the 'price' drop, and the next trade may be another such sale. You can't buy there: you have to pay the
    sellers' price. Taking only the next 5-minute step made 'bet against the jump' look twice as good (window=300)."""
    nxt = [x for x in b if t <= x[0] < min(t + window, m["end"] - 1800)]
    if not nxt:
        return None
    px = max(x[4] for x in nxt) if yes else 1 - min(x[3] for x in nxt)
    if not lo <= px <= hi:
        return None
    c = min(0.99, px + extra)
    sh = stake / c
    win = (m["final"][0] == 1.0) == yes
    return {"ev": m["ev_slug"], "t": nxt[0][0], "cost": stake + bot.taker_fee(sh, c, FEE), "pay": sh if win else 0.0, "sh": sh,
            "px": px, "yes": yes, "id": m["id"]}


def blind(ms, tp, yes, hours=24, plo=0.0, phi=1.0, extra=0.01, sel=None):
    """Buy one side of every market `hours` before the release when the Yes price is inside plo..phi."""
    out = []
    for mid, m in ms.items():
        if sel and not sel(mid, m):
            continue
        b = tp[mid]["b"]
        t = m["end"] - hours * 3600
        p = last_before(b, t)
        if p is None or not plo <= p < phi:
            continue
        x = buy(m, b, t, yes, extra)
        if x:
            out.append(dict(x, q=p if yes else 1 - p))
    return out


def moved(ms, tp, move=0.08, back=72, looks=(48, 24, 12), fade=True, extra=0.01, only=None, window=7200):
    """The price moved `move` or more over the last `back` hours. fade=True bets it comes back, False bets it goes on."""
    out = []
    for mid, m in ms.items():
        b = tp[mid]["b"]
        for H in looks:
            t = m["end"] - H * 3600
            p, p0 = last_before(b, t), last_before(b, t - back * 3600)
            if p is None or p0 is None or abs(p - p0) < move:
                continue
            down = p < p0
            if only and only != ("down" if down else "up"):
                continue
            x = buy(m, b, t, down if fade else not down, extra, window=window)
            if x:
                out.append(dict(x, q=p if x["yes"] else 1 - p))
                break
    return out


def usd(x):
    return "-" if x is None else f"{'+' if x >= 0 else '-'}${abs(x):.2f}"


def per100(b):
    c = sum(x["cost"] for x in b)
    return None if not c else (sum(x["pay"] for x in b) - c) / c * 100


HEAD = "| what | bets | won | per $100 | first half | second half |\n|---|---|---|---|---|---|"


def line(name, b):
    if len(b) < 10:
        return f"| {name} | {len(b)} | - | - | - | - |"
    bs = sorted(b, key=lambda x: x["t"])
    h = len(bs) // 2
    return f"| {name} | {len(b)} | {sum(1 for x in b if x['pay'] > 0)} | {usd(per100(b))} | {usd(per100(bs[:h]))} | {usd(per100(bs[h:]))} |"


def quarter(t):
    g = time.gmtime(t)
    return f"{g.tm_year} Q{(g.tm_mon - 1) // 3 + 1}"


def run():
    import json
    import btcheck
    import exam
    ms, tp = load()
    rec = record(ms)
    L = []
    P = L.append
    n_yes = sum(m["final"][0] for m in ms.values())
    P("# Earnings markets: \"Will company X beat its quarterly earnings forecast?\" (earn.py)\n")
    P(f"Generated {bot.iso()}. {len(ms)} finished markets on {len({m['tick'] for m in ms.values()})} companies, September 2025 "
      f"to 9 November 2026 (the holdout from {btcheck.HOLDOUT_FROM} is not in here), every real trade in 5-minute steps. "
      "Paper only.\n")
    P(f"**What they are.** One Yes/No market per company per quarter: does the reported profit per share beat the analysts' "
      f"forecast written into the market? Yes won {n_yes:.0f} of {len(ms)} ({n_yes / len(ms) * 100:.0f} in 100): companies "
      "usually beat, everybody knows that, and the price knows it too. A typical market trades about $3,000 in total.\n")
    P("**The questions.** (1) Is the price a fair forecast? (2) Does a company's own record of beating or missing add "
      "anything? (3) Does the kind of number (official 'GAAP' profit or the company's own adjusted one, a loss, a tiny "
      "forecast) add anything? (4) When the price jumps in the last days, should you follow it or bet against it?\n")
    P("**Costs.** Every bet: $10, bought at the worst price anyone paid in the 2 hours after the signal, + 1c, + today's "
      "fee (charged on all bets, though half of these markets were still free). One bet per market. Why 2 hours: these "
      "markets are thin, and the gap between what buyers offer and what sellers ask is often 5-10c. A single sale makes "
      "the 'price' drop without anything being cheaper to buy.\n")
    P("## 1. Is the price fair?\n")
    P("| Yes price a day before the release | markets | Yes won | 3 days before: markets | Yes won |")
    P("|---|---|---|---|---|")
    for lo, hi in ((0, .2), (.2, .4), (.4, .6), (.6, .7), (.7, .8), (.8, .9), (.9, 1.01)):
        cells = []
        for H in (24, 72):
            r = [(last_before(tp[k]["b"], m["end"] - H * 3600), m["final"][0]) for k, m in ms.items()]
            r = [y for p, y in r if p is not None and lo <= p < hi]
            cells.append(f"{len(r)} | {sum(r) / max(1, len(r)) * 100:.0f} in 100")
        P(f"| {lo * 100:.0f}-{min(hi, 1) * 100:.0f}c | {cells[0]} | {cells[1]} |")
    P("\nClose to fair everywhere. Cheap Yes (under 40c) won a little more often than its price, on few markets. What that "
      "is worth at real buying prices:\n")
    P(HEAD)
    P(line("buy Yes on everything, a day before", blind(ms, tp, True)))
    P(line("buy No on everything, a day before", blind(ms, tp, False)))
    b_cheap = blind(ms, tp, True, phi=0.40)
    P(line("buy Yes when it costs under 40c", b_cheap))
    P(line("buy Yes at 40-80c", blind(ms, tp, True, plo=0.40, phi=0.80)))
    P(line("buy No when Yes is 90c+", blind(ms, tp, False, plo=0.90)))
    P(line("buy Yes on everything, 3 days before", blind(ms, tp, True, hours=72)))
    P("")
    P("## 2. The company's own record, and the kind of number\n")
    P(HEAD)
    b_miss = blind(ms, tp, True, sel=lambda k, m: sum(1 for y in rec[k] if y == 0) >= 2)
    P(line("Yes on companies that beat every earlier time (2+ earlier markets)", blind(ms, tp, True, sel=lambda k, m: len(rec[k]) >= 2 and all(rec[k]))))
    P(line("No on companies that beat every earlier time", blind(ms, tp, False, sel=lambda k, m: len(rec[k]) >= 2 and all(rec[k]))))
    P(line("Yes on companies that missed last time", blind(ms, tp, True, sel=lambda k, m: rec[k] and rec[k][-1] == 0)))
    P(line("No on companies that missed last time", blind(ms, tp, False, sel=lambda k, m: rec[k] and rec[k][-1] == 0)))
    P(line("Yes on companies that missed 2+ times before", b_miss))
    P(line("Yes, official (GAAP) number", blind(ms, tp, True, sel=lambda k, m: m["gaap"])))
    P(line("Yes, adjusted (non-GAAP) number", blind(ms, tp, True, sel=lambda k, m: not m["gaap"])))
    b_gaap = blind(ms, tp, False, plo=0.80, phi=0.90, sel=lambda k, m: m["gaap"])
    P(line("No, official number, Yes at 80-90c", b_gaap))
    P(line("Yes, forecast is a loss", blind(ms, tp, True, sel=lambda k, m: m["est"] < 0)))
    P(line("No, forecast is a loss", blind(ms, tp, False, sel=lambda k, m: m["est"] < 0)))
    P("\nA company's record on Polymarket (at most 5 earlier quarters) is already in the price. The one loud cell "
      "(official number at 80-90c) is one of many cells looked at, on about 100 markets.\n")
    P("## 3. The price jumped in the last days: follow it or bet against it?\n")
    P("Looks 48, 24 and 12 hours before the release. A jump = the Yes price moved 8c or more against three days earlier.\n")
    P(HEAD)
    b_fade = moved(ms, tp)
    b_follow = moved(ms, tp, fade=False)
    P(line("**bet against the jump**", b_fade))
    P(line("follow the jump", b_follow))
    P(line("against, price fell (buy Yes)", moved(ms, tp, only="down")))
    P(line("against, price rose (buy No)", moved(ms, tp, only="up")))
    P(line("against, if buying costs 3c extra, not 1c", moved(ms, tp, extra=0.03)))
    P(line("against, only the next 5 minutes' prices (too rosy, see Costs)", moved(ms, tp, window=300)))
    P(line("against, worst price of the next 8 hours", moved(ms, tp, window=8 * 3600)))
    P(line("against, jumps of 5c+", moved(ms, tp, move=0.05)))
    P(line("against, jumps of 12c+", moved(ms, tp, move=0.12)))
    P(line("against, jump measured over 1 day", moved(ms, tp, back=24)))
    P(line("against, jump measured over 7 days", moved(ms, tp, back=168)))
    P("\nBy quarter (bet against the jump):\n")
    P(HEAD)
    byq = collections.defaultdict(list)
    for x in b_fade:
        byq[quarter(x["t"])].append(x)
    for k in sorted(byq):
        P(line(k, byq[k]))
    P("\nFollowing a late jump is a clear loser: whoever chases the move overpays. Betting against it looks great if you "
      "pretend you can buy at the next trade's price, and shrinks to about nothing once you pay what sellers really ask. "
      "It also got weaker every quarter. Most of the 'jump' is one impatient trader paying the gap, not news.\n")
    P("## The exam\n")
    tests = [("Earnings markets: bet against an 8c+ jump in the last 3 days (worst price of 2h +1c)", b_fade, "dropped"),
             ("Earnings markets: follow an 8c+ jump in the last 3 days", b_follow, "dropped"),
             ("Earnings markets: buy Yes under 40c a day before the release", b_cheap, "dropped"),
             ("Earnings markets: buy Yes on companies that missed 2+ times before", b_miss, "dropped"),
             ("Earnings markets: buy No on official-number markets at 80-90c", b_gaap, "dropped")]
    for name, bb, status in tests:
        card = exam.score(bb, name, tries=TRIES, src="earn.py, backtest/earn.md", status=status, quiet=True)
        print("LEDGER ROW " + json.dumps(card))
        P(f"- **{name}**: {card['bets']} bets in {card.get('groups')} separate groups, {usd(card.get('per100'))} per $100, "
          f"luck range {usd(card.get('lo100'))} to {usd(card.get('hi100'))}, worst case {usd(card.get('floor100'))} per $100, "
          f"verdict **{card.get('verdict')}**.")
    P("\n**Verdict: dropped, no track.** The price is fair, a company's record is in it, and the one pattern (bet against "
      "late jumps) is mostly the gap between buyers and sellers and has lost since April. Useful lesson for other digs: in "
      "thin markets, never price a buy at the next trade alone.\n")
    open(OUT, "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "peek"
    {"peek": peek, "fetch": fetch, "run": run}[cmd]()
