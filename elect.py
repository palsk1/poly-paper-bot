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


# ---------------------------------------------------------------- downloads
EL_RX = re.compile(r"elect|vote|seats|round|margin|% of|turnout|runoff|winner|place|advance|qualify|after the election|"
                   r"after snap|largest|popular vote|majority", re.I)
NOT_RX = re.compile(r"\bout\b|remain|before|impeach|dissolved|called|next leader of|resign|by\.\.\.|in 202[4-9]\?|"
                    r"coalition will form|visit|deal|agreement", re.I)
PM_MK = os.path.join(CACHE, "pm_markets.json.gz")
K_MK = os.path.join(CACHE, "k_markets.json.gz")


def pm_events(min_vol=30000):
    ev = rj(os.path.join(CACHE, "pm_scan.json.gz"), {}) or {}
    return sorted((e for e in ev.values() if e["vol"] >= min_vol and EL_RX.search(e["title"]) and not NOT_RX.search(e["title"])),
                  key=lambda e: -e["vol"])


def pmfetch():
    """Every market of the foreign election events (Gamma), then every real trade in 5-minute steps (resumable)."""
    import optfair
    t0 = time.time()
    have = rj(PM_MK, {}) or {}
    evs = pm_events()
    print("Polymarket election events to fetch:", len(evs), flush=True)
    for e in evs:
        if any(m.get("ev_slug") == e["slug"] for m in have.values()):
            continue
        try:
            r = bot.http_json(f"{G}/events", {"slug": e["slug"]})
        except Exception as ex:
            print("  event failed", e["slug"], str(ex)[:80], flush=True)
            continue
        for E in (r if isinstance(r, list) else [r]):
            for m in E.get("markets") or []:
                if not isinstance(m, dict):
                    continue
                m = dict(m)
                m.setdefault("events", [{"id": E.get("id"), "slug": E.get("slug")}])
                x = bt.slim_market(m)
                x["cid"] = m.get("conditionId")
                x["title"] = E.get("title")
                x["ev_end"] = str(E.get("endDate") or "")[:19]
                x["item"] = m.get("groupItemTitle")
                x["desc"] = str(m.get("description") or "")[:1500]
                if len(x["toks"]) == 2 and x.get("cid"):
                    have[x["id"]] = x
    wj(PM_MK, have)
    want = sorted((m for m in have.values() if m.get("closed") and (m.get("vol") or 0) >= 300), key=lambda m: m["id"])
    print(f"{len(have)} markets, {len(want)} closed with $300+ traded", flush=True)
    for i in range(0, len(want), 300):
        path = os.path.join(CACHE, f"pm_tapes_{i // 300:02d}.json.gz")
        got = rj(path, None)
        chunk = want[i:i + 300]
        if got is not None and all(m["id"] in got for m in chunk):
            continue
        got = got or {}
        todo = [m for m in chunk if m["id"] not in got]
        with ThreadPoolExecutor(8) as ex:
            for mid, r in ex.map(optfair.fetch_tape, [(m, m["cid"]) for m in todo]):
                got[mid] = r if r is not None else {"b": [], "n": 0, "cut": None}
        wj(path, got)
        print(f"  pm tapes {i // 300 + 1}/{(len(want) + 299) // 300}: {len(got)} ({(time.time() - t0) / 60:.0f} min)", flush=True)
        if time.time() - t0 > 4.2 * 3600:
            print("time's up, run again to go on", flush=True)
            return


def kfetch(min_ser=20000, min_vol=500):
    """Settled markets of every foreign election series on Kalshi + hourly bid/ask + every trade (dates.tape_one)."""
    import dates
    sc = rj(os.path.join(CACHE, "k_scan.json.gz"), {}) or {}
    keep = sorted(t for t, s in sc.items() if s["vol"] >= min_ser and s["cat"] == "Elections"
                  and not NOT_RX.search(s["title"]))
    have = rj(K_MK, None) or {"series": {}, "markets": {}}
    for t in keep:
        if t in have["series"]:
            continue
        _, ok, _ = km.series_markets(t)
        have["series"][t] = sc[t]
        have["markets"].update(ok)
    wj(K_MK, have)
    path = os.path.join(CACHE, "k_tapes.json.gz")
    got = rj(path, {}) or {}
    todo = [m for m in have["markets"].values() if m["vol"] >= min_vol and m["t"] not in got]
    print(f"Kalshi: {len(keep)} series, {len(have['markets'])} markets, {len(todo)} tapes to get", flush=True)
    for i in range(0, len(todo), 150):
        with ThreadPoolExecutor(6) as ex:
            for tk, dd in ex.map(dates.tape_one, todo[i:i + 150]):
                got[tk] = dd
        wj(path, got)
        print(f"  k tapes {len(got)}", flush=True)


# ---------------------------------------------------------------- poll tables (Wikipedia)
WCACHE = os.path.join(bt.CACHE, "elw")
# key -> what to search for on Wikipedia (the "Opinion polling for the ..." page is picked from the hits)
ELECTIONS = {
    "de25": "2025 German federal election", "ca25": "2025 Canadian federal election",
    "ro25": "2025 Romanian presidential election", "kr25": "2025 South Korean presidential election",
    "pl25": "2025 Polish presidential election", "au25": "2025 Australian federal election",
    "pt25": "2025 Portuguese legislative election", "pt26p": "2026 Portuguese presidential election",
    "ie25p": "2025 Irish presidential election", "pe26": "2026 Peruvian general election",
    "hu26": "2026 Hungarian parliamentary election", "cl25": "2025 Chilean presidential election",
    "nl25": "2025 Dutch general election", "co26": "2026 Colombian presidential election",
    "co26l": "2026 Colombian parliamentary election",
    "bo25": "2025 Bolivian general election", "ar25": "2025 Argentine legislative election",
    "hn25": "2025 Honduran general election", "cz25": "2025 Czech parliamentary election",
    "br26": "2026 Brazilian presidential election", "il26": "2026 Israeli legislative election",
    "no25": "2025 Norwegian parliamentary election", "th26": "2026 Thai general election",
    "jp26": "2026 Japanese general election", "jp25c": "2025 Japanese House of Councillors election",
    "dk26": "2026 Danish general election", "si26": "2026 Slovenian parliamentary election",
    "cr26": "2026 Costa Rican general election", "se26": "2026 Swedish general election",
    "sco26": "2026 Scottish Parliament election", "wal26": "2026 Senedd election",
    "bg26p": "2026 Bulgarian presidential election", "rs26": "2026 Serbian parliamentary election",
    "ec25": "2025 Ecuadorian general election", "hr24p": "2024 Croatian presidential election",
    "uk24": "2024 United Kingdom general election", "mx24": "2024 Mexican general election",
    "tw24": "2024 Taiwanese presidential election", "ie24": "2024 Irish general election",
    "ro24": "2024 Romanian parliamentary election", "ro24p": "2024 Romanian presidential election",
    "on25": "2025 Ontario general election", "bc24": "2024 British Columbia general election",
    "bd26": "2026 Bangladeshi general election", "np26": "2026 Nepalese general election",
    "bw26": "2026 Baden-Württemberg state election", "mv26": "2026 Mecklenburg-Vorpommern state election",
    "be26": "2026 Berlin state election", "st26": "2026 Saxony-Anhalt state election",
    "rp26": "2026 Rhineland-Palatinate state election", "fr24": "2024 French legislative election",
    "jp24": "2024 Japanese general election", "at24": "2024 Austrian legislative election",
    "be24": "2024 Belgian federal election", "lt24": "2024 Lithuanian parliamentary election",
    "md24": "2024 Moldovan presidential election", "ge24": "2024 Georgian parliamentary election",
    "uy24": "2024 Uruguayan general election", "ve24": "2024 Venezuelan presidential election",
    "ru26": "2026 Russian legislative election", "gl25": "2025 Greenlandic general election",
    "kr26l": "2026 South Korean local elections", "md25": "2025 Moldovan parliamentary election",
    "ph25": "2025 Philippine Senate election", "sr25": "2025 Surinamese general election",
    "nz26": "2026 New Zealand general election", "ee26": "2026 Estonian parliamentary election",
    "lv26": "2026 Latvian parliamentary election", "ba26": "2026 Bosnian general election",
    "uk26l": "2026 United Kingdom local elections", "de26fr": "2026 French municipal elections",
}


def wiki_page(title):
    r = bot.http_json(WIKI, {"action": "parse", "page": title, "prop": "text|revid", "format": "json", "redirects": 1})
    p = r.get("parse") or {}
    return p.get("title"), p.get("revid"), (p.get("text") or {}).get("*") or ""


def wiki():
    """Raw HTML of every 'Opinion polling for the ...' page (and its sub-pages for big countries) -> bt_cache/elw/."""
    import gzip
    os.makedirs(WCACHE, exist_ok=True)
    index = rj(os.path.join(WCACHE, "index.json.gz"), {}) or {}
    for key, q in ELECTIONS.items():
        if key in index and index[key].get("pages"):
            continue
        titles = []
        try:
            r = bot.http_json(WIKI, {"action": "query", "list": "search", "srsearch": f"Opinion polling for the {q}",
                                     "srlimit": 10, "format": "json"})
            hits = [h["title"] for h in (r.get("query") or {}).get("search") or []]
        except Exception as e:
            print(key, "search failed", str(e)[:80], flush=True)
            continue
        yr = q[:4]
        words = [w for w in re.findall(r"[A-Za-zÀ-ÿ-]+", q) if len(w) > 3 and w.lower() not in ("election", "general")]
        good = [h for h in hits if h.lower().startswith("opinion polling") and yr in h
                and sum(w.lower()[:5] in h.lower() for w in words) >= max(1, len(words) - 1)]
        titles = good[:3] or [f"Opinion polling for the {q}"]
        pages = []
        for t in titles:
            try:
                tt, rev, html = wiki_page(t)
            except Exception as e:
                print(key, t, "failed", str(e)[:80], flush=True)
                continue
            if not html or "wikitable" not in html:
                continue
            fn = f"{key}_{len(pages)}.html.gz"
            with gzip.open(os.path.join(WCACHE, fn), "wt") as f:
                f.write(html)
            pages.append({"title": tt, "rev": rev, "file": fn, "tables": html.count("wikitable")})
        # the election article too (results table, election day)
        try:
            tt, rev, html = wiki_page(q)
            with gzip.open(os.path.join(WCACHE, f"{key}_article.html.gz"), "wt") as f:
                f.write(html)
            art = tt
        except Exception:
            art = None
        index[key] = {"q": q, "hits": hits[:6], "pages": pages, "article": art}
        print(key, "|", q, "|", [(p["title"], p["tables"]) for p in pages], "| article", art, flush=True)
        wj(os.path.join(WCACHE, "index.json.gz"), index)
        time.sleep(0.5)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "scan"
    if cmd == "scan":
        scan()
    elif cmd == "fetch":
        kfetch()
        pmfetch()
    elif cmd == "wiki":
        wiki()
    else:
        print("unknown command", cmd)
