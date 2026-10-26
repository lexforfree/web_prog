# Практическое задание
## Занятие 8: Работа с базой данных

---

### Подготовка окружения с Docker

**Запуск PostgreSQL в Docker:**

```bash
cd materials/pract_08/code
docker-compose up -d
```

**Проверка подключения:**

```bash
# Проверка статуса
docker ps | grep webprog_db

# Подключение к БД
docker exec -it webprog_db psql -U webprog -d webprog

# Тест запрос
docker exec -it webprog_db psql -U webprog -d webprog -c "SELECT 1;"
```

**Остановка:**

```bash
docker-compose down
docker-compose down -v  # Удалить данные
```

---

### Задание 1: Подключение к БД

**Создайте подключение к PostgreSQL в Docker:**

**Требования:**
- Использовать драйвер psycopg2
- Параметры подключения из переменных окружения
- Обработка ошибок подключения
- Context manager для автоматического закрытия

**Пример .env:**
```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=webprog
DB_USER=webprog
DB_PASSWORD=webprog123
```

**Пример кода:**
```python
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 5432)),
        database=os.getenv('DB_NAME', 'webprog'),
        user=os.getenv('DB_USER', 'webprog'),
        password=os.getenv('DB_PASSWORD', 'webprog123')
    )
```

**Проверка через Docker:**
```bash
# Успешное подключение
python your_script.py

# Проверка через CLI
docker exec -it webprog_db psql -U webprog -d webprog -c "\dt"
```

---

### Задание 2: Создание таблицы

**Создайте таблицу users через Docker CLI:**

```bash
docker exec -it webprog_db psql -U webprog -d webprog
```

**SQL запрос:**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    age INTEGER CHECK (age >= 18),
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Требования:**
- Таблица создана в Docker контейнере
- Ограничения работают (UNIQUE, CHECK, NOT NULL)
- Проверить через `\d users`

---

### Задание 3: CRUD операции

**Реализуйте функции для работы с users:**

**Функции:**
1. `create_user(name, email, age)` - INSERT
2. `get_user(user_id)` - SELECT по ID
3. `get_all_users()` - SELECT всех
4. `update_user(user_id, **kwargs)` - UPDATE
5. `delete_user(user_id)` - DELETE

**Требования:**
- Параметризованные запросы
- Возврат количества затронутых строк
- Обработка ошибок (дубликат email, пользователь не найден)
- Использование транзакций

**Проверка через Docker:**
```bash
# После INSERT
docker exec -it webprog_db psql -U webprog -d webprog -c "SELECT * FROM users;"

# После UPDATE
docker exec -it webprog_db psql -U webprog -d webprog -c "SELECT * FROM users WHERE id = 1;"

# После DELETE
docker exec -it webprog_db psql -U webprog -d webprog -c "SELECT * FROM users;"
```

---

### Задание 4: SQL Injection защита

**Создайте уязвимый и защищённый варианты:**

**Уязвимый (для демонстрации):**
```python
def search_user_vulnerable(email):
    query = f"SELECT * FROM users WHERE email = '{email}'"
    cursor.execute(query)
```

**Защищённый:**
```python
def search_user_safe(email):
    query = "SELECT * FROM users WHERE email = %s"
    cursor.execute(query, (email,))
```

**Задания:**
1. Продемонстрируйте атаку на уязвимый вариант
2. Покажите, что защищённый вариант устойчив к атаке
3. Объясните разницу

---

### Задание 5: JOIN операции

**Создайте таблицу orders через Docker:**

```bash
docker exec -it webprog_db psql -U webprog -d webprog

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    product VARCHAR(100),
    total DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Запросы:**
1. INNER JOIN - пользователи с заказами
2. LEFT JOIN - все пользователи (даже без заказов)
3. Подсчёт заказов на пользователя
4. Сумма заказов на пользователя

**Проверка через Docker:**
```bash
docker exec -it webprog_db psql -U webprog -d webprog -c \
  "SELECT u.name, COUNT(o.id) FROM users u LEFT JOIN orders o ON u.id = o.user_id GROUP BY u.name;"
```

---

### Задание 6: Миграции с Docker

**Создайте систему миграций:**

**docker-compose.yml с init script:**
```yaml
services:
  postgres:
    volumes:
      - ./migrations:/docker-entrypoint-initdb.d
```

**Миграции:**
1. `migrations/001_create_users.sql`
2. `migrations/002_create_orders.sql`

**Задания:**
1. Создайте файлы миграций
2. Удалите контейнер и volume
3. Запустите заново - миграции применятся автоматически
4. Проверьте результат

```bash
docker-compose down -v
docker-compose up -d
docker exec -it webprog_db psql -U webprog -d webprog -c "\dt"
```

---

### Задание 7: ORM с SQLAlchemy

**Перепишите CRUD с использованием SQLAlchemy:**

**Модель:**
```python
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
import os

DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    email = Column(String(100), unique=True)
    age = Column(Integer)
```

**Операции:**
- Создание пользователя
- Чтение пользователя
- Обновление пользователя
- Удаление пользователя
- Фильтрация и сортировка

---

### Задание 8: Connection Pooling

**Настройте connection pool:**

```python
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10
)
```

**Сравнение:**
- Без пула
- С пулом
- Измерить производительность

**Проверка в Docker:**
```bash
# Количество подключений
docker exec -it webprog_db psql -U webprog -d webprog -c \
  "SELECT count(*) FROM pg_stat_activity;"
```

---

### Задание 9: Асинхронный доступ

**Реализуйте асинхронный доступ к БД:**

**Требования:**
- Использовать asyncpg
- Асинхронные функции для CRUD
- Обработка ошибок

**Пример:**
```python
import asyncpg

async def get_user(user_id):
    conn = await asyncpg.connect('postgresql://...')
    user = await conn.fetchrow(
        'SELECT * FROM users WHERE id = $1',
        user_id
    )
    await conn.close()
    return user
```

---

### Задание 10: Практическая реализация

**Создайте полноценный API с БД в Docker:**

**docker-compose.yml:**
```yaml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: webprog
      POSTGRES_PASSWORD: webprog123
      POSTGRES_DB: webprog
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  app:
    build: .
    environment:
      DATABASE_URL: postgresql://webprog:webprog123@postgres:5432/webprog
    depends_on:
      - postgres

volumes:
  postgres_data:
```

**Endpoints:**
- POST /users - создать пользователя
- GET /users/{id} - получить пользователя
- GET /users - список пользователей
- PUT /users/{id} - обновить пользователя
- DELETE /users/{id} - удалить пользователя
- GET /users/{id}/orders - заказы пользователя

**Требования:**
- Использовать драйвер БД (psycopg2)
- Параметризованные запросы
- Обработка ошибок (404, 400, 409)
- Connection pooling
- Логирование запросов

---

### Критерии оценки

- **Отлично (5):** Все задания выполнены с Docker, есть docker-compose.yml, миграции применяются автоматически
- **Хорошо (4):** Основные задания выполнены, CRUD работает с Docker
- **Удовлетворительно (3):** Базовые CRUD операции реализованы
- **Неудовлетворительно (2):** Задание не выполнено или не работает

---

### Сдача работы

1. Создайте Git-репозиторий с кодом
2. Добавьте docker-compose.yml
3. Добавьте SQL скрипты для создания таблиц
4. Добавьте requirements.txt с зависимостями
5. Добавьте README с инструкциями по запуску Docker
6. Пришлите ссылку на репозиторий

---

### Дедлайн

Следующее занятие
