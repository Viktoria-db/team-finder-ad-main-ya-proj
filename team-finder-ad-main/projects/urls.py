from django.urls import path

from projects import views

app_name = "projects"

urlpatterns = [
    path("list/", views.ProjectListView.as_view(), name="list"),
    path("create-project/", views.ProjectCreateView.as_view(), name="create"),
    path("<int:pk>/", views.ProjectDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.ProjectEditView.as_view(), name="edit"),
    path("<int:pk>/complete/", views.project_complete, name="complete"),
    path(
        "<int:pk>/toggle-participate/",
        views.project_toggle_participate,
        name="toggle_participate",
    ),
]
