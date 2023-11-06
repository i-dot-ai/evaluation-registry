import pytest


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url",
    [
        "/home/",
        "/evaluations/",
        "/logout/",
    ],
)
@pytest.mark.parametrize("login, status_code", [(True, 200), (False, 401)])
def test_get_pages_logged_in(client, alice, url, login, status_code):
    if login:
        client.force_login(alice)
    response = client.get(url, follow=True)
    assert response.status_code == status_code
