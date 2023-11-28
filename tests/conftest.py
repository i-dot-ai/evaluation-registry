import pytest
import pytz

from evaluation_registry.evaluations.models import (
    Department,
    Evaluation,
    EvaluationDepartmentAssociation,
    EvaluationDesignType,
    EvaluationDesignTypeDetail,
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
def basic_evaluation(alice):
    evaluation = Evaluation.objects.create(
        created_by=alice,
        visibility=Evaluation.Visibility.PUBLIC,
    )
    yield evaluation


@pytest.fixture
def cabinet_office_led_evaluation(basic_evaluation, cabinet_office):
    EvaluationDepartmentAssociation.objects.create(
        evaluation=basic_evaluation,
        department=cabinet_office,
        is_lead=True,
    )
    yield basic_evaluation


@pytest.fixture
def impact():
    yield EvaluationDesignType.objects.get(code="impact")


@pytest.fixture
def other():
    yield EvaluationDesignType.objects.get(code="other")


@pytest.fixture
def evaluation_impact_type_link(basic_evaluation, impact):
    evaluation_type_link = EvaluationDesignTypeDetail.objects.create(
        evaluation=basic_evaluation,
        design_type=impact,
    )
    yield evaluation_type_link


@pytest.fixture
def evaluation_other_type_link(basic_evaluation, other):
    evaluation_type_link = EvaluationDesignTypeDetail.objects.create(
        evaluation=basic_evaluation,
        design_type=other,
        text="hello world",
    )
    yield evaluation_type_link


@pytest.fixture
def impact_evaluation(basic_evaluation, evaluation_impact_type_link):
    basic_evaluation.evaluationdesigntypedetail_set.add(evaluation_impact_type_link)

    yield basic_evaluation
