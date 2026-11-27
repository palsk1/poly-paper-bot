"""Betting exchanges outside Kalshi / Polymarket (Smarkets, Matchbook, Betdaq, Betfair...): research only.

Commands (probe input out_exch_<cmd>_<args>):
  explore            which exchange hosts answer from Actions + a dump of Smarkets v3 shapes
  snap               one snapshot: Smarkets markets with quotes vs Polymarket / Kalshi twins, gap after fees
  watch <min> <sec>  repeat the matched pairs every <sec> seconds for <min> minutes (gap life, who moves first)
  report             score everything saved in bt_cache/out_exch/
Saves raw snapshots under bt_cache/out_exch/ (pushed to the shared store by the probe route).
Never logs in, never places anything.
"""
import json, os, sys, time, re, gzip, math, urllib.request, urllib.parse, difflib
from concurrent.futures import ThreadPoolExecutor

UA = {"User-Agent": "Mozilla/5.0 (research script)", "Accept": "application/json"}
CACHE = "bt_cache/out_exch"
SMK = "https://api.smarkets.com/v3"
GAMMA = "https://gamma-api.polymarket.com"
CLOB = "https://clob.polymarket.com"
KAL = "https://api.elections.kalshi.com/trade-api/v2"


def get(url, timeout=20, tries=3, raw=False, data=None, headers=None):
    last = None
    for i in range(tries):
        try:
            h = dict(UA)
            if headers:
                h.update(headers)
            req = urllib.request.Request(url, headers=h, data=data)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                b = r.read()
                return b if raw else json.loads(b)
        except urllib.error.HTTPError as e:
            last = e
            if e.code in (400, 401, 403, 404, 410, 451):
                raise
            time.sleep(1.5 * (i + 1))
        except Exception as e:  # noqa
            last = e
            time.sleep(1.5 * (i + 1))
    raise last


def tryget(url, **kw):
    try:
        return get(url, **kw)
    except Exception as e:  # noqa
        return {"_err": str(e)[:200]}


# ---------------------------------------------------------------- explore
def explore():
    hosts = [
        "https://api.smarkets.com/v3/events/?limit=1",
        "https://api.matchbook.com/edge/rest/events?per-page=1",
        "https://api.matchbook.com/edge/rest/lookups/sports",
        "https://www.matchbook.com/edge/rest/events?per-page=1",
        "https://api.betdaq.com/",
        "https://www.betdaq.com/",
        "https://api.betfair.com/exchange/betting/rest/v1.0/",
        "https://identitysso.betfair.com/",
        "https://ero.betfair.com/www/sports/exchange/readonly/v1/bymarket?marketIds=1.1&types=EVENT",
        "https://www.betfair.com/www/sports/navigation/facet/v1/search?_ak=nzIFcwyWhrlwYMrh",
        "https://historicdata.betfair.com/",
        "https://www.betfair.se/",
        "https://api.prophetx.co/",
        "https://api.novig.us/",
        "https://www.sporttrade.com/",
        "https://www.orbitxch.com/",
        "https://api.sx.bet/markets/active?onlyMainLine=true",
        "https://api.sx.bet/summary",
        "https://api.overtimemarkets.xyz/v2/networks/10/markets",
        "https://api.azuro.org/",
        "https://www.football-data.co.uk/",
        "https://promo.betfair.com/betfairsp/prices/",
    ]
    for h in hosts:
        try:
            b = get(h, raw=True, tries=1, timeout=15)
            print("OK ", h, len(b), b[:160])
        except urllib.error.HTTPError as e:
            print("HTTP", e.code, h)
        except Exception as e:  # noqa
            print("ERR", h, str(e)[:120])
    # Smarkets shapes
    print("\n--- smarkets event types")
    r = tryget(SMK + "/events/?state=upcoming&limit=5&sort=id")
    print(json.dumps(r)[:1500])
    for dom in ["politics", "current_affairs", "football", "tennis", "american_football", "basketball",
                "horse_racing", "ice_hockey", "baseball", "esports", "entertainment", "golf", "boxing", "mma", "cricket"]:
        r = tryget(SMK + "/events/?" + urllib.parse.urlencode({"type_domain": dom, "state": "upcoming", "limit": 50}))
        evs = r.get("events", []) if isinstance(r, dict) else []
        print(dom, len(evs), r.get("_err", "") if isinstance(r, dict) else "", [e.get("name") for e in evs[:4]])
    r = tryget(SMK + "/events/?" + urllib.parse.urlencode({"type_domain": "politics", "state": "upcoming", "limit": 3}))
    evs = r.get("events", [])
    if evs:
        e = evs[0]
        print("EVENT", json.dumps(e)[:900])
        m = tryget(SMK + f"/events/{e['id']}/markets/")
        print("MARKETS", json.dumps(m)[:900])
        mk = (m.get("markets") or [{}])[0]
        if mk.get("id"):
            for p in ["contracts/", "quotes/", "last_executed_prices/", "volumes/"]:
                print(p, json.dumps(tryget(SMK + f"/markets/{mk['id']}/{p}"))[:900])
            for p in [f"/markets/{mk['id']}/price_history/", f"/markets/{mk['id']}/charts/",
                      f"/contracts/history/?market_id={mk['id']}", f"/markets/{mk['id']}/executions/"]:
                print(p, json.dumps(tryget(SMK + p))[:300])
    print("=== DONE ===")


# ---------------------------------------------------------------- Smarkets
SMK_DOMAINS = ["politics", "current_affairs", "football", "tennis", "american_football", "basketball",
               "ice_hockey", "baseball", "esports", "golf", "boxing", "mma", "cricket",
               "rugby_union", "darts", "snooker", "motorsports"]
DEBUG = {"smk_quote": 0, "mb": 0}


def smk_events(dom, maxn=1200):
    out = []
    for state in ("upcoming", "live"):
        off = 0
        while off < maxn:
            q = {"type_domain": dom, "state": state, "limit": 200, "offset": off, "sort": "id"}
            r = tryget(SMK + "/events/?" + urllib.parse.urlencode(q))
            evs = r.get("events", []) if isinstance(r, dict) else []
            out += [e for e in evs if e.get("bettable")]
            if len(evs) < 200:
                break
            off += 200
    return out


def chunks(xs, n):
    for i in range(0, len(xs), n):
        yield xs[i:i + n]


def smk_markets(event_ids):
    mk = []
    for c in chunks(event_ids, 50):
        r = tryget(SMK + "/events/" + ",".join(map(str, c)) + "/markets/?limit=500")
        mk += r.get("markets", []) if isinstance(r, dict) else []
    return mk


def smk_contracts(mids):
    ct = []
    for c in chunks(mids, 50):
        r = tryget(SMK + "/markets/" + ",".join(map(str, c)) + "/contracts/?limit=1000")
        ct += r.get("contracts", []) if isinstance(r, dict) else []
    return ct


def smk_quotes(mids):
    q = {}
    for c in chunks(mids, 50):
        r = tryget(SMK + "/markets/" + ",".join(map(str, c)) + "/quotes/")
        if isinstance(r, dict) and "_err" not in r:
            q.update(r)
    if q and DEBUG["smk_quote"] < 1:
        DEBUG["smk_quote"] += 1
        k = next(iter(q))
        print("SMK QUOTE SAMPLE", k, json.dumps(q[k])[:400])
    return q


def smk_volumes(mids):
    v = {}
    for c in chunks(mids, 50):
        r = tryget(SMK + "/markets/" + ",".join(map(str, c)) + "/volumes/")
        for x in (r.get("volumes", []) if isinstance(r, dict) else []):
            v[str(x.get("market_id"))] = x
    return v


# ---------------------------------------------------------------- Matchbook (public read, no login)
MB = "https://api.matchbook.com/edge/rest"


def mb_events(maxn=3000):
    out, off = [], 0
    while off < maxn:
        q = {"per-page": 200, "offset": off, "include-prices": "true", "price-depth": 3, "odds-type": "DECIMAL",
             "states": "open", "exchange-type": "back-lay"}
        r = tryget(MB + "/events?" + urllib.parse.urlencode(q), timeout=40)
        evs = r.get("events", []) if isinstance(r, dict) else []
        if isinstance(r, dict) and r.get("_err"):
            print("matchbook err", r["_err"])
        out += evs
        if len(evs) < 200:
            break
        off += 200
    if out and DEBUG["mb"] < 1:
        DEBUG["mb"] += 1
        e = out[0]
        print("MB EVENT SAMPLE", json.dumps(e)[:1200])
    return out


def mb_runner_book(rn):
    """Matchbook runner prices -> (offers to buy Yes [(price, contracts)], bids [(price, contracts)]).
    'back' prices are what you can back at (you buy Yes at 1/odds); 'lay' prices are what you can lay at (you sell Yes
    at 1/odds). available-amount is the backer's stake, so contracts = stake * odds."""
    ofs, bds = [], []
    for p in rn.get("prices", []) or []:
        o = float(p.get("decimal-odds") or p.get("odds") or 0)
        a = float(p.get("available-amount") or 0)
        if o <= 1:
            continue
        if p.get("side") == "back":
            ofs.append((round(1 / o, 4), a * o))
        elif p.get("side") == "lay":
            bds.append((round(1 / o, 4), a * o))
    return sorted(ofs), sorted(bds, reverse=True)


# ---------------------------------------------------------------- Polymarket / Kalshi
def poly_events(maxn=4000):
    out, off = [], 0
    while len(out) < maxn:
        r = tryget(GAMMA + "/events?" + urllib.parse.urlencode(
            {"closed": "false", "active": "true", "limit": 100, "offset": off, "order": "volume24hr", "ascending": "false"}))
        if not isinstance(r, list) or not r:
            break
        out += r
        off += 100
        if len(r) < 100:
            break
    return out


def poly_book(tok):
    r = tryget(CLOB + "/book?token_id=" + str(tok))
    if not isinstance(r, dict) or "_err" in r:
        return None
    asks = sorted([(float(a["price"]), float(a["size"])) for a in r.get("asks", [])])
    bids = sorted([(float(a["price"]), float(a["size"])) for a in r.get("bids", [])], reverse=True)
    return {"asks": asks, "bids": bids}


def kalshi_events(maxn=6000):
    out, cur = [], None
    while len(out) < maxn:
        q = {"status": "open", "limit": 200, "with_nested_markets": "true"}
        if cur:
            q["cursor"] = cur
        r = tryget(KAL + "/events?" + urllib.parse.urlencode(q))
        evs = r.get("events", []) if isinstance(r, dict) else []
        out += evs
        cur = r.get("cursor") if isinstance(r, dict) else None
        if not cur or not evs:
            break
    return out


def kalshi_book(tk):
    r = tryget(KAL + f"/markets/{tk}/orderbook")
    ob = (r or {}).get("orderbook") or {}
    # bids only: yes bids and no bids, [price_cents, qty]
    yb = sorted([(p / 100, q) for p, q in (ob.get("yes") or [])], reverse=True)
    nb = sorted([(p / 100, q) for p, q in (ob.get("no") or [])], reverse=True)
    # a Yes ask at 1 - no bid
    yes_asks = sorted([(round(1 - p, 4), q) for p, q in nb])
    no_asks = sorted([(round(1 - p, 4), q) for p, q in yb])
    return {"yes_asks": yes_asks, "yes_bids": yb, "no_asks": no_asks, "no_bids": nb}


# ---------------------------------------------------------------- matching
STOP = set("the a an of to in on at for vs v versus will be by and or who win wins winner match game fc cf sc afc "
           "ac de real next 2026 2027 2028 election general party us u.s. outright market odds".split())


def toks(s):
    s = (s or "").lower()
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return [w for w in s.split() if w not in STOP and len(w) > 1]


def sim(a, b):
    ta, tb = set(toks(a)), set(toks(b))
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


# ---------------------------------------------------------------- fees and executable prices
EX_COMM = {"smk": 0.02, "mb": 0.02}   # UK-rate commission on net winnings in a market (Smarkets 2%, Matchbook 2% UK / 4% rest)
BAD_Q = ("spread", "o/u", "over ", "under ", "total", "handicap", "1h", "half", "map ", "set ", "both teams",
         "corners", "cards", "exact", "score", "points", "rebounds", "assists", "yards", "goals", "quarter", "period")


def poly_fee(p, rate):
    return rate * p * (1 - p)  # per share


def kal_fee(p):
    return 0.07 * p * (1 - p)  # per contract (ignores the round-up to the cent; fine at $10-50)


def walk_cost(asks, dollars, fee_fn):
    """Average all-in cost per $1-payout contract to spend `dollars` walking `asks` [(price, contracts)]."""
    spent, sh = 0.0, 0.0
    for p, q in asks:
        if spent >= dollars - 1e-9:
            break
        if p <= 0 or p >= 1 or q <= 0:
            continue
        unit = p + fee_fn(p)
        take = min(q, (dollars - spent) / unit)
        spent += take * unit
        sh += take
    if sh <= 0 or spent < dollars * 0.999:
        return None
    return spent / sh


def ex_fee(venue):
    c = EX_COMM[venue]
    return lambda p: c * (1 - p)   # commission on the win of a contract bought at p (charged only if it wins; counted always)


def smk_sides(qt):
    """Smarkets quote -> offers [(price, contracts)], bids [(price, contracts)]. price in basis points of 1.
    quantity in 1/10000 of a GBP contract (a contract pays GBP 1); see report for the check."""
    ofs = sorted([(x["price"] / 10000, x["quantity"] / 10000) for x in qt.get("offers", []) if x.get("price")])
    bds = sorted([(x["price"] / 10000, x["quantity"] / 10000) for x in qt.get("bids", []) if x.get("price")], reverse=True)
    return ofs, bds


# ---------------------------------------------------------------- snapshots
def save(name, obj):
    os.makedirs(CACHE, exist_ok=True)
    with gzip.open(os.path.join(CACHE, name), "wt") as f:
        json.dump(obj, f)


def load_all(prefix):
    out = []
    if not os.path.isdir(CACHE):
        return out
    for fn in sorted(os.listdir(CACHE)):
        if fn.startswith(prefix):
            try:
                with gzip.open(os.path.join(CACHE, fn), "rt") as f:
                    out.append(json.load(f))
            except Exception:  # noqa
                pass
    return out


def exchange_contracts():
    """Every contract on Smarkets and Matchbook: list of dicts {venue, ev, evname, dom, mname, cid, cname, start, n_out}."""
    rows = []
    with ThreadPoolExecutor(8) as ex:
        res = list(ex.map(smk_events, SMK_DOMAINS))
    evs = {}
    for dom, lst in zip(SMK_DOMAINS, res):
        for e in lst:
            e["_dom"] = dom
            evs[str(e["id"])] = e
    print("smarkets bettable events", len(evs), {d: len(l) for d, l in zip(SMK_DOMAINS, res)})
    mk = smk_markets(list(evs))
    ct = smk_contracts([str(m["id"]) for m in mk])
    by_m = {}
    for c in ct:
        by_m.setdefault(str(c["market_id"]), []).append(c)
    for m in mk:
        e = evs.get(str(m.get("event_id")))
        if not e:
            continue
        cs = by_m.get(str(m["id"]), [])
        for c in cs:
            rows.append({"venue": "smk", "ev": str(e["id"]), "evname": e.get("name") or "", "parent": e.get("full_slug") or "",
                         "dom": e["_dom"], "mid": str(m["id"]), "mname": m.get("name") or "", "cid": str(c["id"]),
                         "cname": c.get("name") or "", "start": e.get("start_datetime"), "n_out": len(cs)})
    print("smarkets markets", len(mk), "contracts", len(ct))
    me = mb_events()
    nmb = 0
    for e in me:
        sport = str(e.get("sport-id"))
        for m in e.get("markets", []) or []:
            rs = m.get("runners", []) or []
            for rn in rs:
                rows.append({"venue": "mb", "ev": str(e["id"]), "evname": e.get("name") or "", "parent": "",
                             "dom": "mb_" + sport, "mid": str(m.get("id")), "mname": m.get("name") or "",
                             "cid": str(rn.get("id")), "cname": rn.get("name") or "", "start": e.get("start"),
                             "n_out": len(rs), "mtype": m.get("market-type")})
                nmb += 1
    print("matchbook events", len(me), "runners", nmb)
    return rows


def poly_markets(pe):
    out = []
    for e in pe:
        for m in e.get("markets", []) or []:
            try:
                tids = json.loads(m.get("clobTokenIds") or "[]")
                outs = json.loads(m.get("outcomes") or "[]")
            except Exception:  # noqa
                continue
            if len(tids) != 2 or m.get("closed"):
                continue
            q = (m.get("question") or "").lower()
            out.append({"evt": e.get("title") or "", "q": m.get("question") or "", "grp": m.get("groupItemTitle") or "",
                        "outs": outs, "tok": tids, "fee": m.get("feeRate"), "end": m.get("endDate"),
                        "smt": m.get("sportsMarketType") or "", "bad": any(b in q for b in BAD_Q),
                        "n_in_ev": len(e.get("markets") or [])})
    return out


def norm(s):
    s = (s or "").lower().replace("&", "and")
    s = re.sub(r"\(.*?\)", " ", s)
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return " ".join(w for w in s.split() if w not in ("fc", "cf", "sc", "afc", "the", "de", "ac"))


def name_match(a, b):
    a, b = norm(a), norm(b)
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    return difflib.SequenceMatcher(None, a, b).ratio()


MKT_SKIP = ("handicap", "over/under", "total", "correct score", "half", "corners", "cards", "both teams", "spread",
            "points", "first", "to qualify", "draw no bet", "double chance", "set ", "game ", "map ", "method", "round",
            "goalscorer", "win to nil", "margin", "odd/even", "tie break", "to score")


def match_all(rows, pm, ke):
    """Pair each exchange contract with a Polymarket / Kalshi outcome on the same event. Event names must share
    words; outcome names must match closely. Only main 'who wins' style markets."""
    pairs = []
    pidx = {}
    for i, x in enumerate(pm):
        for w in set(toks(x["evt"])):
            pidx.setdefault(w, set()).add(i)
    kidx, kms = {}, []
    for e in ke:
        for km in e.get("markets") or []:
            kms.append({"evt": (e.get("title") or "") + " " + (e.get("sub_title") or ""), "q": km.get("title") or "",
                        "nm": km.get("yes_sub_title") or "", "kt": km.get("ticker"), "n_in_ev": len(e.get("markets") or [])})
    for i, x in enumerate(kms):
        for w in set(toks(x["evt"])):
            kidx.setdefault(w, set()).add(i)
    for r in rows:
        mlow = r["mname"].lower() + " "
        if any(b in mlow for b in MKT_SKIP):
            continue
        te = set(toks(r["evname"]))
        if not te:
            continue
        cn = r["cname"]
        cand = set()
        for w in te:
            cand |= pidx.get(w, set())
        for i in cand:
            x = pm[i]
            if x["bad"]:
                continue
            tp = set(toks(x["evt"]))
            es = len(te & tp) / max(1, len(te | tp))
            if es < 0.34:
                continue
            opts = []
            if x["grp"]:
                g = x["grp"]
                if cn.lower() == "draw" and g.lower().startswith("draw"):
                    opts.append((1.0, 0, g))
                else:
                    opts.append((name_match(cn, g), 0, g))
            elif x["outs"][0].lower() != "yes":
                opts += [(name_match(cn, x["outs"][0]), 0, x["outs"][0]), (name_match(cn, x["outs"][1]), 1, x["outs"][1])]
            for sc, side, nm in opts:
                if sc >= 0.86:
                    pairs.append(dict(r, site="poly", other_ev=x["evt"], oq=x["q"], nm=nm, tok=x["tok"][side],
                                      tok_not=x["tok"][1 - side], fee=x["fee"], evsim=round(es, 2), csim=round(sc, 2),
                                      n_other=x["n_in_ev"] if x["grp"] else 2))
        cand = set()
        for w in te:
            cand |= kidx.get(w, set())
        for i in cand:
            x = kms[i]
            tk = set(toks(x["evt"]))
            es = len(te & tk) / max(1, len(te | tk))
            if es < 0.34 or not x["nm"]:
                continue
            ql = x["q"].lower()
            if any(b in ql for b in BAD_Q):
                continue
            sc = 1.0 if (cn.lower() == "draw" and x["nm"].lower() in ("tie", "draw")) else name_match(cn, x["nm"])
            if sc >= 0.86:
                pairs.append(dict(r, site="kal", other_ev=x["evt"], oq=x["q"], nm=x["nm"], kt=x["kt"],
                                  evsim=round(es, 2), csim=round(sc, 2), n_other=x["n_in_ev"]))
    best = {}
    for p in pairs:
        k = (p["venue"], p["cid"], p["site"])
        if k not in best or p["evsim"] + p["csim"] > best[k]["evsim"] + best[k]["csim"]:
            best[k] = p
    seen, out = set(), []
    for p in sorted(best.values(), key=lambda p: -(p["evsim"] + p["csim"])):
        k = (p["venue"], p["mid"], p["site"], p.get("tok") or p.get("kt"))
        if k in seen:
            continue
        seen.add(k)
        out.append(p)
    return out


def snap(write=True, maxpairs=500):
    t0 = time.time()
    rows = exchange_contracts()
    pe = poly_events()
    pm = poly_markets(pe)
    print("poly events", len(pe), "markets", len(pm))
    ke = kalshi_events()
    print("kalshi events", len(ke))
    cp = match_all(rows, pm, ke)
    from collections import Counter
    print("matched pairs", len(cp), Counter((p["venue"], p["site"]) for p in cp).most_common())
    print("by domain", Counter(p["dom"] for p in cp).most_common(20))
    cp = cp[:maxpairs]
    res = price_pairs(cp)
    if write:
        save(f"snap_{int(t0)}.json.gz", {"t": t0, "pairs": res, "n_rows": len(rows)})
    show(res)
    return cp, res


def exchange_books(cp):
    """Current (offers, bids) per exchange contract in the pair list."""
    books = {}
    smk_m = sorted({p["mid"] for p in cp if p["venue"] == "smk"})
    q = smk_quotes(smk_m) if smk_m else {}
    for p in cp:
        if p["venue"] == "smk":
            books[("smk", p["cid"])] = smk_sides(q.get(p["cid"]) or {})
    mb_ev = sorted({p["ev"] for p in cp if p["venue"] == "mb"})
    for c in chunks(mb_ev, 50):
        r = tryget(MB + "/events?" + urllib.parse.urlencode({"ids": ",".join(c), "include-prices": "true",
                                                             "price-depth": 3, "odds-type": "DECIMAL", "per-page": 50}),
                   timeout=40)
        for e in (r.get("events", []) if isinstance(r, dict) else []):
            for m in e.get("markets", []) or []:
                for rn in m.get("runners", []) or []:
                    books[("mb", str(rn.get("id")))] = mb_runner_book(rn)
    return books


def poly_rate(p):
    try:
        f = float(p.get("fee"))
        if f > 1:
            f /= 10000
        if f > 0:
            return f
    except Exception:  # noqa
        pass
    return 0.05 if p["dom"] not in ("politics", "current_affairs") else 0.04


def price_pairs(cp, sizes=(10, 50)):
    t = time.time()
    ebooks = exchange_books(cp)

    def other(p):
        if p["site"] == "poly":
            return {"yes": poly_book(p["tok"]), "no": poly_book(p["tok_not"])}
        return {"k": kalshi_book(p["kt"])}
    with ThreadPoolExecutor(12) as ex:
        books = list(ex.map(other, cp))
    out = []
    for p, b in zip(cp, books):
        ofs, bds = ebooks.get((p["venue"], p["cid"]), ([], []))
        r = {k: p.get(k) for k in ("venue", "site", "ev", "evname", "dom", "mname", "cid", "cname", "other_ev", "oq",
                                   "nm", "tok", "kt", "start", "n_out", "n_other")}
        r["t"] = t
        r["x_ask"] = ofs[0][0] if ofs else None
        r["x_bid"] = bds[0][0] if bds else None
        r["x_ask_q"] = ofs[0][1] if ofs else 0
        r["x_bid_q"] = bds[0][1] if bds else 0
        if p["site"] == "poly":
            yb, nb = b.get("yes"), b.get("no")
            if not yb or not nb:
                out.append(r)
                continue
            rate = poly_rate(p)
            fee = lambda pp, rate=rate: poly_fee(pp, rate)  # noqa
            o_yes, o_no = yb["asks"], nb["asks"]
            r["o_bid"] = yb["bids"][0][0] if yb["bids"] else None
        else:
            k = b["k"]
            fee = kal_fee
            o_yes, o_no = k["yes_asks"], k["no_asks"]
            r["o_bid"] = k["yes_bids"][0][0] if k["yes_bids"] else None
        r["o_ask"] = o_yes[0][0] if o_yes else None
        r["o_ask_q"] = o_yes[0][1] if o_yes else 0
        xf = ex_fee(p["venue"])
        lay_as_not = [(round(1 - pp, 4), qq) for pp, qq in bds]  # selling Yes at bid b = buying Not at 1-b
        for d in sizes:
            # A: buy Yes on the exchange + buy No on the other site.  B: buy Yes on the other site + lay on the exchange.
            xa = walk_cost(ofs, d, xf)
            on = walk_cost(o_no, d, fee)
            r[f"A{d}"] = round(xa + on, 4) if xa and on else None
            oy = walk_cost(o_yes, d, fee)
            xl = walk_cost(lay_as_not, d, xf)
            r[f"B{d}"] = round(oy + xl, 4) if oy and xl else None
        out.append(r)
    return out


def mids(r):
    if not (r.get("x_ask") and r.get("x_bid") and r.get("o_ask") and r.get("o_bid")):
        return None
    if r["x_ask"] - r["x_bid"] > 0.06 or r["o_ask"] - r["o_bid"] > 0.06:
        return None
    return (r["x_ask"] + r["x_bid"]) / 2, (r["o_ask"] + r["o_bid"]) / 2


def best_cost(r, d=10):
    return min([x for x in [r.get(f"A{d}"), r.get(f"B{d}")] if x] or [9])


def show(res, top=30):
    ok = [r for r in res if r.get("x_ask") and r.get("o_ask")]
    print(f"priced pairs {len(ok)} of {len(res)}")
    for r in ok:
        m = mids(r)
        r["mid_gap"] = round(m[0] - m[1], 4) if m else None
    ok.sort(key=best_cost)
    print("cheapest $10 cross pairs (cost of a sure $1; under 1.00 = profit if both sites settle the same way):")
    for r in ok[:top]:
        print(f"  {r['venue']}-{r['site']} {str(r['dom'])[:9]:9} A10={r.get('A10')} B10={r.get('B10')} A50={r.get('A50')} "
              f"B50={r.get('B50')} x {r['x_ask']}/{r['x_bid']} o {r['o_ask']}/{r.get('o_bid')} | {r['evname'][:34]} > "
              f"{r['mname'][:18]} > {r['cname'][:22]} ~ {r['nm'][:22]} [{r['oq'][:55]}]")
    print(f"pairs under $1.00 at $10: {sum(1 for r in ok if best_cost(r) < 1)}; under $0.99: "
          f"{sum(1 for r in ok if best_cost(r) < .99)}; at $50 under $1.00: {sum(1 for r in ok if best_cost(r, 50) < 1)}")
    g = [r for r in ok if r.get("mid_gap") is not None]
    g.sort(key=lambda r: -abs(r["mid_gap"]))
    print("biggest middle gaps (exchange middle - other middle), tight books only:")
    for r in g[:15]:
        print(f"  {r['mid_gap']:+.3f} {r['venue']}-{r['site']} {r['evname'][:34]} > {r['cname'][:22]} ~ {r['nm'][:22]} [{r['oq'][:50]}]")
    ag = sorted(abs(r["mid_gap"]) for r in g)
    if ag:
        print("tight pairs", len(ag), "median gap", ag[len(ag) // 2], "gap>=2c", sum(a >= .02 for a in ag),
              "gap>=3c", sum(a >= .03 for a in ag), "gap>=5c", sum(a >= .05 for a in ag))
    sq = sorted(r["x_ask_q"] for r in ok if r.get("x_ask_q"))
    if sq:
        print("exchange best-offer size (contracts, GBP payout) median", round(sq[len(sq) // 2], 1))


def watch(minutes=60, every=60):
    cp, res = snap(write=True)
    keep = {(r["venue"], r["cid"], r["site"]) for r in res if mids(r)}
    cp = [p for p in cp if (p["venue"], p["cid"], p["site"]) in keep][:220]
    print("watching", len(cp), "pairs with tight books on both sides", flush=True)
    series = []
    tend = time.time() + minutes * 60
    while time.time() < tend:
        t = time.time()
        rs = price_pairs(cp, sizes=(10,))
        series.append([{k: r.get(k) for k in ("venue", "cid", "site", "t", "x_ask", "x_bid", "o_ask", "o_bid", "A10", "B10")}
                       for r in rs])
        n_arb = sum(1 for r in rs if best_cost(r) < 1)
        print(time.strftime("%H:%M:%S"), "priced", len(rs), "cross <1.00 at $10:", n_arb,
              f"({time.time() - t:.0f}s)", flush=True)
        time.sleep(max(1, every - (time.time() - t)))
    save(f"watch_{int(tend)}.json.gz", {"pairs": cp, "series": series})
    analyse_watch(cp, series)
    print("=== DONE ===")


def analyse_watch(cp, series):
    from collections import defaultdict
    ts = defaultdict(list)
    names = {(p["venue"], p["cid"], p["site"]): f"{p['evname'][:30]} > {p['cname'][:20]}" for p in cp}
    for sx in series:
        for r in sx:
            m = mids(r)
            if m:
                ts[(r["venue"], r["cid"], r["site"])].append((r["t"], m[0], m[1], r.get("A10"), r.get("B10")))
    # who moves first: for each 2c+ step of one side's middle, did the other side follow within the next 1-5 snapshots
    lead = {"exch_first": 0, "other_first": 0, "same_step": 0, "never_followed": 0}
    examples = []
    for k, xs in ts.items():
        for i in range(1, len(xs)):
            dx = xs[i][1] - xs[i - 1][1]
            do = xs[i][2] - xs[i - 1][2]
            for a, b, lab in ((dx, do, "exch"), (do, dx, "other")):
                if abs(a) < .02:
                    continue
                if abs(b) >= abs(a) / 2 and a * b > 0:
                    if lab == "exch":
                        lead["same_step"] += 1
                    continue
                col = 2 if lab == "exch" else 1
                fol = None
                for j in range(i + 1, min(len(xs), i + 6)):
                    if (xs[j][col] - xs[i][col]) * a > 0 and abs(xs[j][col] - xs[i][col]) >= abs(a) / 2:
                        fol = j - i
                        break
                if fol:
                    lead[lab + "_first"] += 1
                    examples.append((lab, fol, names.get(k), round(a, 3)))
                else:
                    lead["never_followed"] += 1
    print("2c+ middle moves:", lead)
    for e in examples[:12]:
        print("   ", e)
    runs = []
    for k, xs in ts.items():
        run = 0
        for x in xs:
            if (x[3] or 9) < 1 or (x[4] or 9) < 1:
                run += 1
            elif run:
                runs.append((run, names.get(k)))
                run = 0
        if run:
            runs.append((run, names.get(k)))
    print("cross pairs under $1.00 at $10: streaks", len(runs), "longest", sorted(runs, key=lambda x: -x[0])[:10])
    print("pairs tracked", len(ts), "snapshots", len(series))


# ---------------------------------------------------------------- Betfair Exchange closing odds (football-data.co.uk)
FD_LEAGUES = ["E0", "E1", "E2", "E3", "EC", "SC0", "SC1", "SC2", "D1", "D2", "I1", "I2", "SP1", "SP2", "F1", "F2",
              "N1", "B1", "P1", "T1", "G1"]
FD_SEASONS = ["2021", "2122", "2223", "2324", "2425", "2526"]


def fd_load():
    import csv, io
    os.makedirs(CACHE + "/fd", exist_ok=True)
    rows = []
    for s in FD_SEASONS:
        for lg in FD_LEAGUES:
            fn = f"{CACHE}/fd/{s}_{lg}.csv"
            if not os.path.exists(fn) or s == "2526":
                try:
                    b = get(f"https://www.football-data.co.uk/mmz4281/{s}/{lg}.csv", raw=True, timeout=30)
                    open(fn, "wb").write(b)
                except Exception as e:  # noqa
                    print("fd miss", s, lg, str(e)[:60])
                    continue
            txt = open(fn, "rb").read().decode("latin-1")
            for r in csv.DictReader(io.StringIO(txt)):
                r["_lg"], r["_s"] = lg, s
                rows.append(r)
    return rows


def fnum(x):
    try:
        v = float(x)
        return v if v > 1 else None
    except Exception:  # noqa
        return None


def bfe(comm_list=(0.02, 0.05)):
    """Back every side at Betfair Exchange closing odds (BFEC*, else BFE*), by price band; commission on wins.
    Also the same at Pinnacle closing odds (PSC*) for a yardstick. Tells us whether a favourite / long-shot lean
    survives the exchange's own commission."""
    rows = fd_load()
    print("football-data rows", len(rows))
    have = [r for r in rows if fnum(r.get("BFECH")) or fnum(r.get("BFEH"))]
    print("rows with Betfair exchange odds", len(have), "closing", sum(1 for r in rows if fnum(r.get("BFECH"))))
    bands = [(0, .1), (.1, .2), (.2, .3), (.3, .4), (.4, .5), (.5, .6), (.6, .7), (.7, .8), (.8, 1.01)]
    from collections import defaultdict
    agg = defaultdict(lambda: [0, 0.0, 0.0, 0.0])  # n, staked, return@2%, return@5%
    lay = defaultdict(lambda: [0, 0.0, 0.0])
    bets_by = defaultdict(list)
    for r in have:
        res = r.get("FTR")
        if res not in ("H", "D", "A"):
            continue
        for side in "HDA":
            o = fnum(r.get("BFEC" + side)) or fnum(r.get("BFE" + side))
            if not o:
                continue
            p = 1 / o
            band = next((b for b in bands if b[0] <= p < b[1]), None)
            key = (side, band)
            won = res == side
            a = agg[key]
            a[0] += 1
            a[1] += 1
            a[2] += (1 + (o - 1) * (1 - comm_list[0])) if won else 0
            a[3] += (1 + (o - 1) * (1 - comm_list[1])) if won else 0
            # laying at the same odds (best case: no spread) with $1 liability... per $1 risked
            stake_lay = 1 / (o - 1)  # backer stake you accept for $1 liability
            l = lay[key]
            l[0] += 1
            l[1] += 1
            l[2] += (1 + stake_lay * (1 - comm_list[0])) if not won else 0
            bets_by[key].append({"ev": f"{r.get('Date')}_{r.get('HomeTeam')}", "t": 0, "cost": 25.0,
                                 "pay": 25.0 * (1 + (o - 1) * (1 - comm_list[0])) if won else 0.0, "day": r.get("Date")})
    print("BACK at Betfair closing odds: per $100 staked (2% comm / 5% comm). Lay = lay at the SAME odds, per $100 risked (2%),"
          " which flatters the lay side by the 1-tick spread")
    print(" side band          n     back@2%   back@5%   lay@2%(no spread)")
    for side in "HDA":
        for band in bands:
            a = agg[(side, band)]
            if a[0] < 50:
                continue
            l = lay[(side, band)]
            print(f"  {side}  {band[0]:.1f}-{band[1]:.1f}  {a[0]:6d}  {100 * (a[2] / a[1] - 1):+8.2f}  {100 * (a[3] / a[1] - 1):+8.2f}"
                  f"  {100 * (l[2] / l[1] - 1):+8.2f}")
    # by season: is any band steady?
    print("by season, backing draws 20-30c / away 10-20c at 2% (per $100):")
    for s in FD_SEASONS:
        for side, band in (("D", (.2, .3)), ("A", (.1, .2)), ("H", (.7, .8))):
            n, st, rt = 0, 0, 0
            for r in have:
                if r["_s"] != s or r.get("FTR") not in ("H", "D", "A"):
                    continue
                o = fnum(r.get("BFEC" + side)) or fnum(r.get("BFE" + side))
                if not o or not (band[0] <= 1 / o < band[1]):
                    continue
                n += 1
                st += 1
                rt += (1 + (o - 1) * .98) if r["FTR"] == side else 0
            if n:
                print(f"   {s} {side} {band}: n={n} {100 * (rt / st - 1):+.2f}")
    # Betfair vs Pinnacle closing: which forecasts better (log loss) where both exist
    ll_b, ll_p, n = 0, 0, 0
    for r in have:
        res = r.get("FTR")
        ob = [fnum(r.get("BFEC" + x)) or fnum(r.get("BFE" + x)) for x in "HDA"]
        op = [fnum(r.get("PSC" + x)) or fnum(r.get("PS" + x)) for x in "HDA"]
        if res not in ("H", "D", "A") or not all(ob) or not all(op):
            continue
        pb = [1 / o for o in ob]
        pp = [1 / o for o in op]
        sb, sp = sum(pb), sum(pp)
        i = "HDA".index(res)
        ll_b -= math.log(pb[i] / sb)
        ll_p -= math.log(pp[i] / sp)
        n += 1
    if n:
        print(f"log loss per game, Betfair closing {ll_b / n:.4f} vs Pinnacle closing {ll_p / n:.4f} on {n} games "
              f"(lower = better forecast)")
    # overround of Betfair back prices (sum of 1/odds): how much over $1 a full set costs
    ovs = sorted(sum(1 / (fnum(r.get("BFEC" + x)) or fnum(r.get("BFE" + x))) for x in "HDA") for r in have
                 if all(fnum(r.get("BFEC" + x)) or fnum(r.get("BFE" + x)) for x in "HDA"))
    if ovs:
        print("Betfair back-price set cost (sum 1/odds) median", round(ovs[len(ovs) // 2], 4), "share under 1.00",
              round(sum(o < 1 for o in ovs) / len(ovs), 3))
    try:
        sys.path.insert(0, ".")
        import exam
        best = max(((k, v) for k, v in agg.items() if v[0] >= 300), key=lambda kv: kv[1][2] / kv[1][1])
        k = best[0]
        print("best band by looking:", k, "->", "exam:")
        exam.score(bets_by[k], f"exch: back {k[0]} at Betfair close {k[1][0]:.1f}-{k[1][1]:.1f} (2% comm)", tries=27,
                   src="outside/exch.py bfe", note="found by looking; Betfair closing odds from football-data.co.uk")
    except Exception as e:  # noqa
        print("exam skipped", e)
    print("=== DONE ===")


def report():
    snaps = load_all("snap_")
    print("snapshots", len(snaps))
    for s in snaps[-3:]:
        show(s["pairs"], top=10)
    for w in load_all("watch_"):
        analyse_watch(w["pairs"], w["series"])
    print("=== DONE ===")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "explore"
    a = sys.argv[2:]
    if cmd == "explore":
        explore()
    elif cmd == "snap":
        snap()
        print("=== DONE ===")
    elif cmd == "watch":
        watch(int(a[0]) if a else 60, int(a[1]) if len(a) > 1 else 60)
    elif cmd == "report":
        report()
    elif cmd == "bfe":
        bfe()
