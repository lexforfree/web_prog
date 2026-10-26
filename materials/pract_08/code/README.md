# Database Operations Examples with Docker

## Запуск с Docker

### 1. Запуск PostgreSQL контейнера

```bash
docker-compose up -d
```

### 2. Проверка статуса

```bash
docker ps
docker logs webprog_db
```

### 3. Подключение к БД через CLI

```bash
docker exec -it webprog_db psql -U webprog -d webprog
```

### 4. Запуск примеров

```bash
# Прямое подключение к БД (CRUD, Connection Pooling)
python code/db_operations.py

# SQLAlchemy ORM (модели, отношения, eager loading)
python code/sqlalchemy_orm.py

# Асинхронный доступ (asyncpg)
python code/async_db.py

# Конкурентность и консистентность (race conditions, locking, upsert)
python code/concurrency_consistency.py
```

### 5. Остановка

```bash
docker-compose down
docker-compose down -v  # Удалить volumes с данными
```

## Описание примеров

### db_operations.py
**Показывает:**
- Connection Pooling - переиспользование подключений для производительности
- CRUD операции - создание, чтение, обновление, удаление данных
- Параметризованные запросы - защита от SQL injection
- Обработка ошибок - перехват IntegrityError при дубликатах
- Транзакции и rollback - откат транзакции после ошибки
- JOIN операции - объединение таблиц (INNER JOIN, LEFT JOIN)
- Агрегация - подсчёт заказов на пользователя

### sqlalchemy_orm.py
**Показывает:**
- ORM модели - определение таблиц через классы Python
- CRUD через ORM - работа с объектами вместо SQL
- Отношения - связь между таблицами (User → Orders)
- Eager loading - решение N+1 проблемы (joinedload, selectinload)
- Фильтрация и сортировка - query API SQLAlchemy
- Connection pooling через SQLAlchemy

### async_db.py
**Показывает:**
- Асинхронное подключение к БД (asyncpg)
- Connection pool для асинхронных операций
- Асинхронные CRUD операции
- Асинхронные транзакции
- Преимущества асинхронного подхода при высокой нагрузке

### concurrency_consistency.py
**Показывает:**
- **Race Condition** - проблема гонки данных при одновременном обновлении
- **Pessimistic Locking** - SELECT FOR UPDATE блокирует строку
- **Optimistic Locking** - version column для обнаружения конфликтов
- **Upsert** - INSERT ... ON CONFLICT DO UPDATE
- **Уровни изоляции транзакций** - READ COMMITTED, REPEATABLE READ, SERIALIZABLE
- **Savepoints** - частичный откат внутри транзакции
- **Batch Insert** - массовая вставка для производительности

## Структура

- `docker-compose.yml` - конфигурация Docker контейнеров
- `Dockerfile` - образ приложения
- `requirements.txt` - Python зависимости
- `migrations/` - SQL миграции
- `code/` - примеры кода
  - `db_operations.py` - прямые SQL запросы, connection pooling
  - `sqlalchemy_orm.py` - ORM примеры, отношения, eager loading
  - `async_db.py` - асинхронный доступ к БД
  - `concurrency_consistency.py` - конкурентность, locking, транзакции

## Переменные окружения

Скопируйте `.env.example` в `.env`:

```bash
cp .env.example .env
```

Или используйте значения по умолчанию в коде.
