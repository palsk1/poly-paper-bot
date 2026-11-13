#!/usr/bin/env python3
"""A first look at one family of repeating Polymarket markets, by tag: how many, what shapes, what they settle on.

  python3 families.py peek box-office,movies,rotten-tomatoes     (tag slugs, comma separated)
"""
import collections
import re
import sys

import backtest as bt
import bot

G = bt.G


def shape(q):
    q = re.sub(r"\(.*?\)", "#", str(q))
    q = re.sub(r"[\"“'‘].*?[\"”'’]", "'X'", q)
    q = re.sub(r"\$?\d[\d.,]*[a-zA-Z%+]*", "#", q)
    return re.sub(r"\b[A-Z][\w&.'’-]*( [A-Z][\w&.'’-]*)*", "X", q[:1].lower() + q[1:])[:80]


def pages(tag_id, closed, max_pages=120):
    out, cur = [], None
    for _ in range(max_pages):
        p = {"tag_id": tag_id, "closed": closed, "limit": 50}
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
    return out


def peek(slugs):
    for slug in slugs.split(","):
        try:
            t = bot.http_json(f"{G}/tags/slug/{slug}")
        except Exception as e:
            print(f"\n=== tag {slug}: none ({str(e)[:60]})", flush=True)
            continue
        print(f"\n=== tag {slug}: id {t.get('id')} label {t.get('label')}", flush=True)
        for closed in ("true", "false"):
            out = pages(t.get("id"), closed)
            nm = sum(len(e.get("markets") or []) for e in out)
            print(f"  closed={closed}: {len(out)} events, {nm} markets", flush=True)
            if not out:
                continue
            fam, qfam, months, tags, src = (collections.Counter() for _ in range(5))
            vol = []
            ex = {}
            for e in out:
                f = re.sub(r"[-0-9]+$", "", re.sub(r"\d+", "", str(e.get("slug"))))[:50]
                fam[f] += 1
                ex.setdefault(f, e)
                months[str(e.get("endDate"))[:7]] += 1
                for x in e.get("tags") or []:
                    tags[x.get("slug")] += 1
                for m in e.get("markets") or []:
                    qfam[shape(m.get("question"))] += 1
                    vol.append(bot.fnum(bot.pick(m, "volumeNum", "volume")))
                    for u in re.findall(r"https?://([\w.-]+)", str(m.get("description") or "")):
                        src[u] += 1
            vol.sort()
            print("   by month:", sorted(months.items())[-16:])
            print("   other tags:", tags.most_common(25))
            print("   settle sources:", src.most_common(15))
            print("   question shapes:", qfam.most_common(30))
            print(f"   traded per market: median ${vol[len(vol) // 2]:.0f}, top tenth ${vol[int(len(vol) * 0.9)]:.0f}, $1000+ {sum(1 for v in vol if v >= 1000)}")
            print("   slug families:")
            for f, n in fam.most_common(30):
                e = ex[f]
                ms = e.get("markets") or []
                v = sum(bot.fnum(bot.pick(m, "volumeNum", "volume")) for m in ms)
                print(f"     {n:4d} x {f} | e.g. {e.get('title')} | {len(ms)} markets, ${v:.0f} | {str(e.get('endDate'))[:10]}")
                if ms:
                    print(f"            {ms[0].get('question')} {ms[0].get('outcomePrices')} | {str(ms[0].get('description'))[:260]!r}")


def fetch(slugs):
    """Finished markets + every real trade (5-minute steps) of each tag -> bt_cache/fam_<slug>/. The holdout stays out."""
    import concurrent.futures as cf
    import hashlib
    import os
    import time
    import btcheck
    import optfair
    cut = btcheck.T(btcheck.HOLDOUT_FROM)
    for slug in slugs.split(","):
        T0 = time.time()
        try:
            tid = bot.http_json(f"{G}/tags/slug/{slug}").get("id")
        except Exception as e:
            print(f"tag {slug}: none ({str(e)[:60]})", flush=True)
            continue
        d = os.path.join(bt.CACHE, "fam_" + slug.replace("-", "_"))
        os.makedirs(d, exist_ok=True)
        ms = {}
        for e in pages(tid, "true", max_pages=400):
            for m in e.get("markets") or []:
                if not isinstance(m, dict):
                    continue
                m = dict(m)
                m.setdefault("events", [{"id": e.get("id"), "slug": e.get("slug")}])
                s = bt.slim_market(m)
                s["cid"] = m.get("conditionId")
                s["title"] = e.get("title")
                s["desc"] = str(m.get("description") or "")[:1200]
                s["item"] = m.get("groupItemTitle")
                s["tags"] = [x.get("slug") for x in e.get("tags") or []]
                if len(s["toks"]) == 2 and s["end"] and s.get("cid") and s["end"] < cut:
                    ms[s["id"]] = s
        bt.wjson(os.path.join(d, "markets.json.gz"), ms)
        want = sorted((m for m in ms.values() if m.get("closed") and (m.get("vol") or 0) >= 200),
                      key=lambda m: hashlib.md5((slug + m["ev_slug"]).encode()).hexdigest())
        print(f"tag {slug} (id {tid}): {len(ms)} finished markets, {len({m['ev_slug'] for m in ms.values()})} events, {len(want)} with $200+ traded", flush=True)
        n_sh = (len(want) + 499) // 500
        for i in range(n_sh):
            path = os.path.join(d, f"tapes_{i:02d}.json.gz")
            if os.path.exists(path):
                continue
            chunk = want[i * 500:(i + 1) * 500]
            out = {}
            with cf.ThreadPoolExecutor(8) as ex:
                for mid, r in ex.map(optfair.fetch_tape, [(m, m["cid"]) for m in chunk]):
                    if r is not None:
                        out[mid] = r
            bt.wjson(path, out)
            print(f"  tapes file {i + 1}/{n_sh}: {len(out)}/{len(chunk)} ({(time.time() - T0) / 60:.0f} min)", flush=True)


# ================================================================ the comb: patterns in a family's prices alone
BANDS = ((0.03, .10), (.10, .25), (.25, .50), (.50, .75), (.75, .90), (.90, .97))
PARTS = (("first third of its life", 0, .33), ("middle third", .33, .66), ("last third", .66, .95), ("last day", "day", None))


def load(slug):
    """Finished two-way markets of a fetched tag + their real trades, crumbs and small mirror-price steps dropped."""
    import os
    import quakes
    import stocks
    d = os.path.join(bt.CACHE, "fam_" + slug.replace("-", "_"))
    ms = {k: m for k, m in bt.rjson(os.path.join(d, "markets.json.gz")).items() if m["final"] in ([1.0, 0.0], [0.0, 1.0])}
    tp, i = {}, 0
    while os.path.exists(os.path.join(d, f"tapes_{i:02d}.json.gz")):
        tp.update(bt.rjson(os.path.join(d, f"tapes_{i:02d}.json.gz"), {}) or {})
        i += 1
    for v in tp.values():
        keep = []
        for x in v.get("b") or []:
            if x[5] < stocks.MIN_PRINT:
                continue
            if keep and x[5] < quakes.MIRROR_USD and abs(x[2] - keep[-1][2]) > 0.3 and abs(x[2] - (1 - keep[-1][2])) < 0.08:
                continue
            keep.append(x)
        v["b"] = keep
    return ms, tp


def looks(ms, tp, step=6 * 3600, fresh=12 * 3600):
    """Every market every `step`: [(t, share of its life gone, hours left, last real price)]."""
    import stocks
    S = {}
    for k, m in ms.items():
        b = (tp.get(k) or {}).get("b")
        if not b or not m.get("start") or m["end"] - m["start"] < 6 * 3600:
            continue
        rows, t = [], m["start"] + 3600
        st = min(step, max(3600, (m["end"] - m["start"]) // 12))
        while t < m["end"] - 1800:
            pp = stocks._price(b, t, fresh=fresh)
            if pp is not None:
                rows.append((t, (t - m["start"]) / (m["end"] - m["start"]), (m["end"] - t) / 3600, pp))
            t += st
        if rows:
            S[k] = rows
    return S


def bets(ms, tp, S, sel, yes, window=3600, extra=0.02, lo=0.03, hi=0.97, near=0.15):
    """One $10 bet per market, the first look where sel(m, share gone, hours left, price): worst price of the next hour + 2c + fee."""
    import stocks
    out = []
    for k, rows in S.items():
        for t, f, h, pp in rows:
            if sel(ms[k], f, h, pp):
                x = stocks.buy(ms[k], tp[k]["b"], t, yes, extra, lo=lo, hi=hi, window=window)
                if x and abs(x["px"] - (pp if yes else 1 - pp)) <= near:
                    x.update(f=f, pp=pp)
                    out.append(x)
                    break
    return out


def part_sel(fa, fb):
    if fa == "day":
        return lambda f, h: h <= 24
    return lambda f, h: fa <= f < fb and h > 24


def comb(slug, keep=None, name=None):
    """Print the price-only tables for one family. keep(m) narrows it (e.g. drop the mention markets under 'youtube')."""
    import earn
    ms, tp = load(slug)
    if keep:
        ms = {k: m for k, m in ms.items() if keep(m)}
    S = looks(ms, tp)
    cell = lambda b: f"{earn.usd(earn.per100(b))} ({len(b)})" if len(b) >= 15 else f"- ({len(b)})"
    print(f"\n### {name or slug}: {len(ms)} finished markets, {len(S)} with real trades, {len({ms[k]['ev_slug'] for k in S})} events\n")
    print("| when | side | " + " | ".join(f"Yes at {a * 100:.0f}-{b * 100:.0f}c" for a, b in BANDS) + " |")
    print("|---|---|" + "---|" * len(BANDS))
    for nm, fa, fb in PARTS:
        ps = part_sel(fa, fb)
        for yes in (True, False):
            print(f"| {nm} | {'Yes' if yes else 'No'} | " + " | ".join(
                cell(bets(ms, tp, S, lambda m, f, h, pp, a=a, b=b: ps(f, h) and a <= pp < b, yes)) for a, b in BANDS) + " |")
    return ms, tp, S


OUT = "backtest/families_comb.md"
TRIES = 200


def report():
    """YouTube view counts, Rotten Tomatoes scores, flu numbers: the prices alone -> backtest/families_comb.md"""
    import contextlib
    import io
    import json
    import btcheck
    import earn
    import exam
    ment = lambda m: bool(re.search(r"\bsaid\b|\bsay\b|mention", m["q"], re.I))
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        print("# Three more families, prices alone: YouTube views, Rotten Tomatoes scores, flu numbers (families.py)\n")
        print(f"Generated {bot.iso()}. Paper only. The holdout from {btcheck.HOLDOUT_FROM} is not in here.\n")
        print("The families left over from the sweep in `boxoffice.md`. No model here, only the comb Jan asked for: every price band, "
              "at four moments of a market's life, both sides. One $10 bet per market the first time it fits, at the worst price "
              "anyone paid in the next hour + 2c + the fee. Small trades at the mirror of the last price are dropped and a buy more than "
              f"15c from the last price is thrown out (the wrong-side trades found in `quakes.md`). About {TRIES} cuts looked at. Per $100 (bets).")
        ym, yt, yS = comb("youtube", keep=lambda m: not ment(m), name="YouTube (video views, subscriber counts; the \"will he say X\" markets are left to `mentions.md`)")
        print("\nYes buyers lose in almost every box and No buyers don't win it back: the gap between buyers and sellers eats both. "
              "\"Will the channel hit N billion views by a date\" looks good for Yes at 25-75c (+$53.62 per $100) on 13 bets, which is nothing.")
        rm, rt, rS = comb("rotten-tomatoes", name="Rotten Tomatoes (\"will the film score at least N\")")
        lead = bets(rm, rt, rS, lambda m, f, h, pp: f < .33 and .5 <= pp < .75, False)
        wide = bets(rm, rt, rS, lambda m, f, h, pp: f < .33 and .4 <= pp < .8, False)
        print("\nOne lean: early in a market's life, lines priced as \"probably yes\" (Yes at 50-75c) are too dear. A film's score "
              "tends to slide as more critics post, and early buyers don't price that in.\n")
        print(earn.HEAD)
        print(earn.line("No where Yes is 50-75c, first third of the market's life", lead))
        print(earn.line("the same, buying Yes instead", bets(rm, rt, rS, lambda m, f, h, pp: f < .33 and .5 <= pp < .75, True)))
        print(earn.line("No, at the worst price of the next 2 hours + 1c", bets(rm, rt, rS, lambda m, f, h, pp: f < .33 and .5 <= pp < .75, False, window=7200, extra=.01)))
        print(earn.line("No, 4c extra instead of 2c", bets(rm, rt, rS, lambda m, f, h, pp: f < .33 and .5 <= pp < .75, False, extra=.04)))
        print(earn.line("No where Yes is 40-80c, first third", wide))
        print(earn.line("No where Yes is 50-75c, middle third", bets(rm, rt, rS, lambda m, f, h, pp: .33 <= f < .66 and .5 <= pp < .75, False)))
        for h1, h2 in ((24, 72), (72, 120), (120, 240), (240, 5000)):
            print(earn.line(f"No where Yes is 50-75c, {h1}-{h2 if h2 < 5000 else 'more'} hours before the end", bets(rm, rt, rS, lambda m, f, h, pp: h1 <= h < h2 and .5 <= pp < .75, False)))
        print("\nAhead in both halves and at harsher prices, but it is 63 bets on 45 films, it flips sign in the middle third, and cut by "
              "hours left instead it jumps between +$30 and -$20. A lean, not a find.")
        comb("flu", name="Flu hospital numbers")
        print("\n30 events in a year and hardly any trades in each box. Too small to test or to trade.\n")
        print("## The exam\n")
        yv = {k: m for k, m in ym.items() if "views" in m["q"].lower()}
        ySv = {k: v for k, v in yS.items() if k in yv}
        for name, bb, st in (("Rotten Tomatoes: No where Yes is 50-75c, early in the market's life", lead, "lean: 63 bets, no track"),
                             ("Rotten Tomatoes: same, Yes at 40-80c", wide, "lean: small, no track"),
                             ("YouTube view counts: always No, prices alone", bets(yv, yt, ySv, lambda m, f, h, pp: True, False), "dropped")):
            card = exam.score(bb, name, tries=TRIES, src="families.py report, backtest/families_comb.md", status=st, quiet=True)
            print(f"- **{name}**: {card['bets']} bets in {card.get('groups')} separate groups, {earn.usd(card.get('per100'))} per $100, "
                  f"luck range {earn.usd(card.get('lo100'))} to {earn.usd(card.get('hi100'))}, worst case {earn.usd(card.get('floor100'))} per $100, "
                  f"verdict **{card.get('verdict')}**.")
        print("\n**Verdict:** YouTube and flu dropped. Rotten Tomatoes keeps one lean that is too small to call (about 20 films a month "
              "since August, so a live test would need months). No track.")
    open(OUT, "w").write(buf.getvalue())
    print(buf.getvalue())


if __name__ == "__main__":
    cmd = sys.argv[1]
    report() if cmd == "report" else {"peek": peek, "fetch": fetch, "comb": comb}[cmd](sys.argv[2])
