"""Keeps the live part of LEARNINGS.md up to date (research only, never trades).

    python3 learnings.py            # refresh the block between the AUTO markers in LEARNINGS.md
    python3 learnings.py selftest   # offline check

What it writes, from files already in the repo:
  - live numbers of the candidates (state/summary.json, state/tracks.json, state/kfast_live/report.md)
  - days left until each check date
  - the ledger count (backtest/ledger.json, once exam.py from PR #66 is in)
  - a week-by-week scoreboard (one row per week, kept in state/learnings_weeks.json)

daily.yml runs it once a day after `bot.py daily`. The hand-written parts of LEARNINGS.md are never touched.
"""
import datetime as dt
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PAGE = os.path.join(ROOT, "LEARNINGS.md")
WEEKS = os.path.join(ROOT, "state", "learnings_weeks.json")
START, END = "<!-- AUTO:START (learnings.py writes this part every morning, don't edit by hand) -->", "<!-- AUTO:END -->"

DECISION_DAY = dt.date(2027, 1, 1)

# The candidates. Rules here are copies of what's locked elsewhere (PROTOCOL.md); this file only reports them.
CANDIDATES = [
    # track, plain name, check date, what decides it
    ("kc_maker_safe", "Kalshi 15-min crypto bids, spot check", dt.date(2026, 12, 1),
     "after 2,500 bets: pass if above +$0.22 per $100"),
    ("mention_no", "NO on 'will X say Y'", dt.date(2026, 12, 21), "holdout, scored once"),
    ("panic_fade_10c", "Boring side after a 10c scare", dt.date(2026, 12, 21), "holdout, scored once"),
    ("econ_fav", "Economy favorites the forecast backs", None, "not registered yet"),
    ("arb", "Same question on Kalshi and Polymarket", DECISION_DAY, "pays out on 1 Jan"),
]
KC_TARGET, KC_BAR, KC_START = 2500, 0.22, "2026-11-09T19:00"


def usd(x):
    return f"{'+' if x >= 0 else '-'}${abs(x):.2f}"


def load(path, default=None):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default


def verdict(t, few=10):
    """Same words as bot.plain_verdict (copied, so this file doesn't import the whole bot)."""
    if not t or t.get("finished", 0) < few:
        return f"Too early to tell ({(t or {}).get('finished', 0)} finished)"
    if t.get("proven"):
        return "Looks real"
    if t.get("worst_per_100", 0) > 0:
        return "Promising, needs more bets"
    if t.get("avg_per_100", 0) < 0:
        return "Losing"
    return "Ahead, but could be luck"


def kc_progress(tracks, today):
    """kc_maker_safe count toward the locked 2,500-bet look (PROTOCOL.md 5b). A peek, it doesn't count early."""
    tr = (tracks or {}).get("kc_maker_safe") or {}
    c = [r for r in tr.get("closed", []) if str(r.get("opened") or r.get("placed") or "") >= KC_START]
    n = len(c)
    cost = sum(r.get("cost") or 0 for r in c)
    pnl = sum(r.get("pnl") or 0 for r in c)
    lost = sum(1 for r in c if (r.get("pnl") or 0) < 0)
    last = max((str(r.get("closed_at") or "") for r in c), default="")
    try:
        span = (dt.datetime.fromisoformat(last[:16]) - dt.datetime.fromisoformat(KC_START)).total_seconds() / 86400
    except ValueError:
        span = 0
    per_day = n / span if span >= 0.5 else 0
    eta = today + dt.timedelta(days=round((KC_TARGET - n) / per_day)) if per_day and n < KC_TARGET else None
    return {"n": n, "lost": lost, "pnl": pnl, "per100": (pnl / cost * 100) if cost else 0.0,
            "per_day": per_day, "eta": eta}


def kfast_line(path):
    """First 'main' row of the fast Kalshi report (10 contracts), as plain text."""
    try:
        txt = open(path).read()
    except Exception:
        return None
    m = re.search(r"^\| (Wait at 99\.8c[^|]*)\| (\d+) \| (\d+) \| (\d+) \| (\d+) \|[^|]*\| \$([+-][\d.]+) \| \$([+-][\d.]+) \|",
                  txt, re.M)
    if not m:
        return None
    return {"test": m.group(1).strip(), "bought": int(m.group(3)), "lost": int(m.group(5)),
            "pnl": float(m.group(6)), "per100": float(m.group(7))}


def ledger_counts(path):
    L = load(path)
    if not L:
        return None
    rows = L.get("rows", [])
    dropped = sum(1 for r in rows if str(r.get("status", "")).startswith("dropped"))
    real = sum(1 for r in rows if r.get("verdict") == "Looks real")
    return {"ideas": len(rows), "dropped": dropped, "real": real, "open": len(rows) - dropped}


def when(d, today):
    if not d:
        return "no date"
    left = (d - today).days
    return f"{d.day} {d.strftime('%b')} ({left} days)" if left > 0 else f"{d.day} {d.strftime('%b')} (due now)"


def week_key(today):
    y, w, _ = today.isocalendar()
    return f"{y}-W{w:02d}"


def build(today, summary, tracks, kfast, ledger, weeks):
    st = (summary or {}).get("tracks", {})
    out = [START, "", f"## Live numbers (updated {today.isoformat()})", ""]
    left = (DECISION_DAY - today).days
    out.append(f"**{left} days left** until the money decision on 1 Jan 2027.")
    if ledger:
        out.append(f"Ideas tried so far: **{ledger['ideas']}**. Dropped: {ledger['dropped']}. "
                   f"Still in play: {ledger['open']}. Looking real: **{ledger['real']}**.")
    out += ["", "| Candidate | Finished bets | Won / lost | P&L per $100 | What it means | Check |",
            "|---|---|---|---|---|---|"]
    row_week = {}
    for key, name, d, rule in CANDIDATES:
        s = st.get(key) or {}
        t = s.get("trust_paper") or s.get("trust") or {}
        n = s.get("closed", 0)
        if key == "arb":
            lots = list(((tracks or {}).get("arb") or {}).get("arbs", {}).values())
            cost = sum(a.get("cost") or 0 for a in lots)
            pays = sum(a.get("shares") or 0 for a in lots)
            mean = (f"{len(lots)} sets cost ${cost:.2f} and pay ${pays:.2f} if both sites agree. "
                    "Nothing to judge before then.")
            out.append(f"| {name} (`{key}`) | {n} | - | {usd((pays - cost) / cost * 100) if cost else '-'} locked in "
                       f"| {mean} | {when(d, today)}: {rule} |")
            row_week[key] = f"{len(lots)} sets"
            continue
        per = t.get("avg_per_100", 0.0)
        out.append(f"| {name} (`{key}`) | {n} | {s.get('wins', 0)} / {s.get('losses', 0)} | "
                   f"{usd(per) if n else '-'} | {verdict(t)} | {when(d, today)}: {rule} |")
        row_week[key] = f"{n} bets, {usd(per)}" if n else "0 bets"
    kc = kc_progress(tracks, today)
    out += ["", f"**kc_maker_safe toward its locked test:** {kc['n']:,} of {KC_TARGET:,} bets, {kc['lost']} lost, "
                f"{usd(kc['pnl'])} so far ({usd(kc['per100'])} per $100; the bar is +${KC_BAR:.2f}). "
                f"About {kc['per_day']:.0f} bets a day"
                + (f", so the look is due about {kc['eta'].day} {kc['eta'].strftime('%b')}." if kc["eta"] else ".")
                + " This is only a peek: the number counts once, at 2,500."]
    if kfast:
        out.append(f"**Fast Kalshi bot, last 45 seconds** (main test \"{kfast['test']}\", 10 contracts): "
                   f"{kfast['bought']} bought, {kfast['lost']} lost, {usd(kfast['pnl'])} "
                   f"({usd(kfast['per100'])} per $100). Full table: `state/kfast_live/report.md`.")
    # the weekly scoreboard: this week's row is overwritten every day, so each past week keeps its last value
    weeks = dict(weeks or {})
    weeks[week_key(today)] = {"date": today.isoformat(), **row_week,
                              "kc_lock": f"{kc['n']} bets, {usd(kc['per100'])}"}
    keys = [c[0] for c in CANDIDATES if c[0] != "arb"]
    out += ["", "### Week by week (numbers as of the last day of each week, all bets so far)", "",
            "| Week | " + " | ".join(f"`{k}`" for k in keys) + " |", "|---|" + "---|" * len(keys)]
    for wk in sorted(weeks)[-10:]:
        out.append(f"| {wk} | " + " | ".join(weeks[wk].get(k, "-") for k in keys) + " |")
    out += ["", "Too few bets means luck. A row only matters once a track has 30+ finished bets.", "", END]
    return "\n".join(out), weeks


def refresh(page=PAGE, today=None, root=ROOT, weeks_path=WEEKS):
    today = today or dt.datetime.now(dt.timezone.utc).date()
    summary = load(os.path.join(root, "state", "summary.json"), {})
    tracks = load(os.path.join(root, "state", "tracks.json"), {})
    kfast = kfast_line(os.path.join(root, "state", "kfast_live", "report.md"))
    ledger = ledger_counts(os.path.join(root, "backtest", "ledger.json"))
    block, weeks = build(today, summary, tracks, kfast, ledger, load(weeks_path, {}))
    txt = open(page).read()
    if START not in txt or END not in txt:
        raise SystemExit("LEARNINGS.md has no AUTO markers, nothing written")
    a, b = txt.index(START), txt.index(END) + len(END)
    new = txt[:a] + block + txt[b:]
    if new != txt:
        with open(page, "w") as f:
            f.write(new)
    with open(weeks_path, "w") as f:
        json.dump(weeks, f, indent=1, sort_keys=True)
    return block


def selftest():
    import tempfile
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, "state", "kfast_live"))
    os.makedirs(os.path.join(d, "backtest"))
    json.dump({"tracks": {"kc_maker_safe": {"closed": 200, "wins": 198, "losses": 2, "pnl": 1.0,
                                            "trust_paper": {"finished": 200, "avg_per_100": 0.05, "worst_per_100": -3}},
                          "arb": {"closed": 0, "open": 4, "pnl": 0.5}}},
              open(os.path.join(d, "state", "summary.json"), "w"))
    closed = [{"opened": f"2026-11-1{i % 3}T10:00", "closed_at": f"2026-11-1{i % 3}T10:15", "cost": 9.9,
               "pnl": 0.1 if i else -9.8} for i in range(300)]
    json.dump({"kc_maker_safe": {"closed": closed + [{"opened": "2026-11-08T00:00", "cost": 9.9, "pnl": -9.9}]}},
              open(os.path.join(d, "state", "tracks.json"), "w"))
    open(os.path.join(d, "state", "kfast_live", "report.md"), "w").write(
        "| Wait at 99.8c, 45 s left (z 2+) (main) | 135 | 24 | 24 | 0 | 99.50c | $+1.02 | $+0.43 | x |\n")
    json.dump({"rows": [{"status": "dropped"}, {"status": "lead", "verdict": "Looks real"}]},
              open(os.path.join(d, "backtest", "ledger.json"), "w"))
    page = os.path.join(d, "L.md")
    open(page, "w").write(f"# Top\nhand text\n{START}\nSTALE-TEXT\n{END}\nfooter\n")
    wk = os.path.join(d, "state", "w.json")
    refresh(page, dt.date(2026, 11, 10), d, wk)
    refresh(page, dt.date(2026, 11, 11), d, wk)          # same week: row overwritten, not added
    refresh(page, dt.date(2026, 11, 17), d, wk)          # next week: new row
    txt = open(page).read()
    assert txt.startswith("# Top\nhand text\n") and txt.endswith("footer\n") and "STALE-TEXT" not in txt, "hand text kept"
    assert txt.count(START) == 1 and txt.count(END) == 1
    assert "300 of 2,500 bets, 1 lost" in txt, "bets before the start don't count"
    assert "45 days left" in txt and "Ideas tried so far: **2**" in txt and "Looking real: **1**" in txt
    assert "24 bought, 0 lost" in txt
    w = load(wk)
    assert sorted(w) == ["2026-W46", "2026-W47"] and w["2026-W46"]["date"] == "2026-11-11", w
    print("learnings selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["selftest"]:
        selftest()
    else:
        print(refresh())
