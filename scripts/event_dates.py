"""Extract an event date (and optional end date) from a post's title or text.

Heuristic: day+month or month+day, optional year, optional day range. A missing
year resolves to the first occurrence on or after (post date - 14 days).
Returns (start, end, source) with source in {'title', 'content', None}.
"""
import datetime as dt
import html
import re

MONTHS = {m: i for i, m in enumerate(
    "january february march april may june july august september october november december".split(), 1)}
MON = r"(january|february|march|april|may|june|july|august|september|october|november|december)"
DAY = r"(\d{1,2})(?:st|nd|rd|th)?"
RANGE = r"(?:\s*(?:to|-|and|&)\s*" + DAY + r")?"
DMY = re.compile(DAY + RANGE + r"\s+(?:of\s+)?" + MON + r"(?:\s+(20\d\d))?", re.I)
MDY = re.compile(MON + r"\s+" + DAY + RANGE + r"(?:,?\s+(20\d\d))?", re.I)


def _resolve(d1, d2, month, year, posted):
    month = MONTHS[month.lower()]
    d1 = int(d1)
    d2 = int(d2) if d2 else None
    try:
        if year:
            start = dt.date(int(year), month, d1)
        else:
            start = dt.date(posted.year, month, d1)
            if start < posted - dt.timedelta(days=14):
                start = dt.date(posted.year + 1, month, d1)
        end = dt.date(start.year, month, d2) if d2 and d2 >= d1 else None
        return start, end
    except ValueError:
        return None


def _find(text, posted):
    best = []
    for m in DMY.finditer(text):
        r = _resolve(m.group(1), m.group(2), m.group(3), m.group(4), posted)
        if r:
            best.append((m.start(), r))
    for m in MDY.finditer(text):
        r = _resolve(m.group(2), m.group(3), m.group(1), m.group(4), posted)
        if r:
            best.append((m.start(), r))
    return min(best)[1] if best else None


def extract(title, content_html, posted):
    for src, text in (("title", title), ("content", re.sub(r"<[^>]+>", " ", html.unescape(content_html)))):
        r = _find(html.unescape(text), posted)
        if r:
            return r[0], r[1], src
    return None, None, None
