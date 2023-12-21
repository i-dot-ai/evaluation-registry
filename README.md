## Using Docker

1. [Install Docker](https://docs.docker.com/get-docker/) on your machine
2. `docker-compose up --build --force-recreate web`
3. It's now available at: http://localhost:8020/

Migrations are run automatically at startup, and suppliers are added automatically at startup

## Running locally

```commandline
export $(cat envs/web | xargs) POSTGRES_HOST=localhost && poetry run python manage.py runserver
```


## Running tests

```commandline
docker-compose up -d db
POSTGRES_HOST=localhost poetry run pytest tests . --cov=evaluation_registry  --cov-fail-under 70
```

or

```commandline
make test
```

## Checking code

    make check-python-code
