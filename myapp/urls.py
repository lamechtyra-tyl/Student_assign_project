from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("login/", views.StudentLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", views.register, name="register"),
    path("assignments/", views.assignment_list, name="assignment_list"),
    path("assignments/add/", views.AssignmentCreateView.as_view(), name="assignment_create"),
    path("assignments/<int:pk>/edit/", views.AssignmentUpdateView.as_view(), name="assignment_update"),
    path("assignments/<int:pk>/delete/", views.AssignmentDeleteView.as_view(), name="assignment_delete"),
    path("assignments/<int:pk>/status/", views.toggle_assignment_status, name="assignment_toggle_status"),
]