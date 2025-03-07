from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Project, Like
from .forms import ProjectForm, CommentForm

# Create your views here.

def project_home(request):
    projects = Project.objects.all().order_by('-created_at')
    return render(request, 'projects/project_home.html', {'projects': projects})


# Show project details
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    comments = project.comments.all()
    form = CommentForm()
    return render(request, 'projects/project_detail.html', {'project': project, 'comments': comments, 'form': form})

# Add a new project
@login_required
def add_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            return redirect('projects:project_list')
    else:
        form = ProjectForm()
    return render(request, 'projects/add_project.html', {'form': form})

# Add a comment
@login_required
def add_comment(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.project = project
            comment.user = request.user
            comment.save()
    return redirect('projects:project_detail', project_id=project.id)

# Like a project
@login_required
def like_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    like, created = Like.objects.get_or_create(project=project, user=request.user)
    if not created:
        like.delete()  # Toggle like
    return redirect('projects:project_detail', project_id=project.id)