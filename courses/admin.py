from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Category, Course, Section, Rating, CourseIssue, IssueComment, CourseEnrollment, CourseReport

class SectionInline(admin.TabularInline):
    model = Section
    extra = 1
    fields = ('title', 'order')

class RatingInline(admin.TabularInline):
    model = Rating
    extra = 0
    readonly_fields = ('user', 'score', 'comment', 'created_at')
    can_delete = False
    max_num = 0

class IssueInline(admin.TabularInline):
    model = CourseIssue
    extra = 0
    readonly_fields = ('reporter', 'title', 'issue_type', 'status', 'created_at')
    fields = ('title', 'reporter', 'issue_type', 'status', 'created_at')
    can_delete = False
    max_num = 0
    show_change_link = True

class EnrollmentInline(admin.TabularInline):
    model = CourseEnrollment
    extra = 0
    readonly_fields = ('user', 'enrolled_at', 'completed', 'completed_at')
    fields = ('user', 'enrolled_at', 'completed', 'completed_at')
    can_delete = False
    max_num = 0

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'course_count', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    
    def course_count(self, obj):
        return obj.courses.count()
    course_count.short_description = 'Courses'

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'level', 'created_at', 'rating_display', 'enrollment_count')
    list_filter = ('status', 'level', 'category', 'is_featured')
    search_fields = ('title', 'description', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('views_count', 'created_at', 'updated_at', 'published_at')
    autocomplete_fields = ['author', 'category']
    date_hierarchy = 'created_at'
    inlines = [SectionInline, RatingInline, IssueInline, EnrollmentInline]
    fieldsets = (
        ('Course Information', {
            'fields': ('title', 'slug', 'author', 'category', 'description', 'content', 'thumbnail')
        }),
        ('Settings', {
            'fields': ('status', 'level', 'prerequisites', 'estimated_duration', 'is_featured')
        }),
        ('Statistics', {
            'fields': ('views_count', 'created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',),
        }),
    )
    
    def enrollment_count(self, obj):
        return obj.enrollments.count()
    enrollment_count.short_description = 'Enrollments'
    
    def rating_display(self, obj):
        avg_rating = obj.get_average_rating()
        rating_count = obj.ratings.count()
        
        if rating_count == 0:
            return 'No ratings'
        
        stars = ''
        for i in range(5):
            if i < int(avg_rating):
                stars += '<i class="fas fa-star text-warning"></i>'
            elif i < avg_rating:
                stars += '<i class="fas fa-star-half-alt text-warning"></i>'
            else:
                stars += '<i class="far fa-star text-warning"></i>'
        
        return format_html('{} ({} ratings)', stars, rating_count)
    
    rating_display.short_description = 'Rating'

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter = ('course__title',)
    search_fields = ('title', 'content', 'course__title')
    autocomplete_fields = ['course']

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'score', 'created_at')
    list_filter = ('score', 'created_at')
    search_fields = ('user__username', 'course__title', 'comment')
    readonly_fields = ('created_at',)
    autocomplete_fields = ['user', 'course']

@admin.register(CourseIssue)
class CourseIssueAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'reporter', 'issue_type', 'status', 'created_at', 'is_public')
    list_filter = ('status', 'issue_type', 'is_public', 'created_at')
    search_fields = ('title', 'description', 'reporter__username', 'course__title')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ['reporter', 'course']
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('course', 'reporter')

class IssueCommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'issue', 'content_preview', 'created_at')
    list_filter = ('created_at', 'issue__status')
    search_fields = ('content', 'author__username', 'issue__title')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ['author', 'issue']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'

admin.site.register(IssueComment, IssueCommentAdmin)

@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'enrolled_at', 'completed', 'completed_at')
    list_filter = ('completed', 'enrolled_at')
    search_fields = ('user__username', 'course__title')
    readonly_fields = ('enrolled_at', 'completed_at')
    autocomplete_fields = ['user', 'course']
    date_hierarchy = 'enrolled_at'

@admin.register(CourseReport)
class CourseReportAdmin(admin.ModelAdmin):
    list_display = ('course', 'reporter', 'reason', 'status', 'created_at')
    list_filter = ('status', 'reason', 'created_at')
    search_fields = ('details', 'reporter__username', 'course__title')
    readonly_fields = ('created_at', 'reviewed_at')
    autocomplete_fields = ['reporter', 'course', 'reviewed_by']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Report Information', {
            'fields': ('course', 'reporter', 'reason', 'details')
        }),
        ('Moderation', {
            'fields': ('status', 'reviewed_by', 'reviewed_at')
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status != 'pending':
            return self.readonly_fields + ('course', 'reporter', 'reason', 'details', 'status', 'reviewed_by')
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data:
            # If the status is being changed and not during initial creation
            if obj.status != 'pending' and not obj.reviewed_by:
                obj.reviewed_by = request.user
                obj.reviewed_at = timezone.now()
        super().save_model(request, obj, form, change)

