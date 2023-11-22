FROM python:3.11.2
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV TZ=UTC

ARG BASE_URL

ENV BASE_URL=${BASE_URL}

WORKDIR /app

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt update -y && apt install -y postgresql-client

RUN python3 -m pip install -U pip setuptools wheel

COPY ./requirements-dev.lock /app/requirements-dev.lock
RUN python3 -m pip install -r /app/requirements-dev.lock --no-cache-dir

COPY ./docker/web/start.sh /start.sh
RUN chmod +x /start.sh

COPY . /app

WORKDIR /app/

EXPOSE 8000

CMD ["sh","/start.sh"]
