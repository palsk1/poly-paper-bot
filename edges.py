#!/usr/bin/env python3
"""Research probes for new kinds of edge (no pushes, no state changes). Run through the probe workflow:
  edges_shapes   raw API shapes for rewards / negRisk / holding-reward fields
  edges_rewards  liquidity-reward farming: what $100 of resting quotes would earn per day, market by market
  edges_negrisk  negRisk conversion: sell a whole outcome set right now for more than $1 (no waiting for the end)
  edges_holding  which markets pay a holding reward, and what the boring side there pays on top
  edges_all      everything above
"""
import sys
import time
from collections import Counter

import bot
from bot import CLOB, DATA, GAMMA, envelope_rows, fnum, http_json, jlist


def get(url, params=None):
    try:
        return http_json(url, params, retries=2)
    except Exception as e:
        return {"__error__": str(e)}


def short(o, n=1500):
    import json
    return json.dumps(o, default=str)[:n]


# ------------------------------------------------------------ shapes

def shapes():
    for url, p in [(f"{CLOB}/sampling-markets", None), (f"{CLOB}/rewards/markets/current", None),
                   (f"{CLOB}/rewards/markets", None), (f"{CLOB}/sampling-simplified-markets", None)]:
        r = get(url, p)
        print("==", url, "keys:", sorted(r.keys()) if isinstance(r, dict) else type(r).__name__)
        rows = envelope_rows(r, "data", "markets")
        if rows:
            print("   n:", len(rows), "next:", r.get("next_cursor") if isinstance(r, dict) else None)
            print("   sample:", short(rows[0], 2500))
        else:
            print("  ", short(r, 600))
    r = get(f"{GAMMA}/markets/keyset", {"closed": "false", "limit": 50, "order": "volume24hr", "ascending": "false"})
    ms = envelope_rows(r, "markets", "data")
    keys = Counter(k for m in ms for k in m.keys())
    print("== gamma market keys:", sorted(keys))
    for m in ms[:50]:
        rk = {k: v for k, v in m.items() if any(w in k.lower() for w in ("reward", "hold", "incent", "rebate", "fee", "neg"))}
        if rk:
            print("   ", m.get("slug"), short(rk, 700))
            break
    hold = [m for m in ms if any("hold" in k.lower() and m[k] for k in m)]
    print("   markets with a truthy 'hold*' field:", len(hold))
    r = get(f"{GAMMA}/events/keyset", {"closed": "false", "limit": 20})
    evs = envelope_rows(r, "events", "data")
    print("== gamma event keys:", sorted({k for e in evs for k in e.keys()}))
    # are the YES and NO books one mirrored book, or two separate books?
    for m in ms[:3]:
        toks = bot.market_tokens(m)
        if len(toks) == 2:
            a, b = bot.book(toks[0]), bot.book(toks[1])
            if a and b:
                print("== book mirror check", m.get("slug"))
                print("   YES bids", a["bids"][:3], "asks", a["asks"][:3])
                print("   NO  bids", b["bids"][:3], "asks", b["asks"][:3])


# ------------------------------------------------------------ liquidity rewards

def reward_markets(max_pages=60):
    out, cur = [], ""
    for _ in range(max_pages):
        r = get(f"{CLOB}/sampling-markets", {"next_cursor": cur} if cur else None)
        rows = envelope_rows(r, "data", "markets")
        for m in rows:
            rw = m.get("rewards") or {}
            rate = sum(fnum(x.get("rewards_daily_rate")) for x in (rw.get("rates") or []) if isinstance(x, dict))
            if rate <= 0 or not m.get("accepting_orders", True) or m.get("closed"):
                continue
            toks = [t for t in (m.get("tokens") or []) if isinstance(t, dict)]
            if len(toks) != 2:
                continue
            out.append({"cid": m.get("condition_id"), "q": m.get("question"), "slug": m.get("market_slug"),
                        "rate": rate, "min_size": fnum(rw.get("min_size"), 0), "max_spread": fnum(rw.get("max_spread"), 0),
                        "yes": str(toks[0].get("token_id")), "no": str(toks[1].get("token_id")),
                        "end": m.get("end_date_iso"), "neg_risk": m.get("neg_risk")})
        cur = r.get("next_cursor") if isinstance(r, dict) else None
        if not rows or not cur or cur == "LTE=":
            break
    return out


def score(v, s):
    """Polymarket's quadratic reward score per share for an order s cents from the midpoint, max spread v cents."""
    return ((v - s) / v) ** 2 if 0 <= s < v else 0.0


def reward_estimate(rm, bk, stake=100.0, mirrored=True, nob=None):
    """Our estimated $ per day for `stake` dollars of two-sided resting quotes.
    Competitors' score comes from the public book; we assume they are as two-sided as possible (pessimistic)."""
    v = rm["max_spread"]
    ms = max(rm["min_size"], 1)
    bids = [(p, s) for p, s in bk["bids"] if s >= ms] or bk["bids"]
    asks = [(p, s) for p, s in bk["asks"] if s >= ms] or bk["asks"]
    if not bids or not asks or v <= 0:
        return None
    mid = (bids[0][0] + asks[0][0]) / 2
    qb = sum(score(v, (mid - p) * 100) * s for p, s in bk["bids"])
    qa = sum(score(v, (p - mid) * 100) * s for p, s in bk["asks"])
    if not mirrored and nob:  # NO bids act like YES asks, NO asks like YES bids
        qa += sum(score(v, ((1 - p) - mid) * 100) * s for p, s in nob["bids"])
        qb += sum(score(v, (mid - (1 - p)) * 100) * s for p, s in nob["asks"])
    two_sided_ok = 0.10 <= mid <= 0.90
    comp = min(qb, qa) + (abs(qb - qa) / 3 if two_sided_ok else 0)
    # we sit at the best bid/ask (joining the queue, not improving it), or at half the max spread if those are farther
    db = min((mid - bids[0][0]) * 100, v / 2) if (mid - bids[0][0]) * 100 < v else v / 2
    da = min((asks[0][0] - mid) * 100, v / 2) if (asks[0][0] - mid) * 100 < v else v / 2
    top = (mid - bids[0][0]) * 100 >= v or (asks[0][0] - mid) * 100 >= v  # we would be the best price (gets hit first)
    shares = max(ms, stake)  # YES bid + NO bid at mid +- d cost about $1 a share pair
    ours = min(score(v, db), score(v, da)) * shares
    if ours <= 0:
        return None
    share = ours / (ours + comp)
    return {"mid": mid, "spread_c": (asks[0][0] - bids[0][0]) * 100, "comp": comp, "ours": ours, "share": share,
            "per_day": rm["rate"] * share * stake / max(shares, stake), "top": top, "d": (db, da), "shares": shares}


def rewards():
    rms = reward_markets()
    print(f"rewards: {len(rms)} markets pay liquidity rewards; total pool ${sum(r['rate'] for r in rms):,.0f}/day")
    rms.sort(key=lambda r: -r["rate"])
    print("biggest pools:", [(r["slug"], r["rate"], r["max_spread"], r["min_size"]) for r in rms[:10]])
    print("pool sizes:", Counter(int(r["rate"] // 10 * 10) for r in rms).most_common(12))
    # mirrored books? check one
    mirrored = True
    if rms:
        a, b = bot.book(rms[0]["yes"]), bot.book(rms[0]["no"])
        if a and b and a["bids"] and b["asks"]:
            mirrored = abs(a["bids"][0][0] - (1 - b["asks"][0][0])) < 1e-6 and abs(a["bids"][0][1] - b["asks"][0][1]) < 1e-6
        print("books mirrored:", mirrored, "| YES", a and a["bids"][:2], a and a["asks"][:2], "| NO", b and b["bids"][:2], b and b["asks"][:2])
    res = []
    from concurrent.futures import ThreadPoolExecutor

    def one(rm):
        bk = bot.book(rm["yes"])
        nob = None if mirrored else bot.book(rm["no"])
        if not bk:
            return None
        e = reward_estimate(rm, bk, 100.0, mirrored, nob)
        return (rm, e) if e else None
    cand = rms[:600]
    with ThreadPoolExecutor(8) as ex:
        for x in ex.map(one, cand):
            if x:
                res.append(x)
    res.sort(key=lambda x: -x[1]["per_day"])
    tot = sum(e["per_day"] for _, e in res)
    print(f"checked {len(res)} books; if we put $100 in EVERY one, rewards ~${tot:,.2f}/day (snapshot, ignores fills)")
    vals = sorted((e["per_day"] for _, e in res), reverse=True)
    for k in (1, 5, 10, 20, 50):
        if len(vals) >= k:
            print(f"   top {k}: ${sum(vals[:k]):.2f}/day for ${k * 100}")
    print("top 30 ($ per day for $100 of quotes):")
    gm = {}
    for rm, e in res[:30]:
        g = get(f"{GAMMA}/markets", {"condition_ids": rm["cid"]})
        g = (envelope_rows(g, "markets", "data") or [{}])[0] if not isinstance(g, dict) or "__error__" not in g else {}
        gm[rm["cid"]] = g
        print(f"  ${e['per_day']:.3f}/day  pool ${rm['rate']:.0f}  our share {e['share']:.2f}  mid {e['mid']:.3f}"
              f"  spread {e['spread_c']:.1f}c  v {rm['max_spread']}c  min {rm['min_size']:.0f}  top-of-book {e['top']}"
              f"  vol24h ${fnum(g.get('volume24hr')):,.0f}  1d move {fnum(g.get('oneDayPriceChange')):+.3f}"
              f"  ends {str(rm['end'])[:10]}  {rm['slug']}")
    # fill risk: how much traded through our quote level in the last day, for the top 12
    print("fill risk (last trades through our quote levels, top 12):")
    for rm, e in res[:12]:
        r = get(f"{DATA}/v2/trades", {"market": rm["cid"], "limit": 500})
        rows = envelope_rows(r, "data", "trades")
        if not rows:
            print("   trades:", rm["slug"], short(r, 200))
            continue
        cut = time.time() - 86400
        bid_lvl, ask_lvl = e["mid"] - e["d"][0] / 100, e["mid"] + e["d"][1] / 100
        hit_b = hit_a = vol = 0.0
        for t in rows:
            ts = fnum(t.get("timestamp"))
            ts = ts / 1000 if ts > 1e11 else ts
            if ts < cut:
                continue
            px, sz = fnum(t.get("price")), fnum(t.get("size"))
            if str(t.get("asset")) != rm["yes"]:
                px = 1 - px
            vol += sz
            if px < bid_lvl - 1e-9:
                hit_b += sz
            if px > ask_lvl + 1e-9:
                hit_a += sz
        print(f"   {rm['slug'][:60]}: {len(rows)} trades (24h vol {vol:,.0f} sh); traded through our bid {hit_b:,.0f} sh,"
              f" through our ask {hit_a:,.0f} sh")


# ------------------------------------------------------------ negRisk conversion

def neg_events(pages=150):
    out, cur = [], None
    for _ in range(pages):
        p = {"closed": "false", "limit": 100}
        if cur:
            p["after_cursor"] = cur
        r = get(f"{GAMMA}/events/keyset", p)
        evs = envelope_rows(r, "events", "data")
        for e in evs:
            if isinstance(e, dict) and (e.get("negRisk") or e.get("enableNegRisk")):
                ms = [m for m in (e.get("markets") or []) if isinstance(m, dict)]
                if len(ms) >= 2:
                    out.append(e)
        cur = r.get("next_cursor") if isinstance(r, dict) else None
        if not cur or not evs:
            break
    return out


def negrisk():
    evs = neg_events()
    print(f"negrisk: {len(evs)} open negRisk events")
    near, n_aug = [], 0
    for e in evs:
        ms = [m for m in e["markets"] if not m.get("closed") and m.get("active") is not False]
        if any(m.get("closed") and fnum(jlist(m.get("outcomePrices"))[0] if jlist(m.get("outcomePrices")) else 0) > 0.5
               for m in e["markets"]):
            continue  # already decided
        n_aug += bool(e.get("negRiskAugmented"))
        # value of each outcome if we must get rid of its YES now: sell YES at the bid, or (same thing) buy NO at the ask
        vals = []
        for m in ms:
            b, a = fnum(m.get("bestBid"), 0), fnum(m.get("bestAsk"), 1)
            vals.append(b)
        s = sum(vals)
        near.append((s, e, ms))
    near.sort(key=lambda x: -x[0])
    print("sum of best YES bids (listed): >1.00:", sum(1 for s, _, _ in near if s > 1.0),
          " >0.99:", sum(1 for s, _, _ in near if s > 0.99), " >0.97:", sum(1 for s, _, _ in near if s > 0.97),
          " | augmented events:", n_aug)
    print("closest 12 on listed prices:", [(round(s, 3), e.get("slug"), len(ms)) for s, e, ms in near[:12]])
    # on the real books, 5 shares each, with taker fees: split $1 -> YES+NO of one, convert NO -> YES of the rest,
    # sell every YES at the bid; or buy a NO where it is cheaper than selling that YES (1 - NO ask > YES bid)
    found = 0
    for s, e, ms in near[:40]:
        if s < 0.9:
            break
        shares, total, fees, legs, ok = 5, 0.0, 0.0, [], True
        bought_no = False
        for m in ms:
            toks = bot.market_tokens(m)
            if len(toks) != 2:
                legs.append((m.get("groupItemTitle"), 0, "no tokens"))
                continue
            yb, nb = bot.book(toks[0]), bot.book(toks[1])
            sell = bot.walk(yb["bids"], shares) if yb else None
            buy_no = bot.walk(nb["asks"], shares) if nb else None
            rate = bot.fee_rate(m)
            v_sell = (sell - rate * sell * (1 - sell)) if sell else 0.0
            v_no = (1 - buy_no - rate * buy_no * (1 - buy_no)) if buy_no else 0.0
            if v_no > v_sell:
                total += v_no
                bought_no = True
                legs.append((m.get("groupItemTitle"), round(v_no, 4), "buy NO"))
            else:
                total += v_sell
                legs.append((m.get("groupItemTitle"), round(v_sell, 4), "sell YES"))
        gap = total - 1.0  # per share, after fees, realised right away
        tag = "GAP" if gap > 0 else "no"
        found += gap > 0
        print(f"  {tag} {gap * 100:+.2f}c/share  listed {s:.3f}  n={len(ms)}  {e.get('slug')}"
              + (f"  legs {legs[:12]}" if gap > -0.02 else ""))
    print(f"negrisk: {found} instant gaps on the real books")
    # every_horse's all-NO set converts to (n-1) dollars right away (no waiting); how close are those?
    best = []
    for s, e, ms in near:
        nos = [1 - fnum(m.get("bestBid"), 0) for m in ms]  # NO ask ~ 1 - YES bid
        n = len(ms)
        best.append(((n - 1) - sum(nos), e.get("slug"), n))
    best.sort(key=lambda x: -x[0])
    print("all-NO sets (cost vs n-1 now, listed):", [(round(g, 3), sl, n) for g, sl, n in best[:8]])


# ------------------------------------------------------------ holding rewards

def holding():
    r = get(f"{GAMMA}/markets/keyset", {"closed": "false", "limit": 500, "order": "volume24hr", "ascending": "false"})
    ms = envelope_rows(r, "markets", "data")
    flag_keys = Counter()
    for m in ms:
        for k, v in m.items():
            if ("hold" in k.lower() or "reward" in k.lower() or "apy" in k.lower() or "yield" in k.lower()) and v not in (None, False, 0, "", []):
                flag_keys[k] += 1
    print("holding: reward-ish fields that are set, over", len(ms), "top markets:", dict(flag_keys))
    hk = [k for k in flag_keys if "hold" in k.lower()]
    for m in ms:
        if any(m.get(k) for k in hk):
            print("   ", m.get("slug"), {k: m.get(k) for k in hk}, "prices", m.get("outcomePrices"), "ends", str(m.get("endDate"))[:10])


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    for name, fn in [("shapes", shapes), ("rewards", rewards), ("negrisk", negrisk), ("holding", holding)]:
        if what in (name, "all"):
            print(f"\n################ {name}")
            try:
                fn()
            except Exception as ex:
                import traceback
                traceback.print_exc()
                print(f"{name} failed: {ex}")
