"""Swedish pool games (Svenska Spel tips, ATG) research. Commands: explore [urls] | fetch ... | ev | atg."""
import sys, json, os, time, urllib.request, gzip
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36", "Accept": "application/json"}
CACHE = "bt_cache/out_svpool"


def get(url, tries=3):
    err = None
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25) as r:
                b = r.read()
                if r.headers.get("Content-Encoding") == "gzip":
                    b = gzip.decompress(b)
                return json.loads(b)
        except Exception as e:
            err = e
            if getattr(e, "code", 0) in (400, 403, 404, 410):
                break
            time.sleep(1 + i)
    raise err


def shape(o, d=0, maxd=5):
    pad = "  " * d
    if isinstance(o, dict):
        for k, v in list(o.items())[:45]:
            if isinstance(v, (dict, list)) and d < maxd:
                print(f"{pad}{k}: {type(v).__name__}{'[' + str(len(v)) + ']' if isinstance(v, list) else ''}")
                shape(v, d + 1, maxd)
            else:
                print(f"{pad}{k}: {str(v)[:110]}")
    elif isinstance(o, list) and o:
        shape(o[0], d, maxd)


def explore():
    urls = sys.argv[2:] or [
        "https://api.spela.svenskaspel.se/draw/1/stryktipset/draws",
        "https://api.spela.svenskaspel.se/draw/1/stryktipset/draws/4912",
        "https://api.spela.svenskaspel.se/draw/1/stryktipset/draws/4912/result",
    ]
    if sys.argv[2:3] == ["two"]:
        A = "https://api.spela.svenskaspel.se/draw/1/"
        urls = [A + "europatipset/draws", A + "topptipset/draws", A + "powerplay/draws", A + "maltipset/draws",
                A + "topptipset/draws/2000/result", A + "europatipset/draws/2400/result", A + "stryktipset/draws/4975/result",
                "https://www.atg.se/services/racinginfo/v1/api/calendar/day/2026-11-22",
                "https://www.football-data.co.uk/mmz4281/2526/E0.csv"]
        for u in urls[:-2]:
            print("=====", u)
            try:
                shape(get(u), maxd=3)
            except Exception as e:
                print("ERR", str(e)[:200])
        for u in urls[-2:]:
            print("=====", u)
            try:
                with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=25) as r:
                    t = r.read()
                print(len(t), t[:1500])
                if "atg" in u:
                    d = json.loads(t)
                    for tr in d.get("tracks", [])[:3]:
                        print(tr.get("name"), [ (g, [x.get("id") for x in v]) for g, v in (d.get("games") or {}).items()][:5])
                        break
                    gid = None
                    for g, v in (d.get("games") or {}).items():
                        if g in ("V75", "V86", "GS75", "V64"):
                            gid = v[0]["id"]
                    if gid:
                        print("== game", gid)
                        shape(get("https://www.atg.se/services/racinginfo/v1/api/games/" + gid), maxd=6)
            except Exception as e:
                print("ERR", str(e)[:200])
        return
    for u in urls:
        u = u.replace("SLASH", "/").replace("QQ", "?").replace("EQ", "=")
        print("=====", u)
        try:
            shape(get(u))
        except Exception as e:
            print("ERR", str(e)[:200])


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "explore"
    {"explore": explore}[cmd]()
    print("=== DONE ===")
