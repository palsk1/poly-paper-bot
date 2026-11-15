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


if __name__ == "__main__":
    {"peek": peek}[sys.argv[1] if len(sys.argv) > 1 else "peek"]()
