import os
import sys
import django
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# 1. 設定專案根目錄 (假設 crawler.py 在 core/，settings.py 在 backend/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# 2. 設定 Django 環境變數
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# 3. 啟動 Django
django.setup()

# 4. 匯入你的 Model
from core.models import Article


def fetch_cnn_articles(category='business', limit=10):
    base_url = "https://edition.cnn.com"
    category_url = f"{base_url}/{category}"
    headers = {"User-Agent": "Mozilla/5.0"}

    print(f"🌍 正在爬取分類：{category} ...")
    response = requests.get(category_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # CNN 標題選擇器 (最新)
    headline_tags = soup.select('.container_lead-plus-headlines__headline span')

    added_count = 0
    for headline in headline_tags:
        if added_count >= limit:
            break

        title = headline.get_text(strip=True)
        if not title:
            continue

        # 找到該標題對應的 <a> 連結
        link_tag = headline.find_parent('a')
        if not link_tag:
            continue

        href = link_tag.get('href')
        if not href.startswith('/'):
            continue

        url = base_url + href

        # 避免重複
        if Article.objects.filter(title=title).exists() or Article.objects.filter(url=url).exists():
            print(f"⚠️ 文章已存在，跳過：{title}")
            continue

        # 抓取文章內容
        article_res = requests.get(url, headers=headers)
        article_soup = BeautifulSoup(article_res.text, 'html.parser')
        paragraphs = article_soup.select("article p") or article_soup.select("div.l-container p")
        content = '\n'.join(p.get_text(strip=True) for p in paragraphs)

        if not content.strip():
            print(f"⚠️ 文章內容為空，跳過：{title}")
            continue

        summary = content[:150] + '...' if len(content) > 150 else content

        # 儲存到資料庫
        Article.objects.create(
            title=title,
            summary=summary,
            content=content,
            url=url,
            source='CNN',
            category=category,
            published_at=datetime.now()
        )
        added_count += 1
        print(f"✅ 新增文章：{title}")

    print(f"🎯 {category} 類別新增完成，共新增 {added_count} 篇文章。")


# 使用方式: python cnn_crawler.py
if __name__ == '__main__':
    categories = ['world', 'business', 'tech', 'entertainment', 'sport']
    for cat in categories:
        fetch_cnn_articles(category=cat, limit=10)
