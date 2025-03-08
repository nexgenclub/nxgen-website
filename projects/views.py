from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Project
from .forms import ProjectForm
import requests
import markdown
from django.utils.safestring import mark_safe
from django.contrib import messages

# Create your views here.


def project_home(request):
    search_query = request.GET.get('search', '')
    tech_filter = request.GET.get('tech_filter', '')

    projects = Project.objects.all()

    # Filtering by search query
    if search_query:
        projects = projects.filter(title__icontains=search_query)

    # Filtering by tech stack
    if tech_filter:
        projects = [p for p in projects if tech_filter in p.tech_stack.split(",")]

    # Get unique tech choices
    all_techs = set()
    for project in Project.objects.all():
        all_techs.update(project.tech_stack.split(","))

    return render(request, 'projects/project_home.html', {
        'projects': projects,
        'tech_choices': sorted(all_techs),
    })



# Show project details
def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)

    return render(
        request,
        "projects/project_detail.html",
        {
            "project": project,
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


@login_required
def delete_project(request, slug):
    """Deletes a project if the user is the owner and redirects to project_home."""
    project = get_object_or_404(Project, slug=slug)

    if request.user == project.created_by:  # Ensure only the owner can delete
        project.delete()
        messages.success(request, "Project deleted successfully.")
        return redirect('projects:project_home')  
    else:
        messages.error(request, "You are not authorized to delete this project.")
        return redirect('project_detail', slug=slug) 
    

def edit_project(request, slug):
    project = get_object_or_404(Project, slug=slug)
    
    # Check if the current user is the project owner
    if request.user != project.created_by:
        messages.error(request, "You don't have permission to edit this project.")
        return redirect('projects:project_detail', slug=slug)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            updated_project = form.save()
            messages.success(request, "Project updated successfully!")
            return redirect('projects:project_detail', slug=updated_project.slug)
    else:
        form = ProjectForm(instance=project)
    
    context = {
        'form': form,
        'project': project,
        'is_edit_mode': True
    }
    return render(request, 'projects/edit_project.html', context)