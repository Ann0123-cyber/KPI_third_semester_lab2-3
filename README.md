# Task Manager API

REST API для управління проектами та задачами. Реалізовано на **FastAPI + SQLAlchemy + PostgreSQL** з JWT-автентифікацією.

## Структура проекту

```
├── app/
│   ├── main.py              # Точка входу FastAPI
│   ├── config.py            # Налаштування (env vars)
│   ├── database.py          # SQLAlchemy engine + session
│   ├── dependencies.py      # get_current_user (JWT guard)
│   ├── models/              # ORM-моделі (User, Project, Task)
│   ├── schemas/             # Pydantic-схеми + валідація
│   ├── services/            # Бізнес-логіка (auth, project, task)
│   └── routers/             # HTTP-ендпоінти
├── tests/
│   ├── conftest.py          # Фікстури (SQLite in-memory DB)
│   ├── unit/                # Unit-тести (валідація, правила)
│   └── integration/         # Integration-тести (HTTP → DB)
├── docs/
│   └── use-cases.md         # Юзкейси системи
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Запуск

### Через Docker Compose (рекомендовано)

```bash
cp .env.example .env
docker compose up --build
```

API буде доступне на http://localhost:8000  
Swagger UI: http://localhost:8000/docs

### Локально

```bash
# 1. Встановити залежності
pip install -r requirements.txt

# 2. Налаштувати .env
cp .env.example .env
# відредагувати DATABASE_URL та SECRET_KEY

# 3. Запустити PostgreSQL (або змінити DATABASE_URL на SQLite для розробки)

# 4. Запустити сервер
uvicorn app.main:app --reload
```

## Запуск тестів

Тести використовують SQLite (`test.db`) — PostgreSQL не потрібен.

```bash
pip install -r requirements.txt
pytest
```

З покриттям:

```bash
pytest --cov=app --cov-report=term-missing
```

## API Endpoints

### Auth
| Метод | URL | Опис |
|-------|-----|------|
| POST | `/auth/register` | Реєстрація |
| POST | `/auth/login` | Вхід (повертає JWT) |
| GET | `/auth/me` | Профіль поточного користувача |

### Projects
| Метод | URL | Опис |
|-------|-----|------|
| GET | `/projects/` | Список своїх проектів |
| POST | `/projects/` | Створити проект |
| GET | `/projects/{id}` | Отримати проект |
| PATCH | `/projects/{id}` | Оновити проект |
| DELETE | `/projects/{id}` | Видалити проект |

### Tasks
| Метод | URL | Опис |
|-------|-----|------|
| GET | `/projects/{id}/tasks/` | Список задач проекту |
| POST | `/projects/{id}/tasks/` | Створити задачу |
| GET | `/projects/{id}/tasks/{tid}` | Отримати задачу |
| PATCH | `/projects/{id}/tasks/{tid}` | Оновити задачу |
| DELETE | `/projects/{id}/tasks/{tid}` | Видалити задачу |

Усі endpoints (крім `/auth/register`, `/auth/login`, `/health`) вимагають заголовка:
```
Authorization: Bearer <token>
```

## Бізнес-правила (інваріанти)

- Email користувача повинен бути валідним
- Пароль — мінімум 8 символів
- Username — 3–32 символи, лише `[a-zA-Z0-9_]`
- Назва проекту — непорожня, ≤ 128 символів, унікальна в межах користувача
- Назва задачі — непорожня, ≤ 256 символів
- `due_date` задачі — обов'язково в майбутньому
- Переходи між статусами задачі суворо регламентовані (UC-09)

## HTTP статус-коди

| Код | Коли |
|-----|------|
| 200 | Успішний GET або PATCH |
| 201 | Успішне створення (POST) |
| 204 | Успішне видалення (DELETE) |
| 400 | Порушення бізнес-правила (напр. недопустимий перехід статусу) |
| 401 | Невірні credentials або прострочений токен |
| 403 | Токен відсутній |
| 404 | Ресурс не знайдено |
| 409 | Конфлікт (дублікат email, username, назви проекту) |
| 422 | Невалідні вхідні дані (Pydantic validation) |
