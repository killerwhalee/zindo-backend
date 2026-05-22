# zindo-backend

Django REST Framework API for Zindo, a tutoring academy management system. Tracks students, textbook assignments (Sheets), and daily learning records.

## Tech Stack

- **Framework:** Django 6 + Django REST Framework
- **Database:** SQLite
- **Package manager:** uv
- **Linting:** Ruff (enforced via pre-commit)
- **External API:** Naver Book Search (ISBN lookup)

## Getting Started

```bash
uv sync
uv run manage.py migrate
uv run manage.py runserver   # http://localhost:8000
```

**Environment** — create `.env`:

```
SECRET_KEY=...
NAVER_CLIENT_ID=...
NAVER_CLIENT_SECRET=...
```

**Pre-commit hooks** (run on every commit — install once):

```bash
uv run pre-commit install
```

## Project Structure

```
core/               # Django project config (settings, URLs, WSGI)
zindo/              # All domain logic
├── models.py       # Student, TextBook, Sheet, Record
├── serializers.py  # DRF serializers with nested read fields (_detail suffix)
├── viewsets.py     # ModelViewSets with annotations and filtering
└── utils.py        # search_book(isbn), get_subject(title)
```

## API Endpoints

All endpoints are under `/zindo/` via DRF's `DefaultRouter`.

| Endpoint | Methods | Notes |
|---|---|---|
| `/zindo/students/` | GET, POST, PATCH, DELETE | Annotated with sheet counts |
| `/zindo/textbooks/` | GET, POST, PATCH, DELETE | |
| `/zindo/textbooks/search/?isbn=` | GET | DB lookup then Naver API fallback |
| `/zindo/sheets/` | GET, POST, PATCH, DELETE | Filter by `?student__id=` |
| `/zindo/records/` | GET, POST, PATCH, DELETE | Filter by `?sheet__id=` |

## Key Conventions

- Each serializer has an `object` field (type discriminator string).
- Nested read fields use a `_detail` suffix (`student_detail`, `sheet_detail`); write fields are plain FK integers.
- Sheet creation accepts either `isbn` (Naver lookup) or `name` + `subject` (manual). A student cannot have two active sheets for the same textbook.

## Branch Strategy

- **`dev`** — active development; all work goes here
- **`main`** — production; push to `main` triggers GitHub Actions deploy (SSH → `git pull` → `uv sync` → `migrate` → `systemctl restart`)
