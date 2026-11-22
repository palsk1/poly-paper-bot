"""Real bots vs their paper twins, side by side (Jan was burned by a bot that won on paper and lost live).

    python3 live/compare.py            # reads the release `live-data` (public) and state/tracks.json

Kalshi: every 15-minute window the real bot bid on, next to the paper kc_maker_safe_usd bid on the same window.
Polymarket: every draw the real bot bought, next to the paper soccer_draw bet on the same market.
Money is compared per $100 put in, because the real bids are smaller ($4, ~$1.30) than paper ($10, ~$1.40).
"""
import gzip
import io
import json
import os
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO, TAG = "palsk1/poly-paper-bot", "live-data"


def assets():
    url = f"https://api.github.com/repos/{REPO}/releases/tags/{TAG}"
    try:
        rel = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "compare"}), timeout=30))
    except Exception as e:
        sys.exit(f"no live-data release yet ({e}): the bots haven't uploaded anything")
    out = {}
    for a in rel.get("assets", []):
        raw = urllib.request.urlopen(urllib.request.Request(a["browser_download_url"], headers={"User-Agent": "compare"}),
                                     timeout=60).read()
        out[a["name"]] = gzip.GzipFile(fileobj=io.BytesIO(raw)).read().decode()
    return out


def rows(files, bot):
    for name, txt in sorted(files.items()):
        if name.startswith(bot + "-") and name.endswith(".jsonl.gz"):
            for ln in txt.splitlines():
                if ln.strip():
                    yield json.loads(ln)


def per100(pnl, cost):
    return f"${pnl / cost * 100:+.2f} per $100" if cost else "-"


def main():
    files = assets()
    tracks = json.load(open(os.path.join(ROOT, "state", "tracks.json")))

    # ---- Kalshi
    real = {r["key"]: r for r in rows(files, "kalshi") if r["k"] == "settled"}
    paper_t = tracks.get("kc_maker_safe_usd", {})
    paper = {c["ticker"]: c for c in paper_t.get("closed", [])}
    paper_unfilled = {u["ticker"] for u in paper_t.get("unfilled_log", [])}
    live_only = [r for r in real.values() if r.get("how") == "real"]
    both = [r for r in live_only if r["key"] in paper]
    rf = [r for r in live_only if r.get("filled", 0) > 0]
    print(f"KALSHI (kc_maker_safe_usd): {len(live_only)} real bids settled, {len(rf)} filled, "
          f"{sum(1 for r in rf if r['pnl'] < 0)} lost, P&L ${sum(r['pnl'] for r in live_only):+.2f} "
          f"({per100(sum(r['pnl'] for r in rf), sum(r.get('fill_cost', 0) for r in rf))})")
    print(f"  same windows as paper: {len(both)}; paper filled there: {sum(1 for r in both if paper[r['key']]['shares'] > 0)}, "
          f"real filled: {sum(1 for r in both if r.get('filled', 0) > 0)}")
    pr = [paper[r["key"]] for r in both]
    print(f"  on those windows: real {per100(sum(r['pnl'] for r in both), sum(r.get('fill_cost', 0) for r in both))}, "
          f"paper {per100(sum(p['pnl'] for p in pr), sum(p['cost'] for p in pr))}")
    nopaper = [r for r in live_only if r["key"] not in paper and r["key"] not in paper_unfilled]
    print(f"  real bids where paper had no bid (paper runs only every 5 min): {len(nopaper)}, "
          f"P&L ${sum(r['pnl'] for r in nopaper):+.2f}")
    for r in sorted(live_only, key=lambda r: r["t"])[-5:]:
        p = paper.get(r["key"])
        print(f"   {r['key']}: real {r.get('filled', 0):.0f} filled ${r['pnl']:+.2f} | paper "
              + (f"{p['shares']:.0f} filled ${p['pnl']:+.2f}" if p else "no bid"))

    # ---- Polymarket
    real = {r["key"]: r for r in rows(files, "poly") if r["k"] == "settled" and r.get("how") == "real"}
    pt = tracks.get("soccer_draw", {})
    paper = {c.get("slug"): c for c in pt.get("closed", [])}
    both = [r for r in real.values() if r["key"] in paper]
    print(f"\nPOLYMARKET (soccer_draw, every second signal): {len(real)} real bets settled, "
          f"{sum(1 for r in real.values() if r['pnl'] > 0)} won, P&L ${sum(r['pnl'] for r in real.values()):+.2f} "
          f"({per100(sum(r['pnl'] for r in real.values()), sum(r.get('cost', 0) for r in real.values()))})")
    pp = [paper[r["key"]] for r in both]
    print(f"  same markets as paper: {len(both)}: real {per100(sum(r['pnl'] for r in both), sum(r.get('cost', 0) for r in both))}, "
          f"paper {per100(sum(p['pnl'] for p in pp), sum(p['shares'] * p['entry'] + p.get('entry_fee', 0) for p in pp))}")
    gap = [r.get("ask", 0) - paper[r["key"]]["entry"] for r in both]
    if gap:
        print(f"  real price minus paper price: {sum(gap) / len(gap) * 100:+.2f}c a share on average")


if __name__ == "__main__":
    main()
