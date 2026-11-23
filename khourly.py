#!/usr/bin/env python3
"""Kalshi's hourly and daily crypto rounds: the kc_maker_safe_usd bid replayed there (23 Nov 2026, Jan's ask).

PAPER ONLY. Reads public history and never trades.

    python3 khourly.py scan        # probe khr_scan: which crypto series exist on Kalshi (how often, fees, size), what one
                                   # hourly round looks like, and which hourly / daily crypto bets Polymarket lists
"""
import collections
import datetime as dt
import json
import os
import re
import sys
import time

import bot
import kcrypto as kc
import yesno

UTC = dt.timezone.utc
CACHE = os.path.join(bot.ROOT, "bt_cache", "khr")
OUT = os.path.join(bot.ROOT, "backtest")
kget = yesno.kget


def iso(t):
    return dt.datetime.fromtimestamp(t, UTC).strftime("%Y-%m-%d %H:%M")


_LOG = []


def say(*a):
    line = " ".join(str(x) for x in a)
    print(line, flush=True)
    _LOG.append(line)


def save_log(name):
    os.makedirs(CACHE, exist_ok=True)
    with open(os.path.join(CACHE, name), "w") as fh:
        fh.write("\n".join(_LOG) + "\n")


def vol_of(m):
    return bot.fnum(m.get("volume_fp") or m.get("volume"), 0)


def scan():
    """Everything lands in bt_cache/khr/scan.txt (price store), so the workspace can read it without the run log."""
    ser = kget("/series", {"category": "Crypto"}).get("series") or []
    say("Kalshi Crypto series:", len(ser), collections.Counter(s.get("frequency") for s in ser).most_common())
    now = int(time.time())
    keep = {}
    for s in sorted(ser, key=lambda s: s.get("ticker") or ""):
        tk = s.get("ticker")
        try:
            ms = kget("/markets", {"series_ticker": tk, "status": "settled", "limit": 1000,
                                   "min_close_ts": now - 2 * 86400}).get("markets") or []
        except Exception as e:
            say("  failed", tk, str(e)[:80])
            continue
        if not ms:
            continue
        ev = collections.defaultdict(list)
        for m in ms:
            ev[m.get("event_ticker")].append(m)
        life = sorted((kc.tsec(m.get("close_time")) or 0) - (kc.tsec(m.get("open_time")) or 0) for m in ms)
        keep[tk] = ev
        say(f"  {tk:18s} | {s.get('frequency')} | fee {s.get('fee_type')} x{s.get('fee_multiplier')} | 2 days: {len(ev)} rounds, "
            f"{len(ms)} markets{'+' if len(ms) == 1000 else ''}, {sum(map(vol_of, ms)):,.0f} contracts | open for "
            f"{life[len(life) // 2] / 3600:.1f} h (middle) | {str(s.get('title'))[:60]}")
    for tk, ev in sorted(keep.items(), key=lambda kv: -sum(vol_of(m) for mm in kv[1].values() for m in mm)):
        if tk.endswith("15M"):
            continue
        byh = collections.defaultdict(float)
        for e, mm in ev.items():
            c = kc.tsec(mm[0].get("close_time")) or 0
            byh[dt.datetime.fromtimestamp(c, UTC).hour] += sum(map(vol_of, mm))
        say(f"\n== {tk}: contracts by close hour (UTC): {' '.join(f'{h}:{round(v)}' for h, v in sorted(byh.items()))}")
        ek = sorted(ev, key=lambda e: -sum(map(vol_of, ev[e])))
        for e in ek[:1] + ek[len(ek) // 2:len(ek) // 2 + 1]:
            mm = sorted(ev[e], key=lambda m: bot.fnum(m.get("floor_strike"), 0) or bot.fnum(m.get("cap_strike"), 0))
            m0 = mm[len(mm) // 2]
            say(f"  round {e}: {len(mm)} markets, open {m0.get('open_time')} close {m0.get('close_time')} settle {m0.get('expiration_value')} "
                f"| tick {json.dumps(m0.get('price_ranges'))} | rule: {str(m0.get('rules_primary'))[:230]}")
            for m in [m for m in mm if vol_of(m) > 0][:60]:
                say(f"    {m.get('ticker'):34s} {m.get('strike_type')} {m.get('floor_strike')} {m.get('cap_strike')} vol {vol_of(m):,.0f} {m.get('result')}")
        try:
            d = (kget(f"/live_data/events/{ek[0]}").get("live_data") or {}).get("details") or {}
            ts = d.get("timeseries") or []
            say(f"  live settle number for {ek[0]}: {len(ts)} points, first {ts[:1]}, last {ts[-1:]}")
        except Exception as e:
            say("  live settle number failed", str(e)[:100])
    try:
        say("historical cutoff", json.dumps(kget("/historical/cutoff")))
    except Exception as e:
        say("cutoff failed", str(e)[:80])
    pm_scan()
    save_log("scan.txt")


def get_trades(ticker, limit=1000):
    return kget("/markets/trades", {"ticker": ticker, "limit": limit})


def pm_scan():
    """Polymarket: does it list hourly / 4-hour / daily crypto rounds? Looked up by the slug of a recent round."""
    import habits
    G = habits.G
    now = dt.datetime.now(UTC)
    et = now - dt.timedelta(hours=5)
    h1 = (et - dt.timedelta(hours=3)).replace(minute=0, second=0, microsecond=0)
    hh = f"{(h1.hour % 12) or 12}{'am' if h1.hour < 12 else 'pm'}"
    mon = h1.strftime("%B").lower()
    t4 = (int(time.time()) // 14400 - 2) * 14400
    t1 = (int(time.time()) // 3600 - 3) * 3600
    yday = et - dt.timedelta(days=1)
    names = {"bitcoin": "btc", "ethereum": "eth", "solana": "sol", "xrp": "xrp", "dogecoin": "doge", "hyperliquid": "hype", "bnb": "bnb"}
    slugs = []
    for long, short in names.items():
        slugs += [f"{long}-up-or-down-{mon}-{h1.day}-{hh}-et", f"{long}-up-or-down-{mon}-{h1.day}-{h1.year}-{hh}-et",
                  f"{short}-updown-4h-{t4}", f"{short}-updown-1h-{t1}", f"{short}-updown-15m-{t1}",
                  f"{long}-above-on-{yday.strftime('%B').lower()}-{yday.day}-{yday.year}", f"{long}-above-on-{yday.strftime('%B').lower()}-{yday.day}",
                  f"{long}-price-on-{yday.strftime('%B').lower()}-{yday.day}-{yday.year}",
                  f"{long}-up-or-down-on-{yday.strftime('%B').lower()}-{yday.day}-{yday.year}", f"{long}-up-or-down-on-{yday.strftime('%B').lower()}-{yday.day}"]
    say("\nPolymarket, by slug:")
    for sl in slugs:
        try:
            r = bot.http_json(f"{G}/events", {"slug": sl})
        except Exception as e:
            say("  failed", sl, str(e)[:80])
            continue
        rows = [e for e in bot.envelope_rows(r, "events", "data") if isinstance(e, dict)]
        if not rows:
            say(f"  none: {sl}")
            continue
        e = rows[0]
        mk = e.get("markets") or []
        m0 = mk[0] if mk else {}
        say(f"  FOUND {sl}: {len(mk)} markets, ${float(e.get('volume') or 0):,.0f} traded, start {str(m0.get('startDate'))[:16]} end {str(m0.get('endDate'))[:16]}, "
            f"fee {m0.get('feeType')} {json.dumps(m0.get('feeSchedule'))}, tick {m0.get('orderPriceMinTickSize')}, rewards min {m0.get('rewardsMinSize')} "
            f"spread {m0.get('rewardsMaxSpread')}, settles on {str(m0.get('resolutionSource'))[:70]} | {str(m0.get('description'))[:260]!r}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "scan"
    arg = None
    if "_" in cmd:
        cmd, arg = cmd.split("_", 1)
    {"scan": scan}[cmd]()
