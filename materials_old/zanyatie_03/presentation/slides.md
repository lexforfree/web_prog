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

# Занятие 3: Шаблонизация и рендеринг страниц
## Template engines, SSR (Server-Side Rendering)

---

### Слайд 1: Server-Side Rendering vs Client-Side Rendering

**Server-Side Rendering (SSR):**
- HTML генерируется на сервере
- Браузер получает готовый HTML
- Быстрая initial load
- Лучше для SEO
- Примеры: Django, PHP, Ruby on Rails

**Client-Side Rendering (CSR):**
- Браузер получает JSON/JS
- HTML генерируется в браузере
- Интерактивные SPA (Single Page Applications)
- Примеры: React, Vue, Angular

```
SSR:  Server → HTML → Browser → Display
CSR:  Server → JSON → Browser → JS → HTML → Display
```

---

### Слайд 2: Template Engines

**Template Engine** - библиотека для генерации HTML из шаблонов и данных.

**Популярные template engines:**

| Язык | Template Engine | Синтаксис |
|------|-----------------|-----------|
| Python | Jinja2 | `{{ variable }}`, `{% if %}` |
| Python | Django Templates | `{{ variable }}`, `{% if %}` |
| Node.js | EJS | `<%= variable %>`, `<% if %>` |
| Node.js | Pug (Jade) | `#{variable}`, `if` |
| Go | Go Templates | `{{ .variable }}` |

---

### Слайд 3: Jinja2 (Python)

**Установка:**
```bash
pip install jinja2
```

**Базовый пример:**
```python
from jinja2 import Template

template = Template('Hello {{ name }}!')
result = template.render(name='John')
# Результат: Hello John!
```

**Из файла:**
```python
from jjango2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('index.html')
result = template.render(name='John')
```

---

### Слайд 4: Django Templates

**Настройка в settings.py:**
```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
    },
]
```

**Использование в view:**
```python
from django.shortcuts import render

def index(request):
    context = {
        'name': 'John',
        'items': ['apple', 'banana', 'orange']
    }
    return render(request, 'index.html', context)
```

---

### Слайд 5: Синтаксис шаблонов

**Переменные:**
```django
{{ name }}
{{ user.email }}
{{ product.price|currency }}
```

**Условия:**
```django
{% if user.is_authenticated %}
    <p>Welcome, {{ user.name }}!</p>
{% else %}
    <p>Please log in</p>
{% endif %}
```

**Циклы:**
```django
{% for item in items %}
    <li>{{ item }}</li>
{% endfor %}
```

---

### Слайд 6: Фильтры в шаблонах

**Фильтры** - функции для обработки переменных.

**Jinja2 / Django:**
```django
{{ name|upper }}           # JOHN
{{ name|lower }}           # john
{{ text|truncatewords:10 }} # обрезка до 10 слов
{{ price|floatformat:2 }}  # 123.45
{{ date|date:"Y-m-d" }}    # 2024-01-01
{{ list|length }}          # длина списка
```

**Цепочки фильтров:**
```django
{{ name|upper|truncatewords:1 }}
```

---

### Слайд 7: Наследование шаблонов

**Базовый шаблон (base.html):**
```django
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}My Site{% endblock %}</title>
</head>
<body>
    <header>{% block header %}{% endblock %}</header>
    <main>
        {% block content %}{% endblock %}
    </main>
    <footer>{% block footer %}{% endblock %}</footer>
</body>
</html>
```

**Дочерний шаблон (index.html):**
```django
{% extends "base.html" %}

{% block title %}Home Page{% endblock %}

{% block content %}
    <h1>Welcome!</h1>
    <p>This is the home page.</p>
{% endblock %}
```

---

### Слайд 8: Include и компоненты

**Include** - включение другого шаблона:
```django
{% include "header.html" %}
{% include "footer.html" %}
```

**Компоненты с параметрами:**
```django
{% include "card.html" with title="Hello" body="World" %}
```

**card.html:**
```django
<div class="card">
    <h2>{{ title }}</h2>
    <p>{{ body }}</p>
</div>
```

---

### Слайд 9: Передача данных в шаблон

**Простой контекст:**
```python
context = {
    'name': 'John',
    'age': 30,
    'items': ['a', 'b', 'c']
}
return render(request, 'index.html', context)
```

**Сложные структуры:**
```python
context = {
    'user': {
        'name': 'John',
        'email': 'john@example.com'
    },
    'posts': [
        {'title': 'Post 1', 'author': 'John'},
        {'title': 'Post 2', 'author': 'Jane'}
    ]
}
```

**В шаблоне:**
```django
{{ user.name }}
{% for post in posts %}
    <h3>{{ post.title }}</h3>
    <p>By {{ post.author }}</p>
{% endfor %}
```

---

### Слайд 10: Статические файлы

**Настройка в settings.py:**
```python
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
```

**Структура:**
```
static/
├── css/
│   └── style.css
├── js/
│   └── main.js
└── images/
    └── logo.png
```

**В шаблоне:**
```django
{% load static %}
<link rel="stylesheet" href="{% static 'css/style.css' %}">
<script src="{% static 'js/main.js' %}"></script>
<img src="{% static 'images/logo.png' %}">
```

---

### Слайд 11: EJS (Node.js)

**Установка:**
```bash
npm install ejs
```

**Настройка Express:**
```javascript
app.set('view engine', 'ejs');
app.set('views', './views');
```

**Использование:**
```javascript
app.get('/', (req, res) => {
    res.render('index', {
        name: 'John',
        items: ['apple', 'banana']
    });
});
```

---

### Слайд 12: Синтаксис EJS

**Переменные:**
```ejs
<%= name %>
<%= user.email %>
```

**Код JavaScript:**
```ejs
<% if (user) { %>
    <p>Welcome, <%= user.name %></p>
<% } %>

<% items.forEach(function(item) { %>
    <li><%= item %></li>
<% }); %>
```

**Include:**
```ejs
<%- include('header') %>
<%- include('footer') %>
```

---

### Слайд 13: Практическое задание

**Задание 1: Базовый шаблон**
- Создать base.html с header, main, footer
- Реализовать блоки для title, content

**Задание 2: Страница списка**
- Создать index.html, наследующий base.html
- Отобразить список товаров в таблице

**Задание 3: Страница детализации**
- Создать detail.html для одного товара
- Показать всю информацию о товаре

**Задание 4: Форма**
- Создать форму создания товара
- Добавить стили через static files

---

### Слайд 14: Домашнее задание

1. Создать полноценный HTML-шаблон для блога:
   - base.html с навигацией и футером
   - index.html - список постов
   - post.html - детальная страница поста
   - create.html - форма создания поста

2. Добавить стили (CSS) через static files

3. Реализовать пагинацию на странице списка

4. Добавить фильтры в шаблоне (дата форматирование)

5. Создать README с описанием структуры шаблонов

---

### Слайд 15: Полезные ресурсы

**Документация:**
- Django Templates: https://docs.djangoproject.com/en/4.2/topics/templates/
- Jinja2: https://jinja.palletsprojects.com/
- EJS: https://ejs.co/

**Best Practices:**
- Минимизировать логику в шаблонах
- Использовать наследование для DRY
- Хранить стили и скрипты в static
- Использовать фильтры для форматирования
