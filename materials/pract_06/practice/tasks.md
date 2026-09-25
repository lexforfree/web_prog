# Практическое задание
## Занятие 6: Основы автоматического тестирования

---

### Задание 1: Unit-тест для валидации

**Напишите unit-тесты для функции валидации email:**

```python
def validate_email(email: str) -> bool:
    if '@' not in email:
        return False
    parts = email.split('@')
    if len(parts) != 2:
        return False
    local, domain = parts
    if not local or not domain:
        return False
    if '.' not in domain:
        return False
    return True
```

**Сценарии:**
1. Валидный email
2. Email без @
3. Email с несколькими @
4. Пустая локальная часть
5. Пустая доменная часть
6. Домен без точки

---

### Задание 2: Arrange-Act-Assert

**Перепишите тест в формате Arrange-Act-Assert:**

```python
def test_something():
    user = create_user("John", "john@example.com")
    assert user.name == "John"
```

**Должно получиться:**
```python
def test_something():
    # Arrange
    
    # Act
    
    # Assert
```

---

### Задание 3: Unit-тест с моками

**Напишите unit-тест для UserService с моками:**

```python
class UserService:
    def __init__(self, user_repo, email_service):
        self.user_repo = user_repo
        self.email_service = email_service
    
    def create_user(self, name, email):
        if self.user_repo.email_exists(email):
            raise ValueError("Email exists")
        user = User(name=name, email=email)
        user = self.user_repo.save(user)
        self.email_service.send_welcome(email)
        return user
```

**Требования:**
- Мокировать user_repo
- Мокировать email_service
- Проверить вызовы моков
- Проверить возвращаемое значение

---

### Задание 4: Сценарии тестирования

**Для функции create_user определите тесты:**

**Обычные сценарии:**
1. 
2. 

**Граничные сценарии:**
1. 
2. 

**Ошибочные сценарии:**
1. 
2. 
3. 

---

### Задание 5: Integration-тест

**Напишите integration-тест для создания пользователя:**

**Требования:**
- Использовать тестовую БД
- Настоящий UserRepository
- Мокировать EmailService
- Проверить сохранение в БД
- Очистить данные после теста

---

### Задание 6: Регрессионный тест

**Баг: функция расчёта скидки возвращает неправильное значение**

```python
def calculate_discount(price: float, discount_percent: float) -> float:
    return price * discount_percent / 100  # Баг: должно быть price - (price * discount / 100)
```

**Задания:**
1. Напишите тест, который обнаружит баг
2. Исправьте функцию
3. Убедитесь, что тест проходит

---

### Задание 7: Покрытие кода

**Дан код с тестом:**

```python
def divide(a, b):
    if b == 0:
        raise ValueError("Division by zero")
    return a / b

def test_divide():
    assert divide(10, 2) == 5
```

**Задания:**
1. Какое покрытие у этого теста?
2. Какие сценарии не покрыты?
3. Добавьте недостающие тесты

---

### Задание 8: Тестирование API

**Напишите тесты для API endpoint:**

**Endpoint:** POST /users

**Требования:**
- Тест на успешное создание
- Тест на неверные данные
- Тест на дубликат email
- Проверка статус-кода
- Проверка структуры ответа

---

### Задание 9: Практическая реализация

**Реализуйте тесты для UserService:**

**Методы для тестирования:**
- create_user
- get_user
- update_user
- delete_user

**Требования:**
- Unit-тесты с моками
- Integration-тесты с тестовой БД
- Покрытие основных сценариев
- Проверка ошибочных ситуаций

**Дополнительно:**
- Используйте pytest fixtures для подготовки данных
- Добавьте параметризованные тесты
- Измерьте покрытие кода (coverage)
- Добавьте тесты для граничных случаев

---

### Задание 10: Анализ тестов

**Дан тест. Найдите проблемы:**

```python
def test_create_user():
    mock_repo = Mock()
    mock_repo.email_exists.return_value = False
    mock_repo.save.return_value = User(id=1, name="John", email="john@example.com")
    mock_email = Mock()
    service = UserService(mock_repo, mock_email)
    
    user = service.create_user("John", "john@example.com")
    
    assert user is not None
```

**Проблемы:**
1. 
2. 
3. 

---

### Критерии оценки

- **Отлично (5):** Все задания выполнены, тесты качественные
- **Хорошо (4):** Основные задания выполнены, тесты есть
- **Удовлетворительно (3):** Базовые тесты написаны
- **Неудовлетворительно (2):** Задание не выполнено или не работает

---

### Сдача работы

1. Создайте файлы с тестами
2. Добавьте README с описанием
3. Пришлите ссылку на репозиторий

---

### Дедлайн

Следующее занятие
