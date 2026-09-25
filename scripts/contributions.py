#!/usr/bin/env python3
"""Generate a self-hosted contribution calendar from GitHub's public profile data."""
from datetime import date, timedelta
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen

USER = "talh4tr"
OUT = Path("assets/contributions.svg")
COLORS = ["#1c2632", "#144a50", "#1b777a", "#21a69d", "#52e0bd"]
MONTHS = ["Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"]

class Days(HTMLParser):
    def __init__(self):
        super().__init__()
        self.days = {}

    def handle_starttag(self, tag, attrs):
        if tag != "td":
            return
        a = dict(attrs)
        if "ContributionCalendar-day" in a.get("class", "") and "data-date" in a:
            self.days[date.fromisoformat(a["data-date"])] = min(4, max(0, int(a.get("data-level", "0"))))

request = Request(f"https://github.com/users/{USER}/contributions", headers={"User-Agent": "profile-contribution-calendar/1.0"})
with urlopen(request, timeout=25) as response:
    parser = Days()
    parser.feed(response.read().decode("utf-8"))
if len(parser.days) < 300:
    raise SystemExit(f"Contribution data incomplete ({len(parser.days)} dates); keeping the existing SVG.")

end = max(parser.days)
start = min(parser.days)
first_sunday = start - timedelta(days=(start.weekday() + 1) % 7)
weeks = (end - first_sunday).days // 7 + 1
step, size, left, top = 17, 12, 68, 78
width = max(980, left + weeks * step + 34)
parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="264" viewBox="0 0 {width} 264" role="img" aria-labelledby="title desc">',
    '<title id="title">GitHub katkı takvimi</title>',
    f'<desc id="desc">{escape(USER)} için {start.isoformat()} ile {end.isoformat()} arasındaki katkı yoğunluğu.</desc>',
    '<rect width="100%" height="100%" rx="20" fill="#0e1723"/>',
    '<rect x="1" y="1" width="99.8%" height="262" rx="19" fill="none" stroke="#263745"/>',
    '<text x="30" y="38" fill="#ebf5f3" font-size="19" font-family="Arial, sans-serif" font-weight="bold">GitHub etkinliği</text>',
    f'<text x="{width-30}" y="37" text-anchor="end" fill="#82a6ab" font-size="12" font-family="Arial, sans-serif">son 12 ay · {end.isoformat()}</text>']
for weekday, label in [(1, "Pzt"), (3, "Çar"), (5, "Cum")]:
    parts.append(f'<text x="30" y="{top+weekday*step+10}" fill="#829aa3" font-size="11" font-family="Arial, sans-serif">{label}</text>')
last_month = None
for week in range(weeks):
    sunday = first_sunday + timedelta(days=week*7)
    if sunday.month != last_month and week < weeks-2:
        parts.append(f'<text x="{left+week*step}" y="65" fill="#92adb4" font-size="11" font-family="Arial, sans-serif">{MONTHS[sunday.month-1]}</text>')
        last_month = sunday.month
    for weekday in range(7):
        day = sunday + timedelta(days=weekday)
        if day not in parser.days:
            continue
        x, y = left+week*step, top+weekday*step
        parts.append(f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="3" fill="{COLORS[parser.days[day]]}"/>')
parts += ['<text x="30" y="231" fill="#829aa3" font-size="11" font-family="Arial, sans-serif">Az</text>']
for i, color in enumerate(COLORS):
    parts.append(f'<rect x="{56+i*17}" y="221" width="12" height="12" rx="3" fill="{color}"/>')
parts += ['<text x="151" y="231" fill="#829aa3" font-size="11" font-family="Arial, sans-serif">Çok</text>',
    f'<text x="{width-30}" y="231" text-anchor="end" fill="#82a6ab" font-size="11" font-family="Arial, sans-serif">Kaynak: GitHub · Günlük güncellenir</text>', '</svg>']
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(parts)+"\n", encoding="utf-8")
print(f"Generated {OUT} from {len(parser.days)} days")
