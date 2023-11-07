import datetime

import pytest
from django.contrib.sessions.models import Session
from django.test import override_settings
from django.urls import reverse

from evaluation_registry.evaluations.forms import EmailForm
from evaluation_registry.evaluations.models import LoginToken, User


@pytest.mark.django_db
def test_login(client, mailoutbox):
    email_address = "george@cabinetoffice.gov.uk"

    assert not User.objects.filter(email=email_address).exists()

    response = client.post(reverse("login"), data={"email": email_address})

    assert response.status_code == 200
    user = User.objects.get(email=email_address)

    # no sessions == no one is logged in
    # cant use .is_authenticated here, because that only works within the context of a request
    assert Session.objects.count() == 0
    email = next(mail for mail in mailoutbox if email_address in mail.to)
    link = email.body[email.body.find("http") :]

    response = client.get(link, follow=True)
    assert response.redirect_chain == [("/home/", 302)]
    assert response.status_code == 200

    # there is a session for this user, i.e. they are logged in
    assert Session.objects.first().get_decoded()["_auth_user_id"] == str(user.id)


@override_settings(ALLOWED_DOMAINS=["bitishlibrary.org"])
@pytest.mark.django_db
@pytest.mark.parametrize(
    "email, errors",
    [
        ("alice@gamil.com", {"email": ["This email domain is not allowed."]}),
        ("bob@cabinetoffice.gov.uk", {}),
        ("cloe@bitishlibrary.org", {}),
    ],
)
def test_login_fail(email, errors):
    form = EmailForm(data={"email": email})
    assert form.is_valid() != bool(errors)
    assert form.errors == errors


@pytest.mark.parametrize(
    "token, error",
    [
        ("3c0d9810-daf2-4052-b18c-d672acd738ba", "link does not exist, please try again"),
        ("3c0d9810", "link is malformed, please try again"),
    ],
)
@pytest.mark.django_db
def test_link_fails(client, token, error):
    link = f"http://testserver/verify-login-link/?token={token}"

    response = client.get(link, follow=True)
    assert response.status_code == 200
    assert error in str(response.content)


@pytest.mark.django_db
def test_link_expired(client, alice, mocker):
    login_token = LoginToken.objects.create(user=alice, created_at=datetime.date(2000, 1, 1))
    link = f"http://testserver/verify-login-link/?token={login_token.token}"

    mocker.patch("evaluation_registry.evaluations.models.LoginToken.has_expired", return_value=True)

    response = client.get(link, follow=True)
    assert response.status_code == 200
    error = "link has expired, please try again"
    assert error in str(response.content)
