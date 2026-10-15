# Практическое задание
## Занятие 12: Интеграционные проверки и диагностика

---

### Задание 1: Интеграционный тест с реальной БД

**Создайте интеграционный тест с PostgreSQL:**

**Требования:**
- Отдельная тестовая БД
- Fixture для подготовки данных
- Очистка после теста
- Проверка результата в БД

**Пример:**
```python
@pytest.fixture
def test_db():
    conn = psycopg2.connect(TEST_DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("TRUNCATE TABLE users CASCADE")
    conn.commit()
    yield conn
    cursor.execute("TRUNCATE TABLE users CASCADE")
    conn.commit()
    cursor.close()
    conn.close()

def test_create_user_integration(test_db):
    repo = UserRepository(test_db)
    service = UserService(repo)
    user = service.create_user("John", "john@example.com")
    
    saved_user = repo.find_by_id(user.id)
    assert saved_user is not None
```

---

### Задание 2: Request ID реализация

**Добавьте Request ID в приложение:**

**Требования:**
- Генерация Request ID при каждом запросе
- Передача Request ID в логи
- Возврат Request ID в заголовке
- Передача Request ID в downstream сервисы

**Пример:**
```python
@app.before_request
def add_request_id():
    g.request_id = str(uuid.uuid4())

@app.after_request
def add_request_id_header(response):
    response.headers['X-Request-ID'] = g.request_id
    return response
```

---

### Задание 3: Логирование с Request ID

**Настройте структурированное логирование:**

**Требования:**
- Логировать Request ID в каждом сообщении
- Логировать ошибки с контекстом
- Логировать время выполнения запроса
- Логировать параметры запроса

**Пример:**
```python
logger.info(f"[{g.request_id}] GET /api/users - 200 - 0.05s")
logger.error(f"[{g.request_id}] Error: {e}", extra={'context': {...}})
```

---

### Задание 4: Воспроизведение ошибки

**Создайте сценарий воспроизведения ошибки:**

**Сценарий:**
1. Создайте endpoint который иногда падает
2. Добавьте логирование с Request ID
3. Вызовите endpoint и получите Request ID из ошибки
4. Найдите все логи с этим Request ID
5. Проанализируйте последовательность событий
6. Создайте тест воспроизводящий проблему

---

### Задание 5: Регрессионный тест

**Создайте регрессионный тест для бага:**

**Сценарий:**
1. Создайте функцию с багом (например, неправильный расчёт)
2. Напишите тест который обнаруживает баг
3. Исправьте баг
4. Убедитесь что тест проходит
5. Оставьте тест как регрессионный

**Пример:**
```python
def test_price_calculation_regression():
    """Regression test for price calculation bug"""
    product = Product(price=100, discount=10)
    final_price = product.calculate_final_price()
    assert final_price == 90  # Баг был: возвращал 10
```

---

### Задание 6: Тестовое окружение

**Настройте тестовое окружение с Docker Compose:**

**docker-compose.test.yml:**
```yaml
services:
  test-db:
    image: postgres:15
    environment:
      POSTGRES_DB: test_db
  test-redis:
    image: redis:alpine
```

**Задания:**
1. Создайте docker-compose.test.yml
2. Настройте переменные окружения для тестов
3. Запустите тесты с тестовым окружением
4. Остановите окружение после тестов

---

### Задание 7: Независимость тестов

**Обеспечьте независимость тестов:**

**Проблема:**
- Тесты зависят от порядка выполнения
- Тесты зависят от времени
- Тесты зависят от внешних сервисов

**Решения:**
1. autouse fixture для очистки БД
2. Мок времени для тестов с датами
3. Мок внешних API

---

### Задание 8: Проверка результата операции

**Проверяйте не только HTTP статус:**

**Требования:**
- Проверка данных в БД
- Проверка побочных эффектов
- Проверка отправленных email
- Проверка состояния очередей

**Пример:**
```python
def test_create_user():
    response = client.post('/users', json=data)
    assert response.status_code == 201
    
    # Проверка в БД
    user = db.session.query(User).first()
    assert user.email == data['email']
    
    # Проверка email отправки
    assert mock_email.send_welcome.called
```

---

### Задание 9: Мониторинг и метрики

**Добавьте метрики в приложение:**

**Метрики:**
- Количество запросов по endpoint
- Время ответа
- Количество ошибок
- Размер очереди

**Инструменты:**
- Prometheus + Grafana
- StatsD
- Datadog

**Пример:**
```python
from prometheus_client import Counter, Histogram

request_count = Counter('http_requests_total', 'Total requests', ['method', 'endpoint'])
request_duration = Histogram('http_request_duration_seconds', 'Request duration')
```

---

### Задание 10: Практическая реализация

**Создайте систему диагностики:**

**Требования:**
1. Request ID генерация и передача
2. Структурированное логирование
3. Интеграционные тесты с реальной БД
4. Регрессионные тесты
5. Метрики Prometheus
6. Алерты на ошибки

**Endpoints:**
- POST /users - создание с логированием
- GET /users/{id} - получение с Request ID
- GET /health - health check с метриками

---

### Критерии оценки

- **Отлично (5):** Все задания выполнены, есть Request ID, структурированное логирование, интеграционные тесты, метрики
- **Хорошо (4):** Основные задания выполнены, интеграционные тесты работают
- **Удовлетворительно (3):** Базовые интеграционные тесты реализованы
- **Неудовлетворительно (2):** Задание не выполнено или не работает

---

### Сдача работы

1. Создайте Git-репозиторий с кодом
2. Добавьте docker-compose.test.yml
3. Добавьте примеры логов
4. Пришлите ссылку на репозиторий

---

### Дедлайн

Следующее занятие
