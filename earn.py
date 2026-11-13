#!/usr/bin/env python3
"""Earnings markets ("Will Nvidia beat quarterly earnings?"): each company's own record vs Polymarket's price.

  python3 earn.py peek     how Polymarket tags these markets, how many there are
  python3 earn.py fetch    every finished earnings market + real trades -> bt_cache/ern/
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


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "peek"
    {"peek": peek, "fetch": fetch}[cmd]()
