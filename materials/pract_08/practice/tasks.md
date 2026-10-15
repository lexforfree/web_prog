# Практическое задание
## Занятие 8: Работа с базой данных

---

### Задание 1: Подключение к БД

**Создайте подключение к PostgreSQL или MySQL:**

**Требования:**
- Использовать драйвер (psycopg2 или mysql-connector)
- Параметры подключения из переменных окружения
- Обработка ошибок подключения
- Context manager для автоматического закрытия

**Пример:**
```python
import os
import psycopg2

def get_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 5432)),
        database=os.getenv('DB_NAME', 'mydb'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'password')
    )
```

**Проверка:**
- Успешное подключение
- Обработка ошибки при неверных параметрах
- Корректное закрытие подключения

---

### Задание 2: Создание таблицы

**Создайте таблицу users:**

**Требования:**
- id (SERIAL/AUTO_INCREMENT, PRIMARY KEY)
- name (VARCHAR(50), NOT NULL)
- email (VARCHAR(100), UNIQUE, NOT NULL)
- age (INTEGER, CHECK age >= 18)
- created_at (TIMESTAMP, DEFAULT NOW())

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

**Проверка:**
- Таблица создана
- Ограничения работают (UNIQUE, CHECK, NOT NULL)

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

**Создайте таблицу orders:**

```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
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

**Пример:**
```sql
SELECT u.name, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name;
```

---

### Задание 6: Миграции

**Создайте систему миграций:**

**Миграции:**
1. migration_001_create_users.sql
2. migration_002_create_orders.sql
3. migration_003_add_phone_to_users.sql

**Скрипт для применения мигнаций:**
```python
def apply_migration(migration_file):
    with open(migration_file) as f:
        sql = f.read()
    cursor.execute(sql)
    conn.commit()
```

**Требования:**
- Отслеживание применённых миграций
- Возможность отката
- Логирование применённых миграций

---

### Задание 7: ORM с SQLAlchemy

**Перепишите CRUD с использованием SQLAlchemy:**

**Модель:**
```python
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

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

**Требования:**
- Использовать SQLAlchemy с QueuePool
- Настроить pool_size и max_overflow
- Протестировать производительность с пулом и без

**Сравнение:**
```python
# Без пула
engine = create_engine('postgresql://...')

# С пулом
engine = create_engine(
    'postgresql://...',
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10
)
```

---

### Задание 9: Асинхронный доступ

**Реализуйте асинхронный доступ к БД:**

**Требования:**
- Использовать asyncpg (PostgreSQL) или aiomysql
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

**Создайте полноценный API с БД:**

**Endpoints:**
- POST /users - создать пользователя
- GET /users/{id} - получить пользователя
- GET /users - список пользователей
- PUT /users/{id} - обновить пользователя
- DELETE /users/{id} - удалить пользователя
- GET /users/{id}/orders - заказы пользователя

**Требования:**
- Использовать драйвер БД (psycopg2 или mysql-connector)
- Параметризованные запросы
- Обработка ошибок (404, 400, 409)
- Connection pooling
- Логирование запросов

---

### Критерии оценки

- **Отлично (5):** Все задания выполнены, есть подробные комментарии, реализованы все механизмы защиты
- **Хорошо (4):** Основные задания выполнены, CRUD работает, есть защита от SQL injection
- **Удовлетворительно (3):** Базовые CRUD операции реализованы
- **Неудовлетворительно (2):** Задание не выполнено или не работает

---

### Сдача работы

1. Создайте Git-репозиторий с кодом
2. Добавьте SQL скрипты для создания таблиц
3. Добавьте requirements.txt с зависимостями
4. Добавьте README с инструкциями по запуску
5. Пришлите ссылку на репозиторий

---

### Дедлайн

Следующее занятие
