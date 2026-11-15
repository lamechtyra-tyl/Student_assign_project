from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, UpdateView

from .forms import AssignmentForm, StudentRegistrationForm
from .models import Assignment


class StudentLoginView(LoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = True


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = StudentRegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("dashboard")
    return render(request, "registration/register.html", {"form": form})


@login_required
def dashboard(request):
    assignments = Assignment.objects.filter(owner=request.user)
    counts = assignments.aggregate(
        total=Count("id"),
        pending=Count("id", filter=Q(status=Assignment.Status.PENDING)),
        completed=Count("id", filter=Q(status=Assignment.Status.COMPLETED)),
    )
    upcoming = assignments.filter(
        status=Assignment.Status.PENDING,
        due_date__gte=timezone.localdate(),
    )[:5]
    return render(
        request,
        "myapp/dashboard.html",
        {"counts": counts, "upcoming_assignments": upcoming},
    )


@login_required
def assignment_list(request):
    assignments = Assignment.objects.filter(owner=request.user)
    status = request.GET.get("status", "")
    if status in Assignment.Status.values:
        assignments = assignments.filter(status=status)
    return render(
        request,
        "myapp/assignment_list.html",
        {"assignments": assignments, "selected_status": status},
    )


class AssignmentCreateView(LoginRequiredMixin, CreateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = "myapp/assignment_form.html"
    success_url = reverse_lazy("assignment_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class OwnedAssignmentMixin(LoginRequiredMixin):
    def get_queryset(self):
        return Assignment.objects.filter(owner=self.request.user)


class AssignmentUpdateView(OwnedAssignmentMixin, UpdateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = "myapp/assignment_form.html"
    success_url = reverse_lazy("assignment_list")


class AssignmentDeleteView(OwnedAssignmentMixin, DeleteView):
    model = Assignment
    template_name = "myapp/assignment_confirm_delete.html"
    success_url = reverse_lazy("assignment_list")


@login_required
@require_POST
def toggle_assignment_status(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk, owner=request.user)
    if assignment.status == Assignment.Status.PENDING:
        assignment.status = Assignment.Status.COMPLETED
    else:
        assignment.status = Assignment.Status.PENDING
    assignment.save(update_fields=["status"])
    return redirect("assignment_list")

