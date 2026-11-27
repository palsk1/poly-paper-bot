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


def num(x):
    if x is None or x == "":
        return None
    try:
        return float(str(x).replace(",", ".").replace(" ", ""))
    except ValueError:
        return None


def trio(d, keys=("one", "x", "two")):
    if not d:
        return None
    v = [num(d.get(k)) for k in keys]
    return v if all(a is not None for a in v) else None


def compact(game, n):
    A = f"https://api.spela.svenskaspel.se/draw/1/{game}/draws/{n}"
    d = get(A)["draw"]
    try:
        r = get(A + "/result")["result"]
    except Exception:
        r = None
    ev = []
    outc = {}
    if r:
        for e in r.get("events") or []:
            outc[e["eventNumber"]] = (e.get("outcome"), e.get("cancelled"))
    for e in d.get("drawEvents") or []:
        m = e.get("match") or {}
        lg = (m.get("league") or {}).get("name")
        ev.append({"n": e["eventNumber"], "d": e.get("eventDescription"), "lg": lg, "start": m.get("matchStart"),
                   "teams": [p.get("name") for p in (m.get("participants") or [])],
                   "so": trio(e.get("startOdds")), "od": trio(e.get("odds")), "fo": trio(e.get("favouriteOdds")),
                   "sf": trio(e.get("svenskaFolket")), "tt": trio(e.get("tioTidningarsTips")),
                   "out": outc.get(e["eventNumber"], (None, None))[0], "canc": e.get("cancelled") or outc.get(e["eventNumber"], (None, None))[1]})
    rec = {"g": game, "n": n, "close": d.get("regCloseTime"), "state": d.get("drawState"), "sale": num(d.get("currentNetSale")),
           "rp": num(d.get("rowPrice")), "fund": d.get("fund"), "extra": d.get("extraInfo"), "comment": d.get("drawComment"),
           "ev": ev, "dist": [(x.get("name"), x.get("winners"), num(x.get("amount"))) for x in ((r or {}).get("distribution") or [])],
           "rsale": num((r or {}).get("currentNetSale")), "rcanc": (r or {}).get("cancelled")}
    other = {k: v for k, v in d.items() if k not in ("drawEvents",) and isinstance(v, (str, int, float, bool)) is False and v}
    if other and n % 50 == 0:
        print("other fields", n, {k: str(v)[:120] for k, v in other.items()})
    return rec


def fetch():
    from concurrent.futures import ThreadPoolExecutor
    game, a = sys.argv[2], int(sys.argv[3])
    if sys.argv[4] == "auto":
        b = a
        for step in (1000, 300, 100, 30, 10, 3, 1):
            while True:
                try:
                    get(f"https://api.spela.svenskaspel.se/draw/1/{game}/draws/{b + step}")
                    b += step
                except Exception:
                    break
        print("auto end", b)
    else:
        b = int(sys.argv[4])
    os.makedirs(CACHE, exist_ok=True)
    path = f"{CACHE}/{game}.json.gz"
    have = {}
    if os.path.exists(path):
        have = {r["n"]: r for r in json.load(gzip.open(path, "rt"))}
    todo = [n for n in range(a, b + 1) if n not in have or have[n].get("state") not in ("Finalized",)]
    print(game, "have", len(have), "todo", len(todo))
    bad = 0

    def one(n):
        try:
            return compact(game, n)
        except Exception as e:
            return {"n": n, "err": str(e)[:100]}
    with ThreadPoolExecutor(4) as ex:
        for r in ex.map(one, todo):
            if "err" in r:
                bad += 1
                if bad < 6:
                    print("err", r)
                continue
            have[r["n"]] = r
    json.dump(sorted(have.values(), key=lambda r: r["n"]), gzip.open(path, "wt"))
    rs = sorted(have.values(), key=lambda r: r["n"])
    print(game, "saved", len(rs), "bad", bad, "first", rs[0]["n"], rs[0]["close"], "last", rs[-1]["n"], rs[-1]["close"])
    fin = [r for r in rs if r.get("dist")]
    print("with result", len(fin), "with startOdds all", sum(all(e["so"] for e in r["ev"]) for r in fin),
          "with sf all", sum(all(e["sf"] for e in r["ev"]) for r in fin))
    for r in rs[-3:]:
        print(r["n"], r["close"], r["sale"], r["rp"], r["dist"], r["fund"], r["extra"])


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "explore"
    {"explore": explore, "fetch": fetch}[cmd]()
    print("=== DONE ===")
