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


if __name__ == "__main__":
    {"peek": peek}[sys.argv[1]](sys.argv[2] if len(sys.argv) > 2 else "movies")
