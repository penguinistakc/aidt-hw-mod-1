"""URL configuration for the Django project."""
from __future__ import annotations

from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("todos/", include("todos.urls")),
    # Redirect the site root to the todos home page
    path("", RedirectView.as_view(pattern_name="todos:list", permanent=False)),
]
