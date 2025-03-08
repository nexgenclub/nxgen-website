from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.project_home, name='project_home'),
    path('add/', views.add_project, name='add_project'),
    path('<slug:slug>/', views.project_detail, name='project_detail'),
    path('<slug:slug>/delete/', views.delete_project, name='delete_project'),  # New delete route
]