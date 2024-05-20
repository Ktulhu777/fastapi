Перед тем как запустить, надо запустить сервер Redis.

1. "uvicorn main:app --reload" -> Запуск FastAPI
2. "celery -A auth.celery_worker:celery worker --loglevel=INFO --pool=solo" -> Запуск Celery, если Mac & Linux -> "celery -A auth.celery_worker:celery worker --loglevel=INFO"
3. "celery -A auth.celery_worker:celery flower" -> Запуск Flower
