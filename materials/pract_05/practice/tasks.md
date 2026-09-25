# Практическое задание
## Занятие 5: Устройство backend-приложения

---

### Задание 1: Разделение ответственности

**Дан обработчик, который делает всё:**

```python
def create_user(request):
    data = request.json
    
    # Валидация
    if not data.get('name'):
        return {"error": "Name required"}, 400
    if len(data['name']) < 2:
        return {"error": "Name too short"}, 400
    if not data.get('email'):
        return {"error": "Email required"}, 400
    if '@' not in data['email']:
        return {"error": "Invalid email"}, 400
    
    # Проверка бизнес-правил
    existing = db.query("SELECT * FROM users WHERE email = ?", data['email'])
    if existing:
        return {"error": "Email exists"}, 409
    
    # Сохранение
    user_id = db.insert(
        "INSERT INTO users (name, email) VALUES (?, ?)",
        data['name'], data['email']
    )
    
    # Отправка письма
    send_email(data['email'], "Welcome!")
    
    # Получение сохранённого пользователя
    user = db.query("SELECT * FROM users WHERE id = ?", user_id)
    
    return {"id": user['id'], "name": user['name'], "email": user['email']}, 201
```

**Задания:**
1. Разделите на Handler, Service, Repository
2. Определите ответственность каждого компонента
3. Создайте необходимые классы и методы

---

### Задание 2: Dependency Injection

**Переделайте код с созданием зависимостей на DI:**

**Плохо:**
```python
class UserService:
    def __init__(self):
        self.db = Database()
        self.email_service = EmailService()
```

**Хорошо:**
```python
class UserService:
    def __init__(self, db, email_service):
        self.db = db
        self.email_service = email_service
```

**Задания:**
1. Переделайте следующие классы:
   - UserService
   - PostService
   - NotificationService
2. Определите зависимости каждого класса
3. Создайте схему внедрения зависимостей

---

### Задание 3: Конфигурация

**Вынесите конфигурацию в переменные окружения:**

**В коде:**
```python
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "mydb"
DB_USER = "user"
DB_PASSWORD = "secret"
API_KEY = "key123"
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
```

**Задания:**
1. Используйте os.getenv() для чтения переменных
2. Укажите значения по умолчанию
3. Создайте .env.example файл
4. Объясните, зачем это нужно

---

### Задание 4: Побочные эффекты

**Определите, какие функции имеют побочные эффекты:**

```python
def add(a, b):
    return a + b

def save_user(user):
    db.insert(user)

def send_email(to, subject):
    smtp.send(to, subject)

def get_user(user_id):
    return db.query(user_id)

def log(message):
    file.write(message)

def calculate_total(items):
    return sum(item.price for item in items)
```

**Задания:**
1. Отметьте функции с побочными эффектами
2. Объясните, почему они имеют побочные эффекты
3. Как изолировать побочные эффекты?

---

### Задание 5: Архитектура приложения

**Спроектируйте архитектуру для блога:**

**Сущности:**
- Post (пост)
- Comment (комментарий)
- Tag (тег)
- User (пользователь)

**Операции:**
- Создание поста
- Получение поста
- Добавление комментария
- Добавление тега к посту

**Задания:**
1. Определите слои (handlers, services, repositories)
2. Определите зависимости между компонентами
3. Нарисуйте схему архитектуры
4. Опишите ответственность каждого компонента

---

### Задание 6: Рефакторинг

**Рефакторинг кода для создания заказа:**

```python
def create_order(request):
    data = request.json
    
    # Валидация
    if not data.get('user_id'):
        return error("User required")
    if not data.get('items'):
        return error("Items required")
    
    # Проверка пользователя
    user = db.query("SELECT * FROM users WHERE id = ?", data['user_id'])
    if not user:
        return error("User not found"), 404
    
    # Проверка товаров
    total = 0
    for item in data['items']:
        product = db.query("SELECT * FROM products WHERE id = ?", item['product_id'])
        if not product:
            return error(f"Product {item['product_id']} not found"), 404
        if product['stock'] < item['quantity']:
            return error(f"Not enough stock for {product['name']}"), 400
        total += product['price'] * item['quantity']
    
    # Создание заказа
    order_id = db.insert(
        "INSERT INTO orders (user_id, total) VALUES (?, ?)",
        data['user_id'], total
    )
    
    # Создание элементов заказа
    for item in data['items']:
        db.insert(
            "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)",
            order_id, item['product_id'], item['quantity'], product['price']
        )
    
    # Обновление стока
    for item in data['items']:
        db.update(
            "UPDATE products SET stock = stock - ? WHERE id = ?",
            item['quantity'], item['product_id']
        )
    
    # Отправка уведомления
    send_email(user['email'], f"Order #{order_id} created")
    
    return {"order_id": order_id, "total": total}, 201
```

**Задания:**
1. Разделите на слои
2. Выделите бизнес-логику
3. Изолируйте побочные эффекты
4. Примените DI

---

### Задание 7: Тестирование архитектуры

**Как тестировать каждый слой:**

| Слой | Как тестировать | Что мокать |
|------|----------------|------------|
| Handler | | |
| Service | | |
| Repository | | |

**Задания:**
1. Определите подход к тестированию каждого слоя
2. Что нужно мокать при тестировании Handler?
3. Что нужно мокать при тестировании Service?
4. Нужно ли мокать при тестировании Repository?

---

### Задание 8: Практическая реализация

**Реализуйте архитектуру для управления пользователями:**

**Требования:**
- Handler для создания пользователя
- Service с бизнес-логикой
- Repository для работы с БД
- DI для внедрения зависимостей
- Конфигурация через переменные окружения

**Операции:**
- Создание пользователя
- Получение пользователя
- Обновление пользователя
- Удаление пользователя

**Дополнительно:**
- Создайте DI контейнер для управления зависимостями
- Добавьте middleware для логирования запросов
- Реализуйте обработку исключений на уровне handler

---

### Критерии оценки

- **Отлично (5):** Все задания выполнены, архитектура спроектирована правильно
- **Хорошо (4):** Основные задания выполнены, разделение на слои есть
- **Удовлетворительно (3):** Базовые задания выполнены
- **Неудовлетворительно (2):** Задание не выполнено или не работает

---

### Сдача работы

1. Создайте файлы с кодом
2. Добавьте схему архитектуры
3. Пришлите ссылку на репозиторий

---

### Дедлайн

Следующее занятие
