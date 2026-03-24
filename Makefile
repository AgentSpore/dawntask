.PHONY: run dev test smoke

run:
	uv run uvicorn dawntask.main:app --host 0.0.0.0 --port 8000

dev:
	uv run uvicorn dawntask.main:app --host 0.0.0.0 --port 8000 --reload

test:
	uv run pytest tests/ -v

smoke:
	uv run python smoke_test.py
