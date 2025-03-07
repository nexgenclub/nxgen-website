from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    # Course browsing
    path('', views.course_list, name='course_list'),
    path('course/<slug:slug>/', views.course_detail, name='course_detail'),
    path('course/<slug:slug>/enroll/', views.enroll_course, name='enroll_course'),
    path('course/<slug:slug>/complete/', views.complete_course, name='complete_course'),
    
    # Course management
    path('create/', views.create_course, name='create_course'),
    path('course/<slug:slug>/edit/', views.edit_course, name='edit_course'),
    path('course/<slug:slug>/delete/', views.delete_course, name='delete_course'),
    path('course/<slug:slug>/publish/', views.publish_course, name='publish_course'),
    path('my-courses/', views.my_courses, name='my_courses'),
    
    # Section management
    path('course/<slug:course_slug>/add-section/', views.add_section, name='add_section'),
    path('section/<int:section_id>/edit/', views.edit_section, name='edit_section'),
    path('section/<int:section_id>/delete/', views.delete_section, name='delete_section'),
    
    # Issue tracking
    path('course/<slug:course_slug>/create-issue/', views.create_issue, name='create_issue'),
    path('course/<slug:slug>/issues/', views.course_issues, name='course_issues'),
    path('issue/<int:issue_id>/', views.issue_detail, name='issue_detail'),
    path('issue/<int:issue_id>/update-status/', views.update_issue_status, name='update_issue_status'),
    
    # Moderation
    path('course/<slug:slug>/report/', views.report_course, name='report_course'),
    path('moderation/', views.moderation_queue, name='moderation_queue'),
    path('report/<int:report_id>/review/', views.review_report, name='review_report'),
    path('course/<slug:slug>/restore/', views.restore_course, name='restore_course'),
]
