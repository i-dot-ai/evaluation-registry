import functools

import httpx
import testino

import evaluation_registry.wsgi

TEST_SERVER_URL = "http://evaluation-registry-testserver:8020/"


def with_client(func):
    @functools.wraps(func)
    def _inner(*args, **kwargs):
        with httpx.Client(app=evaluation_registry.wsgi.application, base_url=TEST_SERVER_URL) as client:
            return func(client, *args, **kwargs)

    return _inner


def make_testino_client():
    client = testino.WSGIAgent(evaluation_registry.wsgi.application, TEST_SERVER_URL)
    return client
