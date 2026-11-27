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
