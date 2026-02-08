# OpenProject MCP Server

MCP (Model Context Protocol) сервер для интеграции OpenProject с AI IDE, такими как Cursor.

## Возможности

- **get_ai_tasks** — получение списка задач, готовых к разработке AI
  - Возвращает задачи из колонок "Баги" и "Готово к разработке"
  - Фильтрует только задачи с флагом `ai_dev = true`
  - Возвращает: id, url, subject, description, type, status, priority, assignee

- **get_task** — получение детальной информации о задаче по ID

## Установка

### 1. Клонирование и установка зависимостей

```bash
cd /root/repos/openproject_mcp
pip install -e .
```

### 2. Настройка

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Отредактируйте `.env`:

```env
OPENPROJECT_URL=openproject_api_url
OPENPROJECT_API_KEY=your_api_key_here
```

### 3. Настройка Cursor

Добавьте в конфигурацию MCP серверов Cursor (`~/.cursor/mcp.json`).

**Важно:** После `pip install -e .` команда `openproject-mcp` становится доступна в PATH.

#### Вариант A: После установки через pip (рекомендуется)

```json
{
  "mcpServers": {
    "openproject": {
      "command": "openproject-mcp",
      "env": {
        "OPENPROJECT_URL": "openproject_api_url",
        "OPENPROJECT_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

#### Вариант B: Без установки (указать путь к Python)

```json
{
  "mcpServers": {
    "openproject": {
      "command": "python",
      "args": ["-m", "openproject_mcp.server"],
      "cwd": "/path/to/openproject_mcp/src",
      "env": {
        "OPENPROJECT_URL": "openproject_api_url",
        "OPENPROJECT_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

#### Вариант C: Через uv/uvx

```json
{
  "mcpServers": {
    "openproject": {
      "command": "uvx",
      "args": ["--from", "/path/to/openproject_mcp", "openproject-mcp"],
      "env": {
        "OPENPROJECT_URL": "openproject_api_url",
        "OPENPROJECT_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

## Использование

После настройки в Cursor будут доступны инструменты:

### Получить задачи для AI

```
Используй инструмент get_ai_tasks чтобы получить список задач готовых к разработке
```

### Получить конкретную задачу

```
Используй инструмент get_task с task_id=2243 чтобы получить детали задачи
```

## Конфигурация

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `OPENPROJECT_URL` | URL OpenProject | `openproject_api_url` |
| `OPENPROJECT_API_KEY` | API ключ | - |
| `OPENPROJECT_QUERY_ID_BUGS` | ID query колонки "Баги" | `1390` |
| `OPENPROJECT_QUERY_ID_READY` | ID query колонки "Готово к разработке" | `1378` |
| `OPENPROJECT_AI_DEV_FIELD` | Имя кастомного поля ai_dev | `customField2` |

## Получение API ключа

1. Войдите в OpenProject
2. Перейдите в **My Account** → **Access tokens**
3. Создайте новый API токен
4. Скопируйте токен в конфигурацию

## Разработка

```bash
# Установка в режиме разработки
pip install -e ".[dev]"

# Запуск сервера напрямую
python -m openproject_mcp.server
```

## Лицензия

MIT

