from __future__ import annotations

from django.db import models


class Todo(models.Model):
    """A to-do item representing a task with optional due date and completion status."""

    title: models.CharField = models.CharField(max_length=200)
    description: models.TextField = models.TextField(blank=True)
    due_date: models.DateField | None = models.DateField(null=True, blank=True, db_index=True)
    completed: models.BooleanField = models.BooleanField(default=False, db_index=True)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:  # pragma: no cover - trivial
        if self.due_date:
            return f"{self.title} (due {self.due_date})"
        return self.title

    class Meta:
        ordering = ["completed", "due_date", "-created_at"]
        verbose_name = "To‑Do Item"
        verbose_name_plural = "To‑Do Items"
