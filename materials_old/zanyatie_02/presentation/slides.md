---
marp: true
theme: default
paginate: true
style: |
  section {
    font-family: 'Segoe UI', sans-serif;
    font-size: 24px;
  }
  h1 {
    color: #2c3e50;
  }
  h2 {
    color: #3498db;
  }
  code {
    background-color: #f4f4f4;
    padding: 2px 6px;
    border-radius: 3px;
  }
  pre {
    background-color: #f4f4f4;
    padding: 16px;
    border-radius: 8px;
  }
  table {
    border-collapse: collapse;
    width: 100%;
  }
  th, td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
  }
  th {
    background-color: #3498db;
    color: white;
  }
---

# Занятие 2: Маршрутизация и обработка запросов
## Routing, HTTP-методы, обработчики запросов

---

### Слайд 1: Что такое маршрутизация (Routing)?

**Маршрутизация** - процесс определения того, какой обработчик должен выполнить запрос на основе URL и HTTP-метода.

**Компоненты маршрутизации:**
- **URL Pattern** - шаблон URL
- **HTTP Method** - метод запроса (GET, POST, etc.)
- **Handler/View** - функция или класс, обрабатывающий запрос
- **Parameters** - параметры из URL или тела запроса

```
URL + HTTP Method → Router → Handler → Response
```

---

### Слайд 2: HTTP-методы в backend

| Метод | Описание | Idempotent | Использование |
|-------|----------|------------|---------------|
| GET | Получение данных | Да | Чтение ресурсов |
| POST | Создание ресурса | Нет | Создание новых данных |
| PUT | Полное обновление | Да | Замена ресурса |
| PATCH | Частичное обновление | Нет | Изменение части ресурса |
| DELETE | Удаление | Да | Удаление ресурса |
| HEAD | Заголовки ответа | Да | Проверка существования |
| OPTIONS | Доступные методы | Да | CORS preflight |

---

### Слайд 3: Структура URL

```
https://example.com/api/users/123/posts?sort=date&limit=10
│                    │    │    │    │    │
│                    │    │    │    │    └─ Query Parameters
│                    │    │    │    └───── Path
│                    │    │    └────────── Path Parameter
│                    │    └─────────────── Resource
│                    └──────────────────── Path
└───────────────────────────────────────── Protocol + Domain
```

**Path Parameters:** `/users/{id}` - часть URL
**Query Parameters:** `?page=1&limit=10` - после ?

---

### Слайд 4: Параметры маршрута

**Path Parameters (Django):**
```python
path('users/<int:user_id>/', views.user_detail)
# /users/123/ → user_id = 123
```

**Path Parameters (FastAPI):**
```python
@app.get("/users/{user_id}")
def read_user(user_id: int):
    return {"user_id": user_id}
# /users/123 → user_id = 123
```

**Query Parameters:**
```python
# /items?skip=0&limit=10
def read_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}
```

---

### Слайд 5: Обработка тела запроса (Request Body)

**JSON Body - стандарт для REST API:**

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "age": 30
}
```

**Django:**
```python
data = json.loads(request.body)
name = data.get('name')
```

**FastAPI (с Pydantic):**
```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    email: str
    age: int

@app.post("/users")
def create_user(user: User):
    return user
```

---

### Слайд 6: Валидация данных

**Зачем нужна валидация:**
- Защита от некорректных данных
- Безопасность (SQL injection, XSS)
- Улучшение UX (понятные ошибки)

**Типы валидации:**
- Тип данных (int, str, email)
- Обязательные поля
- Диапазоны значений
- Формат данных (regex)

**FastAPI с Pydantic:**
```python
class User(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    age: int = Field(..., ge=18, le=120)
```

---

### Слайд 7: Маршрутизация в Django

**urls.py:**
```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('users/', views.users_list, name='users_list'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
]
```

**Включение app URLs в главный urls.py:**
```python
from django.urls import path, include

urlpatterns = [
    path('api/', include('myapp.urls')),
]
```

---

### Слайд 8: Маршрутизация в FastAPI

**Простые маршруты:**
```python
@app.get("/")
def root():
    return {"message": "Root"}

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}
```

**APIRouter для модульности:**
```python
from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/")
def get_users():
    return {"users": []}

@router.get("/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}
```

---

### Слайд 9: Обработка разных HTTP-методов

**Django:**
```python
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET", "POST"])
def user_list(request):
    if request.method == "GET":
        # Вернуть список
    elif request.method == "POST":
        # Создать пользователя
```

**FastAPI:**
```python
@app.get("/users")
def get_users():
    return {"users": []}

@app.post("/users")
def create_user(user: UserCreate):
    return user

@app.put("/users/{user_id}")
def update_user(user_id: int, user: UserUpdate):
    return {"user_id": user_id}

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    return {"deleted": True}
```

---

### Слайд 10: Статус-коды ответов

| Код | Класс | Значение | Использование |
|-----|-------|----------|---------------|
| 200 | OK | Успех | GET, PUT, PATCH |
| 201 | Created | Ресурс создан | POST |
| 204 | No Content | Успех без тела | DELETE |
| 400 | Bad Request | Ошибка клиента | Неверные данные |
| 404 | Not Found | Не найдено | Ресурс не существует |
| 405 | Method Not Allowed | Метод не разрешен | Неверный HTTP-метод |
| 500 | Server Error | Ошибка сервера | Внутренняя ошибка |

---

### Слайд 11: Возврат статус-кодов

**Django:**
```python
from django.http import JsonResponse, HttpResponseNotFound

def user_detail(request, user_id):
    user = get_user(user_id)
    if not user:
        return HttpResponseNotFound("User not found")
    return JsonResponse(user.to_dict())
```

**FastAPI:**
```python
from fastapi import HTTPException

@app.get("/users/{user_id}")
def get_user(user_id: int):
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

---

### Слайд 12: Практическое задание

**Задание 1: CRUD для пользователей**
- GET /users/ - список всех пользователей
- GET /users/{id}/ - детальная информация
- POST /users/ - создание пользователя
- PUT /users/{id}/ - обновление
- DELETE /users/{id}/ - удаление

**Задание 2: Фильтрация и сортировка**
- GET /users/?age_gt=18&sort=name
- GET /users/?search=John

**Задание 3: Валидация**
- Имя: 2-50 символов
- Email: валидный email
- Возраст: 18-120

---

### Слайд 13: Домашнее задание

1. Реализовать полноценный CRUD API для сущности "Product"
2. Добавить валидацию полей (название, цена, количество)
3. Реализовать фильтрацию по цене и категории
4. Добавить пагинацию (page, page_size)
5. Протестировать все endpoints через Postman
6. Создать README с описанием API

---

### Слайд 14: Полезные ресурсы

**Документация:**
- Django URL Dispatcher: https://docs.djangoproject.com/en/4.2/topics/http/urls/
- FastAPI Path Parameters: https://fastapi.tiangolo.com/tutorial/path-params/
- HTTP Methods: https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods

**Инструменты:**
- Postman: https://www.postman.com/
- Insomnia: https://insomnia.rest/
- HTTPie: https://httpie.io/
