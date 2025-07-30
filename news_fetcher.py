import os, json, feedparser, requests
from datetime import datetime, timezone
from github import Github

# Ayarlar
RSS_FEEDS      = json.load(open('feeds.json'))
WEBHOOK        = os.environ['DISCORD_WEBHOOK']
LAST_RUN_FILE  = 'last_run.txt'

# AI ile ilgili anahtar kelimeler
KEYWORDS = ['ai', 'artificial intelligence', 'machine learning', 'deep learning', 'neural network', 'nlp', 'computer vision']

# 1) Son çalıştırma zamanını oku (yoksa şimdi)
if os.path.exists(LAST_RUN_FILE):
    last_run = datetime.fromisoformat(open(LAST_RUN_FILE).read().strip())
else:
    last_run = datetime.now(timezone.utc)

new_last_run = datetime.now(timezone.utc)
sent_any = False

def contains_keyword(text):
    text = text.lower()
    return any(keyword in text for keyword in KEYWORDS)

for feed_url in RSS_FEEDS:
    feed = feedparser.parse(feed_url)
    for entry in feed.entries:
        # pubDate parse edilip datetime objesine dönüştürülüyor
        pub = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        # sadece son çalıştırmadan sonra yayınlananları al
        if pub <= last_run:
            continue

        title = entry.title
        link  = entry.link
        summary = entry.get('summary', '') or ''

        # Anahtar kelime filtresi
        combined_text = title + ' ' + summary
        if not contains_keyword(combined_text):
            continue

        # Discord’a gönder
        requests.post(WEBHOOK, json={'content': f'**{title}**\n{link}'}).raise_for_status()
        sent_any = True

# 2) Son çalıştırma zamanını güncelle
with open(LAST_RUN_FILE, 'w') as f:
    f.write(new_last_run.isoformat())

# 3) GitHub’a commit et (sadece eğer bir gönderim olduysa)
if sent_any:
    gh   = Github(os.environ['GITHUB_TOKEN'])
    repo = gh.get_repo(os.environ['GITHUB_REPOSITORY'])
    try:
        contents = repo.get_contents(LAST_RUN_FILE)
        repo.update_file(contents.path,
                         f"Update last_run to {new_last_run.isoformat()}",
                         new_last_run.isoformat(),
                         contents.sha, branch='main')
    except:
        repo.create_file(LAST_RUN_FILE,
                         f"Create last_run {new_last_run.isoformat()}",
                         new_last_run.isoformat(),
                         branch='main')
