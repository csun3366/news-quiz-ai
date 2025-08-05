from datetime import timedelta
from django.dispatch import receiver
from allauth.account.signals import user_logged_in, user_signed_up
from .models import Member
from django.utils import timezone

@receiver(user_logged_in)
@receiver(user_signed_up)
def create_or_update_member(sender, request, user, **kwargs):
    print("[INFO]: User login")
    member, created = Member.objects.get_or_create(user=user)

    # 初次註冊：設為免費會員
    if created:
        member.plan = 'free'
        member.article_read_count = 3
        member.subscribed_at = timezone.now()
        member.expires_at = member.subscribed_at + timedelta(days=30)
        member.save()

    elif member.expires_at and member.expires_at < timezone.now():
        member.plan = 'free'
        member.subscribed_at = timezone.now()
        member.expires_at = member.subscribed_at + timedelta(days=30)
        member.article_read_count = 3
        member.save()