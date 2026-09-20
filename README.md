# url-shortener

## Русский

Простой API для сокращения URL: создание auto/custom short codes и redirect на исходный адрес. Слоёный pet-проект на FastAPI с PostgreSQL.

### Возможности

- Создание короткой ссылки из long URL (`POST /shorten`); auto code — base62 кодирование по id записи в бд
- Создание custom short code (`POST /shorten/custom`) с валидацией через Pydantic
- Идемпотентное повторное использование существующего auto code для того же `long_url`
- Повторный `POST /shorten/custom` с тем же `custom_code` и тем же `long_url` возвращает существующий код (у одного URL может быть несколько custom aliases)
- Redirect по code с HTTP `302` (`GET /{code}`); счётчик кликов увеличивается в БД (отдельного stats endpoint нет)
- Health endpoint (`GET /health`)
- JSON-тело ошибок с полями `message`, `detail` и `code`
- Миграции схемы через Alembic (накатываются при старте app в Compose)
- Конфиг из environment / `.env` через pydantic-settings
- CORS origins из конфига

### Стек

- Python `>=3.13`
- FastAPI + Uvicorn
- SQLAlchemy 2 + psycopg 3
- PostgreSQL 16 (Compose image `postgres:16-alpine`)
- Alembic
- pydantic-settings, pybase62
- uv (зависимости и запуск)
- Docker Compose

### Структура проекта

Слои: HTTP → service → repository → ORM.

```text
src/url_shortener/
  api/           # HTTP routes, dependencies
  services/      # business logic (LinkService, ShortenerService)
  repositories/  # DB access
  models/        # SQLAlchemy ORM
  schemas/       # Pydantic request/response
  db/            # engine, session
  config.py      # settings from env
  errors.py      # exception → JSONResponse handlers
  exceptions.py  # domain errors
  main.py        # FastAPI app entry
alembic/         # migrations
alembic.ini
tests/           # pytest
Dockerfile
docker-compose.yaml
pyproject.toml
uv.lock
.env.example
```

### Требования

- Docker и Docker Compose (рекомендуемый быстрый старт)
- Для локального app без Docker: Python `>=3.13`, [uv](https://docs.astral.sh/uv/) и доступный PostgreSQL

### Быстрый старт (Docker Compose)

#### 1. Clone и настройка env

```bash
git clone <repo-url>
cd url-shortener
cp .env.example .env
```

При необходимости отредактируйте `.env` (как минимум `PUBLIC_BASE_URL` и секреты для локальной БД). Compose подставляет credentials из `.env` и задаёт `POSTGRES_HOST=url-shortener-db` для сервиса `app`.

#### 2. Запуск

```bash
docker compose up --build
```

Поднимаются PostgreSQL и API. Контейнер app выполняет `alembic upgrade head`, затем `url-shortener` на порту `8000`.

Postgres проброшен на host-порт `5432`, чтобы подключаться локальными инструментами (`psql`, GUI) или запускать app на хосте к той же БД (`POSTGRES_HOST=localhost`).

#### 3. Проверка

```bash
curl http://localhost:8000/health
```

Ожидаемый ответ: `{"status":"ok"}`.

Интерактивный OpenAPI: [http://localhost:8000/docs](http://localhost:8000/docs).

### Переменные окружения

Читаются из environment и опционально из `.env` (см. `.env.example`).

| Variable | Description | Example |
|----------|-------------|---------|
| `POSTGRES_USER` | Пользователь PostgreSQL | `shortener` |
| `POSTGRES_PASSWORD` | Пароль PostgreSQL | `shortener` |
| `POSTGRES_DB` | Имя базы | `url_shortener` |
| `POSTGRES_HOST` | Хост БД (`localhost` на host; для app в Compose — `url-shortener-db`) | `localhost` |
| `PORT` | Порт PostgreSQL | `5432` |
| `PUBLIC_BASE_URL` | Base URL, встраиваемый в созданные short links | `http://localhost:8000` |
| `CORS_ORIGINS` | JSON-список разрешённых CORS origins | `["http://localhost:8000", "http://127.0.0.1:8000"]` |

### Миграции

В Docker Compose миграции выполняются автоматически до старта app:

```text
uv run alembic upgrade head && uv run url-shortener
```

Локально (app на host, БД доступна):

```bash
uv run alembic upgrade head
```

Новая revision (после изменения models):

```bash
uv run alembic revision --autogenerate -m "describe change"
```

### API

Base URL по умолчанию: `http://localhost:8000`.

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Liveness: `{"status": "ok"}` |
| `POST` | `/shorten` | Создать (или переиспользовать) auto short URL → `201` + `{ "short_url": "..." }` |
| `POST` | `/shorten/custom` | Создать custom code (или вернуть его, если тот же code уже привязан к этому URL) → `201` + `{ "short_url": "..." }` |
| `GET` | `/{code}` | Redirect на long URL (`302`) |

Request bodies:

- `POST /shorten`: `{ "long_url": "https://example.com" }` (`HttpUrl`, max length 2048)
- `POST /shorten/custom`: то же + `"custom_code"` (3–32 символа, `^[a-zA-Z0-9_-]+$`)

#### Примеры (curl)

##### Create short URL

```bash
curl -s -X POST http://localhost:8000/shorten \
  -H 'Content-Type: application/json' \
  -d '{"long_url": "https://example.com"}'
```

##### Create custom short URL

```bash
curl -s -X POST http://localhost:8000/shorten/custom \
  -H 'Content-Type: application/json' \
  -d '{"long_url": "https://example.com", "custom_code": "my-link"}'
```

##### Redirect

```bash
curl -i http://localhost:8000/<code>
```

#### Ответы с ошибками

Ошибки приложения возвращаются в JSON:

```json
{
  "message": "Not found",
  "detail": "No link found for the given short code.",
  "code": "<short-code>"
}
```

| Status | When |
|--------|------|
| `404` | Неизвестный short code при redirect (`LinkNotFoundError`) |
| `409` | Custom code уже занят другим URL (`CustomCodeAlreadyTakenError`) |
| `500` | Внутренние случаи: коллизия auto-code (`CodeAlreadyTakenError`) или отсутствие ожидаемого alias после create (`CodeNotFoundError`) |

Ошибки валидации (некорректный URL / формат custom code) — стандартные ответы FastAPI/Pydantic `422`.

### Локальная разработка (без Docker app)

1. Поднимите только Postgres, например: `docker compose up db`.
2. Скопируйте `.env.example` → `.env` с `POSTGRES_HOST=localhost` и подходящими credentials.
3. Установка и запуск:

```bash
uv sync --group dev
uv run alembic upgrade head
uv run url-shortener
```

API слушает `0.0.0.0:8000`.

### Тесты

```bash
uv sync --group dev
uv run pytest
```

Покрытие сейчас минимальное (unit test для `ShortenerService.create_code`). Отдельная test database для этого теста не нужна.

### Лицензия

MIT — см. [LICENSE](LICENSE).

---

## English

Simple URL shortener API: create auto or custom short codes and redirect to the original URL. Built as a layered FastAPI pet project with PostgreSQL.

### Features

- Create a short link from a long URL (`POST /shorten`); auto code is base62 of the row id
- Create a custom short code (`POST /shorten/custom`), validated by Pydantic
- Idempotent reuse of an existing auto code for the same `long_url`
- Repeating `POST /shorten/custom` with the same `custom_code` and the same `long_url` returns the existing code (one URL may have multiple custom aliases)
- Redirect by code with HTTP `302` (`GET /{code}`); click counter is incremented in the DB (no separate stats endpoint)
- Health endpoint (`GET /health`)
- JSON error body with `message`, `detail`, and `code`
- Schema migrations via Alembic (applied on Compose app start)
- Config from environment / `.env` via pydantic-settings
- CORS origins from config

### Stack

- Python `>=3.13`
- FastAPI + Uvicorn
- SQLAlchemy 2 + psycopg 3
- PostgreSQL 16 (Compose image `postgres:16-alpine`)
- Alembic
- pydantic-settings, pybase62
- uv (deps + run)
- Docker Compose

### Project structure

Layered layout: HTTP → service → repository → ORM.

```text
src/url_shortener/
  api/           # HTTP routes, dependencies
  services/      # business logic (LinkService, ShortenerService)
  repositories/  # DB access
  models/        # SQLAlchemy ORM
  schemas/       # Pydantic request/response
  db/            # engine, session
  config.py      # settings from env
  errors.py      # exception → JSONResponse handlers
  exceptions.py  # domain errors
  main.py        # FastAPI app entry
alembic/         # migrations
alembic.ini
tests/           # pytest
Dockerfile
docker-compose.yaml
pyproject.toml
uv.lock
.env.example
```

### Requirements

- Docker and Docker Compose (recommended quick start)
- For local (non-Docker) app: Python `>=3.13`, [uv](https://docs.astral.sh/uv/), and a reachable PostgreSQL

### Quick start (Docker Compose)

#### 1. Clone and configure env

```bash
git clone <repo-url>
cd url-shortener
cp .env.example .env
```

Edit `.env` if needed (at least `PUBLIC_BASE_URL` and secrets for local DB use). Compose interpolates DB credentials from `.env` and sets `POSTGRES_HOST=url-shortener-db` for the `app` service.

#### 2. Run

```bash
docker compose up --build
```

This starts PostgreSQL and the API. The app container runs `alembic upgrade head`, then `url-shortener` on port `8000`.

Postgres is published on host port `5432` so you can connect with local tools (`psql`, GUI clients) or run the app on the host against the same database (`POSTGRES_HOST=localhost`).

#### 3. Check

```bash
curl http://localhost:8000/health
```

Expected: `{"status":"ok"}`.

Interactive OpenAPI: [http://localhost:8000/docs](http://localhost:8000/docs).

### Environment variables

Loaded from the environment and optionally from `.env` (see `.env.example`).

| Variable | Description | Example |
|----------|-------------|---------|
| `POSTGRES_USER` | PostgreSQL user | `shortener` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `shortener` |
| `POSTGRES_DB` | Database name | `url_shortener` |
| `POSTGRES_HOST` | DB host (`localhost` on host; for the Compose `app` service — `url-shortener-db`) | `localhost` |
| `PORT` | PostgreSQL port (not the API port; the API listens on `8000`) | `5432` |
| `PUBLIC_BASE_URL` | Base URL embedded in created short links | `http://localhost:8000` |
| `CORS_ORIGINS` | JSON list of allowed CORS origins | `["http://localhost:8000", "http://127.0.0.1:8000"]` |

### Migrations

In Docker Compose, migrations run automatically before the app starts:

```text
uv run alembic upgrade head && uv run url-shortener
```

Locally (app on the host, DB reachable):

```bash
uv run alembic upgrade head
```

Create a new revision (when models change):

```bash
uv run alembic revision --autogenerate -m "describe change"
```

### API

Default base URL: `http://localhost:8000`.

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Liveness: `{"status": "ok"}` |
| `POST` | `/shorten` | Create (or reuse) auto short URL → `201` + `{ "short_url": "..." }` |
| `POST` | `/shorten/custom` | Create a custom code (or return it if that code is already bound to this URL) → `201` + `{ "short_url": "..." }` |
| `GET` | `/{code}` | Redirect to long URL (`302`) |

Request bodies:

- `POST /shorten`: `{ "long_url": "https://example.com" }` (`HttpUrl`, max length 2048)
- `POST /shorten/custom`: same + `"custom_code"` (3–32 chars, `^[a-zA-Z0-9_-]+$`)

#### Examples (curl)

##### Create short URL

```bash
curl -s -X POST http://localhost:8000/shorten \
  -H 'Content-Type: application/json' \
  -d '{"long_url": "https://example.com"}'
```

##### Create custom short URL

```bash
curl -s -X POST http://localhost:8000/shorten/custom \
  -H 'Content-Type: application/json' \
  -d '{"long_url": "https://example.com", "custom_code": "my-link"}'
```

##### Redirect

```bash
curl -i http://localhost:8000/<code>
```

#### Error responses

Application errors return JSON:

```json
{
  "message": "Not found",
  "detail": "No link found for the given short code.",
  "code": "<short-code>"
}
```

| Status | When |
|--------|------|
| `404` | Unknown short code on redirect (`LinkNotFoundError`) |
| `409` | Custom code already taken by another URL (`CustomCodeAlreadyTakenError`) |
| `500` | Internal cases: auto-code collision (`CodeAlreadyTakenError`) or missing expected alias after create (`CodeNotFoundError`) |

Validation errors (bad URL / custom code shape) use FastAPI/Pydantic default `422` responses.

### Local development (without Docker app)

1. Start only Postgres, e.g. `docker compose up db`.
2. Copy `.env.example` → `.env` with `POSTGRES_HOST=localhost` and matching credentials.
3. Install and run:

```bash
uv sync --group dev
uv run alembic upgrade head
uv run url-shortener
```

API listens on `0.0.0.0:8000`.

### Tests

```bash
uv sync --group dev
uv run pytest
```

Current coverage is minimal (unit test for `ShortenerService.create_code`). No separate test database wiring is required for that test.

### License

MIT — see [LICENSE](LICENSE).
