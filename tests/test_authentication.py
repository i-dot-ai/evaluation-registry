import pytest
from django.contrib.sessions.models import Session
from django.urls import reverse

from evaluation_registry.evaluations.models import User


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
    assert Session.objects.first().get_decoded()["_auth_user_id"] == user.id
