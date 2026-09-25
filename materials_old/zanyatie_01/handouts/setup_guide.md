# Руководство по установке окружения
## Занятие 1: Введение в серверную разработку

---

## Проверка Python

Убедитесь, что Python установлен (версия 3.8+):

```bash
python --version
# или
python3 --version
```

Если Python не установлен, скачайте с https://www.python.org/

---

## Создание виртуального окружения

Виртуальное окружение изолирует зависимости проекта.

### Linux / macOS:

```bash
# Создаем виртуальное окружение в папке .venv
python -m venv .venv

# Активируем окружение
source .venv/bin/activate
```

### Windows:

```bash
# Создаем виртуальное окружение
python -m venv .venv

# Активируем окружение
.venv\Scripts\activate
```

После активации в командной строке появится префикс `(.venv)`

---

## Установка Django

```bash
pip install django
```

Проверка установки:
```bash
django-admin --version
```

---

## Создание Django проекта

```bash
# Создаем проект
django-admin startproject myproject

# Заходим в папку проекта
cd myproject

# Создаем приложение
python manage.py startapp myapp
```

---

## Запуск сервера

```bash
python manage.py runserver
```

Сервер будет доступен по адресу: http://127.0.0.1:8000/

---

## Установка FastAPI (альтернатива)

```bash
pip install fastapi uvicorn
```

Создайте файл `main.py` с кодом из примера и запустите:

```bash
uvicorn main:app --reload
```

Сервер будет доступен по адресу: http://127.0.0.1:8000/

Документация API: http://127.0.0.1:8000/docs

---

## Полезные команды

### Django:
```bash
python manage.py runserver          # Запуск сервера
python manage.py makemigrations     # Создание миграций
python manage.py migrate            # Применение миграций
python manage.py createsuperuser    # Создание админа
python manage.py shell              # Django shell
```

### FastAPI:
```bash
uvicorn main:app --reload           # Запуск с автоперезагрузкой
uvicorn main:app --host 0.0.0.0     # Запуск на всех интерфейсах
uvicorn main:app --port 8080        # Запуск на порту 8080
```

---

## Деактивация виртуального окружения

```bash
deactivate
```

---

## Структура файлов после установки

```
web_prog/
├── .venv/                    # Виртуальное окружение
├── myproject/                # Django проект
│   ├── manage.py
│   ├── myproject/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── myapp/
│       ├── __init__.py
│       ├── models.py
│       ├── views.py
│       └── templates/
└── requirements.txt          # Список зависимостей
```

---

## Сохранение зависимостей

```bash
pip freeze > requirements.txt
```

Установка зависимостей из файла:
```bash
pip install -r requirements.txt
```
