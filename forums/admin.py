from django.contrib import admin
from .models import Category, Topic, Post, TopicView

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    list_filter = ('created_at',)
    ordering = ('order', 'name')

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'pinned', 'locked', 'created_at')
    list_filter = ('category', 'pinned', 'locked', 'created_at')
    search_fields = ('title', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('topic', 'author', 'created_at', 'edited')
    list_filter = ('created_at', 'edited')
    search_fields = ('content', 'author__username', 'topic__title')
    date_hierarchy = 'created_at'

@admin.register(TopicView)
class TopicViewAdmin(admin.ModelAdmin):
    list_display = ('topic', 'user', 'ip_address', 'viewed_at')
    list_filter = ('viewed_at',)
    search_fields = ('topic__title', 'user__username', 'ip_address')
    date_hierarchy = 'viewed_at'
