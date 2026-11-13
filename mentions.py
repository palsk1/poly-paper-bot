#!/usr/bin/env python3
"""Mention markets ("Will Trump say 'Tariff' during ...?"): a word-history model vs Polymarket's price.

  python3 mentions.py peek     how Polymarket tags these markets, how many there are
  python3 mentions.py fetch    every finished mention market + real trades -> bt_cache/men/
  python3 mentions.py run      the test -> backtest/mentions.md
"""
import collections
import concurrent.futures as cf
import hashlib
import json
import math
import os
import re
import sys
import time

import backtest as bt
import bot
import btcheck

CACHE = os.path.join(bt.CACHE, "men")
G = bt.G
WORKERS = 8
T0 = time.time()
BUDGET_MIN = float(os.environ.get("MEN_BUDGET_MIN", "150"))
TAGS = ("mentions", "mention-markets")


def peek():
    tests = []
    for lim in (5, 20, 50, 100):
        tests.append((f"{G}/events", {"tag_slug": "mention-markets", "closed": "true", "limit": lim}))
    tests += [(f"{G}/events", {"tag_slug": "mention-markets", "closed": "true", "limit": 20, "offset": 20}),
              (f"{G}/events", {"tag_slug": "mention-markets", "closed": "false", "limit": 100}),
              (f"{G}/events", {"tag_id": 100343, "closed": "true", "limit": 20}),
              (f"{G}/events", {"tag_id": 100343, "closed": "true", "limit": 20, "order": "endDate", "ascending": "false"}),
              (f"{G}/events", {"tag_id": 100343, "closed": "true", "limit": 20, "end_date_min": "2026-10-01T00:00:00Z", "end_date_max": "2026-10-03T00:00:00Z"}),
              (f"{G}/events/keyset", {"tag_slug": "mention-markets", "closed": "true", "limit": 20}),
              (f"{G}/events/keyset", {"tag_id": 100343, "closed": "true", "limit": 20}),
              (f"{G}/events/keyset", {"tag_id": 100343, "closed": "true", "limit": 20, "end_date_min": "2026-10-01T00:00:00Z", "end_date_max": "2026-10-03T00:00:00Z"}),
              (f"{G}/events/pagination", {"tag_slug": "mention-markets", "closed": "true", "limit": 20}),
              (f"{G}/markets", {"tag_id": 100343, "closed": "true", "limit": 100}),
              (f"{G}/markets/keyset", {"tag_id": 100343, "closed": "true", "limit": 100}),
              (f"{G}/markets", {"tag_id": 100343, "closed": "true", "limit": 100, "offset": 100, "order": "endDate", "ascending": "true"})]
    for u, p in tests:
        try:
            r = bot.http_json(u, p)
            key = "events" if "/events" in u else "markets"
            rows = bot.envelope_rows(r, key, "data")
            print(f"\n== {u} {p}\n   {len(rows)} rows, keys {list(r.keys())[:8] if isinstance(r, dict) else 'list'}", flush=True)
            for e in rows[:3]:
                if key == "events":
                    print("   ", e.get("id"), e.get("slug"), e.get("endDate"), "markets", len(e.get("markets") or []),
                          "tags", [t.get("slug") for t in e.get("tags") or []][:6], "series", [s.get("slug") for s in e.get("series") or []])
                    for m in (e.get("markets") or [])[:1]:
                        print("       ", m.get("id"), m.get("question"), m.get("outcomePrices"), m.get("volumeNum"), m.get("conditionId"), m.get("endDate"), m.get("closedTime"))
                        print("        desc:", str(m.get("description"))[:300].replace("\n", " "))
                else:
                    print("   ", e.get("id"), e.get("question"), e.get("endDate"), e.get("outcomePrices"), e.get("volumeNum"),
                          [x.get("slug") for x in e.get("events") or []])
        except Exception as e:
            print(f"\n== {u} {p}\n   FAILED {str(e)[:200]}", flush=True)


def slim(e, m):
    m = dict(m)
    m.setdefault("events", [{"id": e.get("id"), "slug": e.get("slug")}])
    s = bt.slim_market(m)
    s["cid"] = m.get("conditionId")
    s["title"] = e.get("title")
    s["series"] = [x.get("slug") for x in e.get("series") or [] if isinstance(x, dict)]
    s["ev_start"] = e.get("startDate") or e.get("creationDate")
    s["desc"] = str(m.get("description") or "")[:600]
    s["item"] = m.get("groupItemTitle")
    return s


def pages():
    """Every finished event carrying the Mentions tag. Tries the listing styles Gamma has, keeps the first that answers."""
    tries = [("keyset", {"tag_id": 100343}), ("offset", {"tag_id": 100343})]   # more than 50 a page answers HTTP 406
    for kind, base in tries:
        out, cur, off, bad = [], None, 0, 0
        for _ in range(6000):
            p = dict(base, closed="true", limit=50)
            if kind == "keyset" and cur:
                p["after_cursor"] = cur
            if kind == "offset":
                p["offset"] = off
            try:
                r = bot.http_json(f"{G}/events/keyset" if kind == "keyset" else f"{G}/events", p)
            except Exception as e:
                bad += 1
                print(f"  {kind} {base} failed: {str(e)[:120]}", flush=True)
                if bad > 3 or not out:
                    break
                time.sleep(3)
                continue
            rows = [e for e in bot.envelope_rows(r, "events", "data") if isinstance(e, dict)]
            if not rows:
                break
            out += rows
            off += 50
            cur = r.get("next_cursor") if isinstance(r, dict) else None
            if len(out) % 2000 == 0:
                print(f"  {kind} {base}: {len(out)} events ({(time.time() - T0) / 60:.0f} min)", flush=True)
            if kind == "keyset" and not cur:
                break
            if len(out) > 120000:
                break
        tagged = sum(1 for e in out if any((t.get("slug") == "mention-markets") for t in e.get("tags") or [] if isinstance(t, dict)))
        print(f"{kind} {base}: {len(out)} events, {tagged} carry the tag", flush=True)
        if len(out) >= 200:
            if tagged and tagged < len(out):
                out = [e for e in out if any((t.get("slug") == "mention-markets") for t in e.get("tags") or [] if isinstance(t, dict))]
            return out
    return []


def fetch():
    """Every finished mention market (any size, back to the start) and the real trades of the ones before the holdout."""
    import optfair
    os.makedirs(CACHE, exist_ok=True)
    mpath = os.path.join(CACHE, "markets.json.gz")
    ms = {}
    evs = pages()
    fam = collections.Counter()
    for e in evs:
        fam[re.sub(r"[-0-9]+$", "", re.sub(r"\d+", "", str(e.get("slug"))))[:40]] += 1
        for m in e.get("markets") or []:
            if isinstance(m, dict):
                s = slim(e, m)
                if len(s["toks"]) == 2 and s["end"] and s.get("cid"):
                    ms[s["id"]] = s
    ends = sorted(m["end"] for m in ms.values())
    print(f"events {len(evs)}, markets {len(ms)}, ends {time.strftime('%Y-%m-%d', time.gmtime(ends[0])) if ends else '-'} .. "
          f"{time.strftime('%Y-%m-%d', time.gmtime(ends[-1])) if ends else '-'}", flush=True)
    print("biggest families:", fam.most_common(80), flush=True)
    if not ms:
        return
    cut = btcheck.T(btcheck.HOLDOUT_FROM)
    ms = {k: m for k, m in ms.items() if m["end"] < cut}   # the holdout stays unseen until 21 Dec
    bt.wjson(mpath, ms)
    want = [m for m in ms.values() if m["end"] < cut and m.get("closed") and (m.get("vol") or 0) >= 200]
    want.sort(key=lambda m: order_key(m["ev_slug"]))
    print(f"markets: {len(ms)}, before the holdout with $200+ traded: {len(want)}", flush=True)
    n_sh = (len(want) + SHARD - 1) // SHARD
    for i in range(n_sh):
        path = os.path.join(CACHE, f"tapes_{i:02d}.json.gz")
        if os.path.exists(path):
            continue
        chunk = want[i * SHARD:(i + 1) * SHARD]
        out = {}
        with cf.ThreadPoolExecutor(WORKERS) as ex:
            for mid, r in ex.map(optfair.fetch_tape, [(m, m["cid"]) for m in chunk]):
                if r is not None:
                    out[mid] = r
        bt.wjson(path, out)
        print(f"  tapes file {i + 1}/{n_sh}: {len(out)}/{len(chunk)} ({(time.time() - T0) / 60:.0f} min), "
              f"cut short {sum(1 for r in out.values() if r['cut'])}", flush=True)
        if (time.time() - T0) / 60 > BUDGET_MIN:
            print("time budget used, run again to continue")
            break


SHARD = 1000


def order_key(ev):
    return hashlib.md5(("men" + str(ev)).encode()).hexdigest()


# ================================================================ the word-history model
MONTHS = "january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec"
DAYS = "monday|tuesday|wednesday|thursday|friday|saturday|sunday"


def who(m):
    """Who talks and at what kind of occasion, from the event title, with dates and numbers taken out."""
    t = (m.get("title") or "").lower()
    t = re.sub(r"\(.*?\)", " ", t)
    t = re.sub(rf"\b({MONTHS})\b\.?", " ", t)
    t = re.sub(rf"\b({DAYS})\b", " ", t)
    t = re.sub(r"\d+(st|nd|rd|th)?", " ", t)
    t = re.sub(r"[^a-z ]", " ", t)
    t = re.sub(r"\b(on|the|his|her|their|next|during|at|in|of|a|an|to|from|by|this|event|events)\b", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    s = (m.get("series") or [""])[0] if m.get("series") else ""
    return s if s else t[:90]            # a recurring series is one kind of occasion, whatever the date or the teams


def speaker(m):
    """Just the person or show (wider than who): 'trump', 'leavitt', 'announcers', a company..."""
    t = (m.get("title") or "").lower()
    x = re.search(r"(?:what|who|which \w+|what \w+) will (.+?) (?:say|post|mention|name|tweet)\b", t)
    if x and x.group(1) not in ("be",):
        s = x.group(1)
    else:
        x = re.search(r"will be (?:said|mentioned) (?:on|during|in|at) (?:the )?(.+)", t)
        s = x.group(1) if x else t
    s = re.sub(r"\(.*?\)", " ", s)
    s = re.sub(rf"\b({MONTHS}|{DAYS})\b\.?", " ", s)
    s = re.sub(r"\d+(st|nd|rd|th)?", " ", s)
    s = re.sub(r"[^a-z ]", " ", s)
    s = re.sub(r"\b(the|next|first|episode|of|week|game|match|vs)\b", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    for a, b_ in (("donald trump", "trump"), ("karoline leavitt", "leavitt"), ("white house press secretary", "leavitt"),
                  ("keir starmer", "starmer"), ("jerome powell", "powell"), ("kevin warsh", "warsh"), ("zohran mamdani", "mamdani")):
        s = s.replace(a, b_)
    return s[:50]


def term(m):
    t = (m.get("item") or "")
    if not t:
        x = re.findall(r'["“]([^"”]+)["”]', m.get("q") or "")
        n = re.search(r"(\d+)\+ times", m.get("q") or "")
        t = " / ".join(x) + (f" {n.group(1)}+ times" if n else "")
    t = t.lower().replace("“", "").replace("”", "").replace('"', "")
    t = re.sub(r"\s*(/| or |,)\s*", "/", t)
    t = re.sub(r"\s+", " ", t).strip(" .?")
    parts = t.split(" ")
    n = ""
    if len(parts) >= 2 and re.fullmatch(r"\d+\+", parts[-2] if parts[-1] == "times" else ""):
        n = parts[-2]
        t = " ".join(parts[:-2])
    return "/".join(sorted(t.split("/"))) + ("#" + n if n else "")


def real(m):
    """Not the 'no qualifying event' / 'will not air' side markets."""
    return "qualifying" not in (m.get("item") or "").lower() and not re.search(r"not air|qualifying event", m.get("q") or "", re.I)


class Hist:
    """Running record of finished markets, read only up to a given moment (never looks ahead)."""

    def __init__(self, ms):
        import bisect
        self.bis = bisect
        self.keys = {}
        rows = sorted(((m["closed_t"] or m["end"], m) for m in ms.values()
                       if m.get("final") in ([0.0, 1.0], [1.0, 0.0]) and (m.get("closed_t") or m.get("end")) and real(m)),
                      key=lambda r: r[0])
        self.d = collections.defaultdict(lambda: ([], [0]))
        for t, m in rows:
            y = int(m["final"][0])
            k = self.key(m)
            for name in k:
                ts_, cs = self.d[name]
                ts_.append(t)
                cs.append(cs[-1] + y)

    def key(self, m):
        mid = m["id"]
        if mid not in self.keys:
            w, s, tm = who(m), speaker(m), term(m)
            self.keys[mid] = ("G", "W:" + w, "S:" + s, "WT:" + w + "|" + tm, "ST:" + s + "|" + tm, "T:" + tm)
        return self.keys[mid]

    def upto(self, name, t):
        ts_, cs = self.d.get(name) or ([], [0])
        i = self.bis.bisect_left(ts_, t)
        return cs[i], i

    def chance(self, m, t, k_w=8.0, k_t=2.0, lag=0):
        """Chance of Yes from history before t: all mention markets -> this speaker -> this occasion -> this word."""
        t = t - lag
        G, W, S, WT, ST, T = self.key(m)
        y, n = self.upto(G, t)
        p = (y + 1) / (n + 2)
        y, n_s = self.upto(S, t)
        p = (y + k_w * p) / (n_s + k_w)
        y, n_w = self.upto(W, t)
        p_w = (y + k_w * p) / (n_w + k_w)
        y, n_t = self.upto(T, t)
        p_t = (y + 4 * k_t * p_w) / (n_t + 4 * k_t)        # the word anywhere, weak
        y, n_st = self.upto(ST, t)
        p_st = (y + k_t * p_t) / (n_st + k_t)               # the word with this speaker
        y, n_wt = self.upto(WT, t)
        p_wt = (y + k_t * p_st) / (n_wt + k_t)              # the word at this kind of occasion
        return p_wt, {"n_s": n_s, "n_w": n_w, "n_t": n_t, "n_st": n_st, "n_wt": n_wt, "p_w": p_w}


def load():
    ms = bt.rjson(os.path.join(CACHE, "markets.json.gz"), {}) or {}
    tp = {}
    i = 0
    while os.path.exists(os.path.join(CACHE, f"tapes_{i:02d}.json.gz")):
        tp.update(bt.rjson(os.path.join(CACHE, f"tapes_{i:02d}.json.gz"), {}) or {})
        i += 1
    return ms, tp


def tbets(ms, tp, H, gap=0.10, lo=0.10, hi=0.90, sides=(0, 1), extra=0.01, stake=10.0, min_age=3600, max_age=None,
          min_hist=0, hist_key="n_st", always=None, looks=None, k_w=8.0, k_t=2.0, first_look_only=False, pick=None,
          edge=None, worst=False, max_wait=None):
    """Walk each market's real trades in 5-minute steps. Signal: the last trade of a step vs the word-history chance.
    Buy at the first trade of the next step with trades (+extra +fee). One bet per market. History = markets that had
    closed before the signal. Stops looking at the market's listed end (after that it is mostly decided)."""
    out = []
    for mid, r in tp.items():
        m = ms.get(mid)
        b = r["b"]
        if not m or len(b) < 2 or m.get("final") not in ([0.0, 1.0], [1.0, 0.0]) or not real(m) or (pick and not pick(m)):
            continue
        t0 = b[0][0]
        for i in range(len(b) - 1):
            t = b[i][0] + 300
            if t - t0 < min_age:
                continue
            if (max_age and t - t0 > max_age) or t >= (m["closed_t"] or m["end"]):
                break
            p = b[i][2]
            if not lo <= p <= hi:
                if first_look_only:
                    break
                continue
            q, info = H.chance(m, t, k_w, k_t)
            if info[hist_key] < min_hist:
                break
            if looks is not None:
                looks.append((mid, t, q, p, m["final"][0], info))
            side = 0 if q - p >= gap else 1 if p - q >= gap else None
            if always is not None:
                side = always
            if side is None or side not in sides:
                if first_look_only:
                    break
                continue
            y = b[i + 1]
            if max_wait and y[0] - t > max_wait:
                continue                                    # nobody traded soon after: a live bot would have looked again
            if worst:                                       # the worst price anyone paid in that 5-minute step
                px = y[4] if side == 0 else 1 - y[3]
            else:
                px = y[1] if side == 0 else 1 - y[1]
            c = min(0.99, px + extra)
            if edge is not None and always is None and (q if side == 0 else 1 - q) - c < edge:
                continue                                    # at the price really paid the gap is gone
            sh = stake / c
            fee = bot.taker_fee(sh, c, m.get("fee") or 0)
            win = (m["final"][0] == 1.0) == (side == 0)
            out.append({"ev": m["ev_slug"], "t": y[0], "cost": stake + fee, "pay": sh if win else 0.0, "sh": sh, "id": mid,
                        "side": side, "q": p if side == 0 else 1 - p, "fair": q if side == 0 else 1 - q, "px": px,
                        "title": m["q"], "who": speaker(m), "series": (m.get("series") or [""])[0] if m.get("series") else "",
                        "wait": y[0] - t, "age": t - t0, **info})
            break
    return out


# ================================================================ report
OUT = os.path.join(bt.OUT, "mentions.md") if hasattr(bt, "OUT") else "backtest/mentions.md"
TRIES = 85                    # versions looked at in this dig
NEW_ERA = 1774992000          # 1 Apr 2026: from here plain "always No" stopped paying
RULE = dict(gap=0.20, min_hist=3, sides=(1,), edge=0.10, extra=0.03, worst=True, max_wait=1800)


class Flat(Hist):
    """Yardstick: no word knowledge, every word gets 40 in 100."""

    def chance(self, m, t, k_w=8.0, k_t=2.0, lag=0):
        q, info = Hist.chance(self, m, t, k_w, k_t)
        return 0.40, info


class Occasion(Hist):
    """Yardstick: the speaker's / occasion's average over all words, not this word's own record."""

    def chance(self, m, t, k_w=8.0, k_t=2.0, lag=0):
        q, info = Hist.chance(self, m, t, k_w, k_t)
        return info["p_w"], info


def rule_bets(ms, tp, H, since=0, until=9e18, before=6, **over):
    """The rule: buy No where Yes trades 20c+ above the word's own record (3+ earlier markets with this speaker), paying the
    worst price of the next 5-minute step + 3c + fee, No at 10-90c, at least 6h before the market's listed end."""
    kw = dict(RULE, **over)
    b = tbets(ms, tp, H, **kw)
    return [x for x in b if since <= x["t"] < until and 0.10 <= x["px"] <= 0.90 and ms[x["id"]]["end"] - x["t"] >= before * 3600]


def usd(x):
    return "-" if x is None else f"{'+' if x >= 0 else '-'}${abs(x):.2f}"


def per100(b):
    c = sum(x["cost"] for x in b)
    return None if not c else (sum(x["pay"] for x in b) - c) / c * 100


def line(name, b):
    if len(b) < 10:
        return f"| {name} | {len(b)} | - | - | - | - | - |"
    bs = sorted(b, key=lambda x: x["t"])
    h = len(bs) // 2
    return (f"| {name} | {len(b)} | {len({x['ev'] for x in b})} | {sum(1 for x in b if x['pay'] > 0)} | {usd(per100(b))} | "
            f"{usd(per100(bs[:h]))} | {usd(per100(bs[h:]))} |")


HEAD = "| what | bets | events | won | per $100 | first half | second half |\n|---|---|---|---|---|---|---|"


def run():
    import exam
    ms, tp = load()
    H, HF, HO = Hist(ms), Flat(ms), Occasion(ms)
    L = []
    P = L.append
    n_ev = len({m["ev_slug"] for m in ms.values()})
    P("# Mention markets vs each word's own record (mentions.py)\n")
    P(f"Generated {bot.iso()}. Markets like \"Will Trump say 'Tariff' during the rally?\". {len(ms)} finished markets in {n_ev} "
      f"events, June 2024 to 9 November 2026 (the holdout from {btcheck.HOLDOUT_FROM} is not in here), {len(tp)} of them with "
      "every real trade in 5-minute steps. Paper only.\n")
    P("**The idea.** The same words come back again and again (\"Bitcoin\", \"Tariff\", \"Biden\"...). For each word we keep "
      "score: how often did this speaker really say it in earlier markets? That record (pulled toward the speaker's average "
      "when there are few earlier markets) is the model's chance. It only ever uses markets that had finished before the bet.\n")
    P("**The test.** Walk each market's real trades. Where the last trade and the model are far apart, buy at the next "
      "5-minute step that has trades. One bet per market, $10 each.\n")
    P("## 1. Who is the better forecaster?\n")
    looks = []
    tbets(ms, tp, H, gap=9, lo=0.03, hi=0.97, looks=looks, first_look_only=True)
    P("| looks (first look per market, 1h+ after its first trade) | model miss | Polymarket miss |")
    P("|---|---|---|")
    for nm, f in (("all", lambda r: True), ("since April 2026", lambda r: r[1] >= NEW_ERA), ("word has 3+ earlier markets", lambda r: r[5]["n_st"] >= 3)):
        rows = [r for r in looks if f(r)]
        br = lambda g: sum((g(r) - r[4]) ** 2 for r in rows) / max(1, len(rows))
        P(f"| {nm} ({len(rows)}) | {br(lambda r: r[2]):.4f} | {br(lambda r: r[3]):.4f} |")
    P("\n(\"Miss\" = average squared distance between forecast and result, smaller is better.) Polymarket's price is the "
      "better forecast. So the word record alone is no crystal ball. The question is whether it helps on one side.\n")
    P("How often Yes really won, by Yes price at that first look:\n")
    P("| Yes price | markets | Yes won (all years) | markets since April 2026 | Yes won (since April 2026) |")
    P("|---|---|---|---|---|")
    for lo, hi in ((0.03, .10), (.10, .20), (.20, .35), (.35, .50), (.50, .65), (.65, .80), (.80, .90), (.90, .97)):
        a = [r for r in looks if lo <= r[3] < hi]
        b = [r for r in a if r[1] >= NEW_ERA]
        P(f"| {lo * 100:.0f}-{hi * 100:.0f}c | {len(a)} | {sum(r[4] for r in a) / max(1, len(a)) * 100:.0f} in 100 | {len(b)} | "
          f"{sum(r[4] for r in b) / max(1, len(b)) * 100:.0f} in 100 |")
    P("\nYes is priced too high almost everywhere, most of all when it looks likely (at 80-90c it won 74 in 100 over all "
      "years). That is the old `mention_no` lean. Since April 2026 the gap is much smaller.\n")
    P("## 2. Plain \"always No\" (no model): it paid for two years, then stopped\n")
    P("First look per market, Yes at 10-90c, buying No at the next real trade + 3c + fee.\n")
    P(HEAD)
    an = tbets(ms, tp, H, always=1, first_look_only=True, extra=0.03)
    byq = collections.defaultdict(list)
    for x in an:
        g = time.gmtime(x["t"])
        byq[f"{g.tm_year} Q{(g.tm_mon - 1) // 3 + 1}"].append(x)
    for k in sorted(byq):
        P(line(k, byq[k]))
    P(line("**all**", an))
    P(line("always Yes instead, all", tbets(ms, tp, H, always=0, first_look_only=True, extra=0.03)))
    P("\nSo blind No made about $10-30 per $100 until March 2026 and has been flat to slightly behind since April. That is also "
      "when Polymarket began charging a fee on these markets, and more people (or bots) seem to have caught on. Our live `mention_no` track runs the blind version.\n")
    P("## 3. No only where the word's own record says Yes is too expensive\n")
    P("The rule: the word has 3+ earlier markets with this speaker, Yes trades 20c or more above the word's record, buy No. "
      "Costs: the worst price anyone paid in the next 5-minute step, + 3c, + fee. No must cost 10-90c, the gap must still be "
      "10c+ at the price paid, and the bet is made at least 6 hours before the market's listed end.\n")
    for title, per in (("Since April 2026 (when blind No stopped paying)", dict(since=NEW_ERA)), ("June 2024 to March 2026", dict(until=NEW_ERA))):
        P(f"### {title}\n")
        P(HEAD)
        P(line("**the rule**", rule_bets(ms, tp, H, **per)))
        P(line("the rule if buying costs 1c, not 3c", rule_bets(ms, tp, H, extra=0.01, **per)))
        P(line("the rule if buying costs 5c", rule_bets(ms, tp, H, extra=0.05, **per)))
        P(line("the rule if buying costs 8c", rule_bets(ms, tp, H, extra=0.08, **per)))
        P(line("yardstick: same rule, but every word gets 40 in 100", rule_bets(ms, tp, HF, **per)))
        P(line("yardstick: same rule, speaker's average instead of the word's record", rule_bets(ms, tp, HO, **per)))
        P(line("gap 10c+ instead of 20c+", rule_bets(ms, tp, H, gap=0.10, edge=0.05, **per)))
        P(line("gap 30c+", rule_bets(ms, tp, H, gap=0.30, edge=0.15, **per)))
        P(line("word needs only 1 earlier market", rule_bets(ms, tp, H, min_hist=1, **per)))
        P(line("word needs 6+ earlier markets", rule_bets(ms, tp, H, min_hist=6, **per)))
        P(line("the other way round: buy Yes where the record is 20c+ above the price", rule_bets(ms, tp, H, sides=(0,), **per)))
        P("")
    P("Read: since April the two yardsticks (no word knowledge) make nothing, the word's own record makes money. Before "
      "April everything on the No side made money, so those years can't tell the rule from blind No. Buying Yes loses, as "
      "in every dig so far.\n")
    b = rule_bets(ms, tp, H, since=NEW_ERA)
    P("### The rule cut up (since April 2026)\n")
    P(HEAD)
    bym = collections.defaultdict(list)
    for x in b:
        bym[time.strftime("%Y-%m", time.gmtime(x["t"]))].append(x)
    for k in sorted(bym):
        P(line(k, bym[k]))
    for nm, f in (("No paid 10-20c", lambda x: x["px"] < .2), ("No paid 20-35c", lambda x: .2 <= x["px"] < .35), ("No paid 35-50c", lambda x: .35 <= x["px"] < .5),
                  ("No paid 50-90c", lambda x: x["px"] >= .5), ("market under 12h old", lambda x: x["age"] < 12 * 3600),
                  ("market 12h+ old", lambda x: x["age"] >= 12 * 3600)):
        P(line(nm, [x for x in b if f(x)]))
    fam = collections.defaultdict(list)
    for x in b:
        fam[x["series"] or x["who"][:24]].append(x)
    for k, v in sorted(fam.items(), key=lambda kv: -len(kv[1]))[:10]:
        P(line("family: " + k, v))
    best = max(b, key=lambda x: x["pay"] - x["cost"]) if b else None
    if best:
        P(f"\nBiggest single win: ${best['pay'] - best['cost']:.0f} of ${sum(x['pay'] - x['cost'] for x in b):.0f} in total "
          f"(\"{best['title']}\", No at {best['px'] * 100:.0f}c). No lottery ticket carries the result.\n")
    late = [x for x in tbets(ms, tp, H, **RULE) if x["t"] >= NEW_ERA and 0.10 <= x["px"] <= 0.90 and ms[x["id"]]["end"] - x["t"] < 6 * 3600]
    P(HEAD)
    P(line("left out: bets within 6h of the listed end or after it", late))
    P("\nThose late bets lose: by then the speech is on and people in the room know more than a word record. The rule "
      "stays out. (This cut was found by looking, like the rest.)\n")
    P("**Weak spots.** (1) Everything here was found by looking at the same data, there is no untouched test set, so the "
      "live paper bets are the real test. (2) Two of eight months lost (June, August). (3) Real cost is the big unknown: "
      "these are thin markets, at +5c the lead halves and at +8c it is gone. The live track must use real asking prices. "
      "(4) All of the profit sits in markets that were already 12+ hours old; in younger ones the rule made nothing. "
      "(5) A fixed single look per market (2h, 6h, 12h after the first trade) shows nothing clear, on few bets: the money "
      "came from waiting for moments when Yes ran up.\n")
    P("## 4. The exam\n")
    tests = [("Mention markets: buy No where Yes is 20c+ above the word's own record (since Apr 2026, worst price +3c)",
              rule_bets(ms, tp, H, since=NEW_ERA), "lead: wants a live paper test"),
             ("Mention markets: same rule, June 2024 - Nov 2026", rule_bets(ms, tp, H), "lead: wants a live paper test"),
             ("Mention markets: same rule if buying costs 5c more (since Apr 2026)", rule_bets(ms, tp, H, since=NEW_ERA, extra=0.05), "lead: cost check"),
             ("Mention markets: always buy No, since Apr 2026 (+3c)", [x for x in an if x["t"] >= NEW_ERA], "dropped"),
             ("Mention markets: buy Yes where the word's record is 20c+ above the price (since Apr 2026)",
              rule_bets(ms, tp, H, since=NEW_ERA, sides=(0,)), "dropped")]
    cards = []
    for name, bb, status in tests:
        card = exam.score(bb, name, tries=TRIES, src="mentions.py, backtest/mentions.md", status=status, quiet=True)
        cards.append(card)
        print("LEDGER ROW " + json.dumps(card))
        P(f"- **{name}**: {card['bets']} bets in {card.get('groups')} separate groups, {usd(card.get('per100'))} per $100, "
          f"luck range {usd(card.get('lo100'))} to {usd(card.get('hi100'))}, worst case {usd(card.get('floor100'))} per $100, "
          f"verdict **{card.get('verdict')}**.")
    P("")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))
    return cards


def selftest():
    m = {"id": "1", "q": 'Will Trump say "Bitcoin" or "Crypto" 3+ times during the rally on May 5?', "item": "Bitcoin / Crypto 3+ times",
         "title": "What will Trump say during Pennsylvania rally on May 5?", "series": []}
    assert term(m) == "bitcoin/crypto#3+", term(m)
    assert speaker(m) == "trump", speaker(m)
    assert who(m) == "what will trump say pennsylvania rally", who(m)
    assert not real({"q": "Will Trump's remarks not air?", "item": "-No Qualifying Event-"})
    ms = {}
    for i in range(12):
        ms[str(i)] = dict(m, id=str(i), closed_t=1000 + i, end=1000 + i, final=[1.0, 0.0] if i % 4 == 0 else [0.0, 1.0])
    H = Hist(ms)
    q, info = H.chance(dict(m, id="x"), 2000)
    assert info["n_st"] == 12 and 0.2 < q < 0.4, (q, info)
    q0, info0 = H.chance(dict(m, id="y"), 1003)
    assert info0["n_st"] == 3, info0                      # only markets finished before the moment count
    tp = {"x": {"cut": False, "n": 3, "b": [[0, .7, .7, .7, .7, 50, 1], [7200, .7, .7, .7, .7, 50, 1], [7500, .68, .7, .66, .7, 50, 2]]}}
    ms["x"] = dict(m, id="x", ev_slug="e", closed_t=90000, end=90000, final=[0.0, 1.0], fee=0)
    b = rule_bets(ms, tp, H)
    assert len(b) == 1 and abs(b[0]["px"] - 0.34) < 1e-9 and b[0]["pay"] > 0, b
    print("mentions selftest ok")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    {"peek": peek, "fetch": fetch, "run": run, "selftest": selftest}[cmd]()
