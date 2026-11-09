# Task Manager API

![tests](https://github.com/YOUR_USERNAME/task-manager-api/actions/workflows/tests.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)

A REST API for managing personal to-do tasks, built with **FastAPI**, **SQLAlchemy** and **JWT authentication**.
Users sign up, log in, and manage their own tasks — with filtering, search, and pagination.

## Features

- 🔐 **User accounts** — register and log in with hashed passwords (bcrypt)
- 🎟️ **JWT authentication** — stateless Bearer tokens that expire
- ✅ **Full CRUD for tasks** — create, read, update (partial), delete
- 🔎 **Filtering & search** — by status, priority, due date, or text
- 📄 **Pagination** — `skip` / `limit` with a total count
- 🛡️ **Data isolation** — users can only ever access their own tasks
- 📚 **Auto-generated docs** — interactive Swagger UI at `/docs`
- 🧪 **Automated tests** — 16 pytest tests, run on every push with GitHub Actions

## Tech stack

| Tool | What it does here |
|------|-------------------|
| [FastAPI](https://fastapi.tiangolo.com/) | Web framework — routing, validation, docs |
| [SQLAlchemy 2](https://www.sqlalchemy.org/) | ORM — talks to the database using Python classes |
| [Pydantic](https://docs.pydantic.dev/) | Validates request/response data |
| SQLite | Simple file-based database (no install needed) |
| PyJWT + bcrypt | Tokens and password hashing |
| pytest | Testing |

## Getting started

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/task-manager-api.git
cd task-manager-api

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env            # Windows: copy .env.example .env

# 5. Run the server
uvicorn app.main:app --reload
```

Open **http://127.0.0.1:8000/docs** to try every endpoint in your browser.

## API endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|:----:|-------------|
| GET | `/` | | Health check |
| POST | `/auth/register` | | Create an account |
| POST | `/auth/login` | | Get an access token |
| GET | `/auth/me` | 🔒 | Current user info |
| POST | `/tasks` | 🔒 | Create a task |
| GET | `/tasks` | 🔒 | List tasks (filters + pagination) |
| GET | `/tasks/{id}` | 🔒 | Get one task |
| PATCH | `/tasks/{id}` | 🔒 | Update a task |
| DELETE | `/tasks/{id}` | 🔒 | Delete a task |

**Filters for `GET /tasks`:** `completed`, `priority` (`low`/`medium`/`high`), `search`, `due_before` (YYYY-MM-DD), `skip`, `limit`

## Example usage (curl)

```bash
# Register
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "email": "alice@example.com", "password": "secret123"}'

# Log in -> copy the "access_token" from the response
curl -X POST http://127.0.0.1:8000/auth/login \
  -d "username=alice&password=secret123"

# Create a task
curl -X POST http://127.0.0.1:8000/tasks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn FastAPI", "priority": "high", "due_date": "2026-12-01"}'

# List high-priority open tasks
curl "http://127.0.0.1:8000/tasks?priority=high&completed=false" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Running tests

```bash
pytest -v
```

Tests use a separate in-memory database, so they never touch your real data.

## Project structure

```
task-manager-api/
├── app/
│   ├── main.py          # Creates the app and plugs in the routers
│   ├── config.py        # Settings read from environment variables
│   ├── database.py      # Database connection and session
│   ├── models.py        # Database tables (User, Task)
│   ├── schemas.py       # Request/response shapes (Pydantic)
│   ├── security.py      # Password hashing + JWT logic
│   └── routers/
│       ├── auth.py      # /auth endpoints
│       └── tasks.py     # /tasks endpoints
├── tests/               # pytest tests
├── .github/workflows/   # CI: runs tests on every push
├── requirements.txt
└── .env.example
```

## What I learned

Building this project taught me the core ideas behind real-world APIs:

- **REST design** — resources (`/tasks`), HTTP methods (GET/POST/PATCH/DELETE), and meaningful status codes (201 Created, 204 No Content, 401, 404, 409, 422)
- **Models vs schemas** — how data is *stored* is different from what the API *exposes* (e.g. never returning password hashes)
- **Validation** — letting Pydantic reject bad input before it reaches the database
- **Authentication** — hashing passwords, issuing JWTs, and protecting endpoints with dependencies
- **Authorization** — making sure users can only touch their own data
- **Dependency injection** — FastAPI's `Depends()` for database sessions and the current user
- **Testing** — isolated test databases, dependency overrides, and CI with GitHub Actions

## Ideas for next steps

- [ ] Add Alembic for database migrations
- [ ] Switch to PostgreSQL and add a Dockerfile / docker-compose
- [ ] Add task categories or tags
- [ ] Add refresh tokens
- [ ] Deploy to Render, Railway or Fly.io

## License

MIT — see [LICENSE](LICENSE).
