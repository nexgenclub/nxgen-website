from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.db.models import Avg
from django.urls import reverse

from .models import Course, CourseReport, CourseIssue, CourseEnrollment

class CoursesAdminDashboard(admin.AdminSite):
    """Custom admin dashboard for courses app"""
    site_header = "NXGen Courses Administration"
    site_title = "NXGen Courses Admin"
    index_title = "Courses Management Dashboard"
    
    def get_app_list(self, request):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        app_list = super().get_app_list(request)
        
        for i, app in enumerate(app_list):
            if app['app_label'] == 'courses':
                app_list.insert(0, app_list.pop(i))
                break
        
        return app_list
    
    def index(self, request, extra_context=None):
        """
        Override the index view to add course stats.
        """
        # Get course statistics
        course_stats = {
            'total': Course.objects.count(),
            'published': Course.objects.filter(status='published').count(),
            'draft': Course.objects.filter(status='draft').count(),
            'moderated': Course.objects.filter(status='moderated').count(),
            'archived': Course.objects.filter(status='archived').count(),
            'avg_rating': Course.objects.filter(ratings__isnull=False).annotate(
                avg_rating=Avg('ratings__score')).aggregate(Avg('avg_rating'))['avg_rating__avg'] or 0,
            'total_enrollments': CourseEnrollment.objects.count(),
            'total_issues': CourseIssue.objects.count(),
            'open_issues': CourseIssue.objects.filter(status='open').count(),
            'pending_reports': CourseReport.objects.filter(status='pending').count(),
        }
        
        # Create links to pending reports
        pending_reports = CourseReport.objects.filter(status='pending').select_related('course', 'reporter')[:5]
        pending_reports_display = []
        
        for report in pending_reports:
            report_url = reverse('admin:courses_coursereport_change', args=[report.id])
            pending_reports_display.append({
                'id': report.id,
                'course': report.course.title,
                'reason': report.get_reason_display(),
                'reporter': report.reporter.username,
                'url': report_url
            })
        
        extra_context = extra_context or {}
        extra_context.update({
            'course_stats': course_stats,
            'pending_reports': pending_reports_display,
        })
        
        return super().index(request, extra_context)

# custom admin site:
courses_admin_site = CoursesAdminDashboard(name='courses_admin')
