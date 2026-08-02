from django.urls import path
from . import views


urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),
    path('project_details/<slug:slug>/', views.ProjectDetail.as_view(), name="project_details"),
]
