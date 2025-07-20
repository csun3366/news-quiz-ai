from django.db import models

class Article(models.Model):
    title = models.CharField(max_length=300, unique=True)  # 標題，避免重複
    summary = models.TextField(blank=True)                 # 摘要可留空
    content = models.TextField()                           # 內文
    url = models.URLField(unique=True)                     # 原始文章連結
    category = models.CharField(max_length=50)             # 分類，如 world, tech...
    published_at = models.DateTimeField()                  # 爬到時的時間

    def __str__(self):
        return f"[{self.category}] {self.title}"