import feedparser
import json
import datetime
from dateutil import parser

with open("sites.json") as f:
    feeds = json.load(f)

with open("last_run.txt") as f:
    last_run_time = parser.parse(f.read().strip())

ai_keywords = ["artificial intelligence", "ai", "machine learning", "deep learning", "llm", "openai", "chatgpt"]

new_items = []

for feed_url in feeds:
    d = feedparser.parse(feed_url)
    for entry in d.entries:
        if hasattr(entry, "published"):
            published = parser.parse(entry.published)
        elif hasattr(entry, "updated"):
            published = parser.parse(entry.updated)
        else:
            continue

        if published <= last_run_time:
            continue

        content = (entry.title + " " + entry.get("summary", "")).lower()

        if any(keyword in content for keyword in ai_keywords):
            new_items.append({
                "title": entry.title,
                "url": entry.link,
                "summary": entry.get("summary", ""),
                "published": published.isoformat()
            })

# Write pending.json
with open("pending.json", "w") as f:
    json.dump(new_items, f, indent=2)

# Update last_run.txt
with open("last_run.txt", "w") as f:
    f.write(datetime.datetime.utcnow().isoformat() + "Z")
