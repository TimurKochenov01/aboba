# Dating Platform API

Веб-платформа для знакомств и общения между пользователями.

## Запуск проекта

1. Клонируйте репозиторий
2. Создайте файл `.env` с настройками:

SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=dating_db
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=db
DB_PORT=5432


3. Запустите проект:
```bash
docker-compose up --build