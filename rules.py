#!/usr/bin/env python3
"""Fine-print hunt (2026-11-09): does the crowd misprice markets whose rules say something the title doesn't?

PAPER ONLY. Reads public market data and the backtest cache (bt_cache/), never trades.

    python3 rules.py peek      # print what Gamma tells us about disputes and clarifications (a few days)
    python3 rules.py fetch     # rule text + UMA status list for every market in bt_cache/markets.json.gz
    python3 rules.py run       # write backtest/rules.md
    python3 rules.py selftest  # offline check

Ideas tested (all checked the same way as calib.py: price at a set time before the end, +1-5c and the taker fee,
held to the result, grouped by event, 90% band, both halves must be ahead, and the flagged markets must beat
look-alike markets in the same price band that have no flag):
  1. "Strict wording": the rules need an OFFICIAL announcement, a named source, or exclude things the title
     seems to include. If people trade the title, the headline outcome (usually YES) is overpriced.
  2. "Title vs rules gap": the rules name a different date/time than the title, or add conditions.
  3. Disputed / clarified markets (known only afterwards): how wrong was the price before the trouble?
     That says how much a screen could earn at best, if it could spot them in advance.
  4. Limbo: after the end date, while the result waits for UMA, is the price right?

Leakage guard: Gamma returns today's rule text, which includes clarifications added later. The screen only reads
the text BEFORE the first added note ("Update", "Clarification", "Note:", dated edits), so it sees about what a
trader saw before the end. Clarified markets are reported separately.
"""
import bisect
import datetime as dt
import json
import os
import random
import re
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor

import backtest as bt
import bot

CACHE, OUT = bt.CACHE, bt.OUT
DAY = 86400
META = os.path.join(CACHE, "rules_meta.json.gz")
EXTRA_KEYS = ("umaResolutionStatuses", "umaResolutionStatus", "resolutionSource", "resolvedBy", "umaBond", "umaReward",
              "automaticallyResolved", "negRisk", "customLiveness", "hasReviewedDates", "clarification", "clarifications")


def statuses(m):
    raw = m.get("umaResolutionStatuses")
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except Exception:
            raw = [raw]
    return [str(x).lower() for x in (raw or [])]


def slim_rules(m):
    return {"d": str(m.get("description") or "")[:8000], "rs": str(m.get("resolutionSource") or "")[:300],
            "st": statuses(m), "q": str(m.get("question") or ""),
            "by": str(m.get("resolvedBy") or "")[:60], "bond": bot.fnum(m.get("umaBond"), None),
            "liv": m.get("customLiveness"), "auto": m.get("automaticallyResolved")}


def peek():
    rng = random.Random(1)
    today = bot.now().replace(hour=0, minute=0, second=0, microsecond=0)
    rows = []
    for back in (5, 20, 60, 120, 200):
        rows += bt.fetch_day(today - dt.timedelta(days=back), True)
    print(f"{len(rows)} closed markets read")
    keys = Counter(k for m in rows for k in m)
    print("keys:", ", ".join(f"{k}({n})" for k, n in sorted(keys.items())))
    for k in EXTRA_KEYS:
        vals = Counter(json.dumps(m.get(k))[:80] for m in rows if k in m)
        print(f"\n{k}: {vals.most_common(12)}")
    disp = [m for m in rows if "disputed" in statuses(m)]
    print(f"\ndisputed: {len(disp)} of {len(rows)}")
    for m in disp[:8]:
        print(" -", m.get("question"), "|", m.get("umaResolutionStatuses"), "| final", m.get("outcomePrices"),
              "| end", m.get("endDate"), "closed", m.get("closedTime"))
    rx = re.compile(r"(update|clarif|note:|edit|additional context)", re.I)
    cl = [m for m in rows if rx.search(str(m.get("description") or ""))]
    print(f"\ndescriptions with update/clarification words: {len(cl)}")
    for m in rng.sample(cl, min(6, len(cl))):
        d = str(m.get("description"))
        i = rx.search(d).start()
        print(" -", m.get("question"), "\n   ...", d[max(0, i - 150):i + 350].replace("\n", " / "))
    print("\nrandom descriptions:")
    for m in rng.sample(rows, 4):
        print(" -", m.get("question"), "\n  ", str(m.get("description"))[:900].replace("\n", " / "))


def fetch():
    """Rule text for every market already in the backtest cache, read day by day like backtest.fetch_markets."""
    markets = bt.rjson(os.path.join(CACHE, "markets.json.gz"), {}).get("markets", {})
    have = bt.rjson(META, {}) or {}
    need_days = sorted({bt.utc(m["end"]).strftime("%Y-%m-%d") for k, m in markets.items() if k not in have and m.get("end")})
    print(f"rules: {len(markets)} markets in cache, {len(have)} with rules, {len(need_days)} days to read")
    t0 = time.time()

    def one(k):
        d = dt.datetime.fromisoformat(k).replace(tzinfo=bt.UTC)
        try:
            return k, bt.fetch_day(d, True)
        except Exception as e:
            print(f"  {k} failed: {e}")
            return k, []

    with ThreadPoolExecutor(bt.WORKERS) as ex:
        for i, (k, rows) in enumerate(ex.map(one, need_days)):
            for m in rows:
                mid = str(m.get("id"))
                if mid in markets:
                    have[mid] = slim_rules(m)
            if i % 20 == 0:
                print(f"  {i + 1}/{len(need_days)} days, {len(have)} markets with rules ({time.time() - t0:.0f}s)")
    bt.wjson(META, have)
    st = Counter(s for v in have.values() for s in set(v["st"]))
    print(f"rules: {len(have)} markets with rule text. Status counts: {dict(st)}")


# ================================================================ screen (text only, known before the end)

import calib  # noqa: E402  (scoring, snapshots and the pass bar are shared with the calibration hunt)

ADDED = re.compile(r"(?:^|\n|\.\s)\s*[\(\[]?\s*(?:update|updated|clarification|edit|edited|additional context)\b[^:\n]{0,40}:", re.I)
MONTHS = "jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec"
DATE_RX = re.compile(rf"\b({MONTHS})[a-z]*\.?\s+(\d{{1,2}})\b", re.I)
EXCL = re.compile(r"will not count|won't count|does not count|do not count|not be considered|will not qualify|"
                  r"does not qualify|do not qualify|not sufficient|insufficient|excluding|excluded|regardless of|"
                  r"irrespective of|shall not|will not be counted|not be included|only count|only .{0,30} will count", re.I)
FLAG_RX = {
    "official": re.compile(r"\bofficial(ly)?\b|\bformal(ly)?\b|\bconfirmed by\b|\bcertif", re.I),
    "announce": re.compile(r"\bannounce", re.I),
    "intent_not_enough": re.compile(r"announcement.{0,40}(alone|itself|not)|intention|plans? to .{0,40}(not|will not)|"
                                    r"must (actually|be completed|take effect)|go into effect|take effect|"
                                    r"(signed|enacted) into law", re.I),
    "consensus": re.compile(r"consensus of credible", re.I),
    "discretion": re.compile(r"discretion|ambigu|subjective|at the sole|in the spirit|may be used|may consider", re.I),
    "fifty_fifty": re.compile(r"50-50|50/50|fifty", re.I),
    "named_site": re.compile(r"https?://(?!(www\.)?(polymarket|x\.com|twitter))[\w.-]+", re.I),
}


def pre_text(d):
    """Rule text as it probably was before any clarification was added (cut at the first added note)."""
    mt = ADDED.search(d or "")
    return (d[:mt.start()] if mt else d or ""), bool(mt)


def flags(q, d):
    """Text flags a trader could compute before the end. q = title, d = rule text before added notes."""
    ql, dl = q.lower(), d.lower()
    f = set()
    for name, rx in FLAG_RX.items():
        if rx.search(dl) and not rx.search(ql):
            f.add(name)  # in the rules but not in the title: the title hides it
    if len(EXCL.findall(dl)) >= 2:
        f.add("exclusions_2plus")
    if len(d) >= 1500:
        f.add("long_rules")
    td = {(m_.group(1)[:3].lower(), int(m_.group(2))) for m_ in DATE_RX.finditer(q)}
    rd = {(m_.group(1)[:3].lower(), int(m_.group(2))) for m_ in DATE_RX.finditer(d)}
    if td and rd and not (rd <= td):
        f.add("date_gap")  # the rules name a date the title doesn't
    n = len([x for x in ("official", "announce", "intent_not_enough", "consensus", "discretion", "exclusions_2plus",
                         "date_gap") if x in f])
    if n >= 3:
        f.add("tricky_3plus")
    if not f & {"official", "announce", "intent_not_enough", "consensus", "discretion", "exclusions_2plus", "date_gap",
                "long_rules"}:
        f.add("plain")
    return f


FLAG_ORDER = ["official", "announce", "intent_not_enough", "consensus", "discretion", "exclusions_2plus", "date_gap",
              "long_rules", "tricky_3plus", "named_site", "fifty_fifty", "plain"]
FLAG_WORDS = {
    "official": "rules need it to be OFFICIAL/formal, title doesn't say so",
    "announce": "rules hinge on an announcement, title doesn't say so",
    "intent_not_enough": "rules say plans/announcements aren't enough, it must take effect",
    "consensus": "decided by 'consensus of credible reporting' (judgment call)",
    "discretion": "rules leave room for judgment ('ambiguity', 'discretion', 'spirit')",
    "exclusions_2plus": "rules list 2+ things that DON'T count",
    "date_gap": "rules name a date the title doesn't",
    "long_rules": "long rules (1,500+ characters)",
    "tricky_3plus": "3+ of the tricky flags at once",
    "named_site": "decided by one named website",
    "fifty_fifty": "has a 50-50 refund clause",
    "plain": "none of the tricky flags (control group)",
}


def label(meta):
    st = meta.get("st") or []
    pre, clar = pre_text(meta.get("d", ""))
    return {"disputed": "disputed" in st, "clarified": clar, "reproposed": st.count("proposed") >= 2, "pre": pre}


def is_yes_no(mk):
    return [o.lower() for o in mk.get("outs", [])] == ["yes", "no"]


def m2(x):
    return "" if x is None else f"{'+' if x >= 0 else '-'}${abs(x):.1f}"


def gap_line(lab, flagged, rest, slip=0.02):
    """Flagged markets vs look-alikes without the flag (same side, band, horizon): the difference and its band."""
    a, b = calib.score(flagged, slip), calib.score(rest, slip)
    if not a or not b:
        return f"| {lab} | | | | |"
    se_a, se_b = (a["per100"] - a["lo"]) / 1.645, (b["per100"] - b["lo"]) / 1.645
    d = a["per100"] - b["per100"]
    se = (se_a ** 2 + se_b ** 2) ** 0.5
    star = " **<-**" if d - 1.645 * se > 0 and a["events"] >= 30 else ""
    return (f"| {lab}{star} | {a['events']} | {m2(a['per100'])} | {m2(b['per100'])} | {m2(d)} ({m2(d - 1.645 * se)} to "
            f"{m2(d + 1.645 * se)}) |")


def build(markets, hist, meta):
    lab, fl = {}, {}
    for mid, mk in markets.items():
        mt = meta.get(mid)
        if not mt:
            continue
        lab[mid] = label(mt)
        fl[mid] = flags(mk["q"], lab[mid]["pre"])
    use = {k: markets[k] for k in lab}
    rows = calib.snapshots(use, hist, horizons=(1, 3, 7, 14, 30, -1, -3, -7))
    for r in rows:
        r["fl"], r["lab"] = fl[r["mid"]], lab[r["mid"]]
        r["yn"] = is_yes_no(markets[r["mid"]])
    return rows, lab, fl


def report(rows, lab, fl, markets):
    calib.FLAGS.clear()
    n = len(lab)
    nd = sum(v["disputed"] for v in lab.values())
    nc = sum(v["clarified"] for v in lab.values())
    nr = sum(v["reproposed"] for v in lab.values())
    L = ["# Fine-print hunt: does the crowd misprice markets with tricky rules?", "",
         f"Generated {bot.iso(bot.now())}. {n:,} finished binary non-sports Polymarket markets since {bt.START} with "
         f"their rule text. {nd:,} were disputed at UMA, {nc:,} got a clarification added, {nr:,} needed a second "
         "proposal. Paper only.", "",
         "How to read: same as calib.md. Buy one side at the history price +1-5c plus the taker fee, hold to the "
         "result, profit per $100 staked, grouped by event. **<-** = 90% band at +2c above $0, 30+ events, both "
         "halves ahead. The 'vs look-alikes' tables compare flagged markets with unflagged ones in the same price "
         "band and time slot: an edge has to come from the flag, not the band.", ""]

    # 1. does the text predict trouble?
    L += ["## 1. Do the text flags predict disputes and clarifications?", "",
          "Share of markets that later got disputed or clarified, flagged vs all. If a flag can't predict trouble, "
          "it can't be the reason for a mispricing.", "",
          "| Flag | Markets | Disputed | Clarified | Disputed per 1,000 | vs all |", "|---|---|---|---|---|---|"]
    base = 1000 * nd / max(1, n)
    for f in FLAG_ORDER:
        ids = [k for k, v in fl.items() if f in v]
        if not ids:
            continue
        d = sum(lab[k]["disputed"] for k in ids)
        c = sum(lab[k]["clarified"] for k in ids)
        r_ = 1000 * d / len(ids)
        L.append(f"| {FLAG_WORDS[f]} | {len(ids):,} | {d} | {c} | {r_:.1f} | {r_ / base if base else 0:.1f}x |")
    L.append(f"| all | {n:,} | {nd} | {nc} | {base:.1f} | 1.0x |")

    yn = [r for r in rows if r["yn"] and r["h"] > 0]
    L += ["", "## 2. Tricky-rule markets: buy YES or NO (Yes/No markets, 1-30 days before the end)", "",
          "Idea: people read the title, the rules are stricter, so YES is too dear and NO too cheap.", ""]
    for hz_set, name in (((1, 3), "1-3 days before the end"), ((7, 14, 30), "7-30 days before the end")):
        sub = [r for r in yn if r["h"] in hz_set]
        L += [f"### {name}", ""] + calib.HEAD
        for f in FLAG_ORDER:
            fs = [r for r in sub if f in r["fl"]]
            for side in ("yes", "no"):
                L.append(calib.line(f"{f}: buy {side.upper()} 10-90c", calib.side_rows(fs, (0.10, 0.90), side),
                                    f"{f} {side} {name}"))
        L.append("")
        L += [f"### {name}: flagged vs look-alikes (buy NO, same band 10-90c, +2c)", "",
              "| Flag | Events | Flagged | Not flagged | Difference (90% band) |", "|---|---|---|---|---|"]
        for side in ("no", "yes"):
            for f in FLAG_ORDER:
                if f == "plain":
                    continue
                fs = [r for r in sub if f in r["fl"]]
                rs = [r for r in sub if f not in r["fl"]]
                L.append(gap_line(f"{f}, buy {side.upper()}", calib.side_rows(fs, (0.10, 0.90), side),
                                  calib.side_rows(rs, (0.10, 0.90), side)))
        L.append("")

    # 3. long shots and favorites, all market shapes
    L += ["## 3. Tricky-rule markets: favorite vs long shot (all market shapes, 1-7 days out)", ""] + calib.HEAD
    sub = [r for r in rows if r["h"] in (1, 3, 7)]
    for f in ("tricky_3plus", "discretion", "consensus", "exclusions_2plus", "date_gap", "plain"):
        fs = [r for r in sub if f in r["fl"]]
        for b in ((0.02, 0.10), (0.10, 0.25), (0.75, 0.90), (0.90, 0.98)):
            side = "cheap" if b[1] <= 0.5 else "dear"
            L.append(calib.line(f"{f}: {'long shot' if side == 'cheap' else 'favorite'} {calib.bandname(b)}",
                                calib.side_rows(fs, b, side), f"{f} {side} {calib.bandname(b)}"))
    L.append("")

    # 4. disputed / clarified: hindsight ceiling
    L += ["## 4. Hindsight: how wrong was the price in markets that later got disputed or clarified?", "",
          "Not a rule (you only know afterwards). It shows the most a perfect trouble-spotter could have earned.", ""]
    L += calib.HEAD
    for name, key in (("disputed", "disputed"), ("clarified", "clarified"), ("second proposal", "reproposed")):
        for hz_set, hn in (((1, 3), "1-3d"), ((7, 14, 30), "7-30d")):
            fs = [r for r in rows if r["lab"][key] and r["h"] in hz_set]
            for b in ((0.02, 0.25), (0.75, 0.98)):
                side = "cheap" if b[1] <= 0.5 else "dear"
                L.append(calib.line(f"{name} {hn}: {'long shot' if side == 'cheap' else 'favorite'} {calib.bandname(b)}",
                                    calib.side_rows(fs, b, side)))
            fy = [r for r in fs if r["yn"]]
            L.append(calib.line(f"{name} {hn}: buy NO 10-90c", calib.side_rows(fy, (0.10, 0.90), "no")))
    L.append("")

    # 5. limbo after the end date
    L += ["## 5. Limbo: after the end date, still waiting for the result", "",
          "Price 1, 3 or 7 days AFTER the end date, market not settled yet. Is the leader right?", ""] + calib.HEAD
    for hz in (-1, -3, -7):
        fs = [r for r in rows if r["h"] == hz]
        for b in ((0.02, 0.10), (0.10, 0.30), (0.70, 0.90), (0.90, 0.98)):
            side = "cheap" if b[1] <= 0.5 else "dear"
            L.append(calib.line(f"{-hz}d after end: {'long shot' if side == 'cheap' else 'leader'} {calib.bandname(b)}",
                                calib.side_rows(fs, b, side), f"limbo {-hz}d {side} {calib.bandname(b)}"))
            fd = [r for r in fs if r["lab"]["disputed"]]
            L.append(calib.line(f"  ...of them later disputed", calib.side_rows(fd, b, side)))
    L.append("")

    # 6. follow-ups on what sections 1-5 showed
    TROUBLE = ("official", "announce", "intent_not_enough", "consensus", "exclusions_2plus", "date_gap", "long_rules")

    def score_n(r):
        return sum(1 for x in TROUBLE if x in r["fl"])

    L += ["## 6. Follow-ups", "", "### 6a. Trouble score (how many of the 7 dispute-predicting flags) vs disputes", "",
          "| Flags | Markets | Disputed per 1,000 |", "|---|---|---|"]
    for k_ in (0, 1, 2, 3, 4):
        ids = [k for k, v in fl.items() if (sum(1 for x in TROUBLE if x in v) >= k_ if k_ == 4 else
                                            sum(1 for x in TROUBLE if x in v) == k_)]
        if ids:
            L.append(f"| {k_}{'+' if k_ == 4 else ''} | {len(ids):,} | {1000 * sum(lab[k]['disputed'] for k in ids) / len(ids):.1f} |")
    L += ["", "### 6b. Long shot 10-30c, by trouble score (same topic mix is NOT controlled here; see 6c)", ""] + calib.HEAD
    for hz_set, hn in (((1, 3), "1-3d before"), ((7, 14, 30), "7-30d before"), ((-1, -3), "1-3d after end (limbo)")):
        for lo_, hi_ in ((0, 0), (1, 1), (2, 3), (4, 9)):
            fs = [r for r in rows if r["h"] in hz_set and lo_ <= score_n(r) <= hi_]
            L.append(calib.line(f"{hn}, score {lo_}{'-' + str(hi_) if hi_ != lo_ else ''}: long shot 10-30c",
                                calib.side_rows(fs, (0.10, 0.30), "cheap"), f"long shot 10-30c {hn} score {lo_}-{hi_}"))
    L += ["", "### 6c. Same, flagged (score 2+) vs unflagged in the SAME topic, long shot 10-30c, +2c", "",
          "| Topic / time | Events | Flagged | Not flagged | Difference (90% band) |", "|---|---|---|---|---|"]
    for hz_set, hn in (((1, 3), "1-3d"), ((7, 14, 30), "7-30d"), ((-1, -3), "limbo")):
        for tp in [n_ for n_, _ in calib.TOPICS] + ["other"]:
            sub = [r for r in rows if r["h"] in hz_set and r["topic"] == tp]
            fs = [r for r in sub if score_n(r) >= 2]
            rs = [r for r in sub if score_n(r) == 0]
            if len(fs) >= 20 and len(rs) >= 20:
                L.append(gap_line(f"{tp}, {hn}", calib.side_rows(fs, (0.10, 0.30), "cheap"),
                                  calib.side_rows(rs, (0.10, 0.30), "cheap")))
    dg = [x for x in calib.side_rows([r for r in yn if r["h"] in (1, 3) and "date_gap" in r["fl"]], (0.10, 0.90), "yes")]
    L += ["", "### 6d. The one pass: 'rules name a date the title doesn't', buy YES 1-3 days out", "",
          "By topic (+2c):", "", "| Topic | Events | Per $100 |", "|---|---|---|"]
    for tp in sorted({r["topic"] for r, _, _ in dg}):
        sc = calib.score([x for x in dg if x[0]["topic"] == tp], 0.02)
        if sc:
            L.append(f"| {tp} | {sc['events']} | {m2(sc['per100'])} |")
    by_ev = defaultdict(list)
    for r, q, pay in dg:
        by_ev[r["ev"]].append((r, q, pay))
    L += ["", "Every event (first market shown, price, won?):", ""]
    for ev, xs in sorted(by_ev.items(), key=lambda kv: kv[1][0][0]["t"]):
        r, q, pay = xs[0]
        dd = DATE_RX.findall(lab[r["mid"]]["pre"])[:4]
        L.append(f"- {bt.iso_t(r['t'])[:10]} {r['q'][:90]} | {q * 100:.0f}c | {'WON' if pay else 'lost'} | "
                 f"{len(xs)} bets | rule dates {dd}")
    L.append("")

    rng = random.Random(4)
    L += ["## Samples (to check the word filters by eye)", ""]
    for f in ("intent_not_enough", "discretion", "date_gap", "tricky_3plus"):
        ids = [k for k, v in fl.items() if f in v]
        L += [f"**{f}**:", ""] + [f"- {markets[k]['q'][:110]}" for k in rng.sample(ids, min(6, len(ids)))] + [""]
    dis = [k for k, v in lab.items() if v["disputed"]]
    L += ["**disputed**:", ""] + [f"- {markets[k]['q'][:110]} (final {markets[k]['final']})"
                                  for k in rng.sample(dis, min(15, len(dis)))] + [""]
    L += ["## Slices that passed the bar", ""] + ([f"- {x}" for x in calib.FLAGS] or ["- none"])
    n_cells = sum(1 for x in L if x.startswith("| ") and not x.startswith("| Slice") and not x.startswith("| Flag")
                  and not x.startswith("|---"))
    L += ["", f"About {n_cells} rows were tested; at a 90% band roughly {n_cells // 20} pass by luck alone."]
    return "\n".join(L) + "\n"


def run():
    markets = bt.rjson(os.path.join(CACHE, "markets.json.gz"), {}).get("markets", {})
    hist = bt.rjson(os.path.join(CACHE, "hist.json.gz"), {})
    meta = bt.rjson(META, {}) or {}
    cut = bot.parse_iso("2026-11-10T00:00:00Z").timestamp()  # holdout (PROTOCOL.md): never look past it here
    markets = {k: v for k, v in markets.items() if v.get("end") and v["end"] < cut}
    rows, lab, fl = build(markets, hist, meta)
    print(f"markets {len(markets)}, with rules {len(lab)}, snapshots {len(rows)}")
    txt = report(rows, lab, fl, markets)
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "rules.md"), "w") as fh:
        fh.write(txt)
    print(txt)


def selftest():
    """Made-up markets: 'official' rules make YES win 20% less often than its price. Buy-NO on that flag must win,
    and the plain control must be near the costs."""
    rng = random.Random(2)
    markets, hist, meta = {}, {}, {}
    t0 = bot.parse_iso("2026-05-01T00:00:00Z").timestamp()
    for i in range(4000):
        end = int(t0 + i * 3600)
        tricky = i % 2 == 0
        p = 0.6
        y = 1 if rng.random() < (0.4 if tricky else 0.6) else 0
        mid = str(i)
        markets[mid] = {"id": mid, "q": "Will X happen by June 30?", "outs": ["Yes", "No"], "toks": ["a", "b"],
                        "end": end, "start": end - 60 * DAY, "closed": True, "closed_t": end + 3600,
                        "final": [float(y), float(1 - y)], "uma": "resolved", "vol": 30000, "fee": 0.0,
                        "sports": False, "slug": mid, "ev": "e" + mid, "ev_slug": ""}
        hist[mid] = [[end - 50 * DAY + k * 12 * 3600 for k in range(100)], [p] * 100]
        d = ("Resolves Yes only if X is officially confirmed. Plans do not count. Rumors will not count. "
             if tricky else "Resolves Yes if X happens by June 30. ")
        if i % 7 == 0:
            d += "\n\nUpdate (June 2): the deadline means 11:59 PM ET."
        meta[mid] = {"d": d, "st": ["proposed", "disputed", "proposed", "resolved"] if i % 50 == 0 else ["proposed", "resolved"]}
    assert pre_text("abc\n\nUpdate (June 2): x")[1] and not pre_text("Polymarket will issue a Clarification to x")[1]
    assert "official" in flags("Will X happen?", "only if officially confirmed") and \
        "official" not in flags("Will X officially happen?", "only if officially confirmed")
    assert "date_gap" in flags("Will X happen by June 30?", "by July 15, 2026") and \
        "date_gap" not in flags("Will X happen by June 30?", "by June 30, 2026")
    rows, lab, fl = build(markets, hist, meta)
    s = calib.score(calib.side_rows([r for r in rows if "official" in r["fl"] and r["h"] > 0], (0.1, 0.9), "no"), 0.0)
    c = calib.score(calib.side_rows([r for r in rows if "plain" in r["fl"] and r["h"] > 0], (0.1, 0.9), "no"), 0.0)
    assert s["per100"] > 30 and abs(c["per100"]) < 10, (s, c)
    txt = report(rows, lab, fl, markets)
    assert "**<-**" in txt and "official" in txt
    print("rules selftest ok:", round(s["per100"]), "per $100 on the planted flag,", round(c["per100"]), "on the control")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    {"peek": peek, "fetch": fetch, "run": run, "selftest": selftest}[cmd]()
