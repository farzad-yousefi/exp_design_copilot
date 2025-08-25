.PHONY: setup fmt lint test run api

setup:
	uv venv .venv-3
	. .venv-3/bin/activate && uv pip install -r requirements.txt

fmt:
	. .venv-3/bin/activate && uv pip install ruff black
	. .venv-3/bin/activate && ruff check --select I --fix .
	. .venv-3/bin/activate && black .

lint:
	. .venv-3/bin/activate && uv pip install ruff
	. .venv-3/bin/activate && ruff check .

test:
	. .venv-3/bin/activate && uv pip install pytest
	. .venv-3/bin/activate && pytest -q

api:
	. .venv-3/bin/activate && uvicorn app.main:app --reload
