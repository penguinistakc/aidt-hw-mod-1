# aidt-hw-mod-1

Simple Django TODO application that lets you:
- Create, edit, and delete TODO items
- Assign due dates
- Mark TODO items as complete

The project follows Django/Python best practices outlined in `.junie/guidelines.md`.

## Developer experience: canonical commands (no Make-like scripts)

This project standardizes on `uv run` for all day-to-day tasks. The commands below are copy/paste‑ready for macOS, Linux, and Windows PowerShell.

### Prerequisites
- Python (the version in `.python-version`, if present)
- `uv` package manager: https://docs.astral.sh/uv/

### First-time setup
Install dependencies from `uv.lock`:
```
uv sync
```

Create and migrate the database:
```
uv run python manage.py migrate
```

Optional but recommended for local dev — create a superuser to access Django Admin:
```
uv run python manage.py createsuperuser
```

### Run the app locally
Start the development server on the default port 8000:
```
uv run python manage.py runserver
```

Specify a different host/port if needed (example: 0.0.0.0:8080):
```
uv run python manage.py runserver 0.0.0.0:8080
```

### Database and migrations
Make migrations after changing models:
```
uv run python manage.py makemigrations
```

Apply migrations:
```
uv run python manage.py migrate
```

(Optional) Load fixtures if/when you add them:
```
uv run python manage.py loaddata <fixture_name>
```

### Testing
Run the test suite (quiet):
```
uv run pytest -q
```

Run a specific test file or node:
```
uv run pytest tests/test_todos.py::test_toggle_complete
```

### Linting and formatting
Format with Ruff and isort:
```
uv run ruff format .
uv run isort .
```

Lint and auto-fix with Ruff:
```
uv run ruff check . --fix
```

### Useful Django utilities
Open a Django shell:
```
uv run python manage.py shell
```

Run system checks (helpful before deploy):
```
uv run python manage.py check --deploy
```

Collect static files (if/when you configure static hosting or use WhiteNoise in production):
```
uv run python manage.py collectstatic --noinput
```

### Environment configuration
Settings are read from environment variables in `config/settings.py`. Common variables:
- `SECRET_KEY` (required in production)
- `DEBUG` (`"True"` for local dev; empty/absent for production)
- `ALLOWED_HOSTS` (comma‑separated for production)
- `DATABASE_URL` (optional; defaults to SQLite if not provided)
- `CSRF_TRUSTED_ORIGINS` (comma‑separated, optional)

For local development, export variables in your shell session or use a `.env` loaded by your shell. Do not commit secrets to version control.

### Why `uv run`?
- Ensures commands run in the locked, reproducible environment defined by `uv.lock`
- Keeps local usage consistent with CI/CD steps
- Avoids platform‑specific task runners or Make-like wrappers

### Quick reference
- Install deps: `uv sync`
- Migrate: `uv run python manage.py migrate`
- Run server: `uv run python manage.py runserver`
- Tests: `uv run pytest -q`
- Format: `uv run ruff format .` and `uv run isort .`
- Lint: `uv run ruff check . --fix`
