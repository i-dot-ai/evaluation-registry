FROM python:3.11.6
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV TZ=UTC

WORKDIR /app

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY . /app

RUN python3 -m pip install poetry
RUN poetry install

COPY ./docker/web/start.sh /start.sh
RUN chmod +x /start.sh

RUN \
    DJANGO_SETTINGS_MODULE=evaluation_registry.settings_base \
    DJANGO_SECRET_KEY="temp" \
    POSTGRES_HOST="temp" \
    poetry run python manage.py collectstatic --no-input

WORKDIR /app/

EXPOSE 8000

CMD ["sh","/start.sh"]