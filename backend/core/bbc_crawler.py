import os
import sys
import django
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Django 設定
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Article


def fetch_bbc_from_rss(category='world', limit=10):
    rss_feeds = {
        'world': 'http://feeds.bbci.co.uk/news/world/rss.xml',
        'business': 'http://feeds.bbci.co.uk/news/business/rss.xml',
        'technology': 'http://feeds.bbci.co.uk/news/technology/rss.xml',
        'entertainment_and_arts': 'http://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml',
        'sport': 'http://feeds.bbci.co.uk/sport/rss.xml',
    }

    feed_url = rss_feeds.get(category)
    if not feed_url:
        print(f"❌ 不支援的分類：{category}")
        return

    print(f"🌍 正在透過 RSS 爬取 BBC 分類：{category} ...")
    res = requests.get(feed_url)
    soup = BeautifulSoup(res.content, 'xml')
    items = soup.find_all('item')[:limit]

    added = 0
    for item in items:
        title = item.title.get_text(strip=True)
        link = item.link.get_text(strip=True)

        if Article.objects.filter(title=title).exists() or Article.objects.filter(url=link).exists():
            print(f"⚠️ 已存在，跳過：{title}")
            continue

        try:
            article_res = requests.get(link)
            article_soup = BeautifulSoup(article_res.text, 'html.parser')
            paragraphs = article_soup.select("main p") or article_soup.select("article p")
            content = '\n'.join(p.get_text(strip=True) for p in paragraphs)
        except Exception as e:
            print(f"⚠️ 抓取失敗：{title}，錯誤：{e}")
            continue

        if not content.strip():
            print(f"⚠️ 文章內容為空，跳過：{title}")
            continue

        summary = content[:150] + '...' if len(content) > 150 else content

        Article.objects.create(
            title=title,
            summary=summary,
            content=content,
            url=link,
            source='BBC',
            category=category,
            published_at=datetime.now()
        )
        added += 1
        print(f"✅ 新增文章：{title}")

    print(f"🎯 BBC {category} RSS 完成，共新增 {added} 篇文章。")


if __name__ == '__main__':
    categories = ['world', 'business', 'technology', 'entertainment_and_arts', 'sport']
    for cat in categories:
        fetch_bbc_from_rss(category=cat, limit=10)
