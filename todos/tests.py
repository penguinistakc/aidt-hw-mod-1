from __future__ import annotations

from datetime import date, timedelta

import pytest
from django.urls import resolve, reverse

from .forms import TodoForm
from .models import Todo


@pytest.mark.django_db
class TestTodoModel:
    def test_str_includes_due_date_when_present(self) -> None:
        todo = Todo.objects.create(title="Pay bills", due_date=date.today())
        assert "Pay bills" in str(todo)
        assert "due" in str(todo)

    def test_str_without_due_date(self) -> None:
        todo = Todo.objects.create(title="No due")
        assert str(todo) == "No due"

    def test_default_ordering_completed_then_due_date_then_created_desc(self) -> None:
        # Create a mix: open items should come before completed.
        Todo.objects.create(title="A", due_date=date.today() + timedelta(days=1), completed=False)
        Todo.objects.create(title="B", due_date=date.today(), completed=False)
        Todo.objects.create(title="C", due_date=None, completed=False)
        Todo.objects.create(title="D", due_date=date.today(), completed=True)
        # Another completed to check ordering among completed by due/created
        Todo.objects.create(title="E", due_date=None, completed=True)

        titles_in_order = list(Todo.objects.all().values_list("title", flat=True))
        # Model Meta.ordering = ["completed", "due_date", "-created_at"].
        # Note: With the default DB behavior (e.g., SQLite/Postgres), NULLs sort first for ascending order fields.
        # Therefore among open items, due_date=None (C) appears before real dates (B, A),
        # and among completed items, due_date=None (E) appears before a real date (D).
        assert titles_in_order == ["C", "B", "A", "E", "D"]


class TestTodoForm:
    def test_due_date_cannot_be_in_past(self) -> None:
        past = date.today() - timedelta(days=1)
        form = TodoForm(data={"title": "Task", "description": "", "due_date": past, "completed": False})
        assert not form.is_valid()
        assert "Due date cannot be in the past." in form.errors["due_date"][0]

    def test_valid_today_due_date(self) -> None:
        today = date.today()
        form = TodoForm(data={"title": "Task", "description": "", "due_date": today, "completed": False})
        assert form.is_valid()

    def test_missing_title_is_invalid(self) -> None:
        form = TodoForm(data={"title": "", "description": "x", "due_date": "", "completed": False})
        assert not form.is_valid()
        assert "title" in form.errors


@pytest.mark.django_db
class TestUrls:
    def test_reverse_and_resolve_names(self) -> None:
        assert reverse("todos:list") == "/todos/"
        # Use dummy pk for patterns requiring it
        assert reverse("todos:create") == "/todos/new/"
        assert reverse("todos:edit", kwargs={"pk": 1}) == "/todos/1/edit/"
        assert reverse("todos:delete", kwargs={"pk": 1}) == "/todos/1/delete/"
        assert reverse("todos:toggle_complete", kwargs={"pk": 1}) == "/todos/1/toggle-complete/"

        # Resolve sanity checks
        assert resolve("/todos/").url_name == "list"
        assert resolve("/todos/new/").url_name == "create"
        assert resolve("/todos/1/edit/").url_name == "edit"
        assert resolve("/todos/1/delete/").url_name == "delete"
        assert resolve("/todos/1/toggle-complete/").url_name == "toggle_complete"


@pytest.mark.django_db
class TestViews:
    def test_list_view_default_open_only(self, client) -> None:
        Todo.objects.create(title="open", completed=False)
        Todo.objects.create(title="done", completed=True)
        resp = client.get(reverse("todos:list"))
        assert resp.status_code == 200
        titles = [t.title for t in resp.context["todos"]]
        assert titles == ["open"]
        assert resp.context["status"] == "open"

    def test_list_view_completed_filter(self, client) -> None:
        Todo.objects.create(title="open", completed=False)
        Todo.objects.create(title="done", completed=True)
        resp = client.get(reverse("todos:list") + "?status=completed")
        assert resp.status_code == 200
        titles = [t.title for t in resp.context["todos"]]
        assert titles == ["done"]
        assert resp.context["status"] == "completed"

    def test_list_view_all_filter(self, client) -> None:
        Todo.objects.create(title="open", completed=False)
        Todo.objects.create(title="done", completed=True)
        resp = client.get(reverse("todos:list") + "?status=all")
        assert resp.status_code == 200
        titles = [t.title for t in resp.context["todos"]]
        assert set(titles) == {"open", "done"}
        assert resp.context["status"] == "all"

    def test_pagination(self, client) -> None:
        for i in range(15):
            Todo.objects.create(title=f"Task {i}")
        resp_page1 = client.get(reverse("todos:list"))
        resp_page2 = client.get(reverse("todos:list") + "?page=2")
        assert resp_page1.status_code == 200
        assert resp_page2.status_code == 200
        assert resp_page1.context["page_obj"].paginator.per_page == 10
        assert resp_page1.context["page_obj"].number == 1
        assert resp_page2.context["page_obj"].number == 2

    def test_create_view_get_contains_csrf(self, client) -> None:
        resp = client.get(reverse("todos:create"))
        assert resp.status_code == 200
        assert "csrfmiddlewaretoken" in resp.content.decode()

    def test_create_view_post_valid(self, client) -> None:
        data = {"title": "New Task", "description": "", "due_date": "", "completed": False}
        resp = client.post(reverse("todos:create"), data=data, follow=True)
        assert resp.status_code == 200
        assert Todo.objects.filter(title="New Task").exists()
        # Redirect to list view
        assert resp.request["PATH_INFO"].endswith("/todos/")

    def test_create_view_post_invalid(self, client) -> None:
        data = {"title": "", "description": "", "due_date": "", "completed": False}
        resp = client.post(reverse("todos:create"), data=data)
        assert resp.status_code == 200  # Re-render form
        assert "This field is required" in resp.content.decode() or "This field is required." in resp.content.decode()

    def test_update_view_flow(self, client) -> None:
        todo = Todo.objects.create(title="Old")
        resp_get = client.get(reverse("todos:edit", args=[todo.pk]))
        assert resp_get.status_code == 200
        assert "csrfmiddlewaretoken" in resp_get.content.decode()

        resp_post = client.post(
            reverse("todos:edit", args=[todo.pk]),
            data={"title": "Updated", "description": "x", "due_date": "", "completed": True},
            follow=True,
        )
        assert resp_post.status_code == 200
        todo.refresh_from_db()
        assert todo.title == "Updated"
        assert todo.completed is True

    def test_delete_view_flow(self, client) -> None:
        todo = Todo.objects.create(title="To delete")
        resp_get = client.get(reverse("todos:delete", args=[todo.pk]))
        assert resp_get.status_code == 200
        assert "csrfmiddlewaretoken" in resp_get.content.decode()

        resp_post = client.post(reverse("todos:delete", args=[todo.pk]), follow=True)
        assert resp_post.status_code == 200
        assert not Todo.objects.filter(pk=todo.pk).exists()

    def test_toggle_complete_preserves_status_filter(self, client) -> None:
        todo = Todo.objects.create(title="X", completed=False)
        url = reverse("todos:toggle_complete", args=[todo.pk]) + "?status=completed"
        resp = client.post(url, follow=False)
        assert resp.status_code in (302, 301)
        todo.refresh_from_db()
        assert todo.completed is True
        # Redirect location should include the preserved status
        assert "?status=completed" in resp["Location"]

    def test_toggle_complete_get_is_safe_redirect(self, client) -> None:
        todo = Todo.objects.create(title="Y", completed=False)
        url = reverse("todos:toggle_complete", args=[todo.pk])
        resp = client.get(url, follow=False)
        assert resp.status_code in (302, 301)
        todo.refresh_from_db()
        assert todo.completed is False
