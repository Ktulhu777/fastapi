Перед тем как запустить, надо запустить сервер Redis.

"uvicorn main:app --reload" -> Запуск FastAPI
"celery -A auth.celery_worker:celery worker --loglevel=INFO --pool=solo" -> Запуск Celery, если Mac & Linux -> "celery -A auth.celery_worker:celery worker --loglevel=INFO"
"celery -A auth.celery_worker:celery flower" -> Запуск Flower
