# Синтаксис шаблонов: справочник
## Занятие 3: Шаблонизация и рендеринг страниц

---

## Django Templates / Jinja2

### Переменные

```django
{{ variable }}
{{ user.name }}
{{ product.price }}
{{ user.email }}
```

### Фильтры

Фильтры применяются к переменным через символ `|`:

```django
{{ name|upper }}              # JOHN
{{ name|lower }}              # john
{{ name|title }}              # John
{{ text|truncatewords:10 }}   # обрезка до 10 слов
{{ text|truncatechars:50 }}   # обрезка до 50 символов
{{ price|floatformat:2 }}     # 123.45
{{ date|date:"Y-m-d" }}        # 2024-01-01
{{ date|time:"H:i" }}          # 14:30
{{ list|length }}             # длина списка
{{ list|first }}              # первый элемент
{{ list|last }}               # последний элемент
{{ value|default:"N/A" }}      # значение по умолчанию
{{ text|escape }}             # экранирование HTML
{{ text|safe }}               # безопасный HTML (без экранирования)
```

### Цепочки фильтров

```django
{{ name|upper|truncatewords:1 }}
{{ text|default:"No text"|escape }}
```

---

## Условия

### If / elif / else

```django
{% if condition %}
    <p>Condition is true</p>
{% elif another_condition %}
    <p>Another condition is true</p>
{% else %}
    <p>None of the conditions are true</p>
{% endif %}
```

### Операторы сравнения

```django
{% if user.age >= 18 %}
    <p>Adult</p>
{% endif %}

{% if user.is_authenticated %}
    <p>Welcome!</p>
{% endif %}

{% if items|length > 0 %}
    <p>Has items</p>
{% endif %}
```

### Логические операторы

```django
{% if user.is_authenticated and user.is_staff %}
    <p>Admin user</p>
{% endif %}

{% if category == "tech" or category == "science" %}
    <p>Tech or Science</p>
{% endif %}

{% if not user.is_authenticated %}
    <p>Please log in</p>
{% endif %}
```

### Проверка существования

```django
{% if user %}
    <p>User exists</p>
{% endif %}

{% if user.email %}
    <p>{{ user.email }}</p>
{% endif %}
```

---

## Циклы

### For loop

```django
{% for item in items %}
    <li>{{ item }}</li>
{% endfor %}
```

### For loop с индексом

```django
{% for item in items %}
    <p>{{ forloop.counter }}: {{ item }}</p>    # 1, 2, 3...
    <p>{{ forloop.counter0 }}: {{ item }}</p>   # 0, 1, 2...
    <p>{{ forloop.revcounter }}: {{ item }}</p>  # 3, 2, 1...
{% endfor %}
```

### For loop с условием

```django
{% for user in users %}
    {% if user.is_active %}
        <p>{{ user.name }}</p>
    {% endif %}
{% endfor %}
```

### For loop с else (пустой список)

```django
{% for item in items %}
    <p>{{ item }}</p>
{% empty %}
    <p>No items found</p>
{% endfor %}
```

### For loop по словарю

```django
{% for key, value in user.items %}
    <p>{{ key }}: {{ value }}</p>
{% endfor %}
```

---

## Наследование шаблонов

### Базовый шаблон (base.html)

```django
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Default Title{% endblock %}</title>
</head>
<body>
    <header>
        {% block header %}{% endblock %}
    </header>
    
    <main>
        {% block content %}{% endblock %}
    </main>
    
    <footer>
        {% block footer %}{% endblock %}
    </footer>
</body>
</html>
```

### Дочерний шаблон

```django
{% extends "base.html" %}

{% block title %}My Page Title{% endblock %}

{% block header %}
    <nav>
        <a href="/">Home</a>
        <a href="/about">About</a>
    </nav>
{% endblock %}

{% block content %}
    <h1>Welcome</h1>
    <p>This is the content</p>
{% endblock %}
```

### Добавление к блоку (append)

```django
{% block content %}
    {{ block.super }}
    <p>Additional content</p>
{% endblock %}
```

---

## Include

### Простой include

```django
{% include "header.html" %}
{% include "footer.html" %}
```

### Include с контекстом

```django
{% include "card.html" with title="Hello" body="World" %}
```

### Include с переменной

```django
{% include template_name %}
```

---

## Пользовательские теги и фильтры

### Создание тега (templatetags/my_tags.py)

```python
from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    return value * arg

@register.simple_tag
def current_time(format_string):
    from datetime import datetime
    return datetime.now().strftime(format_string)
```

### Использование в шаблоне

```django
{% load my_tags %}

{{ price|multiply:1.2 }}
{% current_time "%Y-%m-%d" %}
```

---

## Статические файлы

### Загрузка

```django
{% load static %}
```

### Использование

```django
<link rel="stylesheet" href="{% static 'css/style.css' %}">
<script src="{% static 'js/main.js' %}"></script>
<img src="{% static 'images/logo.png' %}">
```

### С динамическим путём

```django
{% static user.avatar %}
```

---

## URL

### Простая ссылка

```django
<a href="{% url 'home' %}">Home</a>
```

### С параметрами

```django
<a href="{% url 'post_detail' post.id %}">View Post</a>
<a href="{% url 'user_profile' username='john' %}">Profile</a>
```

### С query параметрами

```django
<a href="{% url 'posts_list' %}?page=2">Page 2</a>
```

---

## CSRF Protection

### Для форм

```django
<form method="post">
    {% csrf_token %}
    <!-- form fields -->
</form>
```

---

## Комментарии

### Однострочные

```django
{# This is a comment #}
```

### Многострочные

```django
{% comment %}
    This is a
    multi-line comment
{% endcomment %}
```

---

## EJS (Node.js)

### Переменные

```ejs
<%= name %>
<%= user.email %>
```

### Код JavaScript

```ejs
<% if (user) { %>
    <p>Welcome, <%= user.name %></p>
<% } %>

<% items.forEach(function(item) { %>
    <li><%= item %></li>
<% }); %>
```

### Include

```ejs
<%- include('header') %>
<%- include('footer') %>
```

---

## Best Practices

1. **Минимизируйте логику в шаблонах** - выносите сложную логику в views
2. **Используйте наследование** - избегайте дублирования кода
3. **Фильтры для форматирования** - используйте фильтры вместо логики
4. **Безопасность** - всегда используйте `{% csrf_token %}` для форм
5. **Экранирование** - по умолчанию переменные экранируются, используйте `|safe` только для доверенного HTML
6. **Организация** - храните шаблоны в логичной структуре папок
