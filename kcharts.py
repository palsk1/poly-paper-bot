"""Kalshi's weekly chart markets (Spotify, Billboard, Netflix top 10 ...) vs the public daily charts. Paper research.

  python3 kcharts.py series    # probe kch_series: which chart series Kalshi runs
  python3 kcharts.py list      # probe kch_list: every settled market of those series -> bt_cache/kch/markets.json.gz
"""
import collections, datetime as dt, os, re, sys, time
from concurrent.futures import ThreadPoolExecutor

import bot, khouse, kmentions as km, yesno

ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(ROOT, "bt_cache", "kch")
MK = os.path.join(CACHE, "markets.json.gz")
kget, rj, wj = yesno.kget, khouse.rj, khouse.wj
WORDS = re.compile(r"spotify|billboard|netflix|song|album|chart|hot 100|top 10|top show|top movie|streaming|apple music|"
                   r"youtube|tiktok|rotten|box office|luminate|artist|grammy|podcast|twitch|steam|app store|imdb|metacritic|nielsen", re.I)


def chart_series():
    out, seen = [], set()
    for p in ({"category": "Entertainment"}, {"category": "Culture"}, {"category": "Music"}, {"category": "Movies"}, {"category": "TV"}, {}):
        try:
            r = kget("/series", p)
        except Exception as e:
            print(f"  /series {p} failed: {str(e)[:120]}", flush=True)
            continue
        got = r.get("series") or []
        print(f"  /series {p}: {len(got)} series, categories {collections.Counter(str(s.get('category')) for s in got).most_common(20)}", flush=True)
        for s in got:
            tk = str(s.get("ticker") or "")
            txt = f"{tk} {s.get('title') or ''} {' '.join(s.get('tags') or [])}"
            if tk and tk not in seen and (WORDS.search(txt) or str(s.get("category")) in ("Entertainment", "Culture", "Music")):
                seen.add(tk)
                out.append(s)
    return out


def do_series():
    ser = chart_series()
    print("chart-like series:", len(ser), flush=True)
    print(collections.Counter((s.get("category"), s.get("frequency")) for s in ser).most_common(30), flush=True)
    for s in sorted(ser, key=lambda s: (str(s.get("category")), str(s.get("frequency")), s["ticker"])):
        if WORDS.search(f"{s['ticker']} {s.get('title')}") or s.get("frequency") in ("weekly", "daily"):
            print(f"  {s.get('category')} | {s.get('frequency')} | {s['ticker']} | {str(s.get('title'))[:90]} | {s.get('tags')}", flush=True)


def do_list(pick=None):
    os.makedirs(CACHE, exist_ok=True)
    have = rj(MK, None) or {"series": {}, "markets": {}}
    ser = [s for s in chart_series() if (WORDS.search(f"{s['ticker']} {s.get('title')}") or s.get("frequency") in ("weekly", "daily"))
           and (not pick or re.search(pick, s["ticker"], re.I))]
    print("series to list:", len(ser), flush=True)
    for s in ser:
        have["series"][s["ticker"]] = {"title": str(s.get("title") or "")[:120], "cat": s.get("category"), "freq": s.get("frequency"),
                                       "fee": [s.get("fee_type"), s.get("fee_multiplier")], "tags": s.get("tags"),
                                       "src": [x.get("url") for x in (s.get("settlement_sources") or []) if isinstance(x, dict)][:3]}
    with ThreadPoolExecutor(4) as ex:
        for s, ok, n in ex.map(km.series_markets, sorted(x["ticker"] for x in ser)):
            have["markets"].update(ok)
            have["series"][s]["n"] = len(ok)
    wj(MK, have)
    ms = list(have["markets"].values())
    by = collections.defaultdict(list)
    for m in ms:
        by[m["s"]].append(m)
    d = lambda t: dt.datetime.utcfromtimestamp(t).strftime("%Y-%m-%d")
    print(f"settled markets {len(ms)}, events {len({m['ev'] for m in ms})}", flush=True)
    print("\n| series | title | freq | markets | events | first | last | yes won | middle volume | total volume | middle life days | source |")
    for s, v in sorted(by.items(), key=lambda kv: -sum(m["vol"] for m in kv[1]))[:120]:
        vols = sorted(m["vol"] for m in v)
        life = sorted((m["close"] - m["open"]) / 86400 for m in v)
        i = have["series"][s]
        print(f"| {s} | {i['title'][:50]} | {i['freq']} | {len(v)} | {len({m['ev'] for m in v})} | {d(min(m['close'] for m in v))} | "
              f"{d(max(m['close'] for m in v))} | {sum(m['res'] == 'yes' for m in v)} | {vols[len(vols) // 2]:.0f} | {sum(vols):.0f} | "
              f"{life[len(life) // 2]:.1f} | {i['src']} |", flush=True)
    for s, v in sorted(by.items(), key=lambda kv: -sum(m["vol"] for m in kv[1]))[:25]:
        m = max(v, key=lambda m: m["vol"])
        print("EX", s, {k: m[k] for k in ("t", "q", "w", "res", "vol")}, "| RULE", m["rule"][:300], flush=True)


if __name__ == "__main__":
    a = sys.argv[1] if len(sys.argv) > 1 else "series"
    if a == "series":
        do_series()
    elif a.startswith("list"):
        do_list(a[5:] or None)
