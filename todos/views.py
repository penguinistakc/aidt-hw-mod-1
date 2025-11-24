from __future__ import annotations

from typing import Any

from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import DeleteView, ListView
from django.views.generic.edit import CreateView, UpdateView

from .forms import TodoForm
from .models import Todo


class TodoListView(ListView):
    """List view for `Todo` items with optional status filtering and pagination.

    Supports `?status=all|open|completed` (default: `open`). Orders by
    `completed`, `due_date`, then `-created_at`. Limits selected columns for
    performance using `only()`.
    """

    model = Todo
    context_object_name = "todos"
    paginate_by = 10
    template_name = "todos/home.html"

    def get_queryset(self) -> QuerySet[Todo]:  # type: ignore[override]
        status = self.request.GET.get("status", "open")
        qs = (
            Todo.objects.all()
            .only("id", "title", "due_date", "completed")
            .order_by("completed", "due_date", "-created_at")
        )
        if status == "completed":
            qs = qs.filter(completed=True)
        elif status == "open":
            qs = qs.filter(completed=False)
        # if status == "all": no extra filter
        return qs

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:  # type: ignore[override]
        ctx = super().get_context_data(**kwargs)
        ctx["status"] = self.request.GET.get("status", "open")
        return ctx


class TodoCreateView(CreateView):
    """Create a new `Todo` using `TodoForm`."""

    model = Todo
    form_class = TodoForm
    template_name = "todos/form.html"
    success_url = reverse_lazy("todos:list")


class TodoUpdateView(UpdateView):
    """Update an existing `Todo` using `TodoForm`."""

    model = Todo
    form_class = TodoForm
    template_name = "todos/form.html"
    success_url = reverse_lazy("todos:list")


class TodoDeleteView(DeleteView):
    """Delete a `Todo` with confirmation."""

    model = Todo
    template_name = "todos/confirm_delete.html"
    success_url = reverse_lazy("todos:list")


class ToggleCompleteView(View):
    """Toggle the `completed` flag for a `Todo` item.

    For safety, only allows POST requests. Redirects back to the list view,
    preserving the current `status` filter if present.
    """

    def post(self, request: HttpRequest, pk: int, *args: Any, **kwargs: Any) -> HttpResponse:
        todo = get_object_or_404(Todo, pk=pk)
        # Toggle completion status
        todo.completed = not todo.completed
        todo.save(update_fields=["completed", "updated_at"])

        # Preserve current status filter in redirect if present
        status = request.GET.get("status")
        url = reverse("todos:list")
        if status in {"all", "open", "completed"}:
            url = f"{url}?status={status}"
        return redirect(url)

    # Gracefully handle GET by redirecting without changes (no state change on GET)
    def get(self, request: HttpRequest, pk: int, *args: Any, **kwargs: Any) -> HttpResponse:  # pragma: no cover - safety
        return redirect(reverse("todos:list"))
