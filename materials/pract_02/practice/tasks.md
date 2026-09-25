# Практическое задание
## Занятие 2: Окружение приложения, Docker и YAML

---

### Задание 1: Анализ YAML конфигурации

**Дан файл config.yaml:**
```yaml
server:
  host: localhost
  port: 8080
  ssl:
    enabled: true
    cert: /etc/ssl/cert.pem

database:
  host: db
  port: 5432
  name: myapp
  pool:
    min: 5
    max: 20

features:
  - authentication
  - logging
  - caching

cache:
  enabled: true
  ttl: 3600
```

**Вопросы:**
1. На каком порту работает сервер?
2. Включен ли SSL?
3. Какой размер пула соединений с БД?
4. Какие функции включены?
5. Какое время жизни кэша?

---

### Задание 2: Чтение docker-compose.yml

**Дан docker-compose.yml:**
```yaml
version: '3.8'

services:
  web:
    image: nginx:alpine
    ports:
      - "8080:80"
    volumes:
      - ./html:/usr/share/nginx/html
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - app

  app:
    build: ./app
    environment:
      - DATABASE_URL=postgresql://user:secret@db:5432/mydb
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: mydb
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

volumes:
  pgdata:
```

**Вопросы:**
1. Какие сервисы запускаются?
2. На каких портах они доступны с хоста?
3. Какие переменные окружения заданы для app?
4. Где хранятся данные PostgreSQL?
5. Какие папки монтируются в web?
6. В каком порядке запускаются сервисы?

---

### Задание 3: Создание YAML конфигурации

**Создайте config.yaml для приложения со следующими параметрами:**
- Сервер на порту 3000
- База данных PostgreSQL на порту 5432
- Redis на порту 6379
- Логирование в файл /var/log/app.log
- Включена аутентификация
- Максимальное количество соединений: 100

---

### Задание 4: Создание docker-compose.yml

**Создайте docker-compose.yml для:**
- Web-приложения (сборка из Dockerfile в папке ./app)
- Доступно на порту 8000 хоста
- PostgreSQL базы данных (образ postgres:15)
- Redis для кэширования (образ redis:7)
- Переменная DATABASE_URL для подключения к БД
- Volume для данных БД
- Volume для логов приложения

---

### Задание 5: Создание Dockerfile

**Создайте Dockerfile для Python-приложения:**
- Базовый образ: python:3.11-slim
- Рабочая директория: /app
- Копировать requirements.txt
- Установить зависимости
- Копировать код приложения
- Команда запуска: python app.py

---

### Задание 6: Работа с Docker

**Установите Docker (если не установлен) и выполните:**

```bash
# Проверка установки
docker --version
docker-compose --version

# Запуск контейнера
docker run hello-world

# Запуск nginx
docker run -d -p 8080:80 nginx

# Проверка работающих контейнеров
docker ps

# Просмотр логов
docker logs <container_id>

# Остановка контейнера
docker stop <container_id>

# Удаление контейнера
docker rm <container_id>
```

**Задания:**
1. Запустите nginx на порту 8080
2. Проверьте его работу в браузере
3. Посмотрите логи контейнера
4. Остановите и удалите контейнер

---

### Задание 7: Работа с docker-compose

**Создайте папку проекта и выполните:**

```bash
# Создание docker-compose.yml
# (используйте конфигурацию из задания 4)

# Запуск сервисов
docker-compose up

# Запуск в фоне
docker-compose up -d

# Просмотр состояния
docker-compose ps

# Просмотр логов
docker-compose logs
docker-compose logs -f app

# Остановка
docker-compose stop

# Остановка и удаление
docker-compose down

# Пересоздание
docker-compose up -d --force-recreate
```

**Задания:**
1. Создайте docker-compose.yml
2. Запустите сервисы
3. Проверьте их состояние
4. Посмотрите логи
5. Остановите сервисы

---

### Задание 8: Диагностика проблем

**Дан сценарий: контейнер запускается, но приложение не работает.**

**Шаги диагностики:**
1. Проверьте статус контейнера: `docker ps -a`
2. Посмотрите логи: `docker logs <container_id>`
3. Войдите в контейнер: `docker exec -it <container_id> bash`
4. Проверьте переменные окружения: `env`
5. Проверьте порты: `netstat -tlnp` (если установлен)
6. Проверьте подключение к БД: `ping db`

**Задание:** Опишите, что вы будете делать на каждом шаге.

---

### Задание 9: Volumes и данные

**Создайте docker-compose.yml с:**
- PostgreSQL с volume для данных
- Приложение с volume для логов
- Bind mount для статических файлов

**Вопросы:**
1. В чём разница между bind mount и named volume?
2. Что произойдёт с данными при `docker-compose down`?
3. Как сохранить данные при удалении контейнера?
4. Как посмотреть список volumes?

---

### Задание 10: Сеть контейнеров

**Создайте два сервиса в docker-compose.yml:**
- web (nginx)
- api (ваше приложение)

**Задания:**
1. Настройте nginx как reverse proxy для api
2. Проверьте доступность api через nginx
3. Объясните, как контейнеры общаются между собой
4. Проверьте сетевые настройки: `docker network inspect`
5. Попробуйте подключиться к контейнеру из другого контейнера

**Пример конфигурации nginx:**
```nginx
server {
    listen 80;
    location / {
        proxy_pass http://api:8000;
    }
}
```

---

### Критерии оценки

- **Отлично (5):** Все задания выполнены, есть подробные объяснения
- **Хорошо (4):** Основные задания выполнены, объяснения есть
- **Удовлетворительно (3):** Базовые задания выполнены
- **Неудовлетворительно (2):** Задание не выполнено или не работает

---

### Сдача работы

1. Создайте репозиторий с файлами конфигураций
2. Добавьте README с описанием
3. Пришлите ссылку на репозиторий

---

### Дедлайн

Следующее занятие
