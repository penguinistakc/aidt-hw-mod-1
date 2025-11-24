from __future__ import annotations

from django.urls import path

from .views import (
    TodoCreateView,
    TodoDeleteView,
    TodoListView,
    TodoUpdateView,
    ToggleCompleteView,
)

app_name = "todos"

urlpatterns = [
    path("", TodoListView.as_view(), name="list"),
    path("new/", TodoCreateView.as_view(), name="create"),
    path("<int:pk>/edit/", TodoUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", TodoDeleteView.as_view(), name="delete"),
    path("<int:pk>/toggle-complete/", ToggleCompleteView.as_view(), name="toggle_complete"),
]
