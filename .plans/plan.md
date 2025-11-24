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

## 3. Forms
- Use `ModelForm` for `Todo`
  - Include fields: `title`, `description`, `due_date`, `completed`
  - Add basic widgets (e.g., `DateInput` with type="date")
  - Server-side validation: ensure `due_date` is not in the past (warning/validation error as desired)

## 4. Views and URLs
1. Views (class-based)
   - `TodoListView` (`ListView`):
     - Paginate with `paginate_by = 10` (per guidelines)
     - Allow filtering by completion status via query param `?status=(all|open|completed)`
     - Order by `completed`, `due_date`, then `-created_at`
     - Optimize with `.only("id", "title", "due_date", "completed")`
   - `TodoCreateView` (`CreateView`) with `ModelForm`
   - `TodoUpdateView` (`UpdateView`) with `ModelForm`
   - `TodoDeleteView` (`DeleteView`) with confirmation
   - `toggle_complete` (`View` or small function view): toggles `completed` with `get_object_or_404`
   - All views must validate and sanitize inputs (ModelForm covers most cases), use `try/except` for graceful handling
2. URL configuration (end with trailing slashes)
   - `todos/` → list (name: `todos:list`)
   - `todos/new/` → create (name: `todos:create`)
   - `todos/<int:pk>/edit/` → update (name: `todos:edit`)
   - `todos/<int:pk>/delete/` → delete (name: `todos:delete`)
   - `todos/<int:pk>/toggle-complete/` → toggle (name: `todos:toggle_complete`)
   - Include `app_name = "todos"` in `todos/urls.py`

## 5. Templates
- Use template inheritance with `templates/base.html`
- Templates: `todos/home.html`, `todos/form.html`, `todos/confirm_delete.html`
- Use `{% load static %}` and proper CSRF protection in forms
- Keep logic minimal in templates; formatting and selection happen in views/forms
- Simple, clean UI with accessible labels and buttons; optional styling via basic CSS in `static/`

## 6. Security and Settings
- CSRF protection via Django forms and `{% csrf_token %}` in templates
- Use environment variables for all secrets/settings in `settings.py`
- Configure `ALLOWED_HOSTS` appropriately
- Consider security middlewares already included by Django; keep default `X_FRAME_OPTIONS` and `SECURE_*` toggles produc­tion-ready via env

## 7. Database and Migrations
- Use migrations for all DB changes
- Add indexes via `db_index=True` on frequently queried fields (`completed`, `due_date`)
- Avoid N+1 queries (not likely here); use `only()` in list view to limit columns

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
