.PHONY: install test lint api worker valuation console up

install:
	python3 -m pip install -e ".[dev]"
	cd apps/coach-console && npm install

test:
	python3 -m pytest tests -q

lint:
	python3 -m ruff check services packages tests || true
	python3 -m compileall services packages tests

api:
	uvicorn services.api.app:app --reload --port 8000

worker:
	python3 -m services.cv_worker.pipeline

valuation:
	uvicorn services.valuation.app:app --reload --port 8001

console:
	cd apps/coach-console && npm run dev

up:
	docker compose up --build
