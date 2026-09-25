# Web Programming - Course Materials

Материалы для практических занятий по дисциплине "Веб-программирование".

## Структура проекта

```
materials/
├── pract_01/          # Занятие 1: Как работает веб-приложение
│   ├── presentation/  # Презентация (slides.md, slides.pdf)
│   ├── practice/      # Практические задания (tasks.md)
│   └── code/          # Примеры кода
├── pract_02/          # Занятие 2: Окружение приложения, Docker и YAML
├── pract_03/          # Занятие 3: Проектирование HTTP API
├── pract_04/          # Занятие 4: Валидация, бизнес-правила и обработка ошибок
├── pract_05/          # Занятие 5: Устройство backend-приложения
├── pract_06/          # Занятие 6: Основы автоматического тестирования
└── README.md          # Этот файл
...........
```

## Темы занятий

1. **Как работает веб-приложение** - Клиент-серверная архитектура, HTTP, DNS
2. **Окружение приложения** - Docker, YAML, контейнеризация
3. **Проектирование HTTP API** - REST, методы, параметры, статусы
4. **Валидация и ошибки** - Проверка данных, бизнес-правила, обработка ошибок
5. **Устройство backend-приложения** - Архитектура, DI, разделение ответственности
6. **Автоматическое тестирование** - Unit, Integration, E2E тесты

## Требования

### Docker

**Установка Docker:**

**Linux (Ubuntu/Debian):**
```bash
# Обновление индекса пакетов
sudo apt-get update

# Установка необходимых пакетов
sudo apt-get install ca-certificates curl gnupg

# Добавление официального GPG ключа Docker
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Добавление репозитория
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Установка Docker Engine
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Проверка установки
docker --version
docker compose version
```

**macOS:**
- Скачайте Docker Desktop с https://www.docker.com/products/docker-desktop
- Установите и запустите приложение

**Windows:**
- Скачайте Docker Desktop с https://www.docker.com/products/docker-desktop
- Установите и запустите приложение (требуется WSL 2)

**Проверка установки:**
```bash
docker --version
docker run hello-world
```

### Python Virtual Environment

**Создание виртуального окружения:**
```bash
# В корне проекта
python -m venv .venv
```

**Активация:**

**Linux/macOS:**
```bash
source .venv/bin/activate
```

**Windows:**
```bash
.venv\Scripts\activate
```

**Деактивация:**
```bash
deactivate
```

**Установка зависимостей:**
```bash
pip install -r requirements.txt
```

## Генерация PDF презентаций

Презентации создаются с помощью Marp (Markdown Presentation Ecosystem).

### Установка Marp CLI

Marp CLI устанавливается через npx (входит в состав Node.js/npm).

**Проверка наличия npm:**
```bash
npm --version
```

**Если npm не установлен:**
- Скачайте Node.js с https://nodejs.org
- Установите в систему

**Генерация PDF:**
```bash
# Генерация одной презентации
npx @marp-team/marp-cli pract_01/presentation/slides.md --pdf --output pract_01/presentation/slides.pdf

# Генерация всех презентаций
for i in {01..06}; do
  npx @marp-team/marp-cli pract_$i/presentation/slides.md --pdf --output pract_$i/presentation/slides.pdf
done
```

**Генерация всех презентаций (скрипт):**
```bash
chmod +x generate_pdfs.sh
./generate_pdfs.sh
```

## Работа с материалами

### Просмотр презентаций

**PDF:**
- Откройте файл `pract_XX/presentation/slides.pdf` в любом PDF-просмотрщике

**Markdown:**
- Откройте файл `pract_XX/presentation/slides.md` в редакторе с поддержкой Markdown
- Для предпросмотра используйте VS Code с расширением Marp

### Выполнение практических заданий

1. Перейдите в папку занятия: `cd pract_XX`
2. Откройте `practice/tasks.md`
3. Выполняйте задания по порядку
4. Проверяйте примеры кода в папке `code/`

### Запуск примеров кода

**HTTP примеры (Pract 01):**
```bash
chmod +x pract_01/code/http_examples.sh
./pract_01/code/http_examples.sh
```

**Python примеры:**
```bash
# Активируйте виртуальное окружение
source .venv/bin/activate

# Установите зависимости (если есть requirements.txt)
pip install -r requirements.txt

# Запустите пример
python pract_XX/code/example.py
```

**Docker примеры (Pract 02):**
```bash
cd pract_02/code
docker compose up
```

## План лабораторных работ

Подробный план лабораторных работ находится в файле `../plan_laboratornykh.md`.

**Основные лабораторные (1-8):**
1. Настройка окружения и первый HTTP-сервер
2. REST API для CRUD операций
3. Валидация и обработка ошибок
4. Архитектура с разделением слоёв
5. Тестирование API
6. Аутентификация и работа с БД
7. Транзакции и оптимизация
8. Nginx reverse proxy и безопасность

**Дополнительные лабораторные (9-10):**
9. Интеграционное тестирование и диагностика
10. Redis и фоновые задачи

## Рекомендуемые инструменты

### Редакторы кода
- VS Code - https://code.visualstudio.com
- PyCharm Community - https://www.jetbrains.com/pycharm

### Инструменты для работы с API
- curl - командная строка
- Postman - https://www.postman.com
- HTTPie - https://httpie.io

### Инструменты для работы с Docker
- Docker Desktop - https://www.docker.com/products/docker-desktop
- Portainer - https://www.portainer.io

### Инструменты для тестирования
- pytest - https://docs.pytest.org
- coverage - https://coverage.readthedocs.io

## Полезные ресурсы

### HTTP и REST
- MDN Web Docs - https://developer.mozilla.org
- REST API Tutorial - https://restfulapi.net

### Docker
- Docker Documentation - https://docs.docker.com
- Docker Compose Documentation - https://docs.docker.com/compose

### Тестирование
- pytest Documentation - https://docs.pytest.org
- Python Testing Documentation - https://docs.python.org/3/library/unittest.html

## Формат сдачи работ

1. Создайте Git-репозиторий с решением
2. Добавьте README с инструкциями по запуску
3. Включите результаты выполнения заданий
4. Пришлите ссылку на репозиторий преподавателю

## Критерии оценки

- **Функциональность:** работает ли как требуется
- **Качество кода:** чистота, читаемость, архитектура
- **Тесты:** покрытие и качество
- **Документация:** README, комментарии
- **Дедлайн:** своевременность сдачи

## Поддержка

При возникновении вопросов обращайтесь к преподавателю практики.

## Лицензия

Материалы предназначены для образовательных целей.
