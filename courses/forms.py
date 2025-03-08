from django import forms
from .models import Course, Section, Rating, CourseIssue, IssueComment, CourseReport
from django.core.validators import MinValueValidator, MaxValueValidator

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'category', 'description', 'content', 'level', 
                  'prerequisites', 'estimated_duration', 'thumbnail']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Course Title'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'A brief description of your course'}),
            'content': forms.Textarea(attrs={'class': 'form-control md-editor', 'rows': 15, 'placeholder': 'Write your course content here...\n\nMarkdown is supported.'}),
            'level': forms.Select(attrs={'class': 'form-select'}),
            'prerequisites': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'What should learners know before taking this course?'}),
            'estimated_duration': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Estimated time in minutes'}),
            'thumbnail': forms.FileInput(attrs={'class': 'form-control'}),
        }


class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['title', 'content', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Section Title'}),
            'content': forms.Textarea(attrs={'class': 'form-control md-editor', 'rows': 10, 'placeholder': 'Write your section content here...\n\nMarkdown is supported.'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['score', 'comment']
        widgets = {
            'score': forms.Select(attrs={'class': 'form-select'}, choices=[(i, i) for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Leave a review comment (optional)'}),
        }


class CourseIssueForm(forms.ModelForm):
    class Meta:
        model = CourseIssue
        fields = ['title', 'description', 'issue_type', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Issue Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Describe the issue in detail'}),
            'issue_type': forms.Select(attrs={'class': 'form-select'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class IssueCommentForm(forms.ModelForm):
    class Meta:
        model = IssueComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Add your comment here...'}),
        }


class CourseReportForm(forms.ModelForm):
    class Meta:
        model = CourseReport
        fields = ['reason', 'details']
        widgets = {
            'reason': forms.Select(attrs={'class': 'form-select'}),
            'details': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Please provide specific details about your report...'}),
        }


class CourseSearchForm(forms.Form):
    query = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Search courses...'}))
    category = forms.CharField(required=False, widget=forms.Select(
        attrs={'class': 'form-select'}))
    level = forms.CharField(required=False, widget=forms.Select(
        attrs={'class': 'form-select', 'empty_label': 'All Levels'}, 
        choices=[('', 'All Levels')] + list(Course.LEVEL_CHOICES)))
