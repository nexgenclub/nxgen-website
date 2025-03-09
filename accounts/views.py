import logging
from datetime import datetime

logger = logging.getLogger(__name__)

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView, LogoutView
from django.urls import reverse_lazy
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from .models import Profile
from django.utils import timezone 
from .models import Profile
from courses.models import Course
from projects.models import Project
from forums.models import Post as ForumPost
from events.models import Event

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            message = f'Account created for {username}! You can now log in.'
            messages.success(request, message)
            logger.debug(f"Success message created: {message}")
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        """Add success message when user logs in successfully"""
        response = super().form_valid(form)
        message = f'Welcome back, {self.request.user.username}!'
        messages.success(self.request, message)
        logger.debug(f"Login success message created: {message}")
        return response

class CustomLogoutView(LogoutView):
    next_page = 'home'
    
    def dispatch(self, request, *args, **kwargs):
        """Add success message before logging out the user"""
        if request.user.is_authenticated:
            messages.info(request, f'You have been logged out successfully, {request.user.username}.')
        return super().dispatch(request, *args, **kwargs)

class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'

def home(request):
    context = {
        'is_morning': datetime.now().hour < 12,
        'is_afternoon': 12 <= datetime.now().hour < 18,
        'user_count': Profile.objects.count(),
        'course_count': Course.objects.count(),
        'project_count': Project.objects.count(),
        'forum_post_count': ForumPost.objects.count(),
        'latest_announcement': None,  # Assuming Announcement model is not provided
        'featured_courses': Course.objects.filter(is_featured=True)[:3],
        'recent_activities': None,  # Assuming Activity model is not provided
        'upcoming_events': Event.objects.filter(start_date__gte=timezone.now()).order_by('start_date')[:3],
    }
    return render(request, 'accounts/home.html', context)


@login_required
def view_profile(request):
    """View for displaying user profile details"""
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)
    
    return render(request, 'accounts/profile_view.html', {'user': request.user})

@login_required
def edit_profile(request):
    """View for editing user profile details"""
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'accounts/profile_edit.html', context)
