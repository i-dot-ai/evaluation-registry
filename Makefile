include envs/web


.PHONY: update-requirements
update-requirements:
	poetry update

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
check-migrations:
	docker-compose build web
	docker-compose run web python manage.py migrate
	docker-compose run web python manage.py makemigrations --check

.PHONY: test
test:
	docker-compose up -d web
	docker-compose run web python -m pytest -v

lint:
	poetry run isort .
	poetry run black .

