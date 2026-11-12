"""Build the phone dashboard: site/index.html, one self-contained page (data inline, charts drawn as SVG in the browser).

Reads state/ and config.json only; never writes to state/ (the scoreboard is computed on a temp copy).
    python3 dashboard.py            # prices open bets live (GitHub Actions; the pages workflow runs this)
    python3 dashboard.py --offline  # no network: open bets valued at their entry price (for local tests)
Paper money only, like everything else here.
"""
import collections
import datetime as dt
import json
import re
import time
import os
import shutil
import sys
import tempfile

import bot

OUT = os.path.join(bot.ROOT, "site")
MAX_OPEN, MAX_CLOSED, MAX_POINTS = 40, 12, 80


def r2(x):
    return None if x is None else round(float(x), 2)


def scoreboard(tracks):
    """Run the bot's own write_summary on a throwaway copy of state/, so the numbers match summary.md exactly."""
    real = bot.STATE
    tmp = tempfile.mkdtemp(prefix="dash-")
    try:
        for f in os.listdir(real):
            if os.path.isfile(os.path.join(real, f)):
                shutil.copy(os.path.join(real, f), tmp)
        bot.STATE = tmp
        stats = bot.write_summary(tracks)
    finally:
        bot.STATE = real
        shutil.rmtree(tmp, ignore_errors=True)
    return stats


def curve(tr, pnl_now):
    """Cumulative realized profit after each finished trade, then today's total incl. open bets."""
    pts, run = [], 0.0
    for c in sorted(tr.get("closed", []), key=lambda c: c.get("closed_at") or ""):
        run += c.get("pnl", 0.0)
        if c.get("closed_at"):
            pts.append([c["closed_at"][:16], round(run, 2)])
    if len(pts) > MAX_POINTS:  # thin out, keep the last one
        step = len(pts) / MAX_POINTS
        pts = [pts[int(i * step)] for i in range(MAX_POINTS - 1)] + [pts[-1]]
    start = (tr.get("created") or "2026-11-03T00:00")[:16]
    return [[start, 0.0]] + pts + [[bot.iso()[:16], round(pnl_now, 2)]]


def open_bets(name, tr):
    """Open bets (largest moves first), the count, maker quotes that hold nothing yet, and Kalshi bids not yet
    filled (both shown apart)."""
    rows, waiting, orders = [], [], []
    for tok, p in tr.get("positions", {}).items():
        px = bot.mark(p, tok)
        cost = p["shares"] * p["entry"] + p.get("entry_fee", 0.0)
        rows.append({"t": p.get("title", "")[:90], "o": p.get("outcome"), "e": r2(p["entry"] * 100), "n": r2(px * 100),
                     "pnl": r2(p["shares"] * px - cost), "c": r2(cost), "end": str(p.get("end", ""))[:10],
                     "u": bot.market_link(p.get("slug", ""), p.get("event_slug", ""))})
    for a in tr.get("arbs", {}).values():
        rows.append({"t": a.get("title", "")[:90], "o": f"Kalshi {a.get('k_side')} + Poly {a.get('poly_outcome')}",
                     "e": r2((a.get("k_price", 0) + a.get("p_price", 0)) * 100), "n": None,
                     "pnl": r2(a.get("expected_profit")), "c": r2(a.get("cost")), "end": str(a.get("poly_end", ""))[:10],
                     "u": bot.market_link(a.get("poly_slug", "")), "locked": True})
    for s in tr.get("sets", {}).values():
        rows.append({"t": str(s.get("title", ""))[:90], "o": "every outcome", "e": None, "n": None,
                     "pnl": r2(s.get("expected_profit")), "c": r2(s.get("cost")), "end": str(s.get("end", ""))[:10],
                     "u": bot.market_link(s.get("slug", ""), s.get("event_slug", "")), "locked": True})
    for b in tr.get("books", {}).values():
        held = b.get("yes_cost", 0) + b.get("no_cost", 0)
        if held <= bot.EPS:  # only quoting: nothing bought, nothing at stake
            waiting.append({"t": b.get("title", "")[:90], "n": r2(b.get("mid", 0) * 100), "end": str(b.get("end", ""))[:10],
                            "bonus": r2(b.get("rewards", 0)), "u": bot.market_link(b.get("slug", ""), b.get("event_slug", ""))})
            continue
        hold = f"holding {b.get('yes', 0):.0f} YES, {b.get('no', 0):.0f} NO"
        rows.append({"t": b.get("title", "")[:90], "o": f"offering to buy and sell, {hold}, bonus ${b.get('rewards', 0):.2f} (estimate)",
                     "e": None, "n": r2(b.get("mid", 0) * 100),  # P&L = price move only, rewards shown apart
                     "pnl": r2(bot.maker_inv_value(b, b.get("mid", 0.5)) - held), "c": r2(held),
                     "end": str(b.get("end", ""))[:10], "u": bot.market_link(b.get("slug", ""), b.get("event_slug", ""))})
    for o in tr.get("orders", {}).values():
        if o.get("chance") is None:
            # kc_maker*: a resting Kalshi bid, not a bet yet. Shown apart (Jan, 11 Nov: "waiting order ... bought 96c ...
            # expected P&L +$0.00" read like a stuck bet). Whether anyone sold to it is only known from the trade tape
            # after the close; then it becomes a finished bet or "nobody sold".
            orders.append({"t": str(o.get("title", ""))[:90], "side": str(o.get("side", "")).upper(),
                           "e": r2(o.get("price", 0) * 100), "c": r2(o.get("cost")), "close": str(o.get("close", "")),
                           "u": f"https://kalshi.com/markets/{o.get('series', '').lower()}"})
            continue
        what = o.get("what") or f"bought {str(o.get('side', '')).upper()} on Kalshi, waiting for the release"   # econ_fav holds real buys; kalshi_patient sets its own text
        rows.append({"t": str(o.get("title", ""))[:90], "o": what,
                     "e": r2(o.get("price", 0) * 100), "n": None, "pnl": 0.0, "c": r2(o.get("cost")),
                     "end": str(o.get("close", ""))[:16], "u": f"https://kalshi.com/markets/{o.get('series', '').lower()}",
                     "locked": True})
    rows.sort(key=lambda r: -abs(r["pnl"] or 0))
    return rows[:MAX_OPEN], len(rows), waiting, orders


def recent_closed(tr):
    out = []
    for c in sorted(tr.get("closed", []), key=lambda c: c.get("closed_at") or "", reverse=True)[:MAX_CLOSED]:
        out.append({"t": str(c.get("title", ""))[:90], "o": c.get("outcome"), "e": r2(c["entry"] * 100) if c.get("entry") is not None else None,
                    "x": r2(c["exit"] * 100) if c.get("exit") is not None else None, "pnl": r2(c.get("pnl")), "at": (c.get("closed_at") or "")[:16],
                    "why": c.get("reason", "")})
    return out


TOPICS = [("weather", ("temperature", "weather", "rain", "snow", "hurricane")),
          ("crypto", ("bitcoin", "btc", "ethereum", " eth", "solana", "xrp", "crypto", "dogecoin", "up or down")),
          ("esports", ("dota", "lol:", "counter-strike", "cs2", "valorant", "league of legends", "(bo3)", "(bo5)")),
          ("sports", ("nba", "nfl", "nhl", "mlb", "ufc", "premier league", " vs. ", " vs ", "win on 20", "fc ", "draw?", "spread", "o/u")),
          ("talk ('will X say Y')", (" say ", "said", "mention", "tweet")),
          ("economy", ("fed ", "interest rate", "cpi", "inflation", "gdp", "jobs", "unemployment", "recession", "bps")),
          ("elections", ("election", "senate", "house seat", "governor", "mayor", "primary", "nominee", "popular vote")),
          ("world news", ("iran", "russia", "ukraine", "israel", "china", "ceasefire", "strike", "invade", "venezuela", "military")),
          ("politics", ("trump", "president", "out as", "secretary", "congress", "impeach", "pardon")),
          ("stocks & companies", ("market cap", "largest company", "ipo", "stock", "nvidia", "apple", "tesla"))]


def topic(title):
    s = f" {title} ".lower()
    for name, words in TOPICS:
        if any(w in s for w in words):
            return name
    return "other"


def wallet_style(tr):
    """Copy tracks: a plain one-liner built from the bets we copied (topics, price, Yes/No, how long, how it ended)."""
    items = list(tr.get("positions", {}).values()) + tr.get("closed", [])
    if not items:
        return None
    n = len(items)
    tc = collections.Counter(topic(x.get("title", "")) for x in items).most_common(3)
    tops = ", ".join(f"{k} ({v})" for k, v in tc)
    px = sorted(x["entry"] * 100 for x in items if x.get("entry"))
    lo, mid, hi = px[len(px) // 10], px[len(px) // 2], px[min(len(px) - 1, int(len(px) * .9))]
    no = sum(1 for x in items if str(x.get("outcome", "")).lower() == "no")
    yes = sum(1 for x in items if str(x.get("outcome", "")).lower() == "yes")
    side = (f"mostly No ({no} of {n})" if no >= .7 * n else f"mostly Yes ({yes} of {n})" if yes >= .7 * n
            else f"picks a team or name ({n - yes - no} of {n})" if n - yes - no >= .7 * n
            else f"Yes {yes}, No {no}, a team or name {n - yes - no}" if n - yes - no else f"Yes {yes}, No {no}")
    if mid >= 85:
        kind = "favorites (the likely side)"
    elif mid <= 20:
        kind = "long shots (cheap, unlikely sides)"
    else:
        kind = "close calls"
    out = [f"We copied {n} bets. Topics: {tops}.",
           (f"Typical price {mid:.0f}c (most between {lo:.0f}c and {hi:.0f}c): {kind}." if hi - lo <= 50
            else f"Prices all over the place, from {lo:.0f}c to {hi:.0f}c (middle {mid:.0f}c).") + f" Sides: {side}."]
    done = tr.get("closed", [])
    if done:
        sold = sum(1 for c in done if str(c.get("reason", "")).startswith("wallet"))
        hours = sorted((dt.datetime.fromisoformat(c["closed_at"].replace("Z", "+00:00")) - dt.datetime.fromisoformat(c["opened"].replace("Z", "+00:00"))).total_seconds() / 3600
                       for c in done if c.get("closed_at") and c.get("opened"))
        held = ""
        if hours:
            h = hours[len(hours) // 2]
            held = f" Usually over within {h:.0f} hours." if h < 48 else f" Usually held about {h / 24:.0f} days."
        out.append(f"{len(done)} finished: {sum(1 for c in done if c.get('pnl', 0) > 0)} won, {sum(1 for c in done if c.get('pnl', 0) <= 0)} lost; "
                   + (f"{sold} of them the wallet sold (or switched sides) before the end, so we sold too.{held}" if sold
                    else f"all held to the end.{held}"))
    return " ".join(out)


def first_end(tr):
    """Earliest end date among open bets (when the first one can finish)."""
    ends = [str(p.get("end", ""))[:10] for p in tr.get("positions", {}).values()]
    ends += [str(a.get("poly_end", ""))[:10] for a in tr.get("arbs", {}).values()]
    ends += [str(s.get("end", ""))[:10] for s in tr.get("sets", {}).values()]
    ends += [str(o.get("close", ""))[:10] for o in tr.get("orders", {}).values()]
    ends = sorted(e for e in ends if len(e) == 10 and e[:2] == "20")
    return ends[0] if ends else None


def late_copy(tr):
    """Copy tracks: what buying after the wallet did cost us, vs the wallet's own average price."""
    items = [x for x in list(tr.get("positions", {}).values()) + tr.get("closed", []) if x.get("their_avg")]
    if not items:
        return None
    extra = sum(x["shares"] * (x["entry"] - x["their_avg"]) for x in items)
    shares = sum(x["shares"] for x in items)
    return {"n": len(items), "usd": r2(extra), "c_per_share": r2(extra / shares * 100) if shares else None}


def real_size(tr):
    """Profit per $100 on finished trades, 5-share paper vs each real stake; how much of a $100 order fits."""
    fills = bot.rs_fills(tr)
    if not fills:
        return None
    done = [c for c in tr["closed"] if c.get("rs_pnl")]
    basis = sum(c.get("cost") or (c["shares"] * c["entry"] + c.get("entry_fee", 0)) for c in done)
    out = {"n": len(done), "paper": r2(sum(c["pnl"] for c in done) / basis * 100) if done and basis > bot.EPS else None}
    for sz in bot.rs_sizes():
        rr = [c["rs_pnl"][str(sz)] for c in done if str(sz) in c["rs_pnl"] and c["rs_pnl"][str(sz)][0] > bot.EPS]
        cost = sum(x[0] for x in rr)
        out[str(sz)] = r2(sum(x[1] for x in rr) / cost * 100) if cost > bot.EPS else None
    big = str(max(bot.rs_sizes()))
    fit = [f[big][1] for f in fills if big in f]
    out["fits"] = r2(sum(fit) / len(fit)) if fit else None
    out["big"] = int(big)
    return out


# ---------------------------------------------------------------- tests that run outside the paper bot
# The combo house (Jan's server) and the fast Kalshi bot (its own workflow) keep their own notes. Jan, 12 Nov:
# "Why doesn't this one have a graph? The dashboard doesn't feel standardized". So they are turned into rows of
# the same shape as a paper-bot strategy: same top line, verdict (bot.plain_verdict), worst case (bot.trust), graph
# and finished-bets list. Anything special to them goes in "extra" tiles and notes under the standard card.
COMBO_POT, COMBO_STAKE = 300.0, 5.0    # display only: the locked pass rule (PROTOCOL 5c) is per $100 and doesn't change
KFAST_POT = 100.0                      # like the kc_maker tracks: $100, about $10 an order


def iso_s(sec):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(sec))


def ext_row(name, label, bets, pot, tied=0.0, waiting=0, extra=None, notes=None, recent=None, wins=None):
    """bets: [(seconds, cost, pnl)] of finished bets, oldest first."""
    closed = [{"pnl": p, "cost": c} for _, c, p in bets if c > 0]
    tr = bot.trust({"closed": closed}, size=None)
    pnl = sum(p for _, _, p in bets)
    risk = sum(c for _, c, _ in bets)
    day = time.strftime("%Y-%m-%d", time.gmtime())
    run, cv = 0.0, []
    for t, _, p in bets:
        run += p
        cv.append([time.strftime("%Y-%m-%dT%H:%M", time.gmtime(t)), r2(run)])
    cv = ([[cv[0][0], 0.0]] + cv if cv else [[bot.iso()[:16], 0.0]]) + [[bot.iso()[:16], r2(run)]]
    if wins is None:       # pass it when a won bet can still end a hair below $0 (a 99.8c buy plus the fee)
        wins = sum(1 for _, _, p in bets if p > 0)
    return {"name": name, "label": label, "lab": False, "control": False, "ext": True,
            "pnl": r2(pnl), "today": r2(sum(p for t, _, p in bets if time.strftime("%Y-%m-%d", time.gmtime(t)) == day)),
            "realized": r2(pnl), "open": waiting, "waiting": [], "orders": [], "closed": len(bets), "wins": wins,
            "losses": len(bets) - wins, "cash": r2(pot + pnl - tied), "deposited": r2(pot), "needed": None, "risked": r2(risk),
            "trust": tr, "paper": None, "pv": bot.plain_verdict(tr), "verdict": None, "curve": cv, "bets": [], "n_bets": waiting,
            "recent": recent or [], "late": None, "first_end": None, "wnote": None, "wstyle": None, "rs": None,
            "status": None, "mk": None, "extra": extra or [], "notes": notes or [],
            "legend": "Profit from finished bets, added up over time"}


def combo_row(q):
    if not q or "all" not in q:
        return None
    k = COMBO_STAKE / 25.0      # the server's notes count $25 at risk a parlay; the card shows a pot Jan could really fund
    bets = [(t, c * k, (pay - c) * k) for t, c, pay in q["all"]]
    cents = lambda v: f"{round(v * 100)}c"
    recent, wait = [], []
    for b in q.get("bets") or []:
        legs = " + ".join(f"{lg['title']}{' ' + lg['out'] if lg.get('out') else ''}" for lg in b.get("legs") or [])
        if b["end"] == "waiting":
            wait.append(legs)
        else:
            recent.append({"t": legs, "o": "A leg lost, we keep the buyer's money" if b["end"] == "kept" else f"Every leg won, we pay out ${COMBO_STAKE:.0f}",
                           "e": None, "x": None, "pnl": r2(b["gain"] * k), "why": f"buyer paid a pro {cents(b['price'])} per $1, we'd have asked {cents(b['q'])}",
                           "at": iso_s(b["t"])[:16]})
    last = iso_s(q["last_seen"]) if q.get("last_seen") else None
    tied = COMBO_STAKE * (q.get("waiting") or 0)
    extra = [[f"{q['heard']:,}", "price requests heard"], [f"{q['trades']:,}", "parlays really sold"],
             [f"{q['would_win']:,}", "we'd have been cheapest"]]
    notes = [f"It starts with ${COMBO_POT:.0f} and risks ${COMBO_STAKE:.0f} on every parlay it would have sold. Per $100 the result is the same at any bet size.",
             q.get("pass_rule", "") + ".",
             {"last_seen": last}]
    if tied > COMBO_POT:
        notes.insert(1, f"Right now {q.get('waiting')} parlays are waiting, which needs ${tied:,.0f}. That is more than the ${COMBO_POT:.0f} pot, "
                        f"so a real pot this size would have had to skip some of them.")
    row = ext_row("combo_house", "Combo house (practice, on your AWS server): the server listens to people asking for parlay prices. "
                  "For each one it writes down the price we would have offered (the legs multiplied, plus 5%; 2-4 legs, no two from the same game). "
                  "When the parlay really sells and our price was lower than the pro's, we count it as our sale. No real money moves.",
                  bets, COMBO_POT, tied=tied, waiting=q.get("waiting") or 0, extra=extra, notes=notes, recent=recent[:12])
    row["open_list"] = wait[:30]
    return row


def kfast_rows():
    try:
        import kfastlive as kf
        ws = [w for w in kf.rows() if w.get("result") in ("yes", "no")]
    except Exception as e:
        print(f"dashboard: fast Kalshi notes not read ({e})")
        return []
    out = []
    for k, v in kf.VARIANTS.items():
        if not v.get("main"):
            continue
        bets, recent, chances, won = [], [], 0, 0
        for w in sorted(ws, key=lambda w: w["close"]):
            b = (w.get("bets") or {}).get(k)
            if not b or "won" not in b:
                continue
            chances += 1
            f = b.get("10") or {}
            if not f.get("filled"):
                continue
            cost = f["filled"] * f["avg"] + f.get("fee", 0.0)
            bets.append((w["close"], cost, f["pnl"]))
            won += 1 if b["won"] else 0
            recent.append({"t": w["tk"], "o": b["side"].upper(), "e": r2(f["avg"] * 100), "x": 100.0 if b["won"] else 0.0, "pnl": r2(f["pnl"]),
                           "why": "window ended", "at": iso_s(w["close"])[:16]})
        wait = "waits with a buy offer" if v["kind"] == "bid" else "buys at the asking price"
        out.append(ext_row("kfast_" + k, f"Fast Kalshi bot (its own nonstop job, practice only): Kalshi 15-minute crypto, {v['L']} seconds before "
                           f"the end. It {wait} for the side Binance says is safely ahead, 10 contracts a time (about $10). "
                           f"Test: {kf.LABEL[k]}. Fixed on 10 Nov, not to be changed.",
                           bets, KFAST_POT, extra=[[f"{chances:,}", "chances seen"], [f"{len(bets):,}", "times it really got to buy"]],
                           notes=["One bet makes a few cents and one loss costs about $10, so it needs hundreds of bets without a loss before the number means anything."],
                           recent=recent[::-1][:12], wins=won))
    return out


def stopped_info(tc, tr):
    """Jan, 12 Nov: stopped tracks stay on the page but must look closed. "stopped" (no new bets, open ones settle) or
    "retired" (maker: everything closed). Returns {"on": "2026-11-12", "why": "..."} or None."""
    why = tc.get("stopped") or tc.get("retired")
    if not why:
        return None
    why = why if isinstance(why, str) else ""
    m = re.match(r"(\d{4}-\d{2}-\d{2})[:\s]*(.*)", why)
    on = m.group(1) if m else str((tr.get("retired") or {}).get("on", ""))[:10] or None
    return {"on": on, "why": (m.group(2) if m else why)[:300]}


def build(offline=False):
    if offline:
        def no_net(*a, **k):
            raise RuntimeError("offline")
        bot.http_json = no_net
    tracks = bot.load_tracks()
    stats = scoreboard(tracks)
    names = list(stats)
    n_top = bot.CFG["push"].get("top_n", 10)
    top = [x for x in bot.ranked(stats) if bot.top_eligible(stats[x])][:n_top]
    try:
        with open(os.path.join(bot.ROOT, "wallet_notes.json")) as fh:
            notes = json.load(fh).get("wallets", {})
    except (OSError, ValueError):
        notes = {}
    rows = []
    for n in names:
        s, tr, tc = stats[n], tracks[n], bot.CFG["tracks"].get(n, {})
        ob, n_open, waiting, orders = open_bets(n, tr)
        rows.append({
            "name": n, "label": tc.get("label", ""), "lab": bool(tc.get("lab")), "stopped": stopped_info(tc, tr), "control": n.startswith("control_"),
            "pnl": r2(s["pnl"]), "today": r2(s.get("today", 0)), "realized": r2(s.get("realized")),
            "open": s["open"] - len(waiting) - len(orders), "waiting": waiting, "orders": orders, "closed": s["closed"], "wins": s["wins"], "losses": s["losses"],
            "cash": r2(s.get("cash")), "deposited": r2(s.get("deposited")), "needed": r2(s.get("money_needed")),
            "trust": s["trust"], "paper": s.get("trust_paper"), "pv": bot.plain_verdict(s["trust"], n.startswith("control_")), "verdict": (s.get("proof") or {}).get("verdict"),
            "curve": curve(tr, s["pnl"]), "bets": ob, "n_bets": n_open, "recent": recent_closed(tr),
            "late": late_copy(tr), "first_end": first_end(tr),
            "wnote": notes.get(str(tc.get("address", "")).lower()) if tc.get("source") == "wallet" else None,
            "wstyle": wallet_style(tr) if tc.get("source") == "wallet" else None, "rs": real_size(tr), "status": tr.get("status"),
            "mk": {"rewards": r2(s["maker_rewards"]), "locked": r2(s["maker_locked"]), "open": r2(s["maker_open"]),
                   "exits": s.get("exits", 0)} if "maker_rewards" in s else None,
        })
    try:
        with open(os.path.join(bot.ROOT, "state", "quoter.json")) as fh:
            quoter = {k: v for k, v in json.load(fh).items() if k != "leg_results"}
    except (OSError, ValueError):
        quoter = None
    ext = [r for r in [combo_row(quoter)] + kfast_rows() if r]
    order = bot.ranked(stats)
    rows += ext
    if ext:            # same ranking rule as bot.ranked: worst case first, then P&L
        order = [r["name"] for r in sorted(rows, key=lambda r: (-r["trust"]["worst_per_100"], -r["pnl"]))]
    data = {"generated": bot.iso(), "quoter_pending": bool(quoter) and "all" not in quoter, "ext": [r["name"] for r in ext], "offline": offline, "rank_size": bot.rs_rank_size(), "top": top,
            "order": order, "tracks": rows, "trial_end": "2027-01-01",
            "min_proven": bot.CFG.get("ranking", {}).get("min_trades_proven", 30),
            "repo": "https://github.com/palsk1/poly-paper-bot"}
    with open(os.path.join(bot.ROOT, "dashboard.html")) as fh:
        page = fh.read()
    blob = json.dumps(data, separators=(",", ":")).replace("</", "<\\/")
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "index.html"), "w") as fh:
        fh.write(page.replace("/*DATA*/null", blob))
    with open(os.path.join(OUT, ".nojekyll"), "w") as fh:
        fh.write("")
    print(f"dashboard: {len(rows)} strategies, top {len(top)}, {os.path.getsize(os.path.join(OUT, 'index.html')) // 1024} KB")


if __name__ == "__main__":
    build(offline="--offline" in sys.argv)
