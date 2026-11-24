#!/usr/bin/env python3
"""Trump speech transcripts against his "will he say X" markets (2026-11-15). Research only.

PAPER ONLY. Reads public history, never trades, never writes state/.

    python3 speeches.py peek      # probe sp_peek: which transcript sources can Actions read?
"""
import re
import sys
import urllib.request

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"


def raw(url, n=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/json,*/*"})
    with urllib.request.urlopen(req, timeout=n) as r:
        return r.read().decode("utf-8", "replace")


def peek():
    urls = ["https://trump-archive.com/archive", "https://trump-archive.com/archive/2026-10", "https://trump-archive.com/2026-10",
            "https://trump-archive.com/sitemap.xml", "https://trump-archive.com/robots.txt", "https://trump-archive.com/api/items?month=2026-10",
            "https://www.democrats.senate.gov/newsroom/trump-transcripts?PageNum_rs=2",
            "https://rollcall.com/factbase/trump/search/", "https://rollcall.com/wp-json/factbase/v1/search?media=&type=&sort=date&location=all&place=all&page=1&format=json",
            "https://www.pizzint.watch/mentions"]
    for u in urls:
        try:
            s = raw(u)
        except Exception as e:
            print("FAIL", u, str(e)[:150], flush=True)
            continue
        print("OK", u, len(s), flush=True)
        print("   head:", re.sub(r"\s+", " ", s[:600]), flush=True)
        links = sorted(set(re.findall(r'href="([^"#]+)"', s)))
        print("   links:", len(links), [x for x in links if "css" not in x and "font" not in x][:60], flush=True)
        apis = sorted(set(re.findall(r'["\'](/(?:api|_next/data|wp-json)[^"\']+)["\']', s)))
        print("   apis:", apis[:20], flush=True)


# Bug fix 2026-11-24: the old list address (wp-json/factbase/v1/search) answers 404 since about 18 Nov 2026, which
# left trump_week / trump_week_k with a stale record (no bets). The new one gives the same rows, newest first, 40 a page.
API = "https://rollcall.com/api/factbase/transcripts?person=trump&page={}"


def peek5():
    """Roll Call moved its list API about 18 Nov 2026 (the old wp-json search answers 404). Look at the new one."""
    base = "https://rollcall.com/api/factbase/transcripts"
    for q in ("?person=trump", "?person=trump&page=2", "?person=trump&page=1&per_page=50", "?person=trump&sort=date&page=1"):
        try:
            s = raw(base + q, 40)
        except Exception as e:
            print("FAIL", q, str(e)[:150], flush=True)
            continue
        print("OK", q, len(s), flush=True)
        print("   body:", re.sub(r"\s+", " ", s[:3000]), flush=True)
        try:
            j = json.loads(s)
            print("   keys:", list(j)[:20] if isinstance(j, dict) else type(j).__name__, flush=True)
        except Exception:
            pass


def peek6():
    """Kalshi's weekly KXTRUMPSAY list showed 0 open markets on 24 Nov 2026: newest events, and any similar series."""
    import bot
    for st in ("open", "closed", "settled", None):
        try:
            q = {"series_ticker": "KXTRUMPSAY", "limit": 10, **({"status": st} if st else {})}
            ev = bot.kalshi_get("/events", q).get("events") or []
            print("events", st, [(e.get("event_ticker"), e.get("title"), e.get("strike_date") or e.get("close_time")) for e in ev[:10]], flush=True)
        except Exception as e:
            print("events", st, "FAIL", str(e)[:150], flush=True)
    try:
        sers = bot.kalshi_get("/series", {"category": "Mentions"}).get("series") or []
        print("series with TRUMP:", [(x.get("ticker"), x.get("title"), x.get("frequency")) for x in sers if "TRUMP" in str(x.get("ticker"))][:60], flush=True)
    except Exception as e:
        print("series FAIL", str(e)[:150], flush=True)


def peek7():
    """Does a new transcript page still parse? (24 Nov 2026: list fixed, but new days came back empty)"""
    import json as _j
    rows = _j.loads(raw(API.format(1), 40)).get("data") or []
    for x in [r for r in rows if "no-transcript" not in str(r.get("slug"))][:2]:
        u = x["factbase_url"]
        s = raw(u, 60)
        b = parse(s)
        print("URL", u, "len", len(s), "blocks", len(b), b[:3], flush=True)
        i = max(s.find("Donald Trump"), 0)
        for k in ("speaker", "transcript", "data-", "__NEXT_DATA__", "wp-json", "/api/"):
            j = s.find(k, i)
            print("  near", k, j, re.sub(r"\s+", " ", s[j:j + 700]) if j >= 0 else "", flush=True)


def peek8():
    """Transcript pages now load their text from an API in the browser: find that API."""
    import json as _j
    rows = _j.loads(raw(API.format(1), 40)).get("data") or []
    x = [r for r in rows if "no-transcript" not in str(r.get("slug"))][0]
    slug = x["slug"]
    s = raw(x["factbase_url"], 60)
    for m in re.finditer(r"factbaseTranscript", s):
        print("  page:", re.sub(r"\s+", " ", s[max(0, m.start() - 300):m.start() + 300]), flush=True)
        break
    for js in sorted(set(re.findall(r'src="(https://rollcall.com/build/assets/[^"]+\.js)"', s))):
        try:
            t = raw(js, 60)
        except Exception as e:
            print("JS FAIL", js, str(e)[:100], flush=True)
            continue
        print("JS", js, len(t), flush=True)
        for k in ("factbaseTranscript", "api/factbase", "factbaseSlug"):
            for m in list(re.finditer(re.escape(k), t))[:4]:
                print("   ", k, ":", t[max(0, m.start() - 250):m.start() + 450].replace("\n", " "), flush=True)
    for u in (f"https://rollcall.com/api/factbase/transcripts?person=trump&slug={slug}",
              f"https://rollcall.com/api/factbase/transcript?person=trump&slug={slug}",
              f"https://rollcall.com/api/factbase/transcripts/{slug}",
              f"https://rollcall.com/api/factbase/transcript/{slug}",
              f"https://rollcall.com/api/factbase/transcripts?person=trump&document_id={x['document_id']}"):
        try:
            t = raw(u, 40)
            print("OK", u, len(t), re.sub(r"\s+", " ", t[:1200]), flush=True)
        except Exception as e:
            print("FAIL", u, str(e)[:100], flush=True)


def peek2():
    import json
    d = json.loads(raw(API.format(1)))
    print("meta", d["meta"], flush=True)
    for x in d["data"][:4]:
        print("item", json.dumps(x)[:1500], flush=True)
    u = [x for x in d["data"] if "no-transcript" not in x["factbase_url"]][3]["factbase_url"]
    s = raw(u)
    print("PAGE", u, len(s), flush=True)
    for k in ("President Trump", "Donald Trump", "transcript", "wp-json", "application/json", "document_id"):
        for g in list(re.finditer(k, s))[:4]:
            print("  ctx", k, "|", re.sub(r"\s+", " ", s[max(0, g.start() - 300):g.start() + 500]), flush=True)
    doc = [x for x in d["data"] if x["factbase_url"] == u][0]["document_id"]
    for v in (f"https://rollcall.com/wp-json/factbase/v1/transcript/{doc}", f"https://rollcall.com/wp-json/factbase/v1/transcript?id={doc}",
              "https://rollcall.com/wp-json/factbase/v1", f"https://rollcall.com/wp-json/factbase/v1/document/{doc}"):
        try:
            print("TRY", v, raw(v)[:1500], flush=True)
        except Exception as e:
            print("TRY FAIL", v, str(e)[:100], flush=True)


def peek3():
    u = "https://rollcall.com/factbase/trump/transcript/donald-trump-interview-stephen-a-smith-online-show-november-12-2026/"
    s = raw(u, 60)
    i = s.find("Department of Education announced another")
    j = s.rfind("<script", 0, i)
    k = s.rfind("<div", 0, i)
    print("blob starts: script at", j, "div at", k, "text at", i, flush=True)
    st = max(j, k)
    print("START", s[st:st + 3000], flush=True)
    print("NEAR", s[i - 2500:i + 300], flush=True)
    import collections
    keys = collections.Counter(re.findall(r'\\?"([a-z_]{3,20})\\?":', s[st:st + 2500000]))
    print("KEYS", keys.most_common(60), flush=True)
    try:
        t = raw("https://rollcall.com/wp-json/factbase/v1/twitter?page=1&format=json")
        print("TWITTER", t[:3000], flush=True)
    except Exception as e:
        print("TWITTER FAIL", str(e)[:100], flush=True)


def peek4():
    """what Roll Call's post feed holds"""
    import json
    for q in ("page=1&format=json", "page=2&format=json", "page=1&format=json&platform=truth+social", "page=1&format=json&sort=date&limit=100",
              "page=500&format=json", "page=1&format=json&q=tariff"):
        try:
            d = json.loads(raw("https://rollcall.com/wp-json/factbase/v1/twitter?" + q, 60))
        except Exception as e:
            print("FAIL", q, str(e)[:120], flush=True)
            continue
        rows = d.get("data") or []
        print("Q", q, "meta", d.get("meta"), "rows", len(rows), flush=True)
        if rows:
            print("  keys", sorted(rows[0].keys()), flush=True)
            print("  dates", [(x.get("date"), x.get("platform"), x.get("deleted_flag")) for x in rows[:3]], [(x.get("date")) for x in rows[-2:]], flush=True)
        for x in rows[:3 if q.startswith("page=1&format=json") and len(q) < 20 else 1]:
            print("  item", json.dumps(x)[:1800], flush=True)
        pics = [x for x in rows if x.get("media_text") or x.get("image_text")]
        print("  with picture text", len(pics), "of", len(rows), flush=True)
        for x in pics[:2]:
            print("  pic", json.dumps({k: x.get(k) for k in ("date", "text", "media_text", "image_url", "post_url", "id", "document_id", "platform", "repost_flag", "is_retweet")})[:1500], flush=True)


def do_posts(pages=110):
    """Trump's Truth Social posts from Roll Call's post feed, newest first, with the text read out of pictures
    (social.media_text) -> bt_cache/sp/social.json.gz. 110 pages of 50 reach back to about December 2025."""
    import collections, json, time
    out = rj(cache("social.json.gz"), {}) or {}
    for page in range(1, pages + 1):
        d = None
        for a in range(4):
            try:
                d = json.loads(raw(f"https://rollcall.com/wp-json/factbase/v1/twitter?page={page}&format=json&platform=truth+social", 60))
                break
            except Exception as e:
                print("  posts page failed", page, str(e)[:100], flush=True)
                time.sleep(3 + 3 * a)
        if not d or not d.get("data"):
            continue
        for x in d["data"]:
            so = x.get("social") or {}
            out[str(x["id"])] = {"date": x.get("date"), "text": x.get("text") or "", "pic": [t for t in (so.get("media_text") or []) if t],
                                 "media": so.get("media_count") or 0, "quote": bool(so.get("quote_flag")), "quote_id": so.get("quote_id"),
                                 "repost": bool(so.get("repost_flag")), "deleted": bool(x.get("deleted_flag")), "words": x.get("word_count")}
        if page % 20 == 0:
            print("  page", page, len(out), d["data"][-1].get("date"), flush=True)
        time.sleep(0.25)
    wj(cache("social.json.gz"), out)
    v = list(out.values())
    print("posts", len(v), "from", min(x["date"] for x in v), "to", max(x["date"] for x in v), flush=True)
    print("with picture text", sum(1 for x in v if x["pic"]), "with media", sum(1 for x in v if x["media"]), "reposts", sum(1 for x in v if x["repost"]),
          "quotes", sum(1 for x in v if x["quote"]), "text is only [Video]/[Image]/RT link", sum(1 for x in v if re.fullmatch(r"\[\w+\]|RT: https?://\S+", x["text"].strip())), flush=True)
    mon = collections.Counter((x["date"][:7], bool(x["pic"])) for x in v if x["media"])
    print("media posts by month (with picture text / without)", sorted((m, mon[(m, True)], mon[(m, False)]) for m in {k[0] for k in mon}), flush=True)
    for x in [x for x in v if x["pic"]][:6]:
        print("  sample", x["date"], repr(x["text"][:120]), "| PIC", repr(" ".join(x["pic"])[:300]), flush=True)


def wj(path, obj):
    import gzip, json, os
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with gzip.open(path + ".tmp", "wt") as f:
        json.dump(obj, f, separators=(",", ":"))
    os.replace(path + ".tmp", path)


def rj(path, default=None):
    import gzip, json
    try:
        with gzip.open(path, "rt") as f:
            return json.load(f)
    except Exception:
        return default


def cache(name):
    import os
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "bt_cache", "sp", name)


KEEP = ("date", "document_id", "factbase_url", "record_type", "media_type", "place", "record_title", "slug", "speaker_id", "version_number")


def do_list():
    """every Trump record Roll Call lists (speeches, interviews, remarks...), newest first -> bt_cache/sp/list.json.gz"""
    import json, time
    out, page, pages = {}, 1, 1
    while page <= pages:
        for a in range(4):
            try:
                d = json.loads(raw(API.format(page), 60))
                break
            except Exception as e:
                print("  list page failed", page, str(e)[:100], flush=True)
                time.sleep(3 + 3 * a)
                d = None
        if not d:
            page += 1
            continue
        pages = d["meta"]["total_pages"]
        for x in d["data"]:
            r = {k: x.get(k) for k in KEEP}
            doc = x.get("document") or {}
            r["words"] = doc.get("word_count")
            r["dur"] = doc.get("duration")
            r["speakers"] = [(p.get("speaker"), p.get("words")) for p in (x.get("stresslens") or [])]
            out[x["document_id"]] = r
        if page % 20 == 0:
            print("  list page", page, "of", pages, len(out), flush=True)
        page += 1
        time.sleep(0.3)
    wj(cache("list.json.gz"), out)
    import collections
    print("records", len(out), collections.Counter(r["record_type"] for r in out.values()).most_common(), flush=True)
    print("by year", sorted(collections.Counter(r["date"][:4] for r in out.values()).items()), flush=True)
    # how does the page body mark who is speaking?
    u = "https://rollcall.com/factbase/trump/transcript/donald-trump-interview-stephen-a-smith-online-show-november-12-2026/"
    s = raw(u, 60)
    hits = [g.start() for g in re.finditer("I can have it both ways", s)]
    print("phrase at", hits, "of", len(s), flush=True)
    for h in hits[1:3]:
        print("BODY", s[h - 3500:h + 800], flush=True)


BLOCK = re.compile(r'<h2 class="text-md inline">(.*?)</h2>(.*?)<div class=" flex-auto text-md text-gray-600 leading-loose">(.*?)</div>', re.S)
SINCE = "2024-07-01"
SHARD = 150


def parse(s):
    import html
    out = []
    for g in BLOCK.finditer(s):
        t = re.search(r"(\d\d):(\d\d):(\d\d)-", g[2])
        sec = int(t[1]) * 3600 + int(t[2]) * 60 + int(t[3]) if t else None
        txt = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", g[3]))).strip()
        out.append([html.unescape(g[1]).strip(), sec, txt])
    return out


def do_texts(budget_min=150):
    """every transcript since SINCE, split by who is speaking -> bt_cache/sp/texts_NNN.json.gz (resumable)"""
    import concurrent.futures, glob, time
    L = rj(cache("list.json.gz"), {})
    ids = sorted((d for d, r in L.items() if (r["date"] or "") >= SINCE and "no-transcript" not in (r["slug"] or "")
                  and r["record_type"] not in ("Op-Ed", "Position Paper", "Official Document")), key=lambda d: (L[d]["date"], d))
    have = {}
    for p in glob.glob(cache("texts_*.json.gz")):
        have.update(rj(p, {}))
    todo = [d for d in ids if d not in have]
    print("records", len(ids), "have", len(have), "todo", len(todo), flush=True)
    t0 = time.time()

    def one(d):
        for a in range(3):
            try:
                return d, parse(raw(L[d]["factbase_url"], 90))
            except Exception as e:
                err = str(e)[:80]
                time.sleep(2 + 4 * a)
        print("  failed", d, err, flush=True)
        return d, None

    n_sh = len(glob.glob(cache("texts_*.json.gz")))
    for i in range(0, len(todo), SHARD):
        if time.time() - t0 > budget_min * 60:
            print("out of time, run again to continue", flush=True)
            break
        with concurrent.futures.ThreadPoolExecutor(4) as ex:
            got = dict(ex.map(one, todo[i:i + SHARD]))
        got = {d: v for d, v in got.items() if v is not None}
        wj(cache(f"texts_{n_sh:03d}.json.gz"), got)
        n_sh += 1
        emp = sum(1 for v in got.values() if not v)
        print(f"  shard {n_sh} done: {len(got)} records, {emp} empty, {sum(len(v) for v in got.values())} blocks, "
              f"{(time.time() - t0) / 60:.1f} min", flush=True)
        if i == 0:
            for d, v in list(got.items())[:3]:
                print("   sample", L[d]["record_title"], len(v), v[:3], flush=True)


# ================================================================ the test: "What will Trump say this week / this month"
WIN = re.compile(r"between (\w+) (\d+)(?:, (\d{4}))?(?:, [\d:]+ [AP]M ET)? and (\w+) (\d+), (\d{4}), 11:59 PM ET")
TRIES = 50
RULE = dict(gap=0.15, side=0, pre=True)


def window(m):
    """the market's stretch in ET, from its rules text"""
    import datetime
    import postwords as pw
    g = WIN.search(m.get("desc") or "")
    if not g or g[1].lower() not in pw.MON or g[4].lower() not in pw.MON:
        return None
    y2, m1, m2 = int(g[6]), pw.MON[g[1].lower()], pw.MON[g[4].lower()]
    y1 = int(g[3]) if g[3] else (y2 - 1 if m1 > m2 else y2)
    a = datetime.datetime(y1, m1, int(g[2]), tzinfo=pw.ET)
    b = datetime.datetime(y2, m2, int(g[5]), 23, 59, 59, tzinfo=pw.ET)
    return int(a.timestamp()), int(b.timestamp())


class Words:
    """Trump's own words per day (ET), and on which days he said a term"""

    def __init__(self):
        import collections, datetime, glob
        import postwords as pw
        self.L = rj(cache("list.json.gz"), {})
        T = {}
        for p in sorted(glob.glob(cache("texts_*.json.gz"))):
            T.update(rj(p, {}))
        self.n = len(T)
        days = collections.defaultdict(list)
        for d, v in T.items():
            x = " ".join(b[2] for b in v if b[0] == "Donald Trump")
            if x:
                y, mo, dd = map(int, self.L[d]["date"].split("-"))
                days[int(datetime.datetime(y, mo, dd, tzinfo=pw.ET).timestamp())].append(x.lower().replace("\u2019", "'"))
        self.days = {d: " \n ".join(v) for d, v in days.items()}
        self.keys = sorted(self.days)
        self.c = {}

    def said(self, item):
        import postwords as pw
        if item not in self.c:
            r = pw.rx(item)
            self.c[item] = [d for d in self.keys if r.search(self.days[d])]
        return self.c[item]

    def record(self, item, t, n=8):
        """in how many of the n 7-day stretches before t did he say it (only days that had ended by t)"""
        import bisect
        sd, k = self.said(item), 0
        for i in range(n):
            a, b = t - (i + 1) * 7 * 86400, t - i * 7 * 86400
            j = bisect.bisect_left(sd, a - 86400 + 1)
            k += j < len(sd) and sd[j] + 86400 <= b
        return (k + 1) / (n + 2), k


def load():
    import mentions
    ms, tp = mentions.load()
    sel = [m for m in ms.values() if "trump" in str(mentions.speaker(m)).lower() and "post" not in m["title"].lower()
           and re.search(r"this week|in (january|february|march|april|may|june|july|august|september|october|november|december)\b|this month",
                         m["title"].lower()) and window(m) and m.get("item") and m.get("final") in ([1.0, 0.0], [0.0, 1.0])
           and not re.search(r"\d\+? times|\d\+", m["q"])]
    return sel, {m["id"]: tp[m["id"]] for m in sel if m["id"] in tp}


def looks(W, sel, tp, n=8):
    """every 5-minute step with trades, until the market closes or we could have read the word in a transcript"""
    for m in sel:
        w, r = window(m), tp.get(m["id"])
        if not r:
            continue
        stop, b, sd = min(w[1], m["closed_t"] or w[1]), r["b"], W.said(m["item"])
        for i in range(len(b) - 1):
            t = b[i][0] + 300
            if t >= stop or any(w[0] - 86400 < d and d + 2 * 86400 <= t for d in sd):
                break
            qw, k = W.record(m["item"], t, n)
            q = 1 - (1 - qw) ** ((w[1] - max(t, w[0])) / (7 * 86400))
            yield m, w, i, t, b, q, k


def bets(W, sel, tp, gap=0.15, side=0, plo=0.0, phi=1.0, extra=0.02, hold=7200, stake=10.0, crumb=5.0, pre=None, n=8):
    """one $10 bet per market at the first step that fits. Price: the worst of the next `hold` seconds, never better than
    the price at the signal, + extra + fee. pre=True: only before the week starts; False: only during it."""
    import bot
    out, done = [], set()
    for m, w, i, t, b, q, k in looks(W, sel, tp, n):
        if m["id"] in done or b[i][5] < crumb or (pre is not None and (t < w[0]) != pre):
            continue
        p = b[i][2]
        if not plo <= p <= phi or ((p - q) if side == 1 else (q - p)) < gap:
            continue
        nx = [y for y in b[i + 1:] if y[0] - t <= hold and y[5] >= crumb]
        if not nx:
            continue
        px = max(max(1 - y[3] for y in nx), 1 - p) if side == 1 else max(max(y[4] for y in nx), p)
        c = min(0.99, px + extra)
        sh = stake / c
        fee = bot.taker_fee(sh, c, m.get("fee") or 0)
        win = (m["final"][0] == 1.0) == (side == 0)
        done.add(m["id"])
        sd = W.said(m["item"])
        out.append({"ev": m["ev_slug"], "t": nx[0][0], "cost": stake + fee, "pay": sh if win else 0.0, "id": m["id"], "px": c, "sig": p,
                    "fair": q, "item": m["item"], "k": k, "w0": w[0], "w1": w[1],
                    "sameday": any(w[0] - 86400 < d <= t for d in sd),
                    "near": sum(y[5] for y in b if t <= y[0] <= t + hold and y[4] <= c)})
    return out


def run(score=True):
    import collections, os, statistics, time
    import bot, exam
    import postwords as pw
    sel, tp = load()
    W = Words()
    L = []
    P = L.append
    show, usd = pw.show, pw.usd
    P("# 'What will Trump say this week' vs what he really said in the weeks before (speeches.py)\n")
    P(f"Generated {bot.iso()}. {len(sel)} finished markets in {len({m['ev_slug'] for m in sel})} weeks or months "
      f"(2024 to 9 Nov 2026), {len(tp)} with real trades. Outside number: {W.n} Trump transcripts since July 2024 from "
      f"Roll Call's Factba.se, split by who is speaking, {len(W.keys)} days with Trump's own words. Paper only.\n")
    P("## 1. Do the transcripts match the results?\n")
    c = collections.Counter()
    for m in sel:
        w = window(m)
        c[(m["final"][0] == 1.0, any(w[0] - 86400 < d <= w[1] for d in W.said(m["item"])))] += 1
    P(f"Yes and the word is in a transcript of that stretch: {c[(True, True)]}. Yes but not found: {c[(True, False)]}. "
      f"No and not found: {c[(False, False)]}. No but found: {c[(False, True)]}. So the transcripts tell the result right "
      "about 19 times in 20.\n")
    P("## 2. The bets\n")
    P("Record: in how many of the 8 weeks before did Trump say the word (only days already over when the bet is made). "
      "That gives a chance for the week (or month). $10 a bet, one per market, at a 5-minute step with $5+ traded. Price "
      "paid: the worst price of the next 2 hours, never better than the price at the signal, + 2c + fee. Betting stops "
      "once a transcript with the word could be read.\n")
    P(pw.HEAD)
    B = lambda **kw: bets(W, sel, tp, **kw)
    main = B(**RULE)
    P(show("always Yes, before the week starts", B(gap=-9, side=0, pre=True)))
    P(show("always No, before the week starts", B(gap=-9, side=1, pre=True)))
    P(show("**Yes where the record is 15c+ above the price, before the week starts**", main))
    P(show("... gap 5c+", B(gap=0.05, side=0, pre=True)))
    P(show("... gap 10c+", B(gap=0.10, side=0, pre=True)))
    P(show("... gap 25c+", B(gap=0.25, side=0, pre=True)))
    P(show("... gap 35c+", B(gap=0.35, side=0, pre=True)))
    P(show("... record over 4 weeks", B(n=4, **RULE)))
    P(show("... record over 12 weeks", B(n=12, **RULE)))
    P(show("... without the word 'Transgender'", [x for x in main if x["item"] != "Transgender"]))
    P(show("... weekly markets", [x for x in main if x["w1"] - x["w0"] < 9 * 86400]))
    P(show("... monthly markets", [x for x in main if x["w1"] - x["w0"] >= 9 * 86400]))
    P(show("... markets with a fee (since April 2026)", [x for x in main if x["t"] >= 1774992000]))
    P(show("... Yes at under 20c", [x for x in main if x["sig"] < 0.2]))
    P(show("... Yes at 20-60c", [x for x in main if 0.2 <= x["sig"] < 0.6]))
    P(show("... Yes at 60c+", [x for x in main if x["sig"] >= 0.6]))
    P(show("... 4c extra instead of 2c", B(extra=0.04, **RULE)))
    P(show("... 6c extra", B(extra=0.06, **RULE)))
    P(show("... 10c extra", B(extra=0.10, **RULE)))
    P(show("... worst price of the next 30 minutes", B(hold=1800, **RULE)))
    P(show("... worst price of the next 6 hours", B(hold=21600, **RULE)))
    P(show("... worst price of the next 24 hours", B(hold=86400, **RULE)))
    inw = B(gap=0.15, side=0, pre=False)
    P(show("Yes, same gap, during the week, word not said yet that week", [x for x in inw if not x["sameday"]]))
    P(show("Yes, same gap, during the week, on the day he said it (a speed game, not ours)", [x for x in inw if x["sameday"]]))
    P(show("No where the price is 15c+ above the record, before the week", B(gap=0.15, side=1, pre=True)))
    P(show("No where the price is 15c+ above the record, during the week, Yes at 20-60c", B(gap=0.15, side=1, pre=False, plo=0.2, phi=0.6)))
    P("\nBy quarter (the bold rule):\n\n" + pw.HEAD)
    q = collections.defaultdict(list)
    for x in main:
        g = time.gmtime(x["t"])
        q[f"{g.tm_year} Q{(g.tm_mon - 1) // 3 + 1}"].append(x)
    for k in sorted(q):
        P(show(k, q[k]))
    P("\nBy how many of the 8 weeks before he said the word:\n\n" + pw.HEAD)
    for lo, hi in ((0, 2), (3, 4), (5, 6), (7, 8)):
        P(show(f"{lo}-{hi} of 8", [x for x in main if lo <= x["k"] <= hi]))
    by = collections.Counter()
    n_ = collections.Counter()
    for x in main:
        by[x["item"]] += x["pay"] - x["cost"]
        n_[x["item"]] += 1
    P("\nBiggest wins by word: " + ", ".join(f"{k} {usd(v)} ({n_[k]} bets)" for k, v in by.most_common(6)) + ". Biggest losses: "
      + ", ".join(f"{k} {usd(v)} ({n_[k]})" for k, v in by.most_common()[-6:]) + ".\n")
    near = sorted(x["near"] for x in main)
    P(f"How much money is there: in the 2 hours after a signal, a middle market traded ${statistics.median(near):.0f} at our "
      f"price or better (a quarter under ${near[len(near) // 4]:.0f}, a quarter over ${near[3 * len(near) // 4]:.0f}). So this "
      "is a $5-10 a bet game, about 10 bets a month.\n")
    card = exam.score(main, "Trump weekly say-markets: Yes where the transcript record is 15c+ above the price, before the week",
                      tries=TRIES, src="speeches.py", status="lead", log=score, quiet=True)
    P("## 3. The shared exam\n")
    P(f"Bold rule: **{card['verdict']}**. {usd(card['per100'])} per $100, luck range {usd(card['lo100'])} to {usd(card['hi100'])}, "
      f"worst case per $100 {usd(card['floor100'])}, {card['bets']} bets in {card['groups']} separate weeks, about {card['more']} "
      "more bets needed.\n")
    P("## What it means\n")
    P("Before a week starts, Polymarket prices a word Trump says almost every week like a coin flip. Buying Yes there paid "
      "in 5 of 6 quarters, in both halves, with and without fees, and still at 6c worse prices. Buying every Yes blindly "
      "made $0, so the transcript record is what does the work. Weak spots: found by looking (about 50 versions, no "
      "untouched test set), 150 bets only, thin markets, one word (Transgender) is 18 of the bets, and the same idea "
      "during the week was good early and bad late. A live paper track would be the real test.\n")
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "backtest", "speeches.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


def events():
    """Scratch-grade second test (15 Nov): the same transcripts on Trump's single-event markets (rallies, interviews,
    signings). Record = in how many of his last 20 appearances (800+ own words, days before the bet) he said the word.
    Bets only on days before the event's day. Prints the tables that backtest/speeches_events.md quotes. Slow (~10 min)."""
    import bisect, collections, datetime, glob, time
    import bot, exam, mentions
    import postwords as pw
    ms, tp = mentions.load()

    ev = collections.defaultdict(list)
    for m in ms.values():
        t = m["title"].lower()
        if "trump" in str(mentions.speaker(m)).lower() and "post" not in t and not re.search(r"this week|in (january|february|march|april|may|june|july|august|september|october|november|december)\b|this month| or |melania|elon|first", t) \
           and m.get("item") and m.get("final") in ([1.0, 0.0], [0.0, 1.0]) and not re.search(r"\d\+? times|\d\+", m["q"]) and m["id"] in tp:
            ev[m["ev_slug"]].append(m)
    print("events", len(ev), "markets", sum(len(v) for v in ev.values()), flush=True)
    W = Words()
    # appearances: per record, Trump's own text, by day; keep those with 800+ Trump words
    T = {}
    for p in sorted(glob.glob(cache("texts_*.json.gz"))): T.update(rj(p, {}))
    APP = []
    for d, v in T.items():
        x = " ".join(b[2] for b in v if b[0] == "Donald Trump")
        if len(x.split()) >= 800:
            y, mo, dd = map(int, W.L[d]["date"].split("-"))
            APP.append((int(datetime.datetime(y, mo, dd, tzinfo=pw.ET).timestamp()), W.L[d]["record_type"], x.lower().replace("’", "'")))
    APP.sort(); AT = [a[0] for a in APP]
    print("appearances", len(APP), collections.Counter(a[1] for a in APP), flush=True)
    _c = {}
    def hits(item):
        if item not in _c:
            r = pw.rx(item); _c[item] = [bool(r.search(a[2])) for a in APP]
        return _c[item]
    def record(item, day0, n=20, typ=None):
        j = bisect.bisect_left(AT, day0)      # appearances on days before day0
        h = hits(item); k = tot = 0; i = j - 1
        while i >= 0 and tot < n:
            if typ is None or APP[i][1] in typ: tot += 1; k += h[i]
            i -= 1
        return (k + 1) / (tot + 2), k, tot
    def etday(t):
        d = datetime.datetime.fromtimestamp(t, pw.ET); return int(datetime.datetime(d.year, d.month, d.day, tzinfo=pw.ET).timestamp())
    def kind(title):
        t = title.lower()
        if "interview" in t or "squawk" in t or "podcast" in t: return ("Interview",)
        if "rally" in t or "speech" in t or "address" in t or "cpac" in t or "convention" in t: return ("Speech",)
        return None
    def bets(gap=0.15, side=0, n=20, typed=False, extra=0.02, hold=7200, plo=0, phi=1, crumb=5.0, stake=10.0):
        out = []
        for s, v in ev.items():
            day0 = etday(min(m["closed_t"] or m["end"] for m in v))     # the event's day: bet only on days before it
            typ = kind(v[0]["title"]) if typed else None
            for m in v:
                b = tp[m["id"]]["b"]
                for i in range(len(b) - 1):
                    t = b[i][0] + 300
                    if t >= day0: break
                    if b[i][5] < crumb: continue
                    p = b[i][2]
                    if not plo <= p <= phi: continue
                    q, k, tot = record(m["item"], etday(t), n, typ)
                    if tot < 10: break
                    if ((p - q) if side == 1 else (q - p)) < gap: continue
                    nx = [y for y in b[i + 1:] if y[0] - t <= hold and y[5] >= crumb and y[0] < day0 + 86400]
                    if not nx: continue
                    px = max(max(1 - y[3] for y in nx), 1 - p) if side == 1 else max(max(y[4] for y in nx), p)
                    c = min(0.99, px + extra); sh = stake / c
                    fee = bot.taker_fee(sh, c, m.get("fee") or 0)
                    win = (m["final"][0] == 1.0) == (side == 0)
                    out.append({"ev": s, "t": nx[0][0], "cost": stake + fee, "pay": sh if win else 0.0, "px": c, "sig": p, "fair": q, "item": m["item"], "k": k, "title": v[0]["title"]})
                    break
        return out
    def show(name, b):
        b = sorted(b, key=lambda x: x["t"]); h = len(b) // 2; p = pw.per100
        print(f"{name:44s} bets {len(b):4d} ev {len({x['ev'] for x in b}):3d} won {sum(1 for x in b if x['pay']>0):4d} per100 {p(b):+7.2f} halves {p(b[:h]):+7.2f} {p(b[h:]):+7.2f} avgpx {sum(x['px'] for x in b)/max(1,len(b)):.2f}", flush=True)

    show("always Yes", bets(-9, 0))
    show("always No", bets(-9, 1))
    for gap in (0.15, 0.25):
        show(f"Yes where the record is {gap} above the price", bets(gap, 0))
    show("Yes, record from the same kind of appearance", bets(0.15, 0, typed=True))
    show("No where the price is 0.15 above the record", bets(0.15, 1))
    b = bets(0.15, 1, typed=True)
    show("No, record from the same kind of appearance", b)
    for ex in (0.04, 0.06):
        show(f"... {ex} extra", bets(0.15, 1, typed=True, extra=ex))
    q = collections.defaultdict(list)
    for x in b:
        g = time.gmtime(x["t"])
        q[f"{g.tm_year}Q{(g.tm_mon - 1) // 3 + 1}"].append(x)
    for k in sorted(q):
        show(k, q[k])
    c = exam.score(b, "Trump event say-markets: No where the price is 15c+ above the transcript record", tries=20, src="speeches.py",
                   status="dropped", log="log" in sys.argv, quiet=True)
    print(c["verdict"], c["per100"], c["lo100"], c["hi100"])


def kalshi(score=True):
    """The same rule on Kalshi's weekly "What will Trump say this week" markets (series KXTRUMPSAY, data bt_cache/kmen).
    Only markets planned to live 20 days or less: tapes hold the last 21 days of a market, so for longer ones the
    early hours exist only when the market closed early, which gives the result away. -> backtest/speeches_kalshi.md"""
    import collections, os, statistics, time
    import bot, exam, kmentions as km
    import postwords as pw
    ms, tp = km.load(trades=True)
    sel = [m for m in ms.values() if m["s"].startswith("KXTRUMPSAY") and m["t"] in tp and m["res"] in ("yes", "no")
           and (m["exp"] or m["close"]) - m["open"] <= 20 * 86400]
    W = Words()
    end = {}
    for m in sel:
        end[m["ev"]] = max(end.get(m["ev"], 0), m["close"])

    def bets(gap=0.15, side=0, lo_h=1, hi_h=12, extra=0.01, stake=10.0, n=8, always=False):
        out = []
        for m in sel:
            for c in tp[m["t"]]["c"]:
                t, bid, ask = c[0], c[1], c[2]
                if t < m["open"] + lo_h * 3600:
                    continue
                if t > m["open"] + hi_h * 3600 or t >= m["close"]:
                    break
                if not bid or not ask or ask - bid > 0.15:
                    continue
                qw, k = W.record(m["w"], t, n)
                q = 1 - (1 - qw) ** (max(end[m["ev"]] - t, 3600) / (7 * 86400))
                px = ask if side == 0 else 1 - bid
                if not always and ((q - px) if side == 0 else ((1 - q) - px)) < gap:
                    continue
                c_ = min(0.99, px + extra)
                sh = stake / c_
                win = (m["res"] == "yes") == (side == 0)
                near = sum(x[2] * x[1] / 1000 for x in tp[m["t"]]["tr"] if t < x[0] <= t + 7200 and x[1] / 1000 <= c_ and x[3] == 1)
                out.append({"ev": m["ev"], "t": t, "cost": stake + 0.07 * c_ * (1 - c_) * sh, "pay": sh if win else 0.0, "px": c_,
                            "sig": (bid + ask) / 2, "fair": q, "item": m["w"], "k": k, "id": m["t"], "near": near})
                break
        return out

    L = []
    P = L.append
    show, usd = pw.show, pw.usd
    P("# The Trump weekly words rule on Kalshi (speeches.py kalshi)\n")
    P(f"Generated {bot.iso()}. Kalshi runs the same \"What will Trump say this week\" markets: {len(sel)} finished markets in "
      f"{len({m['ev'] for m in sel})} weeks, August 2025 to November 2026, with real hourly buy and sell quotes and every trade. "
      "A middle market trades about $23,000, four times Polymarket's. Paper only.\n")
    P("The rule is the one found on Polymarket, unchanged: count in how many of the 8 weeks before Trump said the word "
      "(Roll Call transcripts, only days already over), and buy Yes where that record is 15c+ above the price. Here the price "
      "is Kalshi's real sell offer at the end of an hour (offers with a gap over 15c to the best bid are skipped) + 1c + "
      "Kalshi's fee. $10 a bet, one per market. Kalshi opens these markets when the week starts, so there is no \"before "
      "the week\": the test buys in the first 12 hours, or at the first hour of the week that fits.\n")
    P(pw.HEAD)
    first, anyh = bets(), bets(hi_h=24 * 8)
    P(show("always Yes, first 12 hours", bets(always=True)))
    P(show("always No, first 12 hours", bets(side=1, always=True)))
    P(show("**Yes where the record is 15c+ above the offer, first 12 hours**", first))
    P(show("**... the same, at the first hour of the week that fits**", anyh))
    P(show("... first 12 hours, gap 5c+", bets(0.05)))
    P(show("... first 12 hours, gap 25c+", bets(0.25)))
    P(show("... first 12 hours, 3c extra instead of 1c", bets(extra=0.03)))
    P(show("... first 12 hours, 5c extra", bets(extra=0.05)))
    P(show("... first 12 hours, 10c extra", bets(extra=0.10)))
    P(show("... only hours 12 to 48", bets(lo_h=12, hi_h=48)))
    P(show("... only hours 48 to 120", bets(lo_h=48, hi_h=120)))
    P(show("No where the offer is 15c+ above the record, first 12 hours", bets(side=1)))
    P("\nBy quarter (first hour of the week that fits):\n\n" + pw.HEAD)
    q = collections.defaultdict(list)
    for x in anyh:
        g = time.gmtime(x["t"])
        q[f"{g.tm_year} Q{(g.tm_mon - 1) // 3 + 1}"].append(x)
    for k in sorted(q):
        P(show(k, q[k]))
    P("\nBy the price paid (first hour that fits):\n\n" + pw.HEAD)
    for lo, hi in ((0, .2), (.2, .4), (.4, .6), (.6, 1.01)):
        P(show(f"Yes at {int(lo * 100)}-{min(100, int(hi * 100))}c", [x for x in anyh if lo <= x["sig"] < hi]))
    P("\n## How much money fits\n")
    P("A bet only counts here if other people really bought Yes at our price or better in the 2 hours after the signal, "
      "and only for as many dollars as they bought.\n")
    P("| at most per bet | bets that found a seller | dollars bet | profit | per $100 | profit a month | losing months |\n|---|---|---|---|---|---|---|")
    months = max(1.0, (max(x["t"] for x in anyh) - min(x["t"] for x in anyh)) / (30.4 * 86400))
    for cap in (10, 25, 100):
        tc = tpf = n = 0
        mon = collections.Counter()
        for x in anyh:
            st = min(cap, x["near"])
            if st < 1:
                continue
            r = (x["pay"] - x["cost"]) / x["cost"]
            n, tc, tpf = n + 1, tc + st, tpf + st * r
            mon[time.strftime("%Y-%m", time.gmtime(x["t"]))] += st * r
        P(f"| ${cap} | {n} of {len(anyh)} | ${tc:,.0f} | {usd(tpf)} | {usd(100 * tpf / max(1, tc))} | {usd(tpf / months)} | "
          f"{sum(1 for v in mon.values() if v < 0)} of {len(mon)} |")
    c1 = exam.score(anyh, "Kalshi Trump weekly say-markets: Yes where the transcript record is 15c+ above the offer", tries=75,
                    src="speeches.py", status="lead", log=score, quiet=True)
    c2 = exam.score(first, "scratch kalshi first 12h", tries=75, log=False, quiet=True)
    P("\n## The shared exam\n")
    P(f"First hour that fits: **{c1['verdict']}**, {usd(c1['per100'])} per $100, luck range {usd(c1['lo100'])} to {usd(c1['hi100'])}, "
      f"worst case per $100 {usd(c1['floor100'])}, {c1['bets']} bets in {c1['groups']} weeks. First 12 hours only: "
      f"**{c2['verdict']}**, {usd(c2['per100'])} per $100, luck range {usd(c2['lo100'])} to {usd(c2['hi100'])}.\n")
    P("## What it means\n")
    P("The rule was fixed on Polymarket and then run on Kalshi without changes, and it is ahead there too. That is the "
      "closest thing to a fresh test this idea has had. Kalshi adds about 20 bets a month to Polymarket's 10. Weak spots: "
      "the cheap offers are small (a third of the signals found no seller at all), a good part of the profit comes from "
      "long shots under 20c (22 wins in 86 tries, so long dry spells), and the later in the week the weaker it gets. Whether Jan may trade on "
      "Kalshi from Sweden is his to check. Trap found on the way: Kalshi's monthly markets looked like 29 wins of 29, "
      "because our saved quotes only cover a market's last 21 days, so a month-long market shows early hours only when "
      "it closed early, which means the word was said.\n")
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "backtest", "speeches_kalshi.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


def kmonth(score=True):
    """The same rule on Kalshi's month-long Trump word markets (KXTRUMPSAYMONTH / COMPANY / NICKNAME / COUNTRY ...).
    Only looks in the last 20 days before the planned end: the saved quotes cover a market's last 21 days, so earlier
    hours exist only for markets that closed early (word said). -> backtest/speeches_kmonth.md"""
    import os
    import bot, exam, kmentions as km
    import postwords as pw
    ms, tp = km.load(trades=True)
    sel = [m for m in ms.values() if m["s"].startswith("KXTRUMPSAY") and m["s"] != "KXTRUMPSAY" and m["t"] in tp and m["res"] in ("yes", "no")]
    W = Words()
    end = {}
    for m in sel:
        end[m["ev"]] = max(end.get(m["ev"], 0), m["close"], m["exp"] or 0)

    def bets(gap=0.15, side=0, extra=0.01, stake=10.0, n=8, always=False):
        out = []
        for m in sel:
            E = end[m["ev"]]
            for c in tp[m["t"]]["c"]:
                t, bid, ask = c[0], c[1], c[2]
                if t < E - 20 * 86400 or t < m["open"] + 3600:
                    continue
                if t >= m["close"] or E - t < 6 * 3600:
                    break
                if not bid or not ask or ask - bid > 0.15:
                    continue
                qw, k = W.record(m["w"], t, n)
                q = 1 - (1 - qw) ** (max(E - t, 3600) / (7 * 86400))
                px = ask if side == 0 else 1 - bid
                if not always and ((q - px) if side == 0 else ((1 - q) - px)) < gap:
                    continue
                c_ = min(0.99, px + extra)
                sh = stake / c_
                out.append({"ev": m["ev"], "t": t, "cost": stake + 0.07 * c_ * (1 - c_) * sh,
                            "pay": sh if (m["res"] == "yes") == (side == 0) else 0.0, "px": c_, "sig": (bid + ask) / 2, "id": m["t"]})
                break
        return out

    L = []
    P = L.append
    main = bets()
    P("# The Trump weekly words rule on Kalshi's month-long markets (speeches.py kmonth)\n")
    P(f"Generated {bot.iso()}. {len(sel)} finished Kalshi markets that run a month or a quarter (\"What will Trump say in "
      "November\", company names, nicknames, countries). Same rule as the weekly test: Yes where the 8-week transcript record "
      "is 15c+ above the real sell offer + 1c + fee, $10 a bet, one per market. Only the last 20 days before the planned end "
      "are tested, on words not said yet, because our saved quotes don't reach further back without giving the result away. Paper only.\n")
    P(pw.HEAD)
    P(pw.show("always Yes", bets(always=True)))
    P(pw.show("always No", bets(side=1, always=True)))
    P(pw.show("**Yes where the record is 15c+ above the offer**", main))
    P(pw.show("... gap 5c+", bets(0.05)))
    P(pw.show("... gap 25c+", bets(0.25)))
    P(pw.show("... record over 12 weeks instead of 8", bets(n=12)))
    P(pw.show("... 3c extra", bets(extra=0.03)))
    P(pw.show("No where the offer is 15c+ above the record", bets(side=1)))
    c = exam.score(main, "Kalshi month-long Trump say-markets: Yes where the transcript record is 15c+ above the offer", tries=90,
                   src="speeches.py", status="dropped", log=score, quiet=True)
    P(f"\nShared exam: **{c['verdict']}**, {pw.usd(c['per100'])} per $100, luck range {pw.usd(c['lo100'])} to {pw.usd(c['hi100'])}, "
      f"{c['bets']} bets in {c['groups']} months.\n")
    P("## What it means\n")
    P("The rule does not carry over to the month-long markets. Their words are rare ones (company names, nicknames), where "
      "\"he said it once in 8 weeks\" tells little, and by the last 20 days the easy words are already said and gone. The "
      "12-week version looks good but is one of several tried, so it is luck until shown otherwise. Dropped: the weekly "
      "markets stay the only place for this rule, and the live Kalshi track rightly leaves month-long markets out.\n")
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "backtest", "speeches_kmonth.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    {"peek": peek, "peek4": peek4, "peek5": peek5, "peek6": peek6, "peek7": peek7, "peek8": peek8, "posts": do_posts, "peek2": peek2, "peek3": peek3, "list": do_list, "texts": do_texts, "run": run, "events": events, "kalshi": kalshi, "kmonth": kmonth, "kalshi_dry": lambda: kalshi(False), "dry": lambda: run(False)}[sys.argv[1] if len(sys.argv) > 1 else "peek"]()
