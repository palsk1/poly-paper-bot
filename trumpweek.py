"""Live side of the Trump weekly words rule (speeches.py, backtest/speeches.md, backtest/speeches_kalshi.md).

Keeps Trump's own words of the last ~10 weeks in state/trumpweek/ (one small file per day, from Roll Call Factba.se
transcripts) and answers: in how many of the 8 weeks before now did he say this word? bot.py asks it for the two paper
tracks trump_week (Polymarket) and trump_week_k (Kalshi). Paper only.

  python3 trumpweek.py seed   # one-off: fill state/trumpweek/ from the price-store copy bt_cache/sp
  python3 trumpweek.py sync   # read Roll Call's newest records now
"""
import datetime, glob, json, os, re, sys, time

import speeches as sp

HERE = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.join(HERE, "state", "trumpweek")
IDX = os.path.join(DIR, "index.json")
KEEP_DAYS = 75          # 8 weeks of record + room
SKIP_TYPES = ("Op-Ed", "Position Paper", "Official Document")
WEEK = 7 * 86400


def _idx():
    try:
        with open(IDX) as f:
            d = json.load(f)
    except (OSError, ValueError):
        d = {}
    d.setdefault("seen", {})     # document id -> its day (records we have read, or that carry no transcript)
    d.setdefault("fail", {})     # document id -> failed tries
    return d


def _save_idx(d):
    os.makedirs(DIR, exist_ok=True)
    with open(IDX + ".tmp", "w") as f:
        json.dump(d, f, separators=(",", ":"), sort_keys=True)
    os.replace(IDX + ".tmp", IDX)


def _day_path(day):
    return os.path.join(DIR, f"{day}.json.gz")


def trump_text(blocks):
    return " ".join(b[2] for b in blocks if b[0] == "Donald Trump").lower().replace("’", "'")


def transcript_blocks(slug, url):
    """[speaker, None, text] per paragraph. Bug fix 2026-11-24: since about 18 Nov Roll Call's transcript pages load
    their text in the browser, so the page itself has none; the same JSON the page uses has every paragraph.
    Falls back to reading the page the old way."""
    if slug:
        j = json.loads(sp.raw(f"https://rollcall.com/api/factbase/transcripts?person=trump&slug={slug}", 60))
        rows = j.get("data") if isinstance(j, dict) else None
        if isinstance(rows, list) and rows and isinstance(rows[0], dict) and "text" in rows[0]:
            return [[str(r.get("speaker") or "").strip(), None, str(r.get("text") or "")] for r in rows]
    return sp.parse(sp.raw(url, 60))


def _add(day, doc, text):
    p = _day_path(day)
    cur = sp.rj(p, {}) or {}
    cur[str(doc)] = text
    sp.wj(p, cur)


def _prune(d, today):
    cut = (today - datetime.timedelta(days=KEEP_DAYS)).isoformat()
    for p in glob.glob(os.path.join(DIR, "*.json.gz")):
        if os.path.basename(p)[:10] < cut:
            os.remove(p)
    d["seen"] = {k: v for k, v in d["seen"].items() if v >= cut}
    d["fail"] = {k: v for k, v in d["fail"].items() if k not in d["seen"]}


def sync(max_pages=8, budget_s=150):
    """Read Roll Call's newest Trump records and save the transcripts we don't have yet.
    Returns (ok, new): ok is False when the list could not be read (then the record may be stale: no bets)."""
    d = _idx()
    today = datetime.datetime.now(datetime.timezone.utc).date()
    cut = (today - datetime.timedelta(days=KEEP_DAYS)).isoformat()
    t0, new, todo = time.time(), 0, []
    for page in range(1, max_pages + 1):
        try:
            res = json.loads(sp.raw(sp.API.format(page), 40))
        except Exception as e:
            print(f"trumpweek: list page {page} failed: {str(e)[:100]}")
            if page == 1:
                return False, 0
            break
        rows = res.get("data") or []
        fresh = 0
        for x in rows:
            doc, day = str(x.get("document_id")), str(x.get("date") or "")[:10]
            if not day or day < cut or doc in d["seen"]:
                continue
            fresh += 1
            if "no-transcript" in str(x.get("slug") or "") or x.get("record_type") in SKIP_TYPES or not x.get("factbase_url"):
                d["seen"][doc] = day
                continue
            if d["fail"].get(doc, 0) >= 6:      # six scans in a row could not read it: give up on this one
                d["seen"][doc] = day
                continue
            todo.append((doc, day, x["factbase_url"], x.get("slug")))
        if not rows or not fresh:
            break
    for doc, day, url, slug in sorted(todo, key=lambda r: r[1], reverse=True):   # newest first: freshness is what gates bets
        if time.time() - t0 > budget_s:
            print(f"trumpweek: out of time, {len(todo) - new} transcripts left for the next scan")
            break
        try:
            blocks = transcript_blocks(slug, url)
            if not blocks:
                raise ValueError("no paragraphs found (page layout changed?)")
        except Exception as e:
            d["fail"][doc] = d["fail"].get(doc, 0) + 1
            print(f"trumpweek: transcript {doc} failed: {str(e)[:80]}")
            continue
        _add(day, doc, trump_text(blocks))
        d["seen"][doc] = day
        new += 1
    _prune(d, today)
    d["synced"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    _save_idx(d)
    return True, new


class Words(sp.Words):
    """speeches.Words, fed from state/trumpweek/ instead of the big history files"""

    def __init__(self):
        import postwords as pw
        days = {}
        for p in sorted(glob.glob(os.path.join(DIR, "*.json.gz"))):
            y, mo, dd = map(int, os.path.basename(p)[:10].split("-"))
            txt = " \n ".join(v for v in (sp.rj(p, {}) or {}).values() if v)
            if txt:
                days[int(datetime.datetime(y, mo, dd, tzinfo=pw.ET).timestamp())] = txt
        self.days = days
        self.keys = sorted(days)
        self.n = len(days)
        self.c = {}

    def fresh(self, t, max_gap_days=5, min_days=30):
        """is the record good enough to bet on: 30+ days with his words, the newest at most 5 days old"""
        return len(self.keys) >= min_days and t - self.keys[-1] <= max_gap_days * 86400

    def chance(self, item, t, start, end, n=8):
        """chance he says it between max(t, start) and end, from the 8 weeks before t. Returns (chance, weeks said)."""
        qw, k = self.record(item, t, n)
        return 1 - (1 - qw) ** (max(end - max(t, start), 3600) / WEEK), k


def seed(since=None):
    """one-off: copy the last KEEP_DAYS days out of bt_cache/sp (the history files) into state/trumpweek/"""
    L = sp.rj(sp.cache("list.json.gz"), {})
    T = {}
    for p in sorted(glob.glob(sp.cache("texts_*.json.gz"))):
        T.update(sp.rj(p, {}))
    last = max(L[k]["date"] for k in T)
    y, mo, dd = map(int, last.split("-"))
    since = since or (datetime.date(y, mo, dd) - datetime.timedelta(days=KEEP_DAYS)).isoformat()
    d = _idx()
    by = {}
    for doc, blocks in T.items():
        day = L[doc]["date"]
        if day >= since:
            by.setdefault(day, {})[str(doc)] = trump_text(blocks)
            d["seen"][str(doc)] = day
    for doc, r in L.items():        # records without a transcript: nothing to fetch later
        if (r["date"] or "") >= since and str(doc) not in d["seen"] and ("no-transcript" in (r["slug"] or "") or r["record_type"] in SKIP_TYPES):
            d["seen"][str(doc)] = r["date"]
    for day, v in by.items():
        sp.wj(_day_path(day), v)
    _save_idx(d)
    print(f"seeded {len(by)} days, {sum(len(v) for v in by.values())} transcripts, {since} to {last}")


if __name__ == "__main__":
    a = sys.argv[1] if len(sys.argv) > 1 else "sync"
    if a == "seed":
        seed()
    else:
        print(sync())
        W = Words()
        print("days with words", W.n, "newest", time.strftime("%Y-%m-%d", time.gmtime(W.keys[-1] + 43200)) if W.keys else None)
