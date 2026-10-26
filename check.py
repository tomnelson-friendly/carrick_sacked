"""Checks BBC Sport RSS feeds for news about Michael Carrick and writes status.json."""
import json, re, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

FEEDS = [
    "https://feeds.bbci.co.uk/sport/football/teams/manchester-united/rss.xml",
    "https://feeds.bbci.co.uk/sport/football/premier-league/rss.xml",
    "https://feeds.bbci.co.uk/sport/football/rss.xml",
]
SUBJECT = re.compile(r"\bcarrick\b", re.I)
# Words that mean it has actually happened
CONFIRMED = re.compile(r"\b(sacked|sacks|(?:united|utd) sack|dismissed|parted company|part company|leaves|has left|departs|relieved of)\b", re.I)
# Words that mean it's still only talk
HEDGES = re.compile(r"\?|\b(could|would|will|set to|expected|fears?|facing|faces|future|pressure|talks?|if|verdict|should|must|calls? for|urged|backed|why)\b", re.I)

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "carrick-tracker/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return ET.fromstring(r.read())

def items():
    seen, out = set(), []
    for url in FEEDS:
        try:
            root = fetch(url)
        except Exception as e:
            print(f"skip {url}: {e}")
            continue
        for it in root.iter("item"):
            title = (it.findtext("title") or "").strip()
            desc = (it.findtext("description") or "").strip()
            link = (it.findtext("link") or "").strip()
            if not SUBJECT.search(title + " " + desc) or link in seen:
                continue
            seen.add(link)
            try:
                when = parsedate_to_datetime(it.findtext("pubDate")).astimezone(timezone.utc).isoformat()
            except Exception:
                when = ""
            out.append({"title": title, "summary": desc, "link": link, "published": when})
    return sorted(out, key=lambda x: x["published"], reverse=True)

def is_confirmed(item):
    title = item["title"]
    return bool(CONFIRMED.search(title)) and not HEDGES.search(title)

def main():
    try:
        with open("status.json") as f:
            old = json.load(f)
    except Exception:
        old = {}
    news = items()
    hit = next((n for n in news if is_confirmed(n)), None)
    status = {
        # Once sacked, stay sacked even after the story drops out of the feed
        "sacked": bool(hit) or old.get("sacked", False),
        "confirmed_by": hit or old.get("confirmed_by"),
        "headlines": news[:8] or old.get("headlines", []),
        "checked": datetime.now(timezone.utc).isoformat(timespec="minutes"),
    }
    with open("status.json", "w") as f:
        json.dump(status, f, indent=2)
    print("sacked:", status["sacked"], "| headlines:", len(news))

if __name__ == "__main__":
    main()
