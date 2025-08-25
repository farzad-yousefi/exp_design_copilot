.PHONY: setup fmt lint test run api

setup:
	uv venv .venv
	. .venv/bin/activate && uv pip install -r requirements.txt

fmt:
	. .venv/bin/activate && uv pip install ruff black
	. .venv/bin/activate && ruff check --select I --fix .
	. .venv/bin/activate && black .

lint:
	. .venv/bin/activate && uv pip install ruff
	. .venv/bin/activate && ruff check .

test:
	. .venv/bin/activate && uv pip install pytest
	. .venv/bin/activate && pytest -q

api:
	. .venv/bin/activate && uvicorn app.main:app --reload
