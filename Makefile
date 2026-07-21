run:
	python main.py
migrate:
	alembic revision --autogenerate -m"${NAME}"
migrate_up:
	alembic upgrade head
candles_add:
	python main.py candles_add ${SECID}
terminal:
	python main.py terminal

