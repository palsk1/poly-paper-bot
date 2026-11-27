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
        """exact under the model: every result within 3 changes of each row (13, 12, 11, 10 right)."""
        import numpy as np, itertools
        rows = np.asarray(rows)
        R, M = rows.shape
        m = np.arange(M)[None, :]
        q0 = self.S[m, rows]                                   # (R, M) public chance of matching our sign
        p0 = self.P[m, rows]
        subs = [c for d in range(4) for c in itertools.combinations(range(M), d)]
        mask = np.zeros((len(subs), M), bool)
        for i, c in enumerate(subs):
            mask[i, list(c)] = True
        qm = np.where(mask[None], 0.0, q0[:, None, :]).reshape(-1, M)
        base = count_dist(qm).reshape(R, len(subs), M + 1)    # public count over the matches outside the subset
        tot = np.zeros(R)
        lev = {k: np.zeros(R) for k in SPLIT}
        pall = p0.prod(1)
        start = 0
        for d in range(4):
            cs = list(itertools.combinations(range(M), d))
            sl = slice(start, start + len(cs))
            start += len(cs)
            k = M - d
            if k not in self.pool:
                continue
            pos = np.array(cs, int).reshape(len(cs), d)
            B = base[:, sl, :]                                 # (R, nsub, M+1)
            for sh in itertools.product((1, 2), repeat=d):
                sh = np.array(sh, int)
                if d:
                    alt = (rows[:, pos] + sh[None, None, :]) % 3   # (R, nsub, d)
                    qD = self.S[pos[None], alt]
                    pD = self.P[pos[None], alt]
                    pr = pall[:, None] / p0[:, pos].prod(2) * pD.prod(2)
                    poly = np.zeros((R, len(cs), d + 1))
                    poly[..., 0] = 1
                    for j in range(d):
                        qj = qD[..., j:j + 1]
                        poly[..., 1:] = poly[..., 1:] * (1 - qj) + poly[..., :-1] * qj
                        poly[..., 0] *= (1 - qD[..., j])
                    Pk = sum(B[..., k - j] * poly[..., j] for j in range(d + 1))
                else:
                    pr = pall[:, None]
                    Pk = B[..., k]
                W = self.N * Pk
                pool = self.pool[k]
                with np.errstate(divide="ignore", invalid="ignore"):
                    share = np.where(W > 1e-9, -np.expm1(-W) / W, 1.0)
                pay = pool * share
                if k == M:
                    pay = pay + np.exp(-W) * max(0.0, self.guar - pool)
                pay = np.where(pool / (W + 1) >= MINPAY, pay, 0.0)
                v = (pr * pay).sum(1)
                lev[k] += v
                tot += v
        return tot, lev

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
            pub = (np.random.default_rng(r["n"]).random((30, 13, 1)) > S.cumsum(1)[None]).sum(2)
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


def toprows(game, C=3000, K=144, every=1):
    """per round: draw C candidate rows leaning to under-picked signs, score each by the model (blend world),
    keep the best K. Is the model's best-case play above 1.0 back per 1 kr? And what did it really pay?"""
    import numpy as np
    allr = {r["n"]: r for r in load(game)}
    rs = [r for r in sorted(allr.values(), key=lambda r: r["n"]) if ok_draw(r)][::every]
    half = len(rs) // 2
    w = blend_w(rs[:half])
    print(f"{game}: {len(rs)} rounds, blend weight on odds {w:.2f}, {C} candidates a round, best {K} kept")
    res = []
    for r in rs:
        prev = allr.get(r["n"] - 1)
        carry = carry_out(prev, pools(prev, 0.0)) if prev and prev.get("dist") and prev.get("sale") else 0.0
        P, S, O = arrays(r)
        B = w * P + (1 - w) * S
        rng = np.random.default_rng(r["n"])
        cands = []
        for b in (0.0, 0.5, 1.0, 2.0):
            g = B * (B / S) ** b
            g = g / g.sum(1, keepdims=True)
            cands.append((rng.random((C // 4, 13, 1)) > g.cumsum(1)[None]).sum(2))
        cands = np.unique(np.concatenate(cands), axis=0)
        RB = Round(r, B, S, carry, game)
        eb, _ = RB.row_ev(cands)
        top = cands[np.argsort(-eb)[:K]]
        RO = Round(r, P, S, carry, game)
        eo, _ = RO.row_ev(top)
        o = {"n": r["n"], "d": r["close"][:10], "carry": carry, "sale": r["sale"],
             "top1": float(eb.max()), "top10": float(np.sort(eb)[-10:].mean()), "topK": float(np.sort(eb)[-K:].mean()),
             "topK_odds": float(eo.mean()), "real": RB.real(top), "pub_mean": float(eb.mean())}
        res.append(o)
    json.dump(res, open(f"{CACHE}/top_{game}.json", "w"))
    for sub, sel in (("all", lambda o: True), ("carry in", lambda o: o["carry"] > 0), ("no carry", lambda o: o["carry"] == 0),
                     ("first half", lambda o: o["n"] <= rs[half - 1]["n"]), ("second half", lambda o: o["n"] > rs[half - 1]["n"])):
        g = [o for o in res if sel(o)]
        if g:
            print(f"  {sub}: {len(g)} rounds  " + "  ".join(f"{k} {np.mean([o[k] for o in g]):.3f}" for k in ("top1", "top10", "topK", "topK_odds", "real", "pub_mean")))
    good = [o for o in res if o["topK"] > 1.0]
    print(f"  rounds where the best {K} rows average above 1.0 (model): {len(good)} of {len(res)}; their model {np.mean([o['topK'] for o in good] or [0]):.3f}, real {np.mean([o['real'] for o in good] or [0]):.3f}")
    print("  best:", [(o["d"], round(o["topK"], 2), round(o["real"], 2), round(o["carry"] / 1e6, 1)) for o in sorted(res, key=lambda o: -o["topK"])[:10]])
    return res


FD_MAIN = "E0 E1 E2 E3 EC SC0 SC1 SC2 D1 D2 I1 I2 SP1 SP2 F1 F2 N1 B1 P1 T1 G1".split()
FD_NEW = "SWE NOR DNK FIN IRL AUT SWZ POL RUS USA BRA ARG MEX JPN CHN ROU".split()


def fdfetch():
    """football-data.co.uk results with closing odds (Pinnacle + market average), to price the coupons
    with sharp closing odds instead of Svenska Spel's opening odds."""
    d = CACHE + "/fd"
    os.makedirs(d, exist_ok=True)
    n = 0
    for season in ("2122", "2223", "2324", "2425", "2526", "2627"):
        for lg in FD_MAIN:
            url = f"https://www.football-data.co.uk/mmz4281/{season}/{lg}.csv"
            path = f"{d}/{season}_{lg}.csv"
            if os.path.exists(path) and season not in ("2627",):
                continue
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                    open(path, "wb").write(r.read())
                n += 1
            except Exception as e:
                print(url, "ERR", str(e)[:80])
            time.sleep(0.3)
    for lg in FD_NEW:
        url = f"https://www.football-data.co.uk/new/{lg}.csv"
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                open(f"{d}/new_{lg}.csv", "wb").write(r.read())
            n += 1
        except Exception as e:
            print(url, "ERR", str(e)[:80])
    print("fetched", n, "files; header sample:", open(f"{d}/new_SWE.csv", errors="ignore").readline()[:400] if os.path.exists(f"{d}/new_SWE.csv") else "-")


# ---------------------------------------------------------------- sharp closing odds (football-data.co.uk)
ALIAS = {"man city": "manchester city", "man united": "manchester united", "man utd": "manchester united",
         "nott m forest": "nottingham forest", "nottm forest": "nottingham forest", "sheffield weds": "sheffield wednesday",
         "sheffield w": "sheffield wednesday", "sheffield u": "sheffield united", "qpr": "queens park rangers",
         "west brom": "west bromwich", "wolves": "wolverhampton", "spurs": "tottenham", "mk dons": "milton keynes dons",
         "peterboro": "peterborough", "wycombe": "wycombe", "inter": "inter milan", "ath madrid": "atletico madrid",
         "ath bilbao": "athletic bilbao", "sociedad": "real sociedad", "dortmund": "borussia dortmund",
         "m gladbach": "monchengladbach", "ein frankfurt": "eintracht frankfurt", "bayern munich": "bayern",
         "psg": "paris sg", "paris sg": "paris saint germain"}


def norm_team(x):
    import unicodedata, re
    x = unicodedata.normalize("NFKD", x or "").encode("ascii", "ignore").decode().lower()
    x = re.sub(r"[^a-z0-9 ]", " ", x)
    x = re.sub(r"\b(fc|afc|cf|sc|if|ff|bk|fk|ik|sk|ac|as|ssc|club|de|the)\b", " ", x)
    x = " ".join(x.split())
    return ALIAS.get(x, x)


def tsim(a, b):
    import difflib
    a, b = norm_team(a), norm_team(b)
    if not a or not b:
        return 0.0
    if a == b or a.startswith(b) or b.startswith(a):
        return 1.0
    ta, tb = a.split(), b.split()
    if ta[0] == tb[0] and len(ta[0]) >= 4 and (len(ta) == 1 or len(tb) == 1):
        return 0.9
    return difflib.SequenceMatcher(None, a, b).ratio()


def fd_games():
    """every game in the football-data files: (date, home, away, closing odds 1/X/2 from Pinnacle or the average)."""
    import csv, glob, datetime
    out = {}
    for path in glob.glob(CACHE + "/fd/*.csv"):
        try:
            rows = list(csv.DictReader(open(path, encoding="utf-8-sig", errors="ignore")))
        except Exception:
            continue
        for r in rows:
            h = r.get("HomeTeam") or r.get("Home")
            a = r.get("AwayTeam") or r.get("Away")
            ds = r.get("Date")
            if not (h and a and ds):
                continue
            try:
                dd = datetime.datetime.strptime(ds, "%d/%m/%Y").date() if len(ds.split("/")[-1]) == 4 else datetime.datetime.strptime(ds, "%d/%m/%y").date()
            except ValueError:
                continue
            odds = None
            for pre in ("PSC", "AvgC", "PS", "Avg", "B365C", "B365"):
                trip = [num(r.get(pre + x)) for x in ("H", "D", "A")]
                if all(t and t > 1 for t in trip):
                    odds = (pre, trip)
                    break
            if not odds:
                continue
            out.setdefault(dd, []).append((h, a, odds[0], odds[1]))
    return out


def attach_close(rs, games):
    """add 'pc' (closing odds) to each match where a football-data game matches by date and names."""
    import datetime
    hit = tot = 0
    for r in rs:
        for e in r["ev"]:
            tot += 1
            e["pc"] = None
            if not e.get("start") or len(e.get("teams") or []) != 2:
                continue
            d0 = datetime.date.fromisoformat(e["start"][:10])
            best = None
            for dd in (d0, d0 - datetime.timedelta(days=1), d0 + datetime.timedelta(days=1)):
                for h, a, src, trip in games.get(dd, []):
                    sh, sa = tsim(e["teams"][0], h), tsim(e["teams"][1], a)
                    sc = min(sh, sa)
                    if sc >= 0.75 and (best is None or sc > best[0]):
                        best = (sc, trip, src, h, a)
            if best:
                e["pc"] = best[1]
                e["pcsrc"] = best[2]
                hit += 1
    return hit, tot


def closing(game, K=144, C=3000):
    """the main test, priced with sharp closing odds: do the best rows by the model pay more than they cost?"""
    import numpy as np
    games = fd_games()
    allr = {r["n"]: r for r in load(game)}
    rs = [r for r in sorted(allr.values(), key=lambda r: r["n"]) if ok_draw(r)]
    hit, tot = attach_close(rs, games)
    full = [r for r in rs if all(e.get("pc") for e in r["ev"])]
    print(f"{game}: matched {hit} of {tot} matches to closing odds; {len(full)} of {len(rs)} rounds fully matched")
    # forecasting: closing odds vs public vs opening odds on the matched matches
    ll = {"close": 0.0, "open": 0.0, "public": 0.0}
    n = 0
    band = {}
    for r in rs:
        for e in r["ev"]:
            if not e.get("pc"):
                continue
            o = IDX[e["out"]]
            pc, po = fairp(e["pc"]), fairp(e["od"] or e["so"])
            sf = [x / sum(e["sf"]) for x in e["sf"]]
            sf = [max(x, 0.003) for x in sf]
            ll["close"] -= math.log(pc[o])
            ll["open"] -= math.log(po[o])
            ll["public"] -= math.log(sf[o])
            n += 1
            for j in range(3):
                b = int(np.clip(round((sf[j] - pc[j]) * 20), -4, 4))
                t = band.setdefault(b, [0, 0.0, 0.0, 0.0])
                t[0] += 1
                t[1] += pc[j]
                t[2] += sf[j]
                t[3] += (o == j)
    print("  log loss per match:", {k: round(v / max(n, 1), 4) for k, v in ll.items()}, "on", n, "matches (lower = better)")
    print("  public share minus closing chance (5-pt buckets): n, closing chance, public share, real hit rate")
    for b in sorted(band):
        t = band[b]
        print(f"    {b * 5:+4d} pts n={t[0]:5d} close {t[1] / t[0]:.3f} public {t[2] / t[0]:.3f} real {t[3] / t[0]:.3f}")
    res = []
    for r in full:
        prev = allr.get(r["n"] - 1)
        carry = carry_out(prev, pools(prev, 0.0)) if prev and prev.get("dist") and prev.get("sale") else 0.0
        _, S, O = arrays(r)
        P = np.array([fairp(e["pc"]) for e in r["ev"]])
        rng = np.random.default_rng(r["n"])
        cands = []
        for b in (0.0, 0.5, 1.0, 2.0):
            g = P * (P / S) ** b
            g = g / g.sum(1, keepdims=True)
            cands.append((rng.random((C // 4, 13, 1)) > g.cumsum(1)[None]).sum(2))
        cands = np.unique(np.concatenate(cands), axis=0)
        RC = Round(r, P, S, carry, game)
        ec, lev = RC.row_ev(cands)
        order = np.argsort(-ec)
        top = cands[order[:K]]
        favrow = P.argmax(1)[None, :]
        o = {"n": r["n"], "d": r["close"][:10], "carry": carry, "top1": float(ec[order[0]]), "top10": float(ec[order[:10]].mean()),
             "topK": float(ec[order[:K]].mean()), "all": float(ec.mean()), "real": RC.real(top), "fav": float(RC.row_ev(favrow)[0][0]),
             "hitp": float(np.prod(P[np.arange(13)[None, :], top], axis=1).sum()),
             "hit": int((top == O[None, :]).all(1).any()),
             "best12": int((top == O[None, :]).sum(1).max())}
        res.append(o)
    json.dump(res, open(f"{CACHE}/close_{game}.json", "w"))
    for sub, sel in (("all", lambda o: True), ("carry in", lambda o: o["carry"] > 0), ("no carry", lambda o: o["carry"] == 0)):
        g = [o for o in res if sel(o)]
        if g:
            print(f"  {sub}: {len(g)} rounds  " + "  ".join(f"{k} {np.mean([o[k] for o in g]):.3f}" for k in ("top1", "top10", "topK", "all", "fav", "real")))
    if res:
        print(f"  best {K} rows: expected 13-right hits {sum(o['hitp'] for o in res):.2f}, real {sum(o['hit'] for o in res)}")
        good = [o for o in res if o["topK"] > 1.0]
        print(f"  rounds where the model's best {K} rows average above 1.0: {len(good)} of {len(res)}; model {np.mean([o['topK'] for o in good] or [0]):.3f}, real {np.mean([o['real'] for o in good] or [0]):.3f}")
    return res


ATG = "https://www.atg.se/services/racinginfo/v1/api/"


def atg_compact(d, g):
    pool = (d.get("pools") or {}).get(g) or {}
    res = pool.get("result") or {}
    legs = []
    for r in d.get("races") or []:
        win = [w.get("number") for w in ((((r.get("pools") or {}).get("vinnare") or {}).get("result") or {}).get("winners") or [])]
        st = []
        for s in r.get("starts") or []:
            sp = s.get("pools") or {}
            st.append([s.get("number"), (sp.get("vinnare") or {}).get("odds"), (sp.get(g) or {}).get("betDistribution"),
                       bool(s.get("scratched")), (s.get("result") or {}).get("place"), (s.get("result") or {}).get("finalOdds")])
        legs.append({"race": r.get("id"), "win": win, "scr": (r.get("result") or {}).get("scratchings"), "st": st})
    return {"id": d.get("id"), "g": g, "turnover": pool.get("turnover"), "payouts": res.get("payouts"),
            "poolpay": pool.get("payouts"), "systems": pool.get("systemCount"), "jackpot": pool.get("jackpotAmount") or res.get("jackpotAmount"),
            "keys": sorted(pool.keys()), "rkeys": sorted(res.keys()), "legs": legs}


def atgfetch():
    """ATG V75 / V85 / GS75 rounds: per horse win odds, the big game's bet share, winner, payouts."""
    import datetime
    a = datetime.date.fromisoformat(sys.argv[2])
    b = datetime.date.fromisoformat(sys.argv[3])
    path = f"{CACHE}/atg.json.gz"
    have = {}
    if os.path.exists(path):
        have = {x["id"]: x for x in json.load(gzip.open(path, "rt"))}
    day = a
    new = 0
    while day <= b:
        if day.weekday() in (5, 6):
            try:
                cal = get(ATG + "calendar/day/" + day.isoformat())
            except Exception as e:
                print(day, "cal ERR", str(e)[:80])
                day += datetime.timedelta(days=1)
                continue
            for g, v in (cal.get("games") or {}).items():
                if g not in ("V75", "V85", "GS75", "V86"):
                    continue
                for x in v:
                    gid = x["id"]
                    if gid in have:
                        continue
                    try:
                        have[gid] = atg_compact(get(ATG + "games/" + gid), g)
                        new += 1
                    except Exception as e:
                        print(gid, "ERR", str(e)[:80])
        day += datetime.timedelta(days=1)
    json.dump(list(have.values()), gzip.open(path, "wt"))
    print("atg rounds saved", len(have), "new", new)
    import collections
    print(collections.Counter(x["g"] for x in have.values()))
    x = sorted(have.values(), key=lambda x: x["id"])[-1]
    print(x["id"], x["keys"], x["rkeys"], x["poolpay"], x["payouts"])


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


# ---------------------------------------------------------------- ATG: V75 / GS75 (7 legs, pays 7, 6 and 5 right)
ATG_SPLIT = {7: .40, 6: .20, 5: .40}


def atg_round(x, alpha=1.0):
    """per leg: fair win chance from the win-pool odds (power alpha), public share in the big game, winner index."""
    import numpy as np
    legs = []
    for L in x["legs"]:
        st = [s for s in L["st"] if not s[3] and s[1] and s[2] is not None]
        if not st or not L["win"]:
            return None
        nums = [s[0] for s in st]
        win = [nums.index(w) for w in L["win"] if w in nums]
        if len(win) != 1:      # dead heat or winner missing: skip the round
            return None
        odds = np.array([s[1] / 100.0 for s in st])
        p = (1 / odds) ** alpha
        p = p / p.sum()
        sh = np.array([max(s[2], 1) / 10000.0 for s in st])
        sh = sh / sh.sum()
        legs.append((p, sh, win[0]))
    return legs


def atg_rows_ev(legs, rows, N, pool, minpay=15.0):
    """exact expected payout per row: every result within 2 changed legs (7, 6, 5 right)."""
    import numpy as np, itertools
    M = len(legs)
    R = len(rows)
    q0 = np.array([[legs[m][1][r[m]] for m in range(M)] for r in rows])
    p0 = np.array([[legs[m][0][r[m]] for m in range(M)] for r in rows])
    tot = np.zeros(R)
    lev = {k: np.zeros(R) for k in pool}
    for d in range(3):
        k = M - d
        for D in itertools.combinations(range(M), d):
            q = q0.copy()
            q[:, list(D)] = 0.0
            base = count_dist(q)                              # (R, M+1) public right outside D
            if d == 0:
                alts = [((), np.ones(R), np.zeros((R, 0)))]
            else:
                alts = []
                for combo in itertools.product(*[range(len(legs[m][0])) for m in D]):
                    ok = np.array([all(combo[i] != r[D[i]] for i in range(d)) for r in rows])
                    if not ok.any():
                        continue
                    pr = np.prod([legs[D[i]][0][combo[i]] for i in range(d)]) * ok
                    qs = np.array([[legs[D[i]][1][combo[i]] for i in range(d)]] * R)
                    alts.append((combo, pr, qs))
            pnot = p0.prod(1) / np.prod(p0[:, list(D)], axis=1) if d else p0.prod(1)
            for combo, pr, qs in alts:
                poly = np.zeros((R, d + 1))
                poly[:, 0] = 1
                for j in range(d):
                    qj = qs[:, j:j + 1]
                    poly[:, 1:] = poly[:, 1:] * (1 - qj) + poly[:, :-1] * qj
                    poly[:, 0] *= (1 - qs[:, j])
                Pk = sum(base[:, k - j] * poly[:, j] for j in range(d + 1))
                W = N * Pk
                with np.errstate(divide="ignore", invalid="ignore"):
                    share = np.where(W > 1e-9, -np.expm1(-W) / W, 1.0)
                pay = pool[k] * share
                pay = np.where(pool[k] / (W + 1) >= minpay, pay, 0.0)
                v = pnot * pr * pay
                lev[k] += v
                tot += v
    return tot, lev


def atg_system(legs, budget_rows, how):
    """pick horses per leg: add the horse with the best score where it buys the most chance per extra row."""
    import numpy as np
    M = len(legs)
    picks = []
    for p, sh, _ in legs:
        sc = p if how == "fav" else (p * p / sh if how == "value" else sh)
        picks.append(list(np.argsort(-sc)))
    n = [1] * M
    while True:
        best = None
        for m in range(M):
            if n[m] >= len(picks[m]):
                continue
            rows = int(np.prod(n)) // n[m] * (n[m] + 1)
            if rows > budget_rows:
                continue
            cov = sum(legs[m][0][i] for i in picks[m][:n[m]])
            gain = legs[m][0][picks[m][n[m]]] / max(cov, 1e-9)
            if best is None or gain > best[0]:
                best = (gain, m)
        if best is None:
            break
        n[best[1]] += 1
    return [sorted(picks[m][:n[m]]) for m in range(M)]


def atgev(games=("V75", "GS75")):
    import numpy as np, itertools, collections
    xs = [x for x in json.load(gzip.open(f"{CACHE}/atg.json.gz", "rt")) if x["g"] in games and x.get("payouts") and x.get("poolpay")]
    xs.sort(key=lambda x: x["id"].split("_")[1])
    # row price from the published numbers: payout per row x winning rows = pool money at that level
    rp = {"V75": 0.5, "GS75": 1.0}
    # 1) calibration: win-pool chance vs public share in the big game vs real winner
    band = {}
    llp = lls = 0.0
    nn = 0
    rounds = []
    for x in xs:
        legs = atg_round(x)
        if not legs or len(legs) != 7:
            continue
        rounds.append((x, legs))
        for p, sh, w in legs:
            llp -= math.log(p[w])
            lls -= math.log(sh[w])
            nn += 1
            for i in range(len(p)):
                b = int(np.clip(round((sh[i] - p[i]) * 20), -4, 4))
                t = band.setdefault(b, [0, 0.0, 0.0, 0.0])
                t[0] += 1
                t[1] += p[i]
                t[2] += sh[i]
                t[3] += (i == w)
    print(f"ATG {games}: {len(rounds)} rounds {rounds[0][0]['id']} .. {rounds[-1][0]['id']}")
    print(f"  log loss per leg: win-pool odds {llp / nn:.4f}, big-game public share {lls / nn:.4f}")
    for b in sorted(band):
        t = band[b]
        print(f"    share minus win chance {b * 5:+4d} pts: n={t[0]:6d} win-odds chance {t[1] / t[0]:.3f} share {t[2] / t[0]:.3f} real {t[3] / t[0]:.3f}")
    # 2) systems
    res = []
    for x, legs in rounds:
        g = x["g"]
        N = int(x["turnover"]) / 100.0 / rp[g]
        pool = {int(k): int(v) / 100.0 for k, v in x["poolpay"].items()}
        o = {"id": x["id"], "g": g}
        # winners check at the real result
        win = [l[2] for l in legs]
        q = np.array([[legs[m][1][win[m]] for m in range(7)]])
        dist = count_dist(q)[0]
        for k in (7, 6, 5):
            o[f"W{k}m"] = N * dist[k]
            o[f"W{k}r"] = (x["payouts"].get(str(k)) or {}).get("systems", 0)
        for budget in (1, 200, 600):
            for how in ("fav", "value", "public"):
                sysm = atg_system(legs, budget, how)
                rows = np.array(list(itertools.product(*sysm)))
                ev, lev = atg_rows_ev(legs, rows, N, pool)
                right = (rows == np.array(win)[None, :]).sum(1)
                real = 0.0
                for kk in right:
                    if str(kk) in x["payouts"] and int(kk) >= 5:
                        real += (x["payouts"][str(kk)].get("payout") or 0) / 100.0
                cost = len(rows) * rp[g]
                key = f"{budget}_{how}"
                o[key] = ev.sum() / cost
                o[key + "_7"] = lev[7].sum() / cost
                o[key + "_real"] = real / cost
                o[key + "_rows"] = len(rows)
        res.append(o)
    json.dump(res, open(f"{CACHE}/atgev.json", "w"))
    for k in (7, 6, 5):
        a = np.array([(o[f"W{k}m"], o[f"W{k}r"]) for o in res])
        lr = np.log((a[:, 1] + .5) / (a[:, 0] + .5))
        print(f"  winners {k} right: model median {np.median(a[:, 0]):.0f}, real median {np.median(a[:, 1]):.0f}, log ratio mean {lr.mean():+.2f} sd {lr.std():.2f}")
    for sub, sel in (("all", lambda o: True), ("V75", lambda o: o["g"] == "V75"), ("GS75", lambda o: o["g"] == "GS75")):
        g = [o for o in res if sel(o)]
        print(f"  == {sub}: {len(g)} rounds")
        for budget in (1, 200, 600):
            for how in ("fav", "value", "public"):
                key = f"{budget}_{how}"
                print(f"    {budget:4d}-row budget {how:6s}: model {np.mean([o[key] for o in g]):.3f} (7-right part {np.mean([o[key + '_7'] for o in g]):.3f}), real {np.mean([o[key + '_real'] for o in g]):.3f}, avg rows {np.mean([o[key + '_rows'] for o in g]):.0f}")


if __name__ == "__main__":
    cmd =sys.argv[1] if len(sys.argv) > 1 else "explore"
    {"explore": explore, "fetch": fetch, "calib": lambda: calib(sys.argv[2]), "ev": lambda: ev(sys.argv[2], *[int(x) for x in sys.argv[3:5]]), "atgraw": atgraw, "atg": atgfetch, "atgev": atgev, "close": lambda: closing(sys.argv[2]), "fd": fdfetch, "top": lambda: toprows(sys.argv[2], *[int(x) for x in sys.argv[3:6]])}[cmd]()
    print("=== DONE ===")
