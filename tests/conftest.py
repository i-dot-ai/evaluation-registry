import base64
import json
from datetime import datetime

import pytest
import pytz
from django.conf import settings
from freezegun import freeze_time

from ask_ai.conversation import models
from ask_ai.conversation.models import User

UTC = pytz.timezone("UTC")


@pytest.fixture
def create_user():
    def _create_user(email):
        user = User.objects.create_user(email=email)
        return user

    return _create_user


@pytest.fixture
def alice(create_user):
    return create_user("alice@example.com")
