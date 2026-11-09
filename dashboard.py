"""Build the phone dashboard: site/index.html, one self-contained page (data inline, charts drawn as SVG in the browser).

Reads state/ and config.json only; never writes to state/ (the scoreboard is computed on a temp copy).
    python3 dashboard.py            # prices open bets live (GitHub Actions; the pages workflow runs this)
    python3 dashboard.py --offline  # no network: open bets valued at their entry price (for local tests)
Paper money only, like everything else here.
"""
import json
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
    """Open bets (largest moves first), the count, and maker quotes that hold nothing yet (shown apart)."""
    rows, waiting = [], []
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
    for o in tr.get("orders", {}).values():  # kmaker: resting Kalshi bids, settled from the trade tape after the close
        what = (f"bought {str(o.get('side', '')).upper()} on Kalshi, waiting for the release" if o.get("chance") is not None
                else f"waiting order to buy {str(o.get('side', '')).upper()} on Kalshi")   # econ_fav holds real buys
        rows.append({"t": str(o.get("title", ""))[:90], "o": what,
                     "e": r2(o.get("price", 0) * 100), "n": None, "pnl": 0.0, "c": r2(o.get("cost")),
                     "end": str(o.get("close", ""))[:16], "u": f"https://kalshi.com/markets/{o.get('series', '').lower()}",
                     "locked": True})
    rows.sort(key=lambda r: -abs(r["pnl"] or 0))
    return rows[:MAX_OPEN], len(rows), waiting


def recent_closed(tr):
    out = []
    for c in sorted(tr.get("closed", []), key=lambda c: c.get("closed_at") or "", reverse=True)[:MAX_CLOSED]:
        out.append({"t": str(c.get("title", ""))[:90], "o": c.get("outcome"), "e": r2((c.get("entry") or 0) * 100),
                    "x": r2((c.get("exit") or 0) * 100), "pnl": r2(c.get("pnl")), "at": (c.get("closed_at") or "")[:16],
                    "why": c.get("reason", "")})
    return out


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
    rows = []
    for n in names:
        s, tr, tc = stats[n], tracks[n], bot.CFG["tracks"].get(n, {})
        ob, n_open, waiting = open_bets(n, tr)
        rows.append({
            "name": n, "label": tc.get("label", ""), "lab": bool(tc.get("lab")), "control": n.startswith("control_"),
            "pnl": r2(s["pnl"]), "today": r2(s.get("today", 0)), "realized": r2(s.get("realized")),
            "open": s["open"] - len(waiting), "waiting": waiting, "closed": s["closed"], "wins": s["wins"], "losses": s["losses"],
            "cash": r2(s.get("cash")), "deposited": r2(s.get("deposited")), "needed": r2(s.get("money_needed")),
            "trust": s["trust"], "paper": s.get("trust_paper"), "pv": bot.plain_verdict(s["trust"], n.startswith("control_")), "verdict": (s.get("proof") or {}).get("verdict"),
            "curve": curve(tr, s["pnl"]), "bets": ob, "n_bets": n_open, "recent": recent_closed(tr),
            "late": late_copy(tr), "rs": real_size(tr), "status": tr.get("status"),
            "mk": {"rewards": r2(s["maker_rewards"]), "locked": r2(s["maker_locked"]), "open": r2(s["maker_open"]),
                   "exits": s.get("exits", 0)} if "maker_rewards" in s else None,
        })
    data = {"generated": bot.iso(), "offline": offline, "rank_size": bot.rs_rank_size(), "top": top,
            "order": bot.ranked(stats), "tracks": rows, "trial_end": "2027-01-01",
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
