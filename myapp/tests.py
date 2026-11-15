from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from .models import Assignment


class StudentAccountTests(TestCase):
    def test_registration_creates_and_logs_in_student(self):
        response = self.client.post(
            reverse("register"),
            {
                "first_name": "Avery",
                "username": "avery",
                "email": "avery@example.com",
                "password1": "StrongPass!9274",
                "password2": "StrongPass!9274",
            },
        )

        self.assertRedirects(response, reverse("dashboard"))
        self.assertTrue(User.objects.filter(username="avery").exists())
        self.assertEqual(str(response.wsgi_request.user), "avery")

    def test_dashboard_redirects_anonymous_student_to_login(self):
        response = self.client.get(reverse("dashboard"))

        self.assertRedirects(response, f"{reverse('login')}?next={reverse('dashboard')}")


class AssignmentWorkflowTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(username="student", password="StrongPass!9274")
        self.other_student = User.objects.create_user(username="other", password="StrongPass!9274")
        self.client.force_login(self.student)
        self.assignment = Assignment.objects.create(
            owner=self.student,
            title="Research paper",
            description="Draft the introduction",
            subject="History",
            due_date=timezone.localdate(),
            priority=Assignment.Priority.HIGH,
        )

    def test_dashboard_counts_only_current_students_assignments(self):
        Assignment.objects.create(
            owner=self.other_student,
            title="Private work",
            subject="Math",
            due_date=timezone.localdate(),
        )

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.context["counts"], {"total": 1, "pending": 1, "completed": 0})

    def test_student_can_create_update_toggle_and_delete_assignment(self):
        response = self.client.post(
            reverse("assignment_create"),
            {
                "title": "Lab report",
                "description": "",
                "subject": "Biology",
                "due_date": timezone.localdate().isoformat(),
                "priority": Assignment.Priority.MEDIUM,
                "status": Assignment.Status.PENDING,
            },
        )
        self.assertRedirects(response, reverse("assignment_list"))
        created = Assignment.objects.get(title="Lab report")
        self.assertEqual(created.owner, self.student)

        response = self.client.post(
            reverse("assignment_update", args=[created.pk]),
            {
                "title": "Final lab report",
                "description": "",
                "subject": "Biology",
                "due_date": timezone.localdate().isoformat(),
                "priority": Assignment.Priority.HIGH,
                "status": Assignment.Status.PENDING,
            },
        )
        self.assertRedirects(response, reverse("assignment_list"))
        created.refresh_from_db()
        self.assertEqual(created.title, "Final lab report")

        response = self.client.post(reverse("assignment_toggle_status", args=[created.pk]))
        self.assertRedirects(response, reverse("assignment_list"))
        created.refresh_from_db()
        self.assertEqual(created.status, Assignment.Status.COMPLETED)

        response = self.client.post(reverse("assignment_delete", args=[created.pk]))
        self.assertRedirects(response, reverse("assignment_list"))
        self.assertFalse(Assignment.objects.filter(pk=created.pk).exists())

    def test_student_cannot_view_or_change_another_students_assignment(self):
        response = self.client.get(reverse("assignment_update", args=[self._other_assignment().pk]))

        self.assertEqual(response.status_code, 404)

    def _other_assignment(self):
        return Assignment.objects.create(
            owner=self.other_student,
            title="Private assignment",
            subject="Physics",
            due_date=timezone.localdate(),
        )
