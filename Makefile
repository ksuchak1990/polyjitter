.PHONY: install lint typecheck test format check clean

install:
	uv sync

lint:
	uv run ruff check src tests

format:
	uv run ruff format src tests

typecheck:
	uv run mypy src

test:
	uv run pytest

check: lint typecheck test

clean:
	rm -rf .mypy_cache .pytest_cache .ruff_cache

