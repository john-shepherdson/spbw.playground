"""Parse the hand-maintained event tables on the live events pages.

Each event is a table with rows Event, Date/Time, Venue, Details, Contact,
under a 'Month YYYY' heading. Yields dicts with start/end dates, optional start
time, venue and the raw Details and Contact HTML. Years are taken from the
heading and checked against any weekday named in the text.
"""
import datetime as dt
import html
import re

MONTHS = {m: i for i, m in enumerate(
    "january february march april may june july august september october november december".split(), 1)}
MON = "(" + "|".join(MONTHS) + ")"
WEEKDAYS = {d: i for i, d in enumerate("monday tuesday wednesday thursday friday saturday sunday".split())}
ORD = r"(?:\s*(?:st|nd|rd|th))?"
RANGE = re.compile(r"(\d{1,2})" + ORD + r"\s*(?:to|-|&|and)\s*(\d{1,2})" + ORD + r"\b(?!\s*[.:]\d)", re.I)
DAY_MON = re.compile(r"\b(\d{1,2})" + ORD + r"\s+(?:of\s+)?" + MON + r"\b", re.I)
MON_DAY = re.compile(r"\b" + MON + r"\s+(\d{1,2})" + ORD + r"\b", re.I)
DAY_ONLY = re.compile(r"\b(\d{1,2})\s*(?:st|nd|rd|th)\b", re.I)
TIME_COLON = re.compile(r"\b(\d{1,2})[.:](\d{2})\b")
TIME_AMPM = re.compile(r"\b(\d{1,2})(?:[.:](\d{2}))?\s*(am|pm)\b", re.I)
HEAD = re.compile(r"<h[1-6][^>]*>\s*" + MON + r"\s+(20\d\d)\s*</h[1-6]>", re.I)


def text(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


CLOSING = re.compile(r"(?:clos\w*|until|till|finish\w*|ends?)\W*$", re.I)


def _time(s):
    """First start time in the text, ignoring closing or end times."""
    found = []
    for m in TIME_AMPM.finditer(s):
        h, mi, ap = int(m.group(1)), int(m.group(2) or 0), m.group(3).lower()
        found.append((m.start(), dt.time(h % 12 + (12 if ap == "pm" else 0), mi)))
    ampm_starts = {pos for pos, _ in found}
    for m in TIME_COLON.finditer(s):
        if m.start() not in ampm_starts and int(m.group(1)) < 24 and int(m.group(2)) < 60:
            found.append((m.start(), dt.time(int(m.group(1)), int(m.group(2)))))
    for m in re.finditer(r"\bnoon\b", s, re.I):
        found.append((m.start(), dt.time(12, 0)))
    for pos, t in sorted(found):
        if not CLOSING.search(s[max(0, pos - 15):pos]):
            return t
    return None


def _date(s, hy, hm):
    """Return (start, end, weekday_ok) or None. hy/hm: heading year and month."""
    mon = day = end_day = None
    r = RANGE.search(s)
    m1, m2 = DAY_MON.search(s), MON_DAY.search(s)
    if m1:
        day, mon = int(m1.group(1)), MONTHS[m1.group(2).lower()]
    elif m2:
        day, mon = int(m2.group(2)), MONTHS[m2.group(1).lower()]
    elif DAY_ONLY.search(s):
        day, mon = int(DAY_ONLY.search(s).group(1)), hm
    if day is None:
        return None
    if r and int(r.group(1)) == day and int(r.group(2)) > day:
        end_day = int(r.group(2))
    days = [int(x) for x in DAY_ONLY.findall(s)]
    if len(days) > 1 and mon and max(days) - min(days) <= 7 and end_day is None:  # e.g. 29th, 30th & 31st May
        day, end_day = min(days), max(days)
    wd = next((WEEKDAYS[w] for w in WEEKDAYS if re.search(r"\b" + w, s, re.I)), None)
    for year in (hy, hy - 1, hy + 1):
        try:
            d = dt.date(year, mon, day)
        except ValueError:
            continue
        if wd is None or d.weekday() == wd:
            end = dt.date(year, mon, end_day) if end_day else None
            return d, end, True
    try:
        return dt.date(hy, mon, day), None, False
    except ValueError:
        return None


def parse(page_html, source):
    events, bad = [], []
    pos = [(m.start(), "h", m) for m in HEAD.finditer(page_html)]
    pos += [(m.start(), "t", m) for m in re.finditer(r"<table.*?</table>", page_html, re.S)]
    hy = hm = None
    for _, kind, m in sorted(pos, key=lambda x: x[0]):
        if kind == "h":
            hm, hy = MONTHS[m.group(1).lower()], int(m.group(2))
            continue
        rows = {}
        for r in re.findall(r"<tr.*?</tr>", m.group(0), re.S):
            cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r, re.S)
            if len(cells) >= 2:
                rows[text(cells[0]).strip(": ").lower()] = cells[1].strip()
        if "event" not in rows or hy is None:
            continue
        title = text(rows["event"])
        when = text(rows.get("date/time", rows.get("date", "")))
        found = _date(when, hy, hm) or _date(title, hy, hm)
        if not found:
            bad.append((source, title, when))
            continue
        start, end, ok = found
        events.append({"title": title, "start": start.isoformat(), "end": end.isoformat() if end else None,
                       "time": (_time(when) or dt.time(0, 0)).strftime("%H:%M") if _time(when) else None,
                       "when": when, "venue": text(rows.get("venue", "")), "details": rows.get("details", ""),
                       "contact": rows.get("contact", ""), "source": source, "weekday_ok": ok})
    return events, bad
