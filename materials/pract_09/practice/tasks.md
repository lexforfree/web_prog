# Практическое задание
## Занятие 9: Транзакции и индексы

---

### Задание 1: Транзакция для перевода

**Реализуйте перевод денег между счётами:**

**Таблица accounts:**
```sql
CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    balance DECIMAL(10, 2) NOT NULL CHECK (balance >= 0)
);
```

**Функция transfer(from_id, to_id, amount):**
1. Проверить баланс отправителя
2. Списать деньги с from_id
3. Добавить деньги на to_id
4. Использовать транзакцию
5. Обработать ошибки (недостаточно средств, счёт не найден)

**Требования:**
- Использовать BEGIN/COMMIT/ROLLBACK
- Проверять balance >= amount
- Атомарность операции

---

### Задание 2: Демонстрация гонки данных

**Создайте сценарий гонки при регистрации:**

**Таблица courses:**
```sql
CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    seats INTEGER NOT NULL CHECK (seats >= 0)
);
```

**Сценарий:**
1. Два потока одновременно проверяют seats
2. Оба видят seats = 1
3. Оба регистрируются
4. Результат: seats = -1

**Реализация:**
- Использовать threading для одновременных запросов
- Продемонстрировать проблему
- Решить с SELECT FOR UPDATE

---

### Задание 3: Решение с уникальностью

**Используйте UNIQUE ограничение:**

**Таблица registrations:**
```sql
CREATE TABLE registrations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    UNIQUE(user_id, course_id)
);
```

**Задания:**
1. Попробуйте зарегистрировать одного пользователя дважды
2. Обработайте IntegrityError
3. Верните понятное сообщение об ошибке

---

### Задание 4: Атомарное изменение

**Реализуйте регистрацию с атомарным UPDATE:**

```sql
UPDATE courses 
SET seats = seats - 1 
WHERE id = %s AND seats > 0;
```

**Задания:**
1. Проверить rowcount после UPDATE
2. Если rowcount = 0 → мест нет
3. Если rowcount = 1 → успешно
4. Сравнить с SELECT FOR UPDATE

---

### Задание 5: Создание индексов

**Создайте индексы для таблицы users:**

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50),
    email VARCHAR(100),
    age INTEGER,
    city VARCHAR(50),
    active BOOLEAN
);
```

**Индексы:**
1. idx_users_email - для поиска по email
2. idx_users_name_age - составной для name и age
3. idx_users_active_city - для активных пользователей в городе
4. idx_users_age - для фильтрации по возрасту

**Проверка:**
- Использовать EXPLAIN до и после
- Сравнить cost

---

### Задание 6: EXPLAIN анализ

**Проанализируйте следующие запросы:**

```sql
-- Запрос 1
SELECT * FROM users WHERE email = 'john@example.com';

-- Запрос 2
SELECT * FROM users WHERE name = 'John' AND age = 30;

-- Запрос 3
SELECT * FROM users WHERE age = 30;

-- Запрос 4
SELECT * FROM users WHERE active = true AND city = 'Moscow';
```

**Задания:**
1. Выполнить EXPLAIN для каждого запроса
2. Определить, какие используют индексы
3. Объяснить, почему некоторые не используют
4. Добавить недостающие индексы

---

### Задание 7: Проблема N+1

**Создайте пример N+1 проблемы:**

**Сценарий:**
1. Получить 100 пользователей
2. Для каждого получить заказы отдельным запросом
3. Измерить время выполнения

**Решение 1: JOIN**
- Использовать один запрос с JOIN
- Измерить время

**Решение 2: IN**
- Получить пользователей
- Получить все заказы с WHERE user_id IN (...)
- Сгруппировать в Python
- Измерить время

**Сравнение:**
- Сравнить время выполнения
- Сравнить количество запросов

---

### Задание 8: SQLAlchemy eager loading

**Реализуйте N+1 решение с SQLAlchemy:**

**Методы:**
1. `get_users_without_eager()` - без eager loading (N+1)
2. `get_users_with_joinedload()` - с joinedload
3. `get_users_with_subqueryload()` - с subqueryload
4. `get_users_with_selectinload()` - с selectinload

**Сравнение:**
- Измерить время каждого метода
- Посмотреть сгенерированные SQL (echo=True)

---

### Составные индексы

**Проверьте правило левого префикса:**

```sql
CREATE INDEX idx_users_name_age_city ON users(name, age, city);
```

**Запросы:**
```sql
-- Какие используют индекс?
SELECT * FROM users WHERE name = 'John';
SELECT * FROM users WHERE name = 'John' AND age = 30;
SELECT * FROM users WHERE age = 30;
SELECT * FROM users WHERE city = 'Moscow';
SELECT * FROM users WHERE name = 'John' AND city = 'Moscow';
```

**Задания:**
1. Выполнить EXPLAIN для каждого
2. Определить, какие используют индекс
3. Объяснить правило левого префикса
4. Добавить недостающие индексы

---

### Задание 10: Практическая оптимизация

**Оптимизируйте медленный запрос:**

**Схема:**
```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    product VARCHAR(100),
    total DECIMAL(10, 2),
    status VARCHAR(20),
    created_at TIMESTAMP
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50),
    email VARCHAR(100),
    city VARCHAR(50)
);
```

**Медленный запрос:**
```sql
SELECT u.name, u.email, COUNT(o.id) as order_count, SUM(o.total) as total_spent
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE o.status = 'completed'
AND o.created_at > '2024-01-01'
GROUP BY u.id, u.name, u.email
ORDER BY total_spent DESC;
```

**Задания:**
1. Выполнить EXPLAIN
2. Добавить индексы
3. Выполнить EXPLAIN снова
4. Измерить улучшение производительности

---

### Критерии оценки

- **Отлично (5):** Все задания выполнены, есть подробный анализ EXPLAIN, решены все проблемы производительности
- **Хорошо (4):** Основные задания выполнены, транзакции и индексы работают
- **Удовлетворительно (3):** Базовые транзакции реализованы
- **Неудовлетворительно (2):** Задание не выполнено или не работает

---

### Сдача работы

1. Создайте Git-репозиторий с кодом
2. Добавьте SQL скрипты для создания таблиц
3. Добавьте результаты EXPLAIN (до и после оптимизации)
4. Добавьте измерения производительности
5. Пришлите ссылку на репозиторий

---

### Дедлайн

Следующее занятие
