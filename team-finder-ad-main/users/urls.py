from django.urls import path

from users import views

app_name = "users"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("list/", views.ParticipantsListView.as_view(), name="list"),
    path("<int:pk>/", views.UserDetailView.as_view(), name="detail"),
    path("edit-profile/", views.ProfileEditView.as_view(), name="edit_profile"),
    path("change-password/", views.PasswordChangeView.as_view(), name="change_password"),
    path("skills/", views.skills_autocomplete, name="skills_autocomplete"),
    path("<int:pk>/skills/add/", views.skill_add, name="skill_add"),
    path(
        "<int:pk>/skills/<int:skill_id>/remove/",
        views.skill_remove,
        name="skill_remove",
    ),
]
