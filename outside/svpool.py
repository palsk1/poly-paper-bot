"""Swedish pool games (Svenska Spel tips, ATG) research. Commands: explore [urls] | fetch ... | ev | atg."""
import sys, json, os, time, math, urllib.request, gzip
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


def calib(game):
    """1) who forecasts better, the odds or the public? 2) does the independent-public model predict the real
    number of winners per level? 3) how much of the stakes really came back (incl. carries)?"""
    import numpy as np
    rs = [r for r in load(game) if ok_draw(r)]
    print(f"{game}: {len(rs)} usable rounds, {rs[0]['close'][:10]} .. {rs[-1]['close'][:10]}")
    llp = lls = 0.0
    n = 0
    hitp = hits = 0
    band = {}
    for r in rs:
        P, S, O = arrays(r)
        for m in range(13):
            llp -= math.log(P[m, O[m]])
            lls -= math.log(S[m, O[m]])
            n += 1
            hitp += P[m].argmax() == O[m]
            hits += S[m].argmax() == O[m]
            for j in range(3):  # public share minus fair chance, by size, did the sign come in?
                dlt = S[m, j] - P[m, j]
                b = int(np.clip(round(dlt * 20), -4, 4))  # 5-point buckets
                t = band.setdefault(b, [0, 0.0, 0.0, 0.0])
                t[0] += 1
                t[1] += P[m, j]
                t[2] += S[m, j]
                t[3] += (O[m] == j)
    print(f"log loss per match: odds {llp / n:.4f}  public {lls / n:.4f}   (lower = better)  favourite right: odds {hitp / n:.3f} public {hits / n:.3f}")
    print("public share minus odds chance (5-pt buckets): n, avg odds chance, avg public share, real hit rate")
    for b in sorted(band):
        t = band[b]
        print(f"  {b * 5:+4d} pts  n={t[0]:5d}  odds {t[1] / t[0]:.3f}  public {t[2] / t[0]:.3f}  real {t[3] / t[0]:.3f}")
    # 2) winners per level vs the independent model, at the real outcome
    rat = {k: [] for k in SPLIT}
    for r in rs:
        P, S, O = arrays(r)
        q = S[np.arange(13), O][None, :]
        d = count_dist(q)[0]
        N = r["sale"] / (r["rp"] or 1)
        lv = levels(r)
        for k in SPLIT:
            w = lv.get(k, (None, 0))[0]
            if w is None:
                continue
            rat[k].append((N * d[k], w))
    for k in sorted(rat, reverse=True):
        a = np.array(rat[k])
        lr = np.log((a[:, 1] + 0.5) / (a[:, 0] + 0.5))
        print(f"  level {k}: model winners median {np.median(a[:, 0]):9.1f}  real median {np.median(a[:, 1]):9.1f}  "
              f"log(real/model) mean {lr.mean():+.3f} sd {lr.std():.3f}  sum real/sum model {a[:, 1].sum() / a[:, 0].sum():.3f}")
    # 3) money back
    sale = paid = 0.0
    for r in rs:
        lv = levels(r)
        sale += r["sale"]
        paid += sum(w * a for w, a in lv.values())
    print(f"  paid back {paid / sale:.3f} of stakes over all rounds (rules: 0.65 incl. carries, 0.598 before the fund)")


# ---------------------------------------------------------------- the pool model
SPLIT = {13: .40, 12: .15, 11: .12, 10: .25}   # Stryktipset / Europatipset rules: share of the prize money per level
RET = 0.65      # share of stakes paid back as prizes
MINPAY = 15.0   # a level paying under 15 kr a row is cancelled (its money goes to next round's 13 pot)
IDX = {"1": 0, "X": 1, "2": 2}


def load(game):
    return json.load(gzip.open(f"{CACHE}/{game}.json.gz", "rt"))


def fairp(odds):
    inv = [1 / o for o in odds]
    s = sum(inv)
    return [x / s for x in inv]


def levels(r):
    out = {}
    for name, w, a in r.get("dist") or []:
        try:
            k = int(str(name).split()[0])
        except ValueError:
            continue
        out[k] = (w or 0, a or 0.0)
    return out


def ok_draw(r, nm=13):
    if not r.get("dist") or r.get("rcanc") or not r.get("sale") or len(r["ev"]) != nm:
        return False
    return all(not e.get("canc") and e["out"] in IDX and e["sf"] and (e["so"] or e["od"]) and sum(e["sf"]) > 90
               for e in r["ev"])


def arrays(r):
    import numpy as np
    P = np.array([fairp(e["od"] or e["so"]) for e in r["ev"]])
    S = np.array([e["sf"] for e in r["ev"]], float)
    S = np.clip(S / S.sum(1, keepdims=True), 0.003, None)
    S = S / S.sum(1, keepdims=True)
    O = np.array([IDX[e["out"]] for e in r["ev"]])
    return P, S, O


def count_dist(q):
    """q: (samples, M) chance a public row has match m right -> (samples, M+1) chance of exactly k right."""
    import numpy as np
    M = q.shape[1]
    d = np.zeros((q.shape[0], M + 1))
    d[:, 0] = 1
    for m in range(M):
        qm = q[:, m:m + 1]
        d[:, 1:] = d[:, 1:] * (1 - qm) + d[:, :-1] * qm
        d[:, 0] *= (1 - qm[:, 0])
    return d


def pools(r, carry):
    """prize money per level this round: base share of stakes + money carried into the 13 pot."""
    base = {k: RET * SPLIT[k] * r["sale"] for k in SPLIT}
    base[13] += carry
    return base


def carry_out(r, pool):
    """money this round sends on to next round's 13 pot: levels with no winner or under 15 kr a row."""
    lv = levels(r)
    c = 0.0
    for k in SPLIT:
        w, a = lv.get(k, (0, 0))
        if w == 0 or a == 0:
            c += pool[k]
    return c


def our_payout(k, W, pool, guarantee=10e6):
    """what one extra row with k right gets, given W other winners at that level."""
    if k not in pool:
        return 0.0
    a = pool[k] / (W + 1)
    if k == 13 and W == 0 and a < guarantee:
        a = guarantee
    return a if a >= MINPAY else 0.0


GUAR = {"stryktipset": 10e6, "europatipset": 0.0}


def blend_w(rs):
    """weight on the odds (rest on the public) that best forecasts results: fitted on the rounds given."""
    import numpy as np
    best = None
    for w in np.linspace(0, 1, 21):
        ll = 0.0
        for r in rs:
            P, S, O = arrays(r)
            B = w * P + (1 - w) * S
            ll -= np.log(B[np.arange(13), O]).sum()
        if best is None or ll < best[1]:
            best = (w, ll)
    return best[0]


def rows_of(system):
    """system: list of 13 lists of sign indices -> (R,13) array of every row (an M-system)."""
    import numpy as np, itertools
    return np.array(list(itertools.product(*system)), dtype=np.int8)


def frame(P, nhel, nhalv):
    """which matches get 3 / 2 / 1 signs: the most open matches (lowest top chance) get the guards."""
    import numpy as np
    order = np.argsort(P.max(1))
    kind = np.ones(13, int)
    kind[order[:nhel]] = 3
    kind[order[nhel:nhel + nhalv]] = 2
    return kind


def build(P, S, kind, how):
    import numpy as np
    sysm = []
    for m in range(13):
        if kind[m] == 3:
            sysm.append([0, 1, 2])
            continue
        if how == "fav":
            score = P[m]
        elif how == "public":
            score = S[m]
        else:  # value: chance times how under-picked it is
            score = P[m] * (P[m] / S[m])
        sysm.append(sorted(np.argsort(-score)[:kind[m]].tolist()))
    return sysm


_NB = None


def neighbours():
    """every result within 3 changes of a row: shifts (0, 1 or 2 steps of the sign) per match, and how many changed."""
    global _NB
    if _NB is None:
        import numpy as np, itertools
        D = [np.zeros(13, np.int8)]
        for d in (1, 2, 3):
            for pos in itertools.combinations(range(13), d):
                for sh in itertools.product((1, 2), repeat=d):
                    v = np.zeros(13, np.int8)
                    v[list(pos)] = sh
                    D.append(v)
        D = np.array(D)
        _NB = (D, (D > 0).sum(1))
    return _NB


class Round:
    """exact expected payout per row under the model: results drawn from Pfair, the other players' rows
    independent per match with the public shares S, winners per level Poisson around that mean."""

    def __init__(self, r, Pfair, S, carry, game, nsamp=0, seed=0):
        self.r, self.P, self.S = r, Pfair, S
        self.N = r["sale"] / (r["rp"] or 1)
        self.pool = pools(r, carry)
        self.guar = GUAR.get(game, 0.0)

    def row_ev(self, rows):
        import numpy as np
        D, nd = neighbours()
        R = len(rows)
        out = (rows[:, None, :] + D[None, :, :]) % 3                     # (R, K, 13) results
        m = np.arange(13)[None, None, :]
        pr = self.P[m, out].prod(2)                                       # chance of that result
        q = self.S[m, out].reshape(-1, 13)
        dist = count_dist(q).reshape(R, len(D), 14)
        k = 13 - nd                                                       # our rows' number right
        W = self.N * np.take_along_axis(dist, np.broadcast_to(k[None, :, None], (R, len(D), 1)), 2)[:, :, 0]
        pool = np.array([self.pool[x] for x in k])[None, :]
        with np.errstate(divide="ignore", invalid="ignore"):
            share = np.where(W > 1e-9, (1 - np.exp(-W)) / W, 1.0)         # E[1/(1+others)] for Poisson others
        pay = pool * share
        pay = pay + np.where(k[None, :] == 13, np.exp(-W) * max(0.0, self.guar - self.pool[13]), 0.0)
        pay = np.where(pool / (W + 1) >= MINPAY, pay, 0.0)
        lev = {kk: (pr * pay * (k[None, :] == kk)).sum(1) for kk in SPLIT}
        return (pr * pay).sum(1), lev

    def ev(self, rows):
        e, lev = self.row_ev(rows)
        rp = self.r["rp"] or 1
        return e.mean() / rp, {k: v.mean() / rp for k, v in lev.items()}

    def real(self, rows):
        """what these rows really paid at the real result (amounts as published)."""
        import numpy as np
        O = np.array([IDX[e["out"]] for e in self.r["ev"]])
        right = (rows == O[None, :]).sum(1)
        lv = levels(self.r)
        tot = 0.0
        for k in right:
            if k in lv:
                w, a = lv[k]
                if k == 13 and w == 0:
                    a = max(self.pool[13], self.guar)
                tot += a
        return tot / (len(rows) * (self.r["rp"] or 1))


def ev(game, nhel=2, nhalv=4, nsamp=2000):
    """every round since odds exist: model return and real return of simple systems."""
    import numpy as np
    allr = {r["n"]: r for r in load(game)}
    rs = [r for r in sorted(allr.values(), key=lambda r: r["n"]) if ok_draw(r)]
    half = len(rs) // 2
    w = blend_w(rs[:half])
    print(f"{game}: {len(rs)} rounds {rs[0]['close'][:10]}..{rs[-1]['close'][:10]}; blend weight on odds (fitted on first half) {w:.2f}")
    res = []
    for r in rs:
        prev = allr.get(r["n"] - 1)
        carry = carry_out(prev, pools(prev, 0.0)) if prev and prev.get("dist") and prev.get("sale") else 0.0
        P, S, O = arrays(r)
        B = w * P + (1 - w) * S
        out = {"n": r["n"], "d": r["close"][:10], "carry": carry, "sale": r["sale"]}
        for label, Pf in (("odds", P), ("blend", B)):
            R = Round(r, Pf, S, carry, game, nsamp)
            kind = frame(Pf, nhel, nhalv)
            for how in ("fav", "public", "value"):
                rows = rows_of(build(Pf, S, kind, how))
                e, _ = R.ev(rows)
                out[f"{label}_{how}"] = e
                if label == "blend":
                    out[f"real_{how}"] = R.real(rows)
            # a random public row (sanity check: should come back near 0.60-0.65)
            pub = (np.random.default_rng(r["n"]).random((100, 13, 1)) > S.cumsum(1)[None]).sum(2)
            out[f"{label}_pubrow"] = R.ev(pub)[0]
        res.append(out)
    os.makedirs(CACHE, exist_ok=True)
    json.dump(res, open(f"{CACHE}/ev_{game}_{nhel}_{nhalv}.json", "w"))
    cost = 3 ** nhel * 2 ** nhalv
    print(f"system: {nhel} full guards + {nhalv} half guards = {cost} rows = {cost} kr a round")
    keys = [k for k in res[0] if k not in ("n", "d", "carry", "sale")]
    for sub, sel in (("all rounds", lambda o: True), ("carry in (jackpot)", lambda o: o["carry"] > 0),
                     ("no carry", lambda o: o["carry"] == 0), ("first half", lambda o: o["n"] <= rs[half - 1]["n"]),
                     ("second half", lambda o: o["n"] > rs[half - 1]["n"])):
        g = [o for o in res if sel(o)]
        if not g:
            continue
        print(f"  {sub}: {len(g)} rounds   " + "  ".join(f"{k} {np.mean([o[k] for o in g]):.3f}" for k in keys))
    best = sorted(res, key=lambda o: -o["blend_value"])[:8]
    print("  best rounds by model (blend, value):", [(o["d"], round(o["blend_value"], 2), round(o["carry"] / 1e6, 1)) for o in best])
    print("  rounds where blend_value > 1.0:", sum(o["blend_value"] > 1 for o in res), "of", len(res),
          " their real return:", round(np.mean([o["real_value"] for o in res if o["blend_value"] > 1] or [0]), 3))
    return res


ATG = "https://www.atg.se/services/racinginfo/v1/api/"


def atgraw():
    """save the raw ATG game JSON of a few days (to learn the format)."""
    os.makedirs(CACHE + "/raw", exist_ok=True)
    for day in sys.argv[2:]:
        cal = get(ATG + "calendar/day/" + day)
        for g, v in (cal.get("games") or {}).items():
            if g in ("V75", "V85", "GS75", "V86", "V64"):
                for x in v:
                    gid = x["id"]
                    try:
                        d = get(ATG + "games/" + gid)
                    except Exception as e:
                        print(gid, "ERR", str(e)[:100])
                        continue
                    json.dump(d, open(f"{CACHE}/raw/{gid}.json", "w"))
                    races = d.get("races") or []
                    print(gid, d.get("status"), "races", len(races), "turnover", (d.get("pools") or {}).get(g, {}).get("turnover"))


if __name__ == "__main__":
    cmd =sys.argv[1] if len(sys.argv) > 1 else "explore"
    {"explore": explore, "fetch": fetch, "calib": lambda: calib(sys.argv[2]), "ev": lambda: ev(sys.argv[2], *[int(x) for x in sys.argv[3:5]]), "atgraw": atgraw}[cmd]()
    print("=== DONE ===")
