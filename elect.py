#!/usr/bin/env python3
"""Non-US elections on Polymarket and Kalshi vs local poll averages (Wikipedia poll tables). Do US-based traders
misprice foreign races? Report backtest/elect.md.

PAPER ONLY. Reads public data, never trades, never writes state/.

  python3 elect.py scan        (probe el_scan: which foreign-election markets exist on both sites, with size)
"""
import collections
import datetime as dt
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import backtest as bt
import bot
import khouse
import kmentions as km
import yesno

G = bt.G
CACHE = os.path.join(bt.CACHE, "el")
rj, wj = khouse.rj, khouse.wj
d10 = lambda t: dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m-%d")
WIKI = "https://en.wikipedia.org/w/api.php"

# countries and words that mark a non-US race
FOREIGN = re.compile(r"\b(canad|mexic|brazil|argentin|chile|colombi|peru|ecuador|bolivi|venezuel|uruguay|paragua|costa rica|"
                     r"honduras|guatemal|panama|dominican|jamaica|trinidad|"
                     r"uk\b|britain|british|england|scotland|scottish|wales|welsh|ireland|irish|northern ireland|"
                     r"german|france|french|ital|spain|spanish|portug|netherland|dutch|belgi|luxemb|austria|switzerland|swiss|"
                     r"sweden|swedish|norw|denmark|danish|finland|finnish|iceland|poland|polish|czech|slovak|hungar|romania|"
                     r"bulgari|greece|greek|croatia|serbia|slovenia|bosnia|kosovo|albania|macedonia|montenegr|moldova|ukrain|"
                     r"russia|belarus|georgia\b|armenia|azerbaijan|turkey|türkiye|cyprus|malta|estonia|latvia|lithuania|"
                     r"israel|iran|iraq|lebanon|jordan|egypt|morocco|tunisia|algeria|nigeria|kenya|south africa|ghana|"
                     r"ethiopia|india|pakistan|bangladesh|sri lanka|nepal|japan|korea|taiwan|china|hong kong|philippin|"
                     r"indonesia|malaysia|thailand|vietnam|singapore|australia|new zealand|"
                     r"bundestag|chancellor|prime minister|\bpm\b|parliament|knesset|diet\b|riksdag|sejm|"
                     r"labour|tory|tories|conservative party|reform uk|afd|cdu|spd|ldp|likud|liberal party|ndp|"
                     r"carney|poilievre|starmer|farage|macron|le pen|bardella|merz|meloni|sanchez|milei|lula|bolsonaro|"
                     r"modi|netanyahu|takaichi|ishiba|albanese|dutton|sheinbaum)", re.I)
US = re.compile(r"\b(senate|house of representatives|governor|mayor|congress|electoral college|democrat|republican|"
                r"gop|trump|vance|newsom|primary|caucus|midterm|nyc|new york|california|texas|florida)\b", re.I)
PM_TAGS = ("world-elections", "global-elections", "elections", "world", "politics", "geopolitics", "europe",
           "canada", "uk", "germany", "france", "japan", "australia", "brazil", "israel", "south-korea", "netherlands",
           "poland", "portugal", "chile", "argentina", "colombia", "peru", "hungary", "norway", "czech-republic",
           "romania", "ireland", "philippines", "india", "mexico", "spain", "italy", "sweden", "denmark", "bolivia",
           "ecuador", "honduras", "new-zealand", "south-africa", "taiwan", "thailand", "global-politics")


def pm_pages(tag_id, closed, max_pages=200):
    import families
    return families.pages(tag_id, closed, max_pages)


def scan():
    os.makedirs(CACHE, exist_ok=True)
    # --- can Actions read Wikipedia's poll tables?
    try:
        r = bot.http_json(WIKI, {"action": "parse", "page": "Opinion polling for the 2025 German federal election",
                                 "prop": "wikitext", "format": "json"})
        print("WIKI ok,", len(str(r.get("parse", {}).get("wikitext", {}).get("*", ""))), "chars of wikitext", flush=True)
    except Exception as e:
        print("WIKI failed", str(e)[:200], flush=True)
    # --- Polymarket: closed events under election / country tags that look foreign
    evs = {}
    for slug in PM_TAGS:
        try:
            tid = bot.http_json(f"{G}/tags/slug/{slug}").get("id")
        except Exception as e:
            print("tag", slug, "none", str(e)[:60], flush=True)
            continue
        got = pm_pages(tid, "true")
        n0 = len(evs)
        for e in got:
            title = str(e.get("title") or "")
            if not re.search(r"elect|vote|seat|prime minister|chancellor|president|parliament|win|largest|coalition|"
                             r"next leader|snap|referendum|out by|resign", title, re.I):
                continue
            if not FOREIGN.search(title) or US.search(title):
                continue
            ms = e.get("markets") or []
            evs.setdefault(e.get("id"), {"slug": e.get("slug"), "title": title[:100], "end": str(e.get("endDate"))[:10],
                                         "n": len(ms), "tag": slug,
                                         "vol": sum(bot.fnum(bot.pick(m, "volumeNum", "volume")) for m in ms),
                                         "q": [str(m.get("question"))[:90] for m in ms[:3]]})
        print(f"tag {slug} (id {tid}): {len(got)} closed events, {len(evs) - n0} new foreign-politics ones", flush=True)
    wj(os.path.join(CACHE, "pm_scan.json.gz"), evs)
    v = sorted(evs.values(), key=lambda e: -e["vol"])
    print(f"\nPOLYMARKET foreign politics events: {len(v)}, $1M+: {sum(e['vol'] >= 1e6 for e in v)}, "
          f"$100k+: {sum(e['vol'] >= 1e5 for e in v)}, total ${sum(e['vol'] for e in v):,.0f}")
    by_m = collections.Counter(e["end"][:4] for e in v)
    print("by year:", sorted(by_m.items()))
    for e in v[:250]:
        print(f"PM | {e['end']} | ${e['vol']:,.0f} | {e['n']} mk | {e['title']} | {e['slug']} | {e['q'][:2]}")
    # --- Kalshi: every series in Elections / Politics / World that looks foreign
    ser = yesno.kget("/series", {}).get("series") or []
    cats = collections.Counter(s.get("category") for s in ser)
    print("\nKalshi series", len(ser), "categories", cats.most_common(), flush=True)
    pick = [s for s in ser if s.get("ticker") and s.get("category") in ("Elections", "Politics", "World")
            and FOREIGN.search(str(s.get("title")) + " " + str(s.get("ticker"))) and not US.search(str(s.get("title")))]
    print("looked at", len(pick), flush=True)
    info = {s["ticker"]: s for s in pick}
    out = {}
    with ThreadPoolExecutor(6) as ex:
        for t, ok, n in ex.map(km.series_markets, sorted(info)):
            if not ok:
                continue
            vv = list(ok.values())
            s = info[t]
            out[t] = {"title": str(s.get("title"))[:100], "cat": s.get("category"), "n": len(vv),
                      "ev": len({m["ev"] for m in vv}), "vol": sum(m["vol"] for m in vv),
                      "first": d10(min(m["close"] for m in vv)), "last": d10(max(m["close"] for m in vv)),
                      "ex": [(m["q"][:70], m["w"][:30], m["res"], int(m["vol"])) for m in sorted(vv, key=lambda m: -m["vol"])[:3]]}
    wj(os.path.join(CACHE, "k_scan.json.gz"), out)
    print("| series | category | title | markets | events | contracts | first close | last close |")
    for t, s in sorted(out.items(), key=lambda kv: -kv[1]["vol"]):
        print(f"| {t} | {s['cat']} | {s['title']} | {s['n']} | {s['ev']} | {s['vol']:,.0f} | {s['first']} | {s['last']} |")
    for t, s in sorted(out.items(), key=lambda kv: -kv[1]["vol"])[:80]:
        print("EX", t, s["ex"], flush=True)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "scan"
    if cmd == "scan":
        scan()
    else:
        print("unknown command", cmd)
