.PHONY: reset-db
reset-db:
	docker-compose down db --volumes
	docker-compose up -d db

# -------------------------------------- Code Style  -------------------------------------

.PHONY: check-python-code
check-python-code:
	poetry run isort --check .
	poetry run black --check .
	poetry run flake8
	poetry run bandit -ll -r evaluation_registry
	poetry run mypy evaluation_registry/ --ignore-missing-imports

.PHONY: check-migrations

.PHONY: check-migrations
check-migrations:
	docker-compose up -d web
	export $(cat envs/web | xargs)
	POSTGRES_HOST=localhost
	poetry run python manage.py migrate
	poetry run python manage.py makemigrations --check


.PHONY: test
test:
	docker-compose up -d web
	POSTGRES_HOST=localhost poetry run pytest -v --cov=evaluation_registry --cov-fail-under 65

lint:
	poetry run isort .
	poetry run black .
