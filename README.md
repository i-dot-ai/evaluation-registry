## Using Docker

1. [Install Docker](https://docs.docker.com/get-docker/) on your machine
2. `docker-compose up --build --force-recreate web`
3. It's now available at: http://localhost:8020/

Migrations are run automatically at startup, and suppliers are added automatically at startup

## Running locally

```commandline
export $(cat envs/web | xargs) POSTGRES_HOST=localhost && python manage.py runserver
```


## Running tests

```commandline
docker compose up -d db
POSTGRES_HOST=localhost pytest tests . --cov=evaluation_registry  --cov-fail-under 60
```

or

```commandline
make test
```

## Checking code

    make check-python-code


## how to run management commands on the server

1. navigate to EC2 services in the AWS console
2. select an instance, click connect
3. run the following
```commandline
eval $(/opt/elasticbeanstalk/bin/get-config environment | jq -r 'to_entries | .[] | "export \(.key)=\(.value)"' )
source /var/app/venv/staging-LQM1lest/bin/activate
cd /var/app/current

```
4. now run management commands like normal, i.e. `python manage.py showmigrations`