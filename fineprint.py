"""Fine-print flags (2026-11-09, rules.py / backtest/rules.md): text a trader can read BEFORE a market ends that
predicts a later UMA dispute. Plain text in, set of flag names out. No imports from bot, so bot.py and rules.py can
both use it.

Backtest (124,260 finished markets): markets with none of the 7 trouble flags were disputed 0.4 times per 1,000,
markets with 4+ flags 51 times per 1,000.
"""
import re

ADDED = re.compile(r"(?:^|\n|\.\s)\s*[\(\[]?\s*(?:update|updated|clarification|edit|edited|additional context)\b[^:\n]{0,40}:", re.I)
MONTHS = "jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec"
DATE_RX = re.compile(rf"\b({MONTHS})[a-z]*\.?\s+(\d{{1,2}})\b", re.I)
EXCL = re.compile(r"will not count|won't count|does not count|do not count|not be considered|will not qualify|"
                  r"does not qualify|do not qualify|not sufficient|insufficient|excluding|excluded|regardless of|"
                  r"irrespective of|shall not|will not be counted|not be included|only count|only .{0,30} will count", re.I)
FLAG_RX = {
    "official": re.compile(r"\bofficial(ly)?\b|\bformal(ly)?\b|\bconfirmed by\b|\bcertif", re.I),
    "announce": re.compile(r"\bannounce", re.I),
    "intent_not_enough": re.compile(r"announcement.{0,40}(alone|itself|not)|intention|plans? to .{0,40}(not|will not)|"
                                    r"must (actually|be completed|take effect)|go into effect|take effect|"
                                    r"(signed|enacted) into law", re.I),
    "consensus": re.compile(r"consensus of credible", re.I),
    "discretion": re.compile(r"discretion|ambigu|subjective|at the sole|in the spirit|may be used|may consider", re.I),
    "fifty_fifty": re.compile(r"50-50|50/50|fifty", re.I),
    "named_site": re.compile(r"https?://(?!(www\.)?(polymarket|x\.com|twitter))[\w.-]+", re.I),
}


def pre_text(d):
    """Rule text as it probably was before any clarification was added (cut at the first added note)."""
    mt = ADDED.search(d or "")
    return (d[:mt.start()] if mt else d or ""), bool(mt)


def flags(q, d):
    """Text flags a trader could compute before the end. q = title, d = rule text before added notes."""
    ql, dl = q.lower(), d.lower()
    f = set()
    for name, rx in FLAG_RX.items():
        if rx.search(dl) and not rx.search(ql):
            f.add(name)  # in the rules but not in the title: the title hides it
    if len(EXCL.findall(dl)) >= 2:
        f.add("exclusions_2plus")
    if len(d) >= 1500:
        f.add("long_rules")
    td = {(m_.group(1)[:3].lower(), int(m_.group(2))) for m_ in DATE_RX.finditer(q)}
    rd = {(m_.group(1)[:3].lower(), int(m_.group(2))) for m_ in DATE_RX.finditer(d)}
    if td and rd and not (rd <= td):
        f.add("date_gap")  # the rules name a date the title doesn't
    n = len([x for x in ("official", "announce", "intent_not_enough", "consensus", "discretion", "exclusions_2plus",
                         "date_gap") if x in f])
    if n >= 3:
        f.add("tricky_3plus")
    if not f & {"official", "announce", "intent_not_enough", "consensus", "discretion", "exclusions_2plus", "date_gap",
                "long_rules"}:
        f.add("plain")
    return f


TROUBLE = ("official", "announce", "intent_not_enough", "consensus", "exclusions_2plus", "date_gap", "long_rules")


def trouble_score(q, description):
    """How many of the 7 dispute-predicting flags a market has (0-7), from its title and rule text."""
    f = flags(q, pre_text(description or "")[0])
    return sum(1 for x in TROUBLE if x in f)
