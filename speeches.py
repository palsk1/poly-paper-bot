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


API = "https://rollcall.com/wp-json/factbase/v1/search?media=&type=&sort=date&location=all&place=all&page={}&format=json"


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


if __name__ == "__main__":
    {"peek": peek, "peek2": peek2, "peek3": peek3, "list": do_list}[sys.argv[1] if len(sys.argv) > 1 else "peek"]()
