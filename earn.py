#!/usr/bin/env python3
"""Earnings markets ("Will Nvidia beat quarterly earnings?"): each company's own record vs Polymarket's price.

  python3 earn.py peek     how Polymarket tags these markets, how many there are
"""
import collections
import re
import sys

import backtest as bt
import bot

G = bt.G


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
    {"peek": peek}[cmd]()
