from __future__ import annotations

from django.contrib import admin

from .models import Todo


@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = ("title", "due_date", "completed", "created_at")
    search_fields = ("title",)
    list_filter = ("completed", "due_date")
    ordering = ("completed", "due_date", "-created_at")
