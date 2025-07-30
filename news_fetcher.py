import requests
import os
import json
import feedparser # RSS beslemelerini ayrıştırmak için

# Discord Webhook URL'lerini ortam değişkenlerinden alacağız
APPROVAL_WEBHOOK_URL = os.getenv('APPROVAL_WEBHOOK_URL')
NEWS_WEBHOOK_URL = os.getenv('NEWS_WEBHOOK_URL') # Şimdilik kullanılmayacak ama kalsın

# Haber kaynakları (örnekler, bunları kendi belirlediğiniz 5 sitenin RSS URL'leriyle değiştirin)
# Her bir sözlükte 'name' (site adı) ve 'rss_url' (RSS beslemesi URL'si) olmalı.
NEWS_SOURCES = [
    {"name": "Site 1 RSS", "rss_url": "https://example.com/site1/rss"},
    {"name": "Site 2 RSS", "rss_url": "https://example.com/site2/feed"},
    # Diğer 3 sitenizin RSS URL'lerini buraya ekleyin
    # Örnek: {"name": "TechCrunch AI", "rss_url": "https://techcrunch.com/category/artificial-intelligence/feed/"},
    # Örnek: {"name": "VentureBeat AI", "rss_url": "https://venturebeat.com/category/ai/feed/"},
]

# Anahtar kelimeler (Türkçe ve İngilizce olarak AI ile ilgili terimleri ekledim)
KEYWORDS = [
    "yapay zeka", "makine öğrenimi", "derin öğrenme", "sinir ağı", "algoritma",
    "AI", "artificial intelligence", "machine learning", "deep learning",
    "neural network", "algorithm", "LLM", "large language model", "büyük dil modeli"
]

def fetch_and_filter_news():
    all_news = []
    for source in NEWS_SOURCES:
        try:
            feed = feedparser.parse(source["rss_url"])
            if feed.bozo:
                print(f"Hata oluştu {source['name']} RSS beslemesini ayrıştırırken: {feed.bozo_exception}")
                continue

            for entry in feed.entries:
                title = entry.title if hasattr(entry, 'title') else 'Başlıksız'
                link = entry.link if hasattr(entry, 'link') else source["rss_url"]
                summary = entry.summary if hasattr(entry, 'summary') else ''
                
                # Başlık veya özet içinde anahtar kelime filtrelemesi
                if any(keyword.lower() in title.lower() or keyword.lower() in summary.lower() for keyword in KEYWORDS):
                    all_news.append({
                        "title": title,
                        "link": link,
                        "source": source["name"]
                    })
        except Exception as e:
            print(f"Hata oluştu {source['name']} RSS beslemesini çekerken veya işlerken: {e}")
            
    return all_news

def send_to_discord(webhook_url, content):
    if not webhook_url:
        print("Webhook URL ayarlanmadı.")
        return

    headers = {"Content-Type": "application/json"}
    payload = {"content": content}
    try:
        response = requests.post(webhook_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status() # HTTP hatalarını kontrol et (200-299 arası değilse hata fırlatır)
        print(f"Mesaj Discord'a gönderildi: {content[:50]}...")
    except requests.exceptions.RequestException as e:
        print(f"Discord'a gönderirken hata oluştu: {e}")
    except Exception as e:
        print(f"Bilinmeyen bir hata oluştu Discord'a mesaj gönderirken: {e}")


if __name__ == '__main__':
    ai_news = fetch_and_filter_news()
    if ai_news:
        for news_item in ai_news:
            message = f"**Kaynak: {news_item['source']}**\n**Başlık:** {news_item['title']}\n**Link:** {news_item['link']}"
            send_to_discord(APPROVAL_WEBHOOK_URL, message)
    else:
        print("Yeni AI haberi bulunamadı.")
