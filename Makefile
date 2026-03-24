.PHONY: test lint fix coverage build clean install

install:
	pip install -e ".[dev]"

test:
	pytest -v --tb=short

lint:
	ruff check .

fix:
	ruff check . --fix
	ruff format .

coverage:
	pytest --cov=git_flow_cli --cov-report=term-missing --cov-report=html

build:
	python -m build

clean:
	rm -rf dist/ build/ *.egg-info .pytest_cache .ruff_cache htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

docker:
	docker build -t git-flow-cli .

demo:
	git-flow-cli demo

rules:
	git-flow-cli rules
