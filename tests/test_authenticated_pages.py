import pytest
from django.contrib.sessions.models import Session
from django.test import override_settings
from django.urls import reverse

from evaluation_registry.evaluations.forms import EmailForm
from evaluation_registry.evaluations.models import User


@pytest.mark.django_db
def test_login(client, mailoutbox):
    email_address = "george@cabinetoffice.gov.uk"

    assert not User.objects.filter(email=email_address).exists()

    response = client.post(reverse("login"), data={"email": email_address})

    assert response.status_code == 302
    user = User.objects.get(email=email_address)

    # no sessions == no one is logged in
    # cant use .is_authenticated here, because that only works within the context of a request
    assert Session.objects.count() == 0
    email = next(mail for mail in mailoutbox if email_address in mail.to)
    link = email.body[email.body.find("http") :]
    link = link[: link.find("\n")]

    response = client.get(link, follow=True)
    assert response.redirect_chain == [("/post-login/", 302), ("/", 302)]
    assert response.status_code == 200

    # there is a session for this user, i.e. they are logged in
    assert Session.objects.first().get_decoded()["_auth_user_id"] == str(user.id)


@override_settings(ALLOWED_CIVIL_SERVICE_DOMAINS=["britishlibrary.org"])
@pytest.mark.django_db
@pytest.mark.parametrize(
    "email, errors",
    [
        ("alice@gamil.com", {"email": ["This email domain is not allowed."]}),
        ("bob@cabinetoffice.gov.uk", {}),
        ("cloe@britishlibrary.org", {}),
    ],
)
def test_login_fail(email, errors):
    form = EmailForm(data={"email": email})
    assert form.is_valid() != bool(errors)
    assert form.errors == errors


@pytest.mark.django_db
def test_link_fails_invalid_token(
    client,
    alice,
):
    link = f"http://testserver/verify/?token=3c0d9810&email={alice.email}"

    response = client.get(link, follow=True)
    assert response.status_code == 200
    assert "Login failed" in str(response.content), str(response.content)


@pytest.mark.django_db
def test_link_fails_invalid_user(client):
    link = "http://testserver/verify/?token=3c0d9810&email=someone@gov.uk"

    response = client.get(link, follow=True)
    assert response.status_code == 200
    assert "Login failed" in str(response.content)
