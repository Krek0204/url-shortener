# TODO — зрелый пет-проект (url-shortener)

**Цель:** не Production Ready «как в компании», а зрелый портфолио-бэкенд: клонировал → поднял → понял API → тесты зелёные, код без стыдных костылей.

**Вердикт по текущему состоянию:** аккуратный учебный MVP со слоями API → service → repository. До «mature pet» не хватает доков, миграций, нормальных ошибок/тестов и мелкой гигиены.

---

## Что уже хорошо

- Слои: API → service → repository → models
- Pydantic-валидация URL и custom code
- Unique на `long_url` / `code`, частичная обработка race через `IntegrityError`
- Exception handlers отделены от HTTP
- `.env` в `.gitignore`, есть `.env.example`
- Healthcheck у Postgres в compose, `uv.lock`

---

## Делать — высокий ROI

Чеклист до состояния «mature pet».

### 1. Документация и запуск

- [ ] README: что это, как поднять (`docker compose up`), env vars, примеры curl
- [ ] Починить `PUBLIC_BASE_URL` и `.env.example` (`localhost`, не `0.0.0.0`)
- [ ] Добавить `.dockerignore`
- [ ] Секреты в compose брать из `.env`, не хардкодить пароли в yaml
- [ ] В README описать, зачем Postgres проброшен на хост (или убрать проброс)

### 2. Базовая гигиена API

- [ ] Редирект `302` или `307` вместо `301` (`api/links.py`)
- [ ] Нормальные JSON-ошибки (`detail` / `code` / `message`) — без шуток и имён классов (`errors.py`)
- [ ] Простой `GET /health` (хотя бы «жив»)
- [ ] CORS: origins из env, не `allow_origins=['*']`

### 3. Миграции

- [ ] Подключить Alembic
- [ ] Убрать `create_all` из lifespan (или оставить только для тестов)
- [ ] Зафиксировать в README: как накатывать миграции

### 4. Тесты и зависимости

- [ ] Unit-тесты `LinkService`: создание, custom conflict, idempotency по `long_url`
- [ ] 1–2 API-теста через `TestClient` (+ тестовая БД)
- [ ] Вынести `pytest` из runtime-зависимостей в dev / dependency-groups
- [ ] Решить по Redis: либо простой кэш `code → long_url`, либо убрать зависимость

### 5. Мелкий рефакторинг

- [ ] snake_case: `has_url_auto_code`, `get_url_auto_code`, …
- [ ] Убрать мёртвый `get_id_by_code` (если не нужен)
- [ ] URL-encode пароля в DSN; `pool_pre_ping=True`
- [ ] Settings: `extra='forbid'` (или не `allow`)
- [ ] Поправить обработку коллизии auto-code и `CodeNotFoundError` → не отдавать странный 500 клиенту как «норму»

### 6. Лёгкий CI и качество

- [ ] ruff (и при желании минимальный mypy)
- [ ] GitHub Action: lint + pytest
- [ ] Убрать/заменить комментарий `# pylint` без настроенного линтера

### 7. Compose для демо (без prod-оверинжиниринга)

- [ ] env из `.env`
- [ ] Опционально: healthcheck у app
- [ ] Не раздувать в multi-stage / non-root / Helm — этого для пет достаточно не делать

---

## Порядок работ (ориентир)

1. README + env/compose + `.dockerignore`
2. Ошибки + `302/307` + `/health` + CORS из env
3. Alembic
4. Тесты LinkService + API; pytest → dev
5. ruff + CI
6. Redis: кэш или удалить зависимость
7. (Опционально) простой rate limit на `POST /shorten`

---

## Можно позже — если хочется углубить тему

Не блокер для «mature pet», но хорошая история в README/портфолио.

| Тема | Минимальная версия |
|------|--------------------|
| Rate limit | In-memory / Redis на `POST /shorten` |
| Redis-кэш | `code → long_url` на редиректе |
| API prefix | `/api/v1` + редирект отдельно от management |
| Delete / TTL | Одна ручка удаления или `expires_at`, без пользователей |
| Счётчик кликов | На уровне alias или простой Redis INCR |
| Async SQLAlchemy | Не обязательно; sync + нормальный pool ок |

---

## Не делать (перегиб для пет-проекта)

Оставить как «если когда-нибудь в настоящий прод» — сознательно вне скоупа:

- Полноценный auth (JWT, OAuth, роли) — только если цель именно поучить auth
- Phishing-сканеры, CAPTCHA, WAF, allow/deny lists доменов «как у Bitly»
- Multi-stage non-root Docker, ProxyHeaders, SSL к Postgres, prod overlay / Helm / K8s
- Prometheus / Grafana / Sentry «как в компании»
- Soft-delete, `owner_id`, analytics pipeline, очереди ради счётчиков кликов
- Переход на async «ради async»
- Отдельный readiness с проверкой всех зависимостей, graceful shutdown тонкая настройка
- Разделение `dev/stage/prod` конфигов сверх простого `.env`

---

## Контекст из аудита (справочно)

Ниже — исходные находки. Для пет-проекта они **не все** входят в must-have; приоритет — секции выше.

| # | Находка | Для mature pet |
|---|---------|----------------|
| Схема через `create_all` | Нужны миграции | **Делать** |
| Нет auth / rate limit | Спам, phishing | Rate limit — опционально; auth — **не делать** |
| Секреты / `0.0.0.0` / CORS `*` | Слабые дефолты | **Делать** (лёгкая гигиена) |
| Нет `/health` | Неудобно для демо/compose | **Делать** (простой health) |
| Dockerfile не prod-grade | root, полный образ | **Не делать** (перегиб) |
| Open redirect / phishing | Риск домена | **Не делать** (пет) |
| Редирект `301` | Кэш, кривые клики | **Делать** → `302`/`307` |
| Sync SQLAlchemy | Нагрузка | **Не делать** (pool_pre_ping хватит) |
| Пароль в DSN без encoding | Ломается на спецсимволах | **Делать** |
| Хрупкий `LinkService` / 500 | Плохой контракт | **Делать** (ошибки + тесты) |
| Redis не используется | Мёртвая зависимость | **Делать** (кэш или убрать) |
| pytest в runtime | Раздувает образ | **Делать** |
| Нет CI / почти нет тестов | Регрессии | **Делать** |
| Нет метрик / трейсинга | Observability | **Не делать** |
| Нет delete/TTL/stats API | Неполный продукт | **Опционально** |
| `GET /{code}` на корне | Конфликты путей | **Опционально** (prefix) |
| Модель без owner/TTL | Упрощённая схема | **Ок для пет** |
| Compose только локалка | Нет prod overlay | **Ок**; чуть подчистить для демо |
| Пустой README | Нельзя воспроизвести | **Делать** |
| `extra='allow'` | Опечатки в env | **Делать** |
| Нет ProxyHeaders / workers | За прокси | **Не делать** |
