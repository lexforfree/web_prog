# Практическое задание
## Занятие 10: Nginx и Reverse Proxy

---

### Задание 1: Установка и базовая конфигурация

**Установите Nginx:**

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

**Проверка:**
```bash
nginx -v
curl http://localhost
```

**Задания:**
1. Создайте простую HTML страницу в `/var/www/html/index.html`
2. Настройте раздачу страницы
3. Проверьте доступность через браузер

---

### Задание 2: Раздача статических файлов

**Создайте структуру:**

```
/var/www/
├── html/
│   └── index.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
└── images/
    └── logo.png
```

**Конфигурация:**
```nginx
server {
    listen 80;
    
    location /static/ {
        alias /var/www/static/;
        expires 30d;
    }
    
    location /images/ {
        alias /var/www/images/;
        expires 1y;
    }
}
```

**Задания:**
1. Создайте CSS и JS файлы
2. Настройте location блоки
3. Добавьте кэширование (expires)
4. Включите gzip сжатие

---

### Задание 3: Reverse Proxy

**Создайте простое приложение:**

```python
# app.py
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello from backend!"

@app.route('/api/time')
def time():
    from datetime import datetime
    return {"time": datetime.now().isoformat()}

if __name__ == '__main__':
    app.run(port=8000)
```

**Конфигурация Nginx:**
```nginx
server {
    listen 80;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

**Задания:**
1. Запустите приложение на порту 8000
2. Настройте reverse proxy
3. Проверьте передачу заголовков
4. Проверьте X-Forwarded-For

---

### Задание 4: Upstream и балансировка

**Запустите 2 экземпляра приложения:**

```python
# app1.py - порт 8000
app.run(port=8000)

# app2.py - порт 8001
app.run(port=8001)
```

**Конфигурация:**
```nginx
upstream backend {
    server localhost:8000;
    server localhost:8001;
}

server {
    listen 80;
    
    location / {
        proxy_pass http://backend;
    }
}
```

**Задания:**
1. Настройте upstream с 2 серверами
2. Проверьте балансировку (несколько запросов)
3. Настройте least_conn
4. Сравните с round-robin

---

### Задание 5: HTTPS с Let's Encrypt

**Получите сертификат:**

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

**Конфигурация:**
```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    location / {

        proxy_pass http://localhost:8000;
    }
}
```

**Задания:**
1. Получите сертификат (можно использовать staging)
2. Настройте HTTPS
3. Настройте redirect HTTP → HTTPS
4. Добавьте HSTS заголовок

---

### Задание 6: Docker Compose с Nginx

**Создайте docker-compose.yml:**

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - app
```

**Задания:**
1. Создайте Dockerfile для приложения
2. Создайте nginx.conf
3. Настройте proxy_pass к app
4. Запустите через docker-compose
5. Проверьте работу

---

### Задание 7: Логирование

**Настройте логирование:**

```nginx
http {
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for" '
                    '$request_time';
    
    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;
}

server {
    access_log /var/log/nginx/api_access.log main;
}
```

**Задания:**
1. Настройте custom log format
2. Добавьте request_time в лог
3. Разделите логи для разных server блоков
4. Проанализируйте логи

---

### Задание 8: Тайм-ауты

**Настройте тайм-ауты:**

```nginx
server {
    location / {
        proxy_pass http://localhost:8000;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    location /api/long {
        proxy_pass http://localhost:8000;
        proxy_read_timeout 300s;
    }
}
```

**Задания:**
1. Создайте endpoint с долгим выполнением
2. Настройте разные тайм-ауты для разных location
3. Проверьте работу тайм-аутов
4. Обработайте 504 ошибку

---

### Задание 9: Безопасность

**Добавьте защитные заголовки:**

```nginx
server {
    server_tokens off;
    
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    
    client_max_body_size 10M;
}
```

**Задания:**
1. Добавьте все защитные заголовки
2. Скрыть версию Nginx
3. Ограничить размер загружаемого файла
4. Проверьте заголовки через curl

---

### Задание 10: Rate Limiting

**Настройте ограничение частоты:**

```nginx
http {
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    
    server {
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://localhost:8000;
        }
    }
}
```

**Задания:**
1. Настройте rate limiting для API
2. Протестируйте с ab или wrk
3. Настройте burst
4. Обработайте 429 ошибку

---

### Критерии оценки

- **Отлично (5):** Все задания выполнены, HTTPS настроен, балансировка работает, безопасность настроена
- **Хорошо (4):** Основные задания выполнены, reverse proxy работает
- **Удовлетворительно (3):** Базовая конфигурация Nginx работает
- **Неудовлетворительно (2):** Задание не выполнено или не работает

---

### Сдача работы

1. Создайте Git-репозиторий с конфигурациями
2. Добавьте nginx.conf
3. Добавьте docker-compose.yml
4. Добавьте скриншоты/демо работы
5. Пришлите ссылку на репозиторий

---

### Дедлайн

Следующее занятие
