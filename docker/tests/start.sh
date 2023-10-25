#!/bin/sh

set -o errexit
set -o nounset

python manage.py migrate --noinput
echo
echo '----------------------------------------------------------------------'
echo
pytest -v ./pytest_tests
