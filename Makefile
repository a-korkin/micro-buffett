run:
	python main.py
migrate:
	alembic revision --autogenerate -m"${NAME}"
migrate_up:
	alembic upgrade head
