from django.contrib import admin

from .models import Assignment


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ("title", "subject", "owner", "due_date", "priority", "status")
    list_filter = ("status", "priority", "due_date")
    search_fields = ("title", "subject", "owner__username")
