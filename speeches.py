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


if __name__ == "__main__":
    {"peek": peek, "peek2": peek2}[sys.argv[1] if len(sys.argv) > 1 else "peek"]()
