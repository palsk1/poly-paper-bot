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
               "ice_hockey", "baseball", "esports", "entertainment", "golf", "boxing", "mma", "cricket",
               "rugby_union", "darts", "snooker", "motorsports", "horse_racing"]


def smk_events(dom, maxn=600):
    out, off = [], 0
    while len(out) < maxn:
        q = {"type_domain": dom, "state": "upcoming", "limit": 200, "offset": off, "sort": "id"}
        r = tryget(SMK + "/events/?" + urllib.parse.urlencode(q))
        evs = r.get("events", []) if isinstance(r, dict) else []
        out += evs
        if len(evs) < 200:
            break
        off += 200
    # live ones too
    r = tryget(SMK + "/events/?" + urllib.parse.urlencode({"type_domain": dom, "state": "live", "limit": 200}))
    out += r.get("events", []) if isinstance(r, dict) else []
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
    return q


def smk_volumes(mids):
    v = {}
    for c in chunks(mids, 50):
        r = tryget(SMK + "/markets/" + ",".join(map(str, c)) + "/volumes/")
        for x in (r.get("volumes", []) if isinstance(r, dict) else []):
            v[str(x.get("market_id"))] = x
    return v


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
SMK_COMM = 0.02   # Smarkets standard commission on net winnings in a market (see report for the source)
POLY_FEE_SPORT = 0.05


def poly_fee(p, rate):
    return rate * p * (1 - p)  # per share


def kal_fee(p):
    return 0.07 * p * (1 - p)  # per contract (ignores the round-up to the cent; fine at $10-50)


def smk_back_cost(ofs, dollars):
    """Smarkets 'back' at offers. Smarkets prices are probabilities in basis points (price/10000).
    Return (avg price per $1 payout incl. commission on the win, payout units bought) for `dollars`."""
    spent, units = 0.0, 0.0
    for p, q in ofs:  # q = backer stake available in GBP
        if spent >= dollars:
            break
        take = min(q, dollars - spent)
        spent += take
        units += take / p
    if spent < dollars * 0.999:
        return None
    # commission 2% on net win: payout units -> net = units - spent; commission on that
    net_win = units - spent
    payout = spent + net_win * (1 - SMK_COMM)
    return spent / payout  # effective price per $1 paid out


def walk_cost(asks, dollars, fee_fn):
    spent, sh = 0.0, 0.0
    for p, q in asks:
        if spent >= dollars or p <= 0 or p >= 1:
            continue
        cap = q * p
        take = min(cap, dollars - spent)
        s = take / p
        spent += take + s * fee_fn(p)
        sh += s
    if sh <= 0 or spent < dollars * 0.999:
        return None
    return spent / sh


def smk_sides(qt):
    """Smarkets quote: {'bids':[{'price':bp,'quantity':q}], 'offers':[...]}. Back = take offers; lay = take bids
    (selling the contract = buying 'not' at 1 - bid). quantity in units of 1/10000 GBP of backer stake (checked)."""
    ofs = sorted([(x["price"] / 10000, x["quantity"] / 10000) for x in qt.get("offers", []) if x.get("price")])
    bds = sorted([(x["price"] / 10000, x["quantity"] / 10000) for x in qt.get("bids", []) if x.get("price")], reverse=True)
    return ofs, bds


# ---------------------------------------------------------------- snap
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


def smk_universe():
    with ThreadPoolExecutor(8) as ex:
        res = list(ex.map(smk_events, SMK_DOMAINS))
    evs = {}
    for dom, lst in zip(SMK_DOMAINS, res):
        for e in lst:
            e["_dom"] = dom
            evs[str(e["id"])] = e
    print("smarkets events", len(evs), {d: len(l) for d, l in zip(SMK_DOMAINS, res)})
    mk = smk_markets(list(evs))
    print("smarkets markets", len(mk))
    mids = [str(m["id"]) for m in mk]
    ct = smk_contracts(mids)
    print("smarkets contracts", len(ct))
    return evs, mk, ct


def outcome_names_poly(e):
    """(question, outcome name, yes token, no token, fee rate) for each Polymarket market in an event."""
    out = []
    for m in e.get("markets", []) or []:
        try:
            tids = json.loads(m.get("clobTokenIds") or "[]")
            outs = json.loads(m.get("outcomes") or "[]")
        except Exception:  # noqa
            continue
        if len(tids) != 2 or m.get("closed"):
            continue
        out.append({"q": m.get("question") or "", "git": m.get("groupItemTitle") or "", "outs": outs,
                    "tok": tids, "slug": m.get("slug"), "fee": m.get("feeRate") or m.get("takerBaseFee"),
                    "end": m.get("endDate"), "liq": float(m.get("liquidityNum") or 0)})
    return out


def snap(write=True, maxpairs=400):
    t0 = time.time()
    evs, mk, ct = smk_universe()
    pe = poly_events()
    print("poly events", len(pe))
    ke = kalshi_events()
    print("kalshi events", len(ke))
    # Smarkets: contracts grouped per market
    by_m = {}
    for c in ct:
        by_m.setdefault(str(c["market_id"]), []).append(c)
    mk_by_id = {str(m["id"]): m for m in mk}
    # candidate matching: smarkets event name vs poly event title, and vs kalshi event title
    pidx = [(e, toks(e.get("title"))) for e in pe]
    kidx = [(e, toks((e.get("title") or "") + " " + (e.get("sub_title") or ""))) for e in ke]
    pairs = []
    for eid, e in evs.items():
        en = e.get("name") or ""
        te = set(toks(en))
        if len(te) < 1:
            continue
        best = []
        for pev, tp in pidx:
            if not tp:
                continue
            s = len(te & set(tp)) / len(te | set(tp))
            if s >= 0.5:
                best.append((s, "poly", pev))
        for kev, tk in kidx:
            if not tk:
                continue
            s = len(te & set(tk)) / len(te | set(tk))
            if s >= 0.5:
                best.append((s, "kal", kev))
        best.sort(key=lambda x: -x[0])
        for s, site, other in best[:3]:
            pairs.append((eid, s, site, other))
    print("event pairs (name match >= 0.5)", len(pairs))
    # contract-level match: smarkets contract name vs poly groupItemTitle/outcome vs kalshi yes_sub_title
    cpairs = []
    for eid, s, site, other in pairs:
        e = evs[eid]
        smk_mk = [m for m in mk if str(m.get("event_id")) == eid]
        for m in smk_mk:
            cs = by_m.get(str(m["id"]), [])
            if site == "poly":
                pm = outcome_names_poly(other)
                for c in cs:
                    cn = c.get("name") or ""
                    for x in pm:
                        # multi-outcome: groupItemTitle is the outcome; binary team markets: outcomes names
                        cand = []
                        if x["git"]:
                            cand.append((x["git"], 0))
                        elif len(pm) == 1:
                            cand += [(x["outs"][0], 0), (x["outs"][1], 1)]
                        for nm, side in cand:
                            sc = difflib.SequenceMatcher(None, cn.lower(), nm.lower()).ratio()
                            if sc >= 0.86 or (cn.lower() == nm.lower()):
                                cpairs.append({"ev": e.get("name"), "dom": e.get("_dom"), "smk_m": str(m["id"]),
                                               "smk_mname": m.get("name"), "smk_c": str(c["id"]), "cname": cn,
                                               "site": "poly", "other_ev": other.get("title"), "oq": x["q"],
                                               "tok": x["tok"][side], "tok_not": x["tok"][1 - side],
                                               "fee": x["fee"], "nm": nm, "evsim": s, "csim": sc,
                                               "n_out_smk": len(cs), "n_out_other": len(pm) if x["git"] else 2})
            else:
                kms = other.get("markets") or []
                for c in cs:
                    cn = c.get("name") or ""
                    for km in kms:
                        nm = km.get("yes_sub_title") or km.get("subtitle") or ""
                        if not nm:
                            continue
                        sc = difflib.SequenceMatcher(None, cn.lower(), nm.lower()).ratio()
                        if sc >= 0.86:
                            cpairs.append({"ev": e.get("name"), "dom": e.get("_dom"), "smk_m": str(m["id"]),
                                           "smk_mname": m.get("name"), "smk_c": str(c["id"]), "cname": cn,
                                           "site": "kal", "other_ev": other.get("title"), "oq": km.get("title"),
                                           "kt": km.get("ticker"), "nm": nm, "evsim": s, "csim": sc,
                                           "n_out_smk": len(cs), "n_out_other": len(kms)})
    # one per (smk contract, site) best
    seen = {}
    for p in cpairs:
        k = (p["smk_c"], p["site"])
        if k not in seen or (p["evsim"] + p["csim"]) > (seen[k]["evsim"] + seen[k]["csim"]):
            seen[k] = p
    cpairs = list(seen.values())
    print("contract pairs", len(cpairs), "poly", sum(p["site"] == "poly" for p in cpairs),
          "kal", sum(p["site"] == "kal" for p in cpairs))
    cpairs.sort(key=lambda p: -(p["evsim"] + p["csim"]))
    cpairs = cpairs[:maxpairs]
    res = price_pairs(cpairs)
    if write:
        save(f"snap_{int(t0)}.json.gz", {"t": t0, "pairs": res, "n_smk_ev": len(evs), "n_smk_mk": len(mk),
                                         "dom_counts": {}})
    show(res)
    return cpairs, res


def price_pairs(cpairs, sizes=(10, 50)):
    mids = sorted({p["smk_m"] for p in cpairs})
    q = smk_quotes(mids)
    vol = smk_volumes(mids)
    t = time.time()

    def other(p):
        if p["site"] == "poly":
            return {"yes": poly_book(p["tok"]), "no": poly_book(p["tok_not"])}
        return {"k": kalshi_book(p["kt"])}
    with ThreadPoolExecutor(12) as ex:
        books = list(ex.map(other, cpairs))
    out = []
    for p, b in zip(cpairs, books):
        qt = q.get(p["smk_c"]) or {}
        ofs, bds = smk_sides(qt)
        r = dict(p)
        r["t"] = t
        r["smk_back"] = ofs[0][0] if ofs else None
        r["smk_lay"] = bds[0][0] if bds else None
        r["smk_back_depth"] = sum(qq for _, qq in ofs[:3])
        r["smk_vol"] = (vol.get(p["smk_m"]) or {}).get("volume")
        if p["site"] == "poly":
            yb, nb = b.get("yes"), b.get("no")
            if not yb or not nb:
                continue
            rate = POLY_FEE_SPORT if p["dom"] not in ("politics", "current_affairs") else 0.04
            try:
                rate = float(p.get("fee")) if p.get("fee") not in (None, "", "0") else rate
                if rate > 1:
                    rate = rate / 10000
            except Exception:  # noqa
                pass
            ya, na = yb["asks"], nb["asks"]
            r["o_ask"] = ya[0][0] if ya else None
            r["o_bid"] = yb["bids"][0][0] if yb["bids"] else None
            fee = lambda pp, rate=rate: poly_fee(pp, rate)  # noqa
            o_yes, o_no = ya, na
        else:
            k = b["k"]
            r["o_ask"] = k["yes_asks"][0][0] if k["yes_asks"] else None
            r["o_bid"] = k["yes_bids"][0][0] if k["yes_bids"] else None
            fee = kal_fee
            o_yes, o_no = k["yes_asks"], k["no_asks"]
        # two cross trades: (A) back on Smarkets + buy NO on other; (B) buy YES on other + lay on Smarkets
        for d in sizes:
            sb = smk_back_cost(ofs, d)
            on = walk_cost(o_no, d, fee)
            r[f"A{d}"] = round(sb + on, 4) if sb and on else None  # cost of $1 sure payout (if same event!)
            oy = walk_cost(o_yes, d, fee)
            # lay on Smarkets at bid b = buying 'not' at (1-b); liability side; commission on net win
            lay = [(round(1 - pp, 4), qq * pp / (1 - pp) if pp < 1 else 0) for pp, qq in bds]  # stake units
            sl = smk_back_cost(lay, d) if lay else None
            r[f"B{d}"] = round(oy + sl, 4) if oy and sl else None
        out.append(r)
    return out


def show(res, top=25):
    ok = [r for r in res if r.get("smk_back") and r.get("o_ask")]
    print(f"priced pairs {len(ok)}")
    for r in ok:
        sm = (r["smk_back"] + (r["smk_lay"] or r["smk_back"])) / 2
        om = (r["o_ask"] + (r["o_bid"] or r["o_ask"])) / 2
        r["mid_gap"] = round(sm - om, 4)
    ok.sort(key=lambda r: min([x for x in [r.get("A10"), r.get("B10")] if x] or [9]))
    print("best $10 cross costs (under 1.00 = money if both pay on the same result):")
    for r in ok[:top]:
        print(f"  {r['site']:4} {r['dom'][:10]:10} A10={r.get('A10')} B10={r.get('B10')} A50={r.get('A50')} "
              f"B50={r.get('B50')} smk {r['smk_back']}/{r['smk_lay']} oth {r['o_ask']}/{r['o_bid']} | "
              f"{r['ev'][:40]} :: {r['cname'][:25]} ~ {r['nm'][:25]} [{r['oq'][:50]}]")
    gaps = sorted(ok, key=lambda r: -abs(r["mid_gap"]))
    print("mid gaps (smarkets mid - other mid), biggest:")
    for r in gaps[:15]:
        print(f"  {r['mid_gap']:+.3f} {r['site']} {r['ev'][:40]} :: {r['cname'][:25]} [{r['oq'][:50]}]")
    ag = [abs(r["mid_gap"]) for r in ok]
    if ag:
        ag.sort()
        print("median |mid gap|", ag[len(ag) // 2], "n", len(ag),
              "share >=3c", round(sum(a >= .03 for a in ag) / len(ag), 3))


def watch(minutes=60, every=60):
    cpairs, res = snap(write=True)
    # keep pairs that priced
    keep_ids = {(r["smk_c"], r["site"]) for r in res if r.get("smk_back") and r.get("o_ask")}
    cp = [p for p in cpairs if (p["smk_c"], p["site"]) in keep_ids][:250]
    print("watching", len(cp), "pairs")
    series = []
    tend = time.time() + minutes * 60
    while time.time() < tend:
        t = time.time()
        rs = price_pairs(cp, sizes=(10,))
        series.append([{k: r.get(k) for k in ("smk_c", "site", "t", "smk_back", "smk_lay", "o_ask", "o_bid", "A10", "B10")}
                       for r in rs])
        n_arb = sum(1 for r in rs if (r.get("A10") or 9) < 1 or (r.get("B10") or 9) < 1)
        print(time.strftime("%H:%M:%S"), "priced", len(rs), "cross <1.00 at $10:", n_arb, flush=True)
        time.sleep(max(1, every - (time.time() - t)))
    save(f"watch_{int(tend)}.json.gz", {"pairs": cp, "series": series})
    analyse_watch(cp, series)
    print("=== DONE ===")


def analyse_watch(cp, series):
    # per pair: time series of mids; lead-lag via which side moved first on 2c+ moves
    from collections import defaultdict
    ts = defaultdict(list)
    for snapx in series:
        for r in snapx:
            if r.get("smk_back") and r.get("o_ask") and r.get("smk_lay") and r.get("o_bid"):
                sm = (r["smk_back"] + r["smk_lay"]) / 2
                om = (r["o_ask"] + r["o_bid"]) / 2
                ts[(r["smk_c"], r["site"])].append((r["t"], sm, om, r.get("A10"), r.get("B10")))
    lead = {"smk_first": 0, "other_first": 0, "same_step": 0}
    arb_life = []
    for k, xs in ts.items():
        for i in range(1, len(xs)):
            ds = xs[i][1] - xs[i - 1][1]
            do = xs[i][2] - xs[i - 1][2]
            if abs(ds) >= .02 or abs(do) >= .02:
                # who moved; next step did the other follow?
                if abs(ds) >= .02 and abs(do) >= .02 and ds * do > 0:
                    lead["same_step"] += 1
                elif abs(do) >= .02 and i + 1 < len(xs):
                    if (xs[i + 1][1] - xs[i][1]) * do > 0.01 ** 2:
                        lead["other_first"] += 1
                elif abs(ds) >= .02 and i + 1 < len(xs):
                    if (xs[i + 1][2] - xs[i][2]) * ds > 0.01 ** 2:
                        lead["smk_first"] += 1
        run = 0
        for x in xs:
            if (x[3] or 9) < 1 or (x[4] or 9) < 1:
                run += 1
            elif run:
                arb_life.append(run)
                run = 0
        if run:
            arb_life.append(run)
    print("2c+ moves, who moved first (and the other followed next step):", lead)
    print("cross-arb runs (snapshots in a row under $1.00 at $10):", sorted(arb_life)[-20:], "count", len(arb_life))


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
