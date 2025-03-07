from django.urls import path
from . import views

app_name = 'forums'

urlpatterns = [
    path('', views.forum_home, name='forum_home'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('category/<slug:category_slug>/topic/<slug:slug>/', views.topic_detail, name='topic_detail'),
    path('new-topic/', views.create_topic, name='create_topic'),
    path('category/<slug:category_slug>/topic/<slug:slug>/reply/', views.reply_topic, name='reply_topic'),
    path('post/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('search/', views.search, name='search'),
]
