from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Project, Like
from .forms import ProjectForm, CommentForm
import requests
import markdown
from django.utils.safestring import mark_safe
from django.contrib import messages

# Create your views here.


def project_home(request):
    projects = Project.objects.all().order_by("-created_at")
    return render(request, "projects/project_home.html", {"projects": projects})


# Fetch README
def fetch_github_readme(github_link):
    if not github_link:
        return None

    try:
        # Extract username and repo name
        parts = github_link.rstrip("/").split("/")
        username, repo = parts[-2], parts[-1]

        # GitHub API URL to fetch README
        api_url = f"https://raw.githubusercontent.com/{username}/{repo}/main/README.md"

        response = requests.get(api_url)
        if response.status_code == 200:
            readme_html = markdown.markdown(response.text)
            return mark_safe(readme_html)
    except Exception as e:
        print("Error fetching README:", e)

    return None


# Show project details
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    comments = project.comments.all()
    form = CommentForm()

    # Fetch README from GitHub
    readme_content = fetch_github_readme(project.github_link)

    return render(
        request,
        "projects/project_detail.html",
        {
            "project": project,
            "comments": comments,
            "form": form,
            "readme_content": readme_content,
        },
    )


# Add a new project
@login_required
def add_project(request):
    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            github_link = form.cleaned_data.get("github_link")
            if Project.objects.filter(github_link=github_link).exists():
                messages.error(
                    request, "A project with this GitHub link already exists!"
                )
            else:
                project = form.save(commit=False)
                project.created_by = request.user
                project.save()

                messages.success(request, "Your project has been created!")
                return redirect("projects:project_home")
    else:
        form = ProjectForm()

    return render(request, "projects/add_project.html", {"form": form})


# Add a comment
@login_required
def add_comment(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.project = project
            comment.user = request.user
            comment.save()
    return redirect("projects:project_detail", project_id=project.id)


# Like a project
@login_required
def like_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    like, created = Like.objects.get_or_create(project=project, user=request.user)
    if not created:
        like.delete()  # Toggle like
    return redirect("projects:project_detail", project_id=project.id)
