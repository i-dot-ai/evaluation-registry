include envs/web

define _update_requirements
	docker-compose run requirements bash -c "pip install -U pip setuptools && pip install -U -r /app/$(1).txt && pip freeze > /app/$(1).lock"
endef

.PHONY: update-requirements
update-requirements:
	$(call _update_requirements,requirements)
	$(call _update_requirements,requirements-dev)

.PHONY: reset-db
reset-db:
	docker-compose down db --volumes
	docker-compose up -d db

# -------------------------------------- Code Style  -------------------------------------

.PHONY: check-python-code
check-python-code:
	isort --check .
	black --check .
	flake8
	bandit -ll -r evaluation_registry
	mypy evaluation_registry/ --ignore-missing-imports

.PHONY: check-migrations
check-migrations:
	docker-compose build web
	docker-compose run web python manage.py migrate
	docker-compose run web python manage.py makemigrations --check

.PHONY: test
test:
	docker-compose up -d web
	docker-compose run web POSTGRES_HOST=localhost python -m pytest -v

lint:
	isort .
	black .

