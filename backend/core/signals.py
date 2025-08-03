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
        member.save()

    # 如果不是免費會員但已過期 → 自動降級
    elif member.plan != 'free' and member.expires_at and member.expires_at < timezone.now():
        member.plan = 'free'
        member.expires_at = None
        member.subscribed_at = None
        member.article_read_count = 3
        member.save()