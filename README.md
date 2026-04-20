Проект «Фудграм» — это онлайн-сервис и социальная сеть, где пользователи могут публиковать рецепты, подписываться на публикации других авторов, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список покупок.

Стек технологий
Backend: Python 3.13, Django 4.2, DRF, PostgreSQL
Frontend: React (SPA)
Инфраструктура: Docker, Docker Compose, Nginx (Gateway), Gunicorn
CI/CD: GitHub Actions (Build, Push, Deploy)

Установка и запуск (Docker)

Клонируйте репозиторий: git clone github.com && cd foodgram
Создайте файл .env в корневой папке и заполните его: POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, DB_HOST, DB_PORT, SECRET_KEY, DEBUG, ALLOWED_HOSTS.

Запустите контейнеры: docker compose up -d --build
Выполните миграции и соберите статику: docker compose exec backend python manage.py migrate && docker compose exec backend python manage.py collectstatic --noinput
Создайте администратора: docker compose exec backend python manage.py createsuperuser
Импорт ингредиентов
Загрузите данные из JSON-файла с помощью команды:
docker compose exec backend python manage.py shell -c "import json; from recipes.models import Ingredient; f = open('data/ingredients.json', encoding='utf-8'); data = json.load(f); [Ingredient.objects.get_or_create(name=i['name'], measurement_unit=i['measurement_unit']) for i in data]; f.close(); print('Импорт завершен!')"

CI/CD Workflow
Настроенный Workflow (main.yml) выполняет сборку и пуш образов на Docker Hub, автоматический деплой на сервер через SSH, выполнение миграций и обновление статики.
Доступные ресурсы
Главная страница: http://localhost:9000/
Админ-панель: http://localhost:9000/admin/
Документация API (Redoc): http://localhost:9000/api/docs/

