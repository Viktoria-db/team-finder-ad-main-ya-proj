import json

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import TemplateView

from users.forms import (
    CustomPasswordChangeForm,
    LoginForm,
    ProfileEditForm,
    RegistrationForm,
)
from users.models import Skill, User
from users.pagination import build_query_prefix, paginate_queryset


class RegisterView(View):
    template_name = "users/register.html"

    def get(self, request):
        return render(request, self.template_name, {"form": RegistrationForm()})

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("projects:list")
        return render(request, self.template_name, {"form": form})


class LoginView(View):
    template_name = "users/login.html"

    def get(self, request):
        return render(request, self.template_name, {"form": LoginForm()})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            login(request, form.user)
            return redirect("projects:list")
        return render(request, self.template_name, {"form": form})


def logout_view(request):
    logout(request)
    return redirect("projects:list")


class ParticipantsListView(TemplateView):
    template_name = "users/participants.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = User.objects.prefetch_related("skills").order_by("-id")
        active_skill = self.request.GET.get("skill", "").strip()
        if active_skill:
            queryset = queryset.filter(skills__name=active_skill).distinct()
        page_obj = paginate_queryset(queryset, self.request)
        context.update(
            {
                "page_obj": page_obj,
                "all_skills": list(
                    Skill.objects.order_by("name").values_list("name", flat=True)
                ),
                "active_skill": active_skill,
                "query_prefix": build_query_prefix(self.request),
            }
        )
        return context


class UserDetailView(TemplateView):
    template_name = "users/user-details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(
            User.objects.prefetch_related("skills", "owned_projects__participants"),
            pk=self.kwargs["pk"],
        )
        context["user"] = user
        return context


class ProfileEditView(LoginRequiredMixin, View):
    template_name = "users/edit_profile.html"

    def get(self, request):
        form = ProfileEditForm(instance=request.user)
        return render(
            request,
            self.template_name,
            {"form": form, "user": request.user},
        )

    def post(self, request):
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("users:detail", pk=request.user.pk)
        return render(
            request,
            self.template_name,
            {"form": form, "user": request.user},
        )


class PasswordChangeView(LoginRequiredMixin, View):
    template_name = "users/change_password.html"

    def get(self, request):
        form = CustomPasswordChangeForm(user=request.user)
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect("users:detail", pk=request.user.pk)
        return render(request, self.template_name, {"form": form})


@require_GET
def skills_autocomplete(request):
    query = request.GET.get("q", "").strip()
    skills = Skill.objects.filter(name__istartswith=query).order_by("name")[:10]
    data = [{"id": skill.id, "name": skill.name} for skill in skills]
    return JsonResponse(data, safe=False)


@login_required
@require_POST
def skill_add(request, pk):
    profile_user = get_object_or_404(User, pk=pk)
    if profile_user != request.user:
        return JsonResponse({"error": "forbidden"}, status=403)
    try:
        payload = json.loads(request.body.decode() or "{}")
    except json.JSONDecodeError:
        payload = request.POST

    skill_id = payload.get("skill_id")
    name = (payload.get("name") or "").strip()
    created = False
    added = False

    if skill_id:
        skill = get_object_or_404(Skill, pk=skill_id)
    elif name:
        skill, created = Skill.objects.get_or_create(name=name)
    else:
        return JsonResponse({"error": "invalid"}, status=400)

    if not profile_user.skills.filter(pk=skill.pk).exists():
        profile_user.skills.add(skill)
        added = True

    return JsonResponse(
        {
            "skill_id": skill.id,
            "created": created,
            "added": added,
            "id": skill.id,
            "name": skill.name,
        }
    )


@login_required
@require_POST
def skill_remove(request, pk, skill_id):
    profile_user = get_object_or_404(User, pk=pk)
    if profile_user != request.user:
        return JsonResponse({"error": "forbidden"}, status=403)
    skill = get_object_or_404(Skill, pk=skill_id)
    if profile_user.skills.filter(pk=skill.pk).exists():
        profile_user.skills.remove(skill)
    return JsonResponse({"status": "ok"})
