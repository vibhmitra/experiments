# converts youtube activity html file to normal csv / excel
# this is working on backup created on 20250918

from bs4 import BeautifulSoup
from dateutil import parser
import pandas as pd
import re

HTML_FILE = "My Activity.html"

rows = []

with open(HTML_FILE, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "lxml")

cards = soup.find_all("div", class_="outer-cell")

for card in cards:
    content = card.find("div", class_="mdl-typography--body-1")
    if not content:
        continue

    text = content.get_text("\n", strip=True)
    lines = text.split("\n")

    # detect activity type
    if lines[0].startswith("Watched"):
        activity = "WATCH"
        title = lines[0].replace("Watched", "").strip()
    elif lines[0].startswith("Viewed"):
        activity = "VIEWED_POST"
        title = lines[0].replace("Viewed", "").strip()
    else:
        activity = "OTHER"
        title = lines[0]

    links = content.find_all("a")
    url = links[0]["href"] if len(links) > 0 else None
    channel = links[1].get_text(strip=True) if len(links) > 1 else None

    # timestamp is last non-empty line
    raw_ts = lines[-1]
    try:
        iso_ts = parser.parse(raw_ts).isoformat()
    except Exception:
        iso_ts = None

    rows.append({
        "activity_type": activity,
        "title": title,
        "url": url,
        "channel": channel,
        "timestamp": iso_ts,
        "raw_timestamp": raw_ts
    })

df = pd.DataFrame(rows)

df.to_csv("youtube_activity.csv", index=False, encoding="utf-8")
df.to_excel("youtube_activity.xlsx", index=False)

print(f"Saved {len(df)} rows")
