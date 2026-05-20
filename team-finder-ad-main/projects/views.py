import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, TemplateView

from projects.forms import ProjectForm
from projects.models import Project
from users.pagination import build_query_prefix, paginate_queryset


class ProjectListView(TemplateView):
    template_name = "projects/project_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = Project.objects.select_related("owner").prefetch_related(
            "participants"
        )
        page_obj = paginate_queryset(queryset, self.request)
        context.update(
            {
                "page_obj": page_obj,
                "projects": page_obj.object_list,
                "query_prefix": build_query_prefix(self.request),
            }
        )
        return context


class ProjectDetailView(DetailView):
    model = Project
    template_name = "projects/project-details.html"
    context_object_name = "project"

    def get_queryset(self):
        return Project.objects.select_related("owner").prefetch_related("participants")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        return context


class ProjectCreateView(LoginRequiredMixin, View):
    template_name = "projects/create-project.html"

    def get(self, request):
        form = ProjectForm()
        return render(
            request,
            self.template_name,
            {"form": form, "is_edit": False},
        )

    def post(self, request):
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            return redirect("projects:detail", pk=project.pk)
        return render(
            request,
            self.template_name,
            {"form": form, "is_edit": False},
        )


class ProjectEditView(LoginRequiredMixin, View):
    template_name = "projects/create-project.html"

    def get_project(self):
        project = get_object_or_404(Project, pk=self.kwargs["pk"])
        if project.owner != self.request.user:
            return None
        return project

    def get(self, request, pk):
        project = self.get_project()
        if project is None:
            return redirect("projects:detail", pk=pk)
        form = ProjectForm(instance=project)
        return render(
            request,
            self.template_name,
            {"form": form, "is_edit": True},
        )

    def post(self, request, pk):
        project = self.get_project()
        if project is None:
            return redirect("projects:detail", pk=pk)
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect("projects:detail", pk=project.pk)
        return render(
            request,
            self.template_name,
            {"form": form, "is_edit": True},
        )


@login_required
@require_POST
def project_complete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner != request.user or project.status != Project.STATUS_OPEN:
        return JsonResponse({"status": "error"}, status=400)
    project.status = Project.STATUS_CLOSED
    project.save(update_fields=["status"])
    return JsonResponse({"status": "ok", "project_status": "closed"})


@login_required
@require_POST
def project_toggle_participate(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner == request.user:
        return JsonResponse({"status": "error"}, status=400)
    is_participant = project.participants.filter(pk=request.user.pk).exists()
    if is_participant:
        project.participants.remove(request.user)
        participant = False
    else:
        project.participants.add(request.user)
        participant = True
    return JsonResponse({"status": "ok", "participant": participant})
