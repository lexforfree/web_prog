# Практическое задание
## Занятие 7: Состояние пользователя (Cookies, сессии, токены)

---

### Задание 1: Работа с Cookies

**Создайте простое приложение для работы с cookies:**

**Endpoints:**
1. `POST /set-cookie` - установить cookie
2. `GET /get-cookie` - прочитать cookie
3. `POST /delete-cookie` - удалить cookie

**Требования:**
- Cookie с атрибутами HttpOnly, Secure, SameSite
- Разные сроки действия (сессия, 1 день, 30 дней)
- Логирование всех операций с cookies

**Пример запроса:**
```bash
curl -X POST http://localhost:5000/set-cookie \
  -H "Content-Type: application/json" \
  -d '{"name": "user_id", "value": "123", "days": 30}'
```

---

### Задание 2: Session-based авторизация

**Реализуйте систему авторизации с использованием сессий:**

**Endpoints:**
1. `POST /register` - регистрация пользователя
2. `POST /login` - вход (сохранить user_id в session)
3. `GET /profile` - профиль (требует авторизации)
4. `POST /logout` - выход (удалить session)

**Требования:**
- Хранение паролей в хешированном виде (bcrypt)
- Проверка авторизации в middleware
- Возврат 401 если не авторизован
- Логирование попыток входа

**Данные пользователя:**
- username (уникальный)
- email (уникальный)
- password (хешированный)

---

### Задание 3: JWT авторизация

**Реализуйте систему авторизации с JWT:**

**Endpoints:**
1. `POST /login` - вход (выдать access_token и refresh_token)
2. `POST /refresh` - обновление access_token
3. `GET /profile` - профиль (требует access_token)
4. `POST /logout` - выход (добавить в blacklist)

**Требования:**
- Access token: 15 минут
- Refresh token: 7 дней
- Проверка expiration
- Blacklist для отозванных токенов (Redis)
- Middleware для проверки токена

**Payload JWT:**
```json
{
  "user_id": 123,
  "username": "john",
  "exp": 1234567890
}
```

---

### Задание 4: Сравнение Session vs JWT

**Создайте два варианта одного API:**
- Вариант A: Session-based
- Вариант B: JWT-based

**Сравните:**
- Сложность реализации
- Производительность
- Масштабируемость
- Безопасность
- Возможность отзыва

**Создайте таблицу сравнения с выводами.**

---

### Задание 5: CSRF защита

**Добавьте CSRF защиту в форму:**

**Endpoints:**
1. `GET /form` - форма с CSRF token
2. `POST /submit` - обработка с проверкой CSRF

**Требования:**
- Генерация CSRF token при загрузке формы
- Проверка CSRF token при отправке
- SameSite cookie
- Логирование попыток CSRF

**Пример формы:**
```html
<form action="/submit" method="POST">
  <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
  <input type="text" name="message">
  <button>Submit</button>
</form>
```

---

### Задание 6: Redis для сессий

**Перенесите хранение сессий в Redis:**

**Требования:**
- Использовать Flask-Session или аналогичное решение
- Настроить TTL для сессий (24 часа)
- Реализовать автоматическое удаление
- Логирование операций с Redis

**Проверка:**
- Сессия сохраняется после перезапуска приложения
- Сессия удаляется через TTL
- Несколько экземпляров приложения видят одни сессии

---

### Задание 7: Анализ заголовков Cookie

**Проанализируйте заголовки Set-Cookie:**

**Примеры:**
```
Set-Cookie: session_id=abc123; HttpOnly; Secure; SameSite=Strict
Set-Cookie: user_id=123; Expires=Wed, 09 Jun 2025 10:18:14 GMT
Set-Cookie: theme=dark; Path=/settings; SameSite=Lax
```

**Задания:**
1. Объясните каждый атрибут
2. Какие cookie будут отправлены на `/settings`?
3. Какие cookie будут отправлены при переходе с другого сайта?
4. Какие cookie доступны из JavaScript?

---

### Задание 8: Refresh Token реализация

**Реализуйте полный цикл refresh token:**

**Сценарий:**
1. User логинится → получает access_token (15 мин) и refresh_token (7 дней)
2. User делает запросы с access_token
3. Access token истёк → User отправляет refresh_token
4. Сервер проверяет refresh_token → выдаёт новый access_token
5. Refresh token истёк → User логинится снова

**Требования:**
- Хранение refresh_token в БД/Redis
- Проверка валидности refresh_token
- Ротация refresh_token (новый при обновлении)
- Отзыв refresh_token при logout

---

### Задание 9: Безопасность cookie

**Проверьте безопасность cookie в вашем приложении:**

**Проверки:**
1. Все аутентификационные cookie имеют HttpOnly?
2. Все cookie передаются только по HTTPS (Secure)?
3. Настроен SameSite?
4. Cookie подписаны (для session)?
5. Нет чувствительных данных в cookie?

**Исправьте найденные проблемы.**

---

### Задание 10: Практическая реализация

**Реализуйте полноценную систему авторизации:**

**Требования:**
- Регистрация с валидацией email
- Логин с выдачей JWT
- Защищённые endpoints
- Refresh token
- Logout с blacklist
- CSRF защита для форм
- Логирование всех операций
- Обработка ошибок

**Endpoints:**
- POST /register
- POST /login
- POST /refresh
- GET /profile (защищённый)
- POST /logout
- GET /settings (защищённый, CSRF)

---

### Критерии оценки

- **Отлично (5):** Все задания выполнены, есть подробные комментарии, реализованы все механизмы безопасности
- **Хорошо (4):** Основные задания выполнены, базовая авторизация работает
- **Удовлетворительно (3):** Базовые задания выполнены
- **Неудовлетворительно (2):** Задание не выполнено или не работает

---

### Сдача работы

1. Создайте Git-репозиторий с кодом
2. Добавьте README с инструкциями по запуску
3. Добавьте примеры запросов (curl или Postman collection)
4. Пришлите ссылку на репозиторий

---

### Дедлайн

Следующее занятие
