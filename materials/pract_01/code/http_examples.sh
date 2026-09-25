#!/bin/bash
# HTTP Examples for Practice
# Занятие 1: Как работает веб-приложение

# GET запрос с подробным выводом
echo "=== GET Request ==="
curl -v https://httpbin.org/get

echo -e "\n\n=== POST Request with JSON ==="
curl -v -X POST https://httpbin.org/post \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com", "age": 30}'

echo -e "\n\n=== Request with Custom Headers ==="
curl -v -H "Authorization: Bearer token123" \
  -H "X-Custom-Header: value" \
  https://httpbin.org/headers

echo -e "\n\n=== 404 Status ==="
curl -v https://httpbin.org/status/404

echo -e "\n\n=== 500 Status ==="
curl -v https://httpbin.org/status/500

echo -e "\n\n=== Different Content Types ==="
curl -v -H "Accept: application/json" https://httpbin.org/get
curl -v -H "Accept: text/html" https://httpbin.org/html

echo -e "\n\n=== User-Agent Header ==="
curl -v -H "User-Agent: MyCustomBot/1.0" https://httpbin.org/user-agent

echo -e "\n\n=== Request with Query Parameters ==="
curl -v "https://httpbin.org/get?name=John&age=30&city=Moscow"
