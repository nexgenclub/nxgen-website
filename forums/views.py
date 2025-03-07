from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.utils.text import slugify
from .models import Category, Topic, Post, TopicView
from .forms import TopicForm, PostForm

def forum_home(request):
    """Display all categories and some stats"""
    categories = Category.objects.all()
    
    
    total_topics = Topic.objects.count()
    total_posts = Post.objects.count()
    total_users = Post.objects.values('author').distinct().count()
    
    recent_topics = Topic.objects.select_related('author', 'category').order_by('-created_at')[:5]
    
    context = {
        'categories': categories,
        'recent_topics': recent_topics,
        'total_topics': total_topics,
        'total_posts': total_posts,
        'total_users': total_users,
    }
    return render(request, 'forums/forum_home.html', context)

def category_detail(request, slug):
    """Display all topics in a category"""
    category = get_object_or_404(Category, slug=slug)
    topics = Topic.objects.filter(category=category).select_related('author')
    
    
    query = request.GET.get('q')
    if query:
        topics = topics.filter(title__icontains=query)
    
    
    paginator = Paginator(topics, 20)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
        'query': query,
    }
    return render(request, 'forums/category_detail.html', context)

def topic_detail(request, category_slug, slug):
    """Display a topic and its posts"""
    topic = get_object_or_404(Topic, slug=slug, category__slug=category_slug)
    posts = topic.posts.select_related('author').all()
    
    
    if request.user.is_authenticated:
        TopicView.objects.get_or_create(topic=topic, user=request.user)
    else:
        ip_address = request.META.get('REMOTE_ADDR')
        if ip_address:
            TopicView.objects.get_or_create(topic=topic, ip_address=ip_address)
    
    
    paginator = Paginator(posts, 15)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    
    form = PostForm()
    
    context = {
        'topic': topic,
        'page_obj': page_obj,
        'form': form,
    }
    return render(request, 'forums/topic_detail.html', context)

@login_required
def create_topic(request):
    """Create a new discussion topic"""
    if request.method == 'POST':
        topic_form = TopicForm(request.POST)
        post_form = PostForm(request.POST)
        
        if topic_form.is_valid() and post_form.is_valid():
            
            topic = topic_form.save(commit=False)
            topic.author = request.user
            topic.save()
            
            
            post = post_form.save(commit=False)
            post.topic = topic
            post.author = request.user
            post.save()
            
            messages.success(request, 'Your topic has been created!')
            return redirect(topic.get_absolute_url())
    else:
        
        category_id = request.GET.get('category')
        if category_id:
            topic_form = TopicForm(initial={'category': category_id})
        else:
            topic_form = TopicForm()
        
        post_form = PostForm()
    
    context = {
        'topic_form': topic_form,
        'post_form': post_form,
    }
    return render(request, 'forums/create_topic.html', context)

@login_required
def reply_topic(request, category_slug, slug):
    """Reply to an existing topic"""
    topic = get_object_or_404(Topic, slug=slug, category__slug=category_slug)
    
    
    if topic.locked:
        messages.error(request, 'This topic is locked and cannot be replied to.')
        return redirect(topic.get_absolute_url())
    
    if request.method == 'POST':
        form = PostForm(request.POST)
        
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.author = request.user
            post.save()
            
            messages.success(request, 'Your reply has been posted!')
            return redirect(topic.get_absolute_url())
    else:
        form = PostForm()
    
    context = {
        'topic': topic,
        'form': form,
    }
    return render(request, 'forums/reply_topic.html', context)

@login_required
def edit_post(request, post_id):
    """Edit an existing post"""
    post = get_object_or_404(Post, pk=post_id)
    
    
    if post.author != request.user and not request.user.is_staff:
        messages.error(request, "You don't have permission to edit this post.")
        return redirect(post.topic.get_absolute_url())
    
    
    if post.topic.locked and not request.user.is_staff:
        messages.error(request, 'This topic is locked and posts cannot be edited.')
        return redirect(post.topic.get_absolute_url())
    
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Your post has been updated!')
            return redirect(post.topic.get_absolute_url())
    else:
        form = PostForm(instance=post)
    
    context = {
        'form': form,
        'post': post,
    }
    return render(request, 'forums/edit_post.html', context)

@login_required
def search(request):
    """Search functionality for topics and posts"""
    query = request.GET.get('q', '')
    
    if query:
        
        topics = Topic.objects.filter(title__icontains=query).select_related('author', 'category')
        
        
        posts = Post.objects.filter(content__icontains=query).select_related('author', 'topic')
    else:
        topics = Topic.objects.none()
        posts = Post.objects.none()
    
    context = {
        'query': query,
        'topics': topics[:20],  
        'posts': posts[:20],    
    }
    return render(request, 'forums/search_results.html', context)
