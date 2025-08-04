from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api/articles/', views.get_articles_by_category),
    path('api/generate_questions/', views.generate_questions, name='generate_questions'),
    path("sitemap.xml", views.sitemap_view, name="sitemap"),
    path("robots.txt", views.robots_txt_view, name="robots"),
    path('pricing/', views.pricing, name="pricing"),
    path('account/', views.account, name="account"),
    path('create-checkout/<str:plan>/', views.create_checkout_session, name='create-checkout-session'),
    path('success/', views.checkout_success, name='checkout-success'),
    path('cancel/', views.checkout_cancel, name='checkout-cancel'),
    path('stripe-webhook/', views.stripe_webhook, name='stripe-webhook'),
]