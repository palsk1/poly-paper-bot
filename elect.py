#!/usr/bin/env python3
"""Non-US elections on Polymarket and Kalshi vs local poll averages (Wikipedia poll tables). Do US-based traders
misprice foreign races? Report backtest/elect.md.

PAPER ONLY. Reads public data, never trades, never writes state/.

  python3 elect.py scan        (probe el_scan: which foreign-election markets exist on both sites, with size)
  python3 elect.py fetch       (probe el_fetch: Kalshi markets + hourly quotes, Polymarket markets + real trades -> bt_cache/el/)
  python3 elect.py wiki        (probe el_wiki: Wikipedia "Opinion polling for the ..." pages -> bt_cache/elw/)
  python3 elect.py report [log]   (offline after `store.py pull bt_cache/el` and `bt_cache/elw`; needs lxml + numpy)
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
        exact = f"Opinion polling for the {q}"
        titles = [exact] + [h for h in good if h != exact][:2]
        pages = []
        for t in titles:
            try:
                tt, rev, html = wiki_page(t)
            except Exception as e:
                print(key, t, "failed", str(e)[:80], flush=True)
                continue
            if any(p["title"] == tt for p in pages):
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


# ---------------------------------------------------------------- poll tables -> poll lists
SKIP_COL = re.compile(r"sample|margin|lead|other|undecided|don.?t know|\bdk\b|dk/|n/?a\b|abs\.?|turnout|link|none|blank|"
                      r"would not|no one|refus|null|spoil|method|mode|size|moe|error|date|firm|pollster|agency|source|"
                      r"commission|aggregat|area|region|type|lean|swing|gov|opp|total|white|invalid|no answer|nota|"
                      r"\bnr\b|ns/nc|blanco|nulo|indecis|ninguno|neither|others|abstain|unsure", re.I)
OTHER_COL = re.compile(r"^others?\b|^oth\b|^altri|^otros|^outros", re.I)
DATE_COL = re.compile(r"date|fieldwork|conducted|polling$|last date|period|when|fecha|data", re.I)
MONTHS = {m: i + 1 for i, m in enumerate(("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"))}


def _num(x):
    x = re.sub(r"\[.*?\]|%|\s", "", str(x)).replace(",", ".").replace("−", "-")
    m = re.match(r"^<?(\d{1,2}(\.\d+)?)$", x)
    return float(m.group(1)) if m else None


def _end_date(txt, year):
    """Last date in a fieldwork string like '17–19 Feb 2025', 'Feb 28 – Mar 2, 2025', '2025-02-19'. -> 'YYYY-MM-DD' or None."""
    t = str(txt).lower()
    if "result" in t or "election" in t:
        return None
    t = re.sub(r"\[.*?\]", "", t)
    iso = re.findall(r"(20\d\d)-(\d\d)-(\d\d)", t)
    if iso:
        y, m, d = iso[-1]
        return f"{y}-{m}-{d}"
    yrs = re.findall(r"20\d\d", t)
    y = int(yrs[-1]) if yrs else year
    t2 = re.sub(r"20\d\d", " ", t)
    toks = re.findall(r"[a-z]+|\d+", t2)
    mon, day, last = None, None, None
    for i, k in enumerate(toks):
        if k[:3] in MONTHS:
            mon = MONTHS[k[:3]]
            if day is not None and last is None:
                last = (mon, day)
            elif i + 1 < len(toks) and toks[i + 1].isdigit() and int(toks[i + 1]) <= 31:
                last = (mon, int(toks[i + 1]))
            elif day is not None:
                last = (mon, day)
            day = None
        elif k.isdigit() and int(k) <= 31:
            day = int(k)
            if mon is not None:
                last = (mon, day)
    if mon is not None and day is not None:
        last = (mon, day)
    if not last:
        nums = re.findall(r"(\d{1,2})[./](\d{1,2})[./]?(\d{2,4})?", t)
        if not nums:
            return None
        d, m, yy = nums[-1]
        last = (int(m), int(d))
        if yy:
            y = int(yy) + (2000 if len(yy) == 2 else 0)
    try:
        return dt.date(y, last[0], last[1]).isoformat()
    except ValueError:
        return None


def _flat(col):
    parts = col if isinstance(col, tuple) else (col,)
    out = []
    for p in parts:
        p = re.sub(r"\[.*?\]", "", str(p)).strip()
        if p.startswith("Unnamed") or not p or p in out:
            continue
        out.append(p)
    return " / ".join(out)


def _cell_name(c):
    t = re.sub(r"\[.*?\]", "", c.text_content()).strip()
    if t:
        return re.sub(r"\s+", " ", t)
    for a in c.xpath(".//a[@title]"):
        return a.get("title").strip()
    for a in c.xpath(".//img[@alt]"):
        if a.get("alt").strip():
            return a.get("alt").strip()
    return ""


def _grid(el):
    """A wikitable as a grid of (is_header, name) cells with row/col spans spread out."""
    rows, pend = [], {}
    for tr in el.xpath("./tr|./thead/tr|./tbody/tr|./tfoot/tr"):
        row, ci = [], 0
        cells = tr.xpath("./th|./td")
        k = 0
        while k < len(cells) or ci in pend:
            if ci in pend:
                v, left = pend[ci]
                row.append(v)
                if left <= 1:
                    del pend[ci]
                else:
                    pend[ci] = (v, left - 1)
                ci += 1
                continue
            c = cells[k]
            k += 1
            try:
                cs = int(re.match(r"\d+", c.get("colspan") or "1").group(0))
                rs = int(re.match(r"\d+", c.get("rowspan") or "1").group(0))
            except Exception:
                cs, rs = 1, 1
            v = (c.tag == "th", _cell_name(c))
            for j in range(min(cs, 60)):
                row.append(v)
                if rs > 1:
                    pend[ci] = (v, rs - 1)
                ci += 1
        rows.append(row)
    return rows


def parse_page(html, year):
    """Every poll table of a page -> [{'cols': [names], 'polls': [(end day, {name: share of valid votes})]}]."""
    import lxml.html
    try:
        doc = lxml.html.fromstring(html)
    except Exception:
        return []
    out = []
    vote_days = set()
    for el in doc.xpath('//table[contains(@class, "wikitable")]'):
        g = _grid(el)
        if len(g) < 4:
            continue
        # header = the top rows until the first row with 3+ numbers
        h = 0
        while h < len(g) and sum(_num(v) is not None and not th for th, v in g[h]) < 3:
            h += 1
        if h == 0 or h >= len(g):
            continue
        width = max(len(r) for r in g)
        names = []
        for i in range(width):
            parts = []
            for r in g[:h]:
                if i < len(r) and r[i][1] and len(r[i][1]) <= 40 and r[i][1] not in parts and _num(r[i][1]) is None:
                    parts.append(r[i][1])
            names.append(" / ".join(parts))
        dcol = next((i for i, n in enumerate(names) if DATE_COL.search(n)), None)
        if dcol is None:
            continue
        body = [r for r in g[h:] if len(r) > 3]
        cand, oth = [], None
        for i, n in enumerate(names):
            if i == dcol or not n:
                continue
            vals = [_num(r[i][1]) if i < len(r) else None for r in body]
            ok = [v for v in vals if v is not None]
            if len(ok) < max(2, 0.4 * len(vals)) or max(ok) > 100:
                continue
            if OTHER_COL.search(n):
                oth = i
            elif not SKIP_COL.search(n):
                cand.append(i)
        if len(cand) < 2:
            continue
        polls = []
        for r in body:
            first = " ".join(r[j][1] for j in range(min(2, len(r)))).lower()
            if re.search(r"result|election|official|exit poll|count", first) or dcol >= len(r):
                if re.search(r"result|election", first) and dcol < len(r):
                    vd = _end_date(re.sub(r"(?i)result|election", "", r[dcol][1]), year)
                    if vd:
                        vote_days.add(vd)
                continue
            d = _end_date(r[dcol][1], year)
            if not d:
                continue
            sh = {names[i]: _num(r[i][1]) for i in cand if i < len(r)}
            sh = {k: v for k, v in sh.items() if v is not None}
            if len(sh) < 2:
                continue
            o = _num(r[oth][1]) if oth is not None and oth < len(r) else None
            tot = sum(sh.values()) + (o or 0)
            if tot < 50 or tot > 103:
                continue
            explicit = bool(re.search(r"20\d\d", r[dcol][1]))
            if polls and not explicit:          # newest first: a later row dated after the row above lost its year
                prev = dt.date.fromisoformat(polls[-1][0])
                cur = dt.date.fromisoformat(d)
                while cur > prev + dt.timedelta(days=45):
                    try:
                        cur = cur.replace(year=cur.year - 1)
                    except ValueError:
                        cur = cur - dt.timedelta(days=365)
                d = cur.isoformat()
            polls.append((d, {k: round(100 * v / tot, 2) for k, v in sh.items()}, explicit))
        if len(polls) >= 3:
            out.append({"cols": [names[i] for i in cand], "polls": polls})
    if out:
        out[0]["vote_days"] = sorted(vote_days)
    return out


def polls_all():
    """Parse every saved poll page -> {election key: [tables]} (pages whose title doesn't fit the election are skipped)."""
    import gzip
    idx = rj(os.path.join(WCACHE, "index.json.gz"), {}) or {}
    res = {}
    for key, info in idx.items():
        q = info["q"]
        year = int(q[:4])
        country = q.split()[1][:6].lower()
        files = [p["file"] for p in info["pages"] if country in p["title"].lower() and q[:4] in p["title"]]
        files.append(f"{key}_article.html.gz")
        tabs = []
        for fn in files:
            path = os.path.join(WCACHE, fn)
            if not os.path.exists(path):
                continue
            with gzip.open(path, "rt") as f:
                html = f.read()
            for tb in parse_page(html, year):
                tb["src"] = fn
                tabs.append(tb)
        res[key] = tabs
    return res


# ---------------------------------------------------------------- markets -> elections, outcomes -> poll columns
COUNTRY = [  # (key prefix, title words); checked in this order (states and cities before their country)
    ("bw", r"baden"), ("mv", r"mecklenburg"), ("be26", r"berlin"), ("st", r"saxony-anhalt|sachsen-anhalt"),
    ("rp", r"rhineland"), ("sco", r"scotland|scottish|holyrood|\bsnp\b"), ("wal", r"wales|welsh|senedd"),
    ("on", r"ontario"), ("bc", r"british columbia"), ("kr26l", r"korea.*local|local.*korea"),
    ("co26l", r"colombia.*(chamber|senate|congress|legislative|parliament)"),
    ("de", r"german|bundestag"), ("ca", r"canad"), ("ro", r"romania"), ("kr", r"korea"), ("pl", r"poland|polish"),
    ("au", r"australia"), ("pt", r"portug"), ("ie", r"ireland|irish"), ("pe", r"peru"), ("hu", r"hungar"),
    ("cl", r"chile"), ("nl", r"dutch|netherlands"), ("co", r"colombia"), ("bo", r"bolivia"), ("ar", r"argentin"),
    ("hn", r"hondur"), ("cz", r"czech"), ("br", r"brazil"), ("il", r"israel|knesset|likud"), ("no", r"norw"),
    ("th", r"thai"), ("jp", r"japan"), ("dk", r"denmark|danish"), ("si", r"sloven"), ("cr", r"costa rica"),
    ("se", r"swed"), ("bg", r"bulgari"), ("rs", r"serbia"), ("ec", r"ecuador"), ("hr", r"croatia"),
    ("uk", r"\buk\b|united kingdom|britain|british"), ("mx", r"mexic"), ("tw", r"taiwan"), ("bd", r"bangladesh"),
    ("np", r"nepal"), ("fr", r"france|french"), ("at", r"austria"), ("be24", r"belgi"), ("lt", r"lithuania"),
    ("md", r"moldova"), ("uy", r"uruguay"), ("ve", r"venezuela"), ("ru", r"russia"), ("gl", r"greenland"),
    ("lv", r"latvia"), ("nz", r"new zealand"), ("ee", r"estonia"), ("ph", r"philippin"), ("sr", r"suriname"),
]


def elec_key(title, end_year):
    t = str(title).lower()
    for pre, rx in COUNTRY:
        if not re.search(rx, t):
            continue
        best = None
        for k, q in ELECTIONS.items():
            if not (k == pre or (k.startswith(pre) and k[len(pre):len(pre) + 1].isdigit())):
                continue
            yy = int(q[:4])
            if abs(yy - end_year) > 1:
                continue
            ql = q.lower()
            pen = abs(yy - end_year) * 10
            if "president" in t and not re.search(r"president|general", ql):
                pen += 5
            if "president" not in t and "presidential" in ql:
                pen += 5
            if ("councillor" in t) != ("councillor" in ql):
                pen += 5
            if best is None or pen < best[0]:
                best = (pen, k)
        return best[1] if best else None
    return None


def kind_of(title, q):
    """What an event asks, in words the poll model can answer, or None."""
    t = str(title).lower().strip()
    if re.search(r"margin|turnout|seats?\b.*\?|# of|number of|how many|coalition|prime minister|chancellor|"
                 r"premier|districts|bloc|majority|lose (his|her) seat|mandate|percent|by-election", t) and \
            not re.search(r"% of (the )?(popular )?vote|vote share", t):
        if not re.search(r"most seats|gains? most seats|largest", t):
            return None
    if re.search(r"% of (the )?(popular )?vote|vote share|% vote", t):
        return "share"
    if re.search(r"4th|fourth|5th|fifth|bloc|% or more|win election to|outright|annul|mayor|chamber of deputies|"
                 r"legislative assembly|more votes|\bvs\.?\b|head.to.head", t):
        return None
    if re.search(r"2nd place|second place|2nd most|second most", t):
        return "rank2"
    if re.search(r"3rd place|third place|3rd most|third most", t):
        return "rank3"
    if re.search(r"advance|qualify|make (it to )?the (second round|runoff)|go to (the )?runoff", t):
        return "top2"
    if re.search(r"1st round|first round", t) and re.search(r"winner|win|most votes", t):
        return "rank1_r1"
    if re.search(r"winner|win|most seats|most votes|popular vote|largest|who will|next president|election\??$", t):
        return "rank1"
    return None


def _norm(x):
    import unicodedata
    x = unicodedata.normalize("NFKD", str(x))
    x = "".join(c for c in x if not unicodedata.combining(c))
    x = re.sub(r"([a-z])([A-Z])", r"\1 \2", x)          # 'TrzaskowskiPO' -> 'Trzaskowski PO'
    return re.sub(r"[^a-z0-9/+ ]", " ", x.lower())


ALIAS = {"union": "cdu csu", "cdu/csu": "union cdu csu", "labour": "lab", "labor": "alp lab", "conservative": "con cpc",
         "conservatives": "con cpc", "liberal": "lpc lib", "liberals": "lpc lib", "green": "grn gpc grune greens",
         "greens": "grn gpc grune green", "reform": "ref", "new democratic": "ndp", "bloc quebecois": "bq",
         "coalition": "l/np lnp", "liberal national": "l/np lnp", "social democrats": "spd sd s", "sinn fein": "sf",
         "fianna fail": "ff", "fine gael": "fg", "party for freedom": "pvv", "freedom party": "fpo pvv",
         "people's party": "ovp pp", "tisza": "tisza", "fidesz": "fidesz", "united russia": "ur", "likud": "likud",
         "democratic party": "dpk dp", "people power": "ppp", "liberal democratic": "ldp", "pt": "lula pt",
         "snp": "snp", "plaid": "pc plaid", "afd": "afd", "spd": "spd", "bsw": "bsw", "fdp": "fdp", "linke": "linke",
         "left": "linke left", "ano": "ano", "spolu": "spolu", "chega": "ch chega", "democratic alliance": "ad",
         "socialist": "ps psoe", "national rally": "rn", "new popular front": "nfp", "ensemble": "ens"}
STOP = {"the", "will", "win", "party", "of", "and", "de", "da", "do", "del", "la", "le", "von", "van", "for", "most",
        "seats", "next", "election", "be", "a", "in", "ind", "independent", "other", "others", "candidate", "jr", "dr"}


def toks(x):
    return {w for w in _norm(x).split() if len(w) >= 2 and w not in STOP}


def _w(w):
    return 3 if len(w) >= 4 else 2 if len(w) == 3 else 1


def match_col(item, cols):
    """The poll column for a market outcome ('AfD', 'Friedrich Merz', 'Lee Jae-myung'), or None if unsure."""
    if re.search(r" & | and |/.*/", str(item)) and not re.search(r"cdu/csu|gl/pvda", str(item), re.I):
        return None                         # a pair of candidates ('Jara & Matthei'): no single poll column
    it = _norm(item).strip()
    words = toks(item)
    al = set()
    for k, v in ALIAS.items():
        if re.search(r"\b" + re.escape(k) + r"\b", it):
            al |= set(v.split())
    best, bs = None, 0
    first = (re.findall(r"[A-Za-zÀ-ÿ]+", str(item)) or [""])[0][:1].lower()
    for c in cols:
        ini = re.findall(r"(?:^|\s)([A-Z])\.\s?[A-Z]", str(c))
        if ini and first and ini[0].lower() != first:
            continue                        # 'F. Bolsonaro' is not Michelle Bolsonaro
        ct = toks(c)
        sc = sum(_w(w) for w in words & ct) + 3 * len((al - words) & ct)
        if sc > bs:
            best, bs = c, sc
        elif sc == bs and sc > 0 and best != c:
            best = best if len(toks(best)) <= len(ct) else c
    return best if bs >= 2 or (bs >= 1 and len(words) == 1) else None


def vote_days(P):
    """Vote day(s) of each election from the result rows of its poll tables, inside the election's own year(s)."""
    out = {}
    for k, tabs in P.items():
        q = ELECTIONS.get(k)
        if not q:
            continue
        y = int(q[:4])
        ds = sorted({d for tb in tabs for d in tb.get("vote_days", []) if int(d[:4]) in (y, y + 1)})
        if k in FIX_DAYS:
            ds = FIX_DAYS[k]
        out[k] = [bt.ts(bot.parse_iso(d + "T12:00:00Z")) for d in ds]
    return out


def poll_avg(table, T, eday, window=14, min_polls=3, lag=2):
    """Average of the polls that ended 2+ days before T, in the last `window` days (widened to 45 if too few)."""
    cut = T - lag * 86400
    key = (id(table), eday)
    if key not in _SHIFTED:
        # a table whose rows carry no year was read as the election year; if that puts polls after the vote,
        # the whole table is from an earlier year: move its year-less rows back until none is after the vote
        rows = [(dt.date.fromisoformat(p[0]), p[1], p[2] if len(p) > 2 else True) for p in table["polls"]]
        ev = dt.datetime.fromtimestamp(eday, dt.timezone.utc).date() + dt.timedelta(days=1)
        for _ in range(4):
            if not any(d > ev and not ex for d, sh, ex in rows):
                break
            rows = [(d if ex else (d.replace(year=d.year - 1) if not (d.month == 2 and d.day == 29) else d - dt.timedelta(days=365)), sh, ex)
                    for d, sh, ex in rows]
        _SHIFTED[key] = [(bt.ts(bot.parse_iso(d.isoformat() + "T12:00:00Z")), sh) for d, sh, ex in rows if d <= ev]
    ps = [(t, sh) for t, sh in _SHIFTED[key] if t <= cut]
    for w in (window, 45):
        got = [sh for t, sh in ps if t >= cut - w * 86400]
        if len(got) >= min_polls:
            break
    else:
        return None, 0
    avg = collections.defaultdict(float)
    for sh in got:
        for k, v in sh.items():
            avg[k] += v / len(got)
    NEWEST[0] = max(t for t, sh in ps)
    return dict(avg), len(got)


NEWEST = [0]
_SHIFTED = {}


SIG_X = [1.0]       # poll-miss size multiplier (the test tries a few)


def sim(avg, days, n=4000, seed=1):
    """Final shares = poll average + error that grows with the share and with days left. -> array (n, k) and names."""
    import numpy as np
    rng = np.random.default_rng(seed)
    names = list(avg)
    a = np.array([avg[k] for k in names])
    sig = (0.6 + 0.05 * a) * min(3.0, 1 + days / 45) * SIG_X[0]
    x = np.clip(a + rng.standard_normal((n, len(a))) * sig, 0, None)
    rest = max(0.0, 100 - a.sum())
    x = x / (x.sum(axis=1, keepdims=True) + rest) * 100
    return x, names


BR = re.compile(r"(less than|under|below|fewer than|<)\s*(\d+(?:\.\d+)?)\s*%|(\d+(?:\.\d+)?)\s*%?\s*(?:-|–|to|and)\s*(\d+(?:\.\d+)?)\s*%|"
                r"(more than|over|above|at least|greater than|>|≥)\s*(\d+(?:\.\d+)?)\s*%|(\d+(?:\.\d+)?)\s*%\s*(or more|\+|or higher|or above)", re.I)


def bracket(q):
    m = BR.search(str(q))
    if not m:
        return None
    if m.group(1):
        return (-1, float(m.group(2)))
    if m.group(3):
        return (float(m.group(3)), float(m.group(4)))
    if m.group(5):
        return (float(m.group(6)), 101)
    return (float(m.group(7)), 101)

# vote days, written by hand (the result rows of the poll tables are too messy to trust); first round first
FIX_DAYS = {
    "de25": ["2025-02-23"], "ca25": ["2025-04-28"], "ro25": ["2025-05-04", "2025-05-18"], "ro24p": ["2024-11-24"],
    "ro24": ["2024-12-01"], "kr25": ["2025-06-03"], "pl25": ["2025-05-18", "2025-06-01"], "au25": ["2025-05-03"],
    "pt25": ["2025-05-18"], "pt26p": ["2026-01-18", "2026-02-08"], "ie25p": ["2025-10-24"], "ie24": ["2024-11-29"],
    "pe26": ["2026-04-12", "2026-06-07"], "hu26": ["2026-04-12"], "cl25": ["2025-11-16", "2025-12-14"],
    "nl25": ["2025-10-29"], "co26": ["2026-05-31", "2026-06-21"], "co26l": ["2026-03-08"],
    "bo25": ["2025-08-17", "2025-10-19"], "ar25": ["2025-10-26"], "hn25": ["2025-11-30"], "cz25": ["2025-10-04"],
    "br26": ["2026-10-04", "2026-10-25"], "il26": ["2026-10-27"], "th26": ["2026-02-08"], "jp26": ["2026-02-08"],
    "jp25c": ["2025-07-20"], "jp24": ["2024-10-27"], "si26": ["2026-03-22"], "cr26": ["2026-02-01"],
    "se26": ["2026-09-13"], "sco26": ["2026-05-07"], "wal26": ["2026-05-07"], "bg26p": ["2026-10-25", "2026-11-01"],
    "ec25": ["2025-02-09", "2025-04-13"], "hr24p": ["2024-12-29", "2025-01-12"], "uk24": ["2024-07-04"],
    "mx24": ["2024-06-02"], "tw24": ["2024-01-13"], "on25": ["2025-02-27"], "bc24": ["2024-10-19"],
    "bd26": ["2026-02-12"], "np26": ["2026-03-05"], "bw26": ["2026-03-08"], "rp26": ["2026-03-22"],
    "mv26": ["2026-09-20"], "be26": ["2026-09-20"], "st26": ["2026-09-06"], "fr24": ["2024-06-30", "2024-07-07"],
    "at24": ["2024-09-29"], "be24": ["2024-06-09"], "lt24": ["2024-10-13", "2024-10-27"],
    "md24": ["2024-10-20", "2024-11-03"], "ge24": ["2024-10-26"], "uy24": ["2024-10-27", "2024-11-24"],
    "ve24": ["2024-07-28"], "ru26": ["2026-09-20"], "gl25": ["2025-03-11"], "no25": ["2025-09-08"],
    "md25": ["2025-09-28"], "lv26": ["2026-10-03"],
}
FIRST_ROUND_KINDS = ("rank1_r1", "top2", "rank2", "rank3")
FPTP = ("ca", "uk", "au", "fr", "bc", "on")


# ---------------------------------------------------------------- the test
DAYS = (60, 30, 14, 7, 3, 1)          # looks: this many days before the vote


def pm_load():
    import glob
    ms = rj(PM_MK, {}) or {}
    tp = {}
    for f in sorted(glob.glob(os.path.join(CACHE, "pm_tapes_*.json.gz"))):
        tp.update(rj(f, {}) or {})
    ms = {k: m for k, m in ms.items() if m.get("final") in ([1.0, 0.0], [0.0, 1.0])}
    return ms, tp


def last_px(b, t, fresh=86400):
    p = None
    for x in b:
        if x[0] + 300 <= t:
            p = x[2] if x[0] >= t - fresh else None
        else:
            break
    return p


def pm_buy(m, b, t, yes, extra=0.01, stake=25.0, window=3600):
    """Worst price anyone paid in the hour after t + 1c + the market's fee."""
    nxt = [x for x in b if t <= x[0] < t + window]
    if not nxt:
        return None
    px = max(x[4] for x in nxt) if yes else 1 - min(x[3] for x in nxt)
    if not 0.02 <= px <= 0.98:
        return None
    c = min(0.99, px + extra)
    sh = stake / c
    won = (m["final"][0] == 1.0) == yes
    return {"cost": stake + bot.taker_fee(sh, c, m.get("fee") or 0.0), "pay": sh if won else 0.0, "px": px, "t": nxt[0][0]}


def pm_groups(ms):
    """Polymarket events -> (election key, kind, vote day, [markets])."""
    ev = collections.defaultdict(list)
    for m in ms.values():
        ev[m["ev_slug"]].append(m)
    out = []
    for slug, v in ev.items():
        title = v[0].get("title") or ""
        endtxt = v[0].get("ev_end") or ""
        try:
            eday = bt.ts(bot.parse_iso(endtxt[:10] + "T12:00:00Z"))
        except Exception:
            continue
        k = elec_key(title, int(endtxt[:4]))
        kd = kind_of(title, v[0]["q"])
        if kd and kd != "share" and k and k[:2] in FPTP and re.search(r"seat|parliament|legislat|party", title, re.I):
            kd = None              # first-past-the-post: national vote shares don't give the seat order (Canada's Bloc)
        days = [bt.ts(bot.parse_iso(d + "T12:00:00Z")) for d in FIX_DAYS.get(k, [])]
        if not days:
            continue
        if len(days) > 1 and (kd in FIRST_ROUND_KINDS or re.search(r"1st round|first round", title, re.I)):
            eday = days[0]
        else:
            eday = days[-1]
        out.append({"slug": slug, "title": title, "key": k, "kind": kd, "eday": eday, "ms": v})
    return out


def group_rows(g, tabs, two, price_fn, st, gap_days=DAYS):
    """One event (all its outcome markets) at every look -> rows with the poll chance and the price."""
    out = []
    for d in gap_days:
        T = g["eday"] - d * 86400 - 12 * 3600       # noon the day before 'd days out'
        prices = {}
        for m in g["ms"]:
            p = price_fn(m, T)
            if p is not None and (m.get("start") or 0) < T:
                prices[m["id"]] = p
        if not prices:
            continue
        wsum = sum(prices.values()) or 1
        best = None
        for tb in tabs:
            avg, n = poll_avg(tb, T, g["eday"])
            if not avg:
                continue
            if g["kind"] == "rank1" and g["key"] in two:
                if len(avg) != 2:
                    continue      # a two-round vote: the overall winner comes from head-to-head polls only
            elif len(avg) < 3:
                continue          # a head-to-head table can't answer a first-round or vote-share question
            cov, mp = 0.0, {}
            who = re.split(r"%|\bvote\b", g["title"], flags=re.I)[0] if g["kind"] == "share" else None
            for m in g["ms"]:
                if m["id"] not in prices:
                    continue
                c = match_col(who or m.get("item") or m["q"], list(avg))
                if who:
                    if c:
                        mp[m["id"]] = c
                    continue
                if c and c not in mp.values():
                    mp[m["id"]] = c
                    cov += prices[m["id"]]
            cov /= wsum
            if g["kind"] == "share":
                if not mp:
                    continue
            elif cov < 0.85:
                continue
            fresh = NEWEST[0] >= T - 12 * 86400
            score = (cov >= 0.95, fresh, n >= 5, -len(avg) if g["kind"] == "rank1" else len(avg), n)
            if best is None or score > best[0]:
                best = (score, avg, n, mp, cov)
        if not best:
            st["look: no poll table fits"] += 1
            continue
        _, avg, n, mp, cov = best
        x, names = sim(avg, d)
        rank = (-x).argsort(axis=1).argsort(axis=1)            # 0 = first
        for m in g["ms"]:
            if m["id"] not in prices or m["id"] not in mp:
                continue
            j = names.index(mp[m["id"]])
            kd = g["kind"]
            if kd in ("rank1", "rank1_r1"):
                p = float((rank[:, j] == 0).mean())
            elif kd == "rank2":
                p = float((rank[:, j] == 1).mean())
            elif kd == "rank3":
                p = float((rank[:, j] == 2).mean())
            elif kd == "top2":
                p = float((rank[:, j] <= 1).mean())
            else:
                br = bracket(m.get("item") or "") or bracket(m["q"])
                if not br:
                    continue
                p = float(((x[:, j] >= br[0]) & (x[:, j] < br[1])).mean())
            p = min(0.995, max(0.005, p))
            out.append({"m": m, "g": g, "d": d, "T": T, "p": p, "px": prices[m["id"]], "col": mp[m["id"]],
                        "poll": round(avg[mp[m["id"]]], 1), "npolls": n, "cov": round(cov, 2), "won": m["won"]})
            st["rows"] += 1
    return out


def model_rows(P=None, ms=None, tp=None):
    """Polymarket: every outcome market of every foreign election event at every look."""
    P = P if P is not None else polls_all()
    if ms is None:
        ms, tp = pm_load()
    for m in ms.values():
        m["won"] = m["final"][0] == 1.0
    G_ = [g for g in pm_groups(ms) if "(old)" not in g["title"].lower()]
    two = {g["key"] for g in G_ if re.search(r"1st round|first round|second round|2nd round|runoff|run-off", g["title"], re.I)}
    rows, st = [], collections.Counter()
    pf = lambda m, T: last_px((tp.get(m["id"]) or {}).get("b") or [], T)
    for g in G_:
        st["events"] += 1
        if not g["key"] or not g["kind"]:
            st["events: not a vote-count question"] += 1
            continue
        if not P.get(g["key"]):
            st["events: no poll table"] += 1
            continue
        st["events with polls"] += 1
        rr = group_rows(g, P[g["key"]], two, pf, st)
        for r in rr:
            r["tp"] = (tp.get(r["m"]["id"]) or {}).get("b") or []
        rows += rr
    return rows, st, G_


def k_load():
    have = rj(K_MK, {}) or {"series": {}, "markets": {}}
    tp = rj(os.path.join(CACHE, "k_tapes.json.gz"), {}) or {}
    for v in tp.values():                        # the 100-times-too-small quote trap
        vals = [x for c in v["c"] for x in c[1:3] if x is not None]
        if vals and max(vals) <= 0.0101 and v["tr"] and max(t[1] for t in v["tr"]) > 20:
            for c in v["c"]:
                c[1] = None if c[1] is None else round(c[1] * 100, 4)
                c[2] = None if c[2] is None else round(c[2] * 100, 4)
    return have, tp


def k_quote(c, T, fresh=6 * 3600, gap=0.10):
    q = None
    for x in c:
        if x[0] > T:
            break
        if T - x[0] <= fresh:
            q = x
    if not q or q[1] is None or q[2] is None or q[1] <= 0 or q[2] >= 1 or q[2] - q[1] > gap:
        return None
    return q


def k_rows(P, G_pm):
    """Kalshi: the same model on Kalshi's foreign election series; vote day taken from the matching Polymarket event."""
    have, tp = k_load()
    two = {g["key"] for g in G_pm if re.search(r"1st round|first round|second round|2nd round|runoff|run-off", g["title"], re.I)}
    eday = collections.defaultdict(list)
    for g in G_pm:
        if g["key"] and g["kind"]:
            eday[(g["key"], g["kind"])].append(g["eday"])
            eday[(g["key"], None)].append(g["eday"])
    ev = collections.defaultdict(list)
    for m in have["markets"].values():
        if m["t"] in tp:
            ev[m["ev"]].append(m)
    rows, st = [], collections.Counter()
    for e, v in ev.items():
        s = have["series"].get(v[0]["s"]) or {}
        title = f"{s.get('title', '')} {v[0]['q']}"
        yr = int(d10(max(m["close"] for m in v))[:4])
        k = elec_key(title, yr)
        kd = kind_of(s.get("title", "") + " winner" if re.search(r"winner|election|presiden|party", s.get("title", ""), re.I)
                     and not re.search(r"seat|mov|margin|%|percent|vote share|coalition|pm\b|chancellor|leader|turnout",
                                       title, re.I) else title, "")
        if re.search(r"% of|percent|vote share|\bvote\b", s.get("title", ""), re.I) and re.search(r"%|percent|share", title, re.I):
            kd = "share"
        if kd and re.search(r"\bsecond\b|2nd", title, re.I):
            kd = "rank2"
        if kd and re.search(r"\bthird\b|3rd", title, re.I):
            kd = "rank3"
        if kd and kd != "share" and k and k[:2] in FPTP and re.search(r"seat|parliament|legislat|party", title, re.I):
            kd = None
        st["events"] += 1
        if not k or not kd or not P.get(k):
            st["events: no key, kind or polls"] += 1
            continue
        cand = sorted(eday.get((k, kd)) or eday.get((k, None)) or [])
        close = min(m["close"] for m in v)
        cand = [t for t in cand if t <= close + 86400]
        if not cand:
            st["events: no vote day"] += 1
            continue
        g = {"slug": e, "title": title, "key": k, "kind": kd, "eday": cand[-1], "ms": []}
        for m in v:
            g["ms"].append({"id": m["t"], "item": m["w"], "q": m["q"] + " " + m.get("ck", ""), "won": m["res"] == "yes",
                            "start": m["open"], "km": m})
        st["events with polls"] += 1

        def pf(m, T):
            q = k_quote(tp[m["id"]]["c"], T)
            return None if q is None else (q[1] + q[2]) / 2
        for r in group_rows(g, P[k], two, pf, st):
            q = k_quote(tp[r["m"]["id"]]["c"], r["T"])
            r["bid"], r["ask"] = q[1], q[2]
            rows.append(r)
    return rows, st


def k_bets(rows, rule):
    import dates
    out, seen = [], set()
    for r in sorted(rows, key=lambda r: r["T"]):
        k = r["m"]["id"]
        if k in seen:
            continue
        side = rule(r)
        if not side:
            continue
        seen.add(k)
        yes = side == "yes"
        p = r["ask"] if yes else 1 - r["bid"]
        if not 0.02 <= p <= 0.98:
            continue
        c = p + dates.k_fee(p)
        out.append({"ev": r["g"]["slug"], "t": r["T"], "cost": c, "pay": 1.0 if r["won"] == yes else 0.0, "px": p,
                    "key": r["g"]["key"], "d": r["d"], "p": r["p"], "question": r["m"]["q"], "yes": yes, "won": r["won"]})
    return out


def brier(rows, f):
    return sum((f(r) - r["won"]) ** 2 for r in rows) / max(1, len(rows))


def pm_bets(rows, rule, extra=0.01):
    """One $25 bet per market: the first look (farthest out first) where rule(r) says 'yes'/'no'."""
    out, seen = [], set()
    for r in sorted(rows, key=lambda r: r["T"]):
        k = r["m"]["id"]
        if k in seen:
            continue
        side = rule(r)
        if not side:
            continue
        x = pm_buy(r["m"], r["tp"], r["T"], side == "yes", extra)
        if not x:
            continue
        seen.add(k)
        x.update(ev=r["g"]["slug"], key=r["g"]["key"], d=r["d"], p=r["p"], question=r["m"]["q"], yes=side == "yes", won=r["won"])
        out.append(x)
    return out


# ---------------------------------------------------------------- backward look: prices alone
REGION = {"Latin America": ("br", "cl", "co", "pe", "bo", "ar", "hn", "ec", "cr", "mx", "uy", "ve"),
          "Asia": ("kr", "jp", "th", "tw", "bd", "np", "ph"),
          "Europe and the rest": ()}


def region(k):
    for r, pre in REGION.items():
        if k[:2] in pre:
            return r
    return "Europe and the rest"


def comb_rows(ms, tp):
    """Every foreign election outcome market (any question about the vote) at 30, 7 and 1 days before the vote."""
    out = []
    for g in pm_groups(ms):
        if not g["key"] or "(old)" in g["title"].lower():
            continue
        for d in (30, 7, 1):
            T = g["eday"] - d * 86400 - 12 * 3600
            for m in g["ms"]:
                b = (tp.get(m["id"]) or {}).get("b") or []
                p = last_px(b, T)
                if p is None or (m.get("start") or 0) >= T:
                    continue
                out.append({"m": m, "g": g, "d": d, "T": T, "px": p, "tp": b, "won": m["final"][0] == 1.0})
    return out


def first_bets(R, sel, yes):
    out, seen = [], set()
    for r in sorted(R, key=lambda r: r["T"]):
        k = (r["m"]["id"], r["d"])
        if k in seen or not sel(r):
            continue
        x = pm_buy(r["m"], r["tp"], r["T"], yes)
        if not x:
            continue
        seen.add(k)
        x.update(ev=r["g"]["key"], key=r["g"]["key"], d=r["d"], question=r["m"]["q"], yes=yes, won=r["won"])
        out.append(x)
    return out


# ---------------------------------------------------------------- report (backtest/elect.md tables)
def per100(b):
    c = sum(x["cost"] for x in b)
    return sum(x["pay"] - x["cost"] for x in b) / c * 100 if c else 0.0


def f2(x):
    return f"{'+' if x >= 0 else '-'}${abs(x):.2f}"


TRIES = 40     # cuts looked at: 4 poll-miss sizes, 2 gaps, 3 sides, both sites, 6 days, 6 price bands x 2 sides x 3 days, regions


def report(log=False):
    import exam
    P = polls_all()
    ms, tp = pm_load()
    print("## How good are the polls against the price?\n")
    print("| poll-miss size | looks | price score | poll score |\n|---|---|---|---|")
    for x in (1.0, 1.5, 2.0, 3.0):
        SIG_X[0] = x
        rows, st, G = model_rows(P, ms, tp)
        print(f"| x{x} | {len(rows)} | {brier(rows, lambda r: r['px']):.4f} | {brier(rows, lambda r: r['p']):.4f} |")
    SIG_X[0] = 2.0
    rows, st, G = model_rows(P, ms, tp)
    kr, kst = k_rows(P, G)
    print(f"\nPolymarket: {len({r['g']['slug'] for r in rows})} events, {len({r['g']['key'] for r in rows})} elections, "
          f"{len(rows)} looks; Kalshi: {len({r['g']['slug'] for r in kr})} events, {len({r['g']['key'] for r in kr})} elections, {len(kr)} looks\n")
    print("| days before the vote | Polymarket looks | price score | poll score | Kalshi looks | price score | poll score |\n|---|---|---|---|---|---|---|")
    for d in DAYS:
        a = [r for r in rows if r["d"] == d]
        b = [r for r in kr if r["d"] == d]
        print(f"| {d} | {len(a)} | {brier(a, lambda r: r['px']):.4f} | {brier(a, lambda r: r['p']):.4f} | {len(b)} | "
              f"{brier(b, lambda r: r['px']):.4f} | {brier(b, lambda r: r['p']):.4f} |")
    rules = {
        "follow the polls, 10c+ apart": lambda r: "yes" if r["p"] - r["px"] >= 0.10 else "no" if r["px"] - r["p"] >= 0.10 else None,
        "follow the polls, 20c+ apart": lambda r: "yes" if r["p"] - r["px"] >= 0.20 else "no" if r["px"] - r["p"] >= 0.20 else None,
        "follow the polls, Yes only": lambda r: "yes" if r["p"] - r["px"] >= 0.10 else None,
        "follow the polls, No only": lambda r: "no" if r["px"] - r["p"] >= 0.10 else None,
        "against the polls, 10c+ apart": lambda r: "no" if r["p"] - r["px"] >= 0.10 else "yes" if r["px"] - r["p"] >= 0.10 else None,
    }
    print("\n## Betting where the polls and the price disagree ($25 a bet, one bet per market, real prices)\n")
    print("| site | rule | bets | elections | won | per $100 | first half / second half | luck range per $100 | "
          "exam verdict | without the best election |\n|---|---|---|---|---|---|---|---|---|---|")
    for name, f in rules.items():
        for site, bb in (("Polymarket", pm_bets(rows, f)), ("Kalshi", k_bets(kr, f))):
            for x in bb:
                x["ev"] = x["key"]          # one election = one group: its markets win and lose together
            bb.sort(key=lambda x: x["t"])
            lg = log and name == "follow the polls, 10c+ apart"
            c = exam.score(bb, f"Foreign elections, {site}: {name} (Wikipedia poll average vs price)", tries=TRIES,
                           log=lg, quiet=True, status="dropped" if lg else None, src="elect.py, backtest/elect.md")
            byk = collections.defaultdict(float)
            for x in bb:
                byk[x["key"]] += x["pay"] - x["cost"]
            best = max(byk, key=byk.get) if byk else None
            h = len(bb) // 2
            print(f"| {site} | {name} | {len(bb)} | {len(byk)} | {sum(x['pay'] > 0 for x in bb)} | {f2(per100(bb))} | "
                  f"{f2(per100(bb[:h]))} / {f2(per100(bb[h:]))} | {c.get('lo100')} to {c.get('hi100')} | {c.get('verdict')} | "
                  f"{f2(per100([x for x in bb if x['key'] != best]))} (without {best}) |")
    print("\n## Prices alone (backward look): every foreign election market, Polymarket, real prices\n")
    R = comb_rows(ms, tp)
    BANDS = [(0.02, 0.10), (0.10, 0.25), (0.25, 0.50), (0.50, 0.75), (0.75, 0.90), (0.90, 0.98)]
    print("| days before | Yes price | markets | elections | Yes won | buy Yes per $100 | buy No per $100 |\n|---|---|---|---|---|---|---|")
    for d in (30, 7, 1):
        for lo, hi in BANDS:
            sel = lambda r, lo=lo, hi=hi, d=d: r["d"] == d and lo <= r["px"] < hi
            y, n = first_bets(R, sel, True), first_bets(R, sel, False)
            if y:
                print(f"| {d} | {lo * 100:.0f}-{hi * 100:.0f}c | {len(y)} | {len({x['key'] for x in y})} | {sum(x['won'] for x in y)} | "
                      f"{f2(per100(y))} | {f2(per100(n))} |")
    print("\n| region | long shots (2-25c) a week before: buy Yes | buy No | favourites (50-98c) a week before: buy Yes |\n|---|---|---|---|")
    for reg in REGION:
        sl = lambda r, reg=reg: r["d"] == 7 and region(r["g"]["key"]) == reg and 0.02 <= r["px"] < 0.25
        sf = lambda r, reg=reg: r["d"] == 7 and region(r["g"]["key"]) == reg and 0.50 <= r["px"] < 0.98
        y, n, fv = first_bets(R, sl, True), first_bets(R, sl, False), first_bets(R, sf, True)
        print(f"| {reg} | {f2(per100(y))} ({len(y)}) | {f2(per100(n))} | {f2(per100(fv))} ({len(fv)}) |")
    fav = [r for r in R if r["d"] == 7 and r["px"] >= 0.6 and kind_of(r["g"]["title"], "") in ("rank1", "rank1_r1")]
    print(f"\nWinner questions, favourite at 60c+ a week before: {len(fav)}, won {sum(r['won'] for r in fav)}, "
          f"average price {sum(r['px'] for r in fav) / max(1, len(fav)):.2f}. Upsets:")
    print("\n| backward look: No on the favourite (winner questions) | bets | elections | No won | per $100 | luck range | exam verdict | without the best election |\n|---|---|---|---|---|---|---|---|")
    for d in (30, 7, 1):
        sel = lambda r, d=d: r["d"] == d and 0.6 <= r["px"] < 0.98 and kind_of(r["g"]["title"], "") in ("rank1", "rank1_r1")
        n = first_bets(R, sel, False)
        for x in n:
            x["ev"] = x["key"]
        n.sort(key=lambda x: x["t"])
        lg = log and d == 7
        c = exam.score(n, "Foreign elections, Polymarket: No on the 60-98c favourite a week before (backward look)",
                       tries=TRIES, log=lg, quiet=True, status="dropped" if lg else None, src="elect.py, backtest/elect.md")
        byk = collections.defaultdict(float)
        for x in n:
            byk[x["key"]] += x["pay"] - x["cost"]
        best = max(byk, key=byk.get) if byk else None
        print(f"| {d} days before, favourite at 60-98c | {len(n)} | {len(byk)} | {sum(x['pay'] > 0 for x in n)} | {f2(per100(n))} | "
              f"{c.get('lo100')} to {c.get('hi100')} | {c.get('verdict')} | {f2(per100([x for x in n if x['key'] != best]))} (without {best}) |")
    pmr = {(r["m"]["id"], 7): r for r in rows}
    for r in fav:
        if not r["won"]:
            x = pmr.get((r["m"]["id"], 7))
            print(f"- {r['g']['key']}: {r['m'].get('item')} at {r['px'] * 100:.0f}c ({r['g']['title'][:60]}); "
                  f"polls: {'%.0f in 100' % (x['p'] * 100) if x else 'no poll table'}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "scan"
    if cmd == "scan":
        scan()
    elif cmd == "fetch":
        kfetch()
        pmfetch()
    elif cmd == "wiki":
        wiki()
    elif cmd == "report":
        report(log="log" in sys.argv[2:])
    else:
        print("unknown command", cmd)
