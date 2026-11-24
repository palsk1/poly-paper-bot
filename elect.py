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
    "nl25": "2025 Dutch general election", "co26": "2026 Colombian presidential election", "pe26b": "2026 Peruvian presidential election",
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
            polls.append((d, {k: round(100 * v / tot, 2) for k, v in sh.items()}))
        if len(polls) >= 3:
            out.append({"cols": [names[i] for i in cand], "polls": polls})
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
