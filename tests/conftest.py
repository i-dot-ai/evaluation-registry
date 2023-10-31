import pytest
import pytz

from evaluation_registry.evaluations.models import (
    Department,
    Evaluation,
    EvaluationDepartmentAssociation,
    User,
)

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


@pytest.fixture
def cabinet_office():
    yield Department.objects.get(code="cabinet-office")


@pytest.fixture
def home_office():
    yield Department.objects.get(code="home-office")


@pytest.fixture
def foreign_office():
    yield Department.objects.get(code="foreign-commonwealth-development-office")


@pytest.fixture
def basic_evaluation(alice):
    evaluation = Evaluation.objects.create(
        created_by=alice,
        visibility=Evaluation.Visibility.PUBLIC,
    )
    yield evaluation


@pytest.fixture
def cabinet_office_led_evaluation(alice, cabinet_office):
    evaluation = Evaluation.objects.create(
        created_by=alice,
        visibility=Evaluation.Visibility.PUBLIC,
    )

    EvaluationDepartmentAssociation.objects.create(
        evaluation=evaluation,
        department=cabinet_office,
        is_lead=True,
    )
    yield evaluation


@pytest.fixture
def home_office_led_evaluation(alice, home_office):
    evaluation = Evaluation.objects.create(
        created_by=alice,
        visibility=Evaluation.Visibility.PUBLIC,
    )

    EvaluationDepartmentAssociation.objects.create(
        evaluation=evaluation,
        department=home_office,
        is_lead=True,
    )
    yield evaluation


@pytest.fixture
def multi_department_evaluation(alice, cabinet_office, home_office):
    evaluation = Evaluation.objects.create(
        created_by=alice,
        visibility=Evaluation.Visibility.PUBLIC,
    )

    for department in home_office, cabinet_office:
        EvaluationDepartmentAssociation.objects.create(
            evaluation=evaluation,
            department=department,
            is_lead=False,
        )
    yield evaluation
