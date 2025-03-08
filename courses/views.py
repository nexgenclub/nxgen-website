from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from django.utils import timezone
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import user_passes_test

from .models import (
    Course, Category, Section, Rating, CourseIssue, 
    IssueComment, CourseEnrollment, CourseReport
)
from .forms import (
    CourseForm, SectionForm, RatingForm, CourseIssueForm, 
    IssueCommentForm, CourseReportForm, CourseSearchForm
)

def is_moderator(user):
    return user.is_staff or user.is_superuser

# Course listing and browsing
def course_list(request):
    search_form = CourseSearchForm(request.GET)
    courses = Course.objects.filter(status='published')
    
    if search_form.is_valid():
        query = search_form.cleaned_data.get('query')
        category = search_form.cleaned_data.get('category')
        level = search_form.cleaned_data.get('level')
        
        if query:
            courses = courses.filter(Q(title__icontains=query) | Q(description__icontains=query))
        if category:
            courses = courses.filter(category__slug=category)
        if level:
            courses = courses.filter(level=level)
    
    # Add average rating to each course
    for course in courses:
        course.avg_rating = course.get_average_rating()
    
    # Get categories for the filter
    categories = Category.objects.all()
    
    # Pagination
    paginator = Paginator(courses, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'categories': categories
    }
    return render(request, 'courses/course_list.html', context)

def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug, status='published')
    sections = course.sections.all().order_by('order')
    
    # Increment view count, this is a bad way though shame on me :)
    course.views_count += 1
    course.save(update_fields=['views_count'])
    
    # Check if user is enrolled
    is_enrolled = False
    has_rated = False
    if request.user.is_authenticated:
        is_enrolled = CourseEnrollment.objects.filter(course=course, user=request.user).exists()
        has_rated = Rating.objects.filter(course=course, user=request.user).exists()
    
    # Get ratings and calculate stats
    ratings = course.ratings.all()
    avg_rating = course.get_average_rating()
    rating_count = ratings.count()
    
    # Rating form
    if request.method == 'POST' and request.user.is_authenticated and not has_rated:
        rating_form = RatingForm(request.POST)
        if rating_form.is_valid():
            rating = rating_form.save(commit=False)
            rating.course = course
            rating.user = request.user
            rating.save()
            messages.success(request, 'Thank you for rating this course!')
            return redirect('courses:course_detail', slug=slug)
    else:
        rating_form = RatingForm()
    
    # Related courses
    related_courses = Course.objects.filter(
        category=course.category, 
        status='published'
    ).exclude(id=course.id)[:3]
    
    context = {
        'course': course,
        'sections': sections,
        'is_enrolled': is_enrolled,
        'has_rated': has_rated,
        'avg_rating': avg_rating,
        'rating_count': rating_count,
        'rating_form': rating_form,
        'related_courses': related_courses,
    }
    return render(request, 'courses/course_detail.html', context)

@login_required
def enroll_course(request, slug):
    course = get_object_or_404(Course, slug=slug, status='published')
    
    # Check if already enrolled
    enrollment, created = CourseEnrollment.objects.get_or_create(
        course=course,
        user=request.user
    )
    
    if created:
        messages.success(request, f"You've successfully enrolled in {course.title}")
    else:
        messages.info(request, f"You're already enrolled in this course")
    
    return redirect('courses:course_detail', slug=slug)

@login_required
def complete_course(request, slug):
    course = get_object_or_404(Course, slug=slug)
    
    try:
        enrollment = CourseEnrollment.objects.get(course=course, user=request.user)
        enrollment.completed = True
        enrollment.completed_at = timezone.now()
        enrollment.save()
        messages.success(request, f"Congratulations on completing {course.title}!")
    except CourseEnrollment.DoesNotExist:
        messages.error(request, "You need to enroll in this course first.")
    
    return redirect('courses:course_detail', slug=slug)

# Course creation and management
@login_required
def create_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.author = request.user
            course.status = 'draft'
            course.save()
            messages.success(request, 'Your course has been created as a draft. You can now add sections or publish it.')
            return redirect('courses:edit_course', slug=course.slug)
    else:
        form = CourseForm()
    
    context = {'form': form, 'creating': True}
    return render(request, 'courses/course_form.html', context)

@login_required
def edit_course(request, slug):
    course = get_object_or_404(Course, slug=slug, author=request.user)
    sections = course.sections.all().order_by('order')
    
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your course has been updated.')
            return redirect('courses:edit_course', slug=course.slug)
    else:
        form = CourseForm(instance=course)
    
    context = {
        'form': form, 
        'course': course,
        'sections': sections,
        'creating': False
    }
    return render(request, 'courses/course_form.html', context)

@login_required
def delete_course(request, slug):
    course = get_object_or_404(Course, slug=slug, author=request.user)
    
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Your course has been deleted.')
        return redirect('courses:my_courses')
    
    return render(request, 'courses/course_confirm_delete.html', {'course': course})

@login_required
def publish_course(request, slug):
    course = get_object_or_404(Course, slug=slug, author=request.user)
    
    if request.method == 'POST':
        # Check if course has at least one section
        if not course.sections.exists():
            messages.error(request, 'Your course needs at least one section before it can be published.')
            return redirect('courses:edit_course', slug=slug)
        
        course.status = 'published'
        course.published_at = timezone.now()
        course.save(update_fields=['status', 'published_at'])
        messages.success(request, 'Your course has been published!')
        return redirect('courses:course_detail', slug=slug)
    
    return render(request, 'courses/publish_confirm.html', {'course': course})

@login_required
def my_courses(request):
    authored_courses = Course.objects.filter(author=request.user)
    enrolled_courses = CourseEnrollment.objects.filter(user=request.user).select_related('course')
    
    context = {
        'authored_courses': authored_courses,
        'enrolled_courses': enrolled_courses
    }
    return render(request, 'courses/my_courses.html', context)

# Section management
@login_required
def add_section(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug, author=request.user)
    
    if request.method == 'POST':
        form = SectionForm(request.POST)
        if form.is_valid():
            section = form.save(commit=False)
            section.course = course
            
            # If no order specified, add as last section
            if not section.order:
                max_order = course.sections.order_by('-order').first()
                section.order = max_order.order + 1 if max_order else 1
                
            section.save()
            messages.success(request, 'Section added successfully.')
            return redirect('courses:edit_course', slug=course_slug)
    else:
        form = SectionForm()
    
    context = {'form': form, 'course': course}
    return render(request, 'courses/section_form.html', context)

@login_required
def edit_section(request, section_id):
    section = get_object_or_404(Section, id=section_id)
    course = section.course
    
    # Check if the user is the course author
    if request.user != course.author:
        messages.error(request, "You don't have permission to edit this section.")
        return redirect('courses:course_detail', slug=course.slug)
    
    if request.method == 'POST':
        form = SectionForm(request.POST, instance=section)
        if form.is_valid():
            form.save()
            messages.success(request, 'Section updated successfully.')
            return redirect('courses:edit_course', slug=course.slug)
    else:
        form = SectionForm(instance=section)
    
    context = {'form': form, 'section': section, 'course': course}
    return render(request, 'courses/section_form.html', context)

@login_required
def delete_section(request, section_id):
    section = get_object_or_404(Section, id=section_id)
    course = section.course
    
    # Check if the user is the course author
    if request.user != course.author:
        messages.error(request, "You don't have permission to delete this section.")
        return redirect('courses:course_detail', slug=course.slug)
    
    if request.method == 'POST':
        section.delete()
        messages.success(request, 'Section deleted successfully.')
        return redirect('courses:edit_course', slug=course.slug)
    
    context = {'section': section, 'course': course}
    return render(request, 'courses/section_confirm_delete.html', context)

# Issue tracking
@login_required
def create_issue(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    
    if request.method == 'POST':
        form = CourseIssueForm(request.POST)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.course = course
            issue.reporter = request.user
            issue.save()
            messages.success(request, 'Issue reported successfully. Thank you for your feedback!')
            return redirect('courses:course_issues', slug=course_slug)
    else:
        form = CourseIssueForm()
    
    context = {'form': form, 'course': course}
    return render(request, 'courses/issue_form.html', context)

@login_required
def course_issues(request, slug):
    course = get_object_or_404(Course, slug=slug)
    
    # Determine which issues to show based on user
    if request.user == course.author or is_moderator(request.user):
        # Author and moderators can see all issues
        issues = course.issues.all()
    else:
        # Normal users can see public issues and their own private issues
        issues = course.issues.filter(Q(is_public=True) | Q(reporter=request.user))
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter and status_filter != 'all':
        issues = issues.filter(status=status_filter)
    
    context = {
        'course': course, 
        'issues': issues,
        'status_filter': status_filter or 'all',
        'is_author': request.user == course.author,
        'is_moderator': is_moderator(request.user),
    }
    return render(request, 'courses/course_issues.html', context)

@login_required
def issue_detail(request, issue_id):
    issue = get_object_or_404(CourseIssue, id=issue_id)
    course = issue.course
    
    # Check if the user has permission to view this issue
    if not (issue.is_public or request.user == issue.reporter or 
            request.user == course.author or is_moderator(request.user)):
        raise Http404("Issue not found")
    
    # Handle comments
    if request.method == 'POST':
        comment_form = IssueCommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.issue = issue
            comment.author = request.user
            comment.save()
            messages.success(request, 'Your comment has been added.')
            return redirect('courses:issue_detail', issue_id=issue.id)
    else:
        comment_form = IssueCommentForm()
    
    comments = issue.comments.all()
    
    context = {
        'issue': issue,
        'course': course,
        'comments': comments,
        'comment_form': comment_form,
        'is_author': request.user == course.author,
        'is_moderator': is_moderator(request.user),
    }
    return render(request, 'courses/issue_detail.html', context)

@login_required
def update_issue_status(request, issue_id):
    issue = get_object_or_404(CourseIssue, id=issue_id)
    course = issue.course
    
    # Only course author or moderators can change issue status
    if not (request.user == course.author or is_moderator(request.user)):
        messages.error(request, "You don't have permission to change issue status.")
        return redirect('courses:issue_detail', issue_id=issue_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(CourseIssue.ISSUE_STATUS).keys():
            issue.status = new_status
            issue.save(update_fields=['status'])
            messages.success(request, f"Issue status updated to {issue.get_status_display()}")
        else:
            messages.error(request, "Invalid status")
    
    return redirect('courses:issue_detail', issue_id=issue_id)

# Moderation views
@login_required
def report_course(request, slug):
    course = get_object_or_404(Course, slug=slug)
    
    if request.method == 'POST':
        form = CourseReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.course = course
            report.reporter = request.user
            report.save()
            messages.success(request, 'Your report has been submitted. Our moderators will review it.')
            return redirect('courses:course_detail', slug=slug)
    else:
        form = CourseReportForm()
    
    context = {'form': form, 'course': course}
    return render(request, 'courses/report_form.html', context)

@user_passes_test(is_moderator)
def moderation_queue(request):
    reports = CourseReport.objects.filter(status='pending')
    moderated_courses = Course.objects.filter(status='moderated')
    
    context = {
        'reports': reports,
        'moderated_courses': moderated_courses
    }
    return render(request, 'courses/moderation_queue.html', context)

@user_passes_test(is_moderator)
def review_report(request, report_id):
    report = get_object_or_404(CourseReport, id=report_id)
    course = report.course
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'dismiss':
            report.status = 'dismissed'
            report.reviewed_by = request.user
            report.reviewed_at = timezone.now()
            report.save()
            messages.success(request, 'Report has been dismissed.')
        
        elif action == 'moderate':
            report.status = 'actioned'
            course.status = 'moderated'
            course.save()
            report.reviewed_by = request.user
            report.reviewed_at = timezone.now()
            report.save()
            messages.success(request, f'Course "{course.title}" has been put under moderation.')
        
        return redirect('courses:moderation_queue')
    
    context = {'report': report, 'course': course}
    return render(request, 'courses/review_report.html', context)

@user_passes_test(is_moderator)
def restore_course(request, slug):
    course = get_object_or_404(Course, slug=slug, status='moderated')
    
    if request.method == 'POST':
        course.status = 'published'
        course.save(update_fields=['status'])
        messages.success(request, f'Course "{course.title}" has been restored to published status.')
        return redirect('courses:course_detail', slug=slug)
    
    return render(request, 'courses/restore_confirm.html', {'course': course})
