# Project Name: Cloud Email Parser Service

## Назначение проекта
Это облачный HTTP-сервис, предназначен для приема EML-файлов и возврата структурированного JSON с результатом их разбора. Сервис извлекает метаданные (Subject, From, To, Date, Message-ID) и содержимое письма (Plain Text, HTML), а также информацию о вложениях.

## API
**Endpoint:** `POST /parse`
**Описание:** Принимает EML-файл для парсинга.
**Формат запроса:** Multipart/form-data
*   Параметр: `file` (содержимое — EML файл)

**Пример запроса (curl):**
```bash
curl -X POST "http://localhost:8000/parse" \
     -H "accept: application/json" \
     -F "file=@message.eml;type=text/plain"
```

**Формат ответа (Успех):**
{
  "ok": true,
  "file": "message.eml",
  "headers": {
    "subject": "Тема письма",
    "from": "Имя Отправителя <email@example.com>",
    "to": ["Получатель 1 <p1@example.com>"],
    "cc": [],
    "bcc": [],
    "replyTo": "Reply-To <r@example.com>",
    "date": "2026-08-27T12:00:00Z",
    "messageId": "<abc123@example.com>"
  },
  "body": {
    "text": "Полный текст письма...",
    "html": "<html>...</html>"
  },
  "attachments": {
    "count": 1,
    "items": [
      {"filename": "report.pdf", "contentType": "application/pdf", "sizeBytes": 1024}
    ]
  },
  "metadata": {
    "rawSizeBytes": 5120,
    "hasText": true,
    "hasHtml": true
  }
}

**Формат ответа (Ошибка):**
{
  "ok": false,
  "error": "Не удалось обработать EML файл: Ошибка парсинга."
}

## Запуск локально
1. Установите зависимости: `pip install -r requirements.txt`
2. Запустите сервис: `uvicorn app.main:app --reload`

## Запуск через Docker
1. Соберите образ: `docker build -t email-parser-cloud .`
2. Запустите контейнер: `docker run -p 8000:8000 email-parser-cloud`

## Текущий статус проекта
Проект находится на стадии **Initial Boilerplate**. Реализован базовый HTTP API и структура парсера. Требуется интеграция логики извлечения данных (headers, body, attachments) в `app/parser.py`.