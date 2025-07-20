from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api/articles/', views.get_articles_by_category),
    path('api/generate_questions/', views.generate_questions, name='generate_questions'),
]