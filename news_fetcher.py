import os, json, feedparser, requests

# 1) Ayarlar
RSS_FEEDS   = json.load(open('feeds.json'))
WEBHOOK     = os.environ['DISCORD_WEBHOOK']
KEYWORDS    = ['artificial intelligence','machine learning','deep learning',
               'neural network','ai ','gpt','transformer']
LAST_FILE   = 'last_urls.json'

# 2) Önceki hali oku
last_map = json.load(open(LAST_FILE)) if os.path.exists(LAST_FILE) else {}

updated = False

for feed_url in RSS_FEEDS:
    feed = feedparser.parse(feed_url)
    if not feed.entries: continue

    latest = feed.entries[0]
    url, title, desc = latest.link, latest.title.lower(), (latest.summary or '').lower()

    # 3) Filtre: en az bir keyword eşleşmeli
    if not any(k in title or k in desc for k in KEYWORDS):
        continue

    if last_map.get(feed_url) == url:
        continue

    # 4) Gönder
    requests.post(WEBHOOK, json={'content': f'**{latest.title}**\n{url}'}).raise_for_status()
    last_map[feed_url] = url
    updated = True
    # eğer feed başına sadece 1 haber yollayacaksan:
    # break

# 5) Güncelle ve commit et (aynı önceki örnekteki gibi)
if updated:
    with open(LAST_FILE, 'w') as f:
        json.dump(last_map, f, indent=2)
    # … GitHub commit kısmı …
