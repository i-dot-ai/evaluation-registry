#!/bin/sh

set -o errexit
set -o nounset

poetry run python manage.py migrate --noinput
watchmedo auto-restart --directory=./  --pattern=""*.py"" --recursive -- waitress-serve --port=$PORT evaluation_registry.wsgi:application
