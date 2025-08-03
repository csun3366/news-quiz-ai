from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Article(models.Model):
    title = models.CharField(max_length=300, unique=True)  # 標題，避免重複
    summary = models.TextField(blank=True)                 # 摘要可留空
    content = models.TextField()                           # 內文
    url = models.URLField(unique=True)                     # 原始文章連結
    source = models.CharField(max_length=50, default='CNN')
    category = models.CharField(max_length=50)             # 分類，如 world, tech...
    published_at = models.DateTimeField()                  # 爬到時的時間

    def __str__(self):
        return f"[{self.category}] {self.title}"

class SubscriptionPlan(models.TextChoices):
    FREE = 'free', '免費版'
    STANDARD = 'standard', '標準版'
    PREMIUM = 'premium', '旗艦版'

class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.CharField(max_length=20, choices=SubscriptionPlan.choices, default=SubscriptionPlan.FREE)
    article_read_count = models.PositiveIntegerField(default=0)
    subscribed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)