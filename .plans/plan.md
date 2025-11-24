# Django TODO Application – Implementation Plan

This plan outlines how to build a simple Django web application that can:
- Create, edit, and delete TODO items
- Assign due dates
- Mark TODO items as complete

The plan follows the Django and Python best practices defined in `.junie/guidelines.md` and the project README.

## 1. Project Setup
1. Initialize environment and dependencies — [x] Completed (2025-11-24)
   - Use `uv` for package management — [x] (uv.lock present)
   - Add runtime and dev dependencies — [x]
     - django — [x]
     - psycopg2-binary (optional; use SQLite by default for local dev) — [x] (optional extra: `postgres` group)
     - pytest — [x]
     - pytest-django — [x]
     - isort — [x]
     - ruff (formatter and linter; configure to 120-char line length) — [x]
   - Configure `pyproject.toml` for tools (isort/ruff) — [x]
2. Start Django project — [x] Completed (2025-11-24)
   - `django-admin startproject config .` (single settings module approach) — [x]
   - Ensure secrets are read from environment variables (e.g., `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `DATABASE_URL`) — [x]
   - Do not commit secrets; reference `.env` (not committed) via `os.environ` — [x] (secrets read from env; no secrets committed)
3. Static and templates setup — [x] Completed (2025-11-24)
   - Configure `TEMPLATES` with `DIRS=[BASE_DIR / "templates"]` — [x]
   - Configure `STATIC_URL` and `STATICFILES_DIRS = [BASE_DIR / "static"]` — [x]
   - Optionally add WhiteNoise for static serving in production (not required for local dev) — [ ] Optional, not required for local dev

## 2. App Creation and Data Model — [x] Completed (2025-11-24 16:12)
1. Create app `todos` — [x]
   - `python manage.py startapp todos` — [x]
   - Add `todos` to `INSTALLED_APPS` — [x]
2. Model design (use Django ORM; avoid raw SQL) — [x]
   - `Todo` model — [x]
     - `title: CharField(max_length=200)` (required) — [x]
     - `description: TextField(blank=True)` — [x]
     - `due_date: DateField(null=True, blank=True, db_index=True)` — [x]
     - `completed: BooleanField(default=False, db_index=True)` — [x]
     - `created_at: DateTimeField(auto_now_add=True)` — [x]
     - `updated_at: DateTimeField(auto_now=True)` — [x]
     - `__str__`: return f"{title} (due {due_date})" when due date exists, else title — [x]
     - `class Meta`:
       - `ordering = ["completed", "due_date", "-created_at"]` — [x]
       - `verbose_name = "To‑Do Item"`, `verbose_name_plural = "To‑Do Items"` — [x]
3. Admin — [x]
   - Register `Todo` with list display (`title`, `due_date`, `completed`, `created_at`), search (`title`), filters (`completed`, `due_date`) — [x]

## 3. Forms — [x] Completed (2025-11-24 16:44)
- Use `ModelForm` for `Todo` — [x]
  - Include fields: `title`, `description`, `due_date`, `completed` — [x]
  - Add basic widgets (e.g., `DateInput` with type="date") — [x]
  - Server-side validation: ensure `due_date` is not in the past (warning/validation error as desired) — [x]

## 4. Views and URLs — [x] Completed (2025-11-24 16:44)
1. Views (class-based)
   - `TodoListView` (`ListView`) — [x]
     - Paginate with `paginate_by = 10` (per guidelines) — [x]
     - Allow filtering by completion status via query param `?status=(all|open|completed)` — [x]
     - Order by `completed`, `due_date`, then `-created_at` — [x]
     - Optimize with `.only("id", "title", "due_date", "completed")` — [x]
   - `TodoCreateView` (`CreateView`) with `ModelForm` — [x]
   - `TodoUpdateView` (`UpdateView`) with `ModelForm` — [x]
   - `TodoDeleteView` (`DeleteView`) with confirmation — [x]
   - `toggle_complete` (`View` or small function view): toggles `completed` with `get_object_or_404` — [x]
   - All views must validate and sanitize inputs (ModelForm covers most cases), use `try/except` for graceful handling — [x]
2. URL configuration (end with trailing slashes)
   - `todos/` → list (name: `todos:list`) — [x]
   - `todos/new/` → create (name: `todos:create`) — [x]
   - `todos/<int:pk>/edit/` → update (name: `todos:edit`) — [x]
   - `todos/<int:pk>/delete/` → delete (name: `todos:delete`) — [x]
   - `todos/<int:pk>/toggle-complete/` → toggle (name: `todos:toggle_complete`) — [x]
   - Include `app_name = "todos"` in `todos/urls.py` — [x]

## 5. Templates — [x] Completed (2025-11-24 16:44)
- Use template inheritance with `templates/base.html` — [x]
- Templates: `todos/home.html`, `todos/form.html`, `todos/confirm_delete.html` — [x]
- Use `{% load static %}` and proper CSRF protection in forms — [x]
- Keep logic minimal in templates; formatting and selection happen in views/forms — [x]
- Simple, clean UI with accessible labels and buttons; optional styling via basic CSS in `static/` — [x]

## 6. Security and Settings — [x] Completed (2025-11-24 16:50)
- CSRF protection via Django forms and `{% csrf_token %}` in templates — [x]
- Use environment variables for all secrets/settings in `settings.py` — [x]
- Configure `ALLOWED_HOSTS` appropriately — [x]
- Consider security middlewares already included by Django; keep default `X_FRAME_OPTIONS` and `SECURE_*` toggles production-ready via env — [x]
  - Added env-driven `CSRF_TRUSTED_ORIGINS`, secure cookies, HSTS, SSL redirect, `SECURE_REFERRER_POLICY`, `X_FRAME_OPTIONS`, and optional `SECURE_PROXY_SSL_HEADER` — [x]

## 7. Database and Migrations — [x] Completed (2025-11-24 16:54)
- Use migrations for all DB changes — [x]
  - Initial migration created: `todos/migrations/0001_initial.py` — [x]
  - Local database migrated (SQLite default) — [x]
- Add indexes via `db_index=True` on frequently queried fields (`completed`, `due_date`) — [x]
- Avoid N+1 queries (not likely here); use `only()` in list view to limit columns — [x]

## 8. Testing (pytest-django)
1. Configure pytest
   - Add `pytest.ini` with `DJANGO_SETTINGS_MODULE = config.settings`
2. Tests to write
   - Model tests: `__str__`, ordering, validation (no past due date if enforced)
   - View tests: list pagination, create/update/delete flows, toggle complete, redirects, CSRF
   - URL tests: reverse/resolve names with trailing slashes
   - Template tests: important context variables, presence of CSRF token in forms
   - Negative scenarios: invalid form data (missing title, invalid date)

## 9. Developer Experience
- `make`-like scripts (optional) or `uv run` commands for:
  - `uv run python manage.py migrate`
  - `uv run python manage.py runserver`
  - `uv run pytest -q`
- Enforce style: run `isort` and `ruff format`/`ruff check --fix` on commit hooks if desired

## 10. Delivery Checklist
- App bootstraps with `uv` and installs
- `config` project created, `todos` app added
- CRUD works from UI with CSRF protection
- Pagination on list view
- All URL names descriptive and end with trailing slashes
- Templates use inheritance and `{% load static %}`
- Migrations created and applied
- Tests for key paths passing with `pytest-django`
