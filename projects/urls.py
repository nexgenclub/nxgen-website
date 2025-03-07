from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.project_home, name='project_home'),
    path('<int:project_id>/', views.project_detail, name='project_detail'),
    path('add/', views.add_project, name='add_project'),
    path('<int:project_id>/comment/', views.add_comment, name='add_comment'),
    path('<int:project_id>/like/', views.like_project, name='like_project'),
]
