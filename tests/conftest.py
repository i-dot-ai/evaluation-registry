import pytest
import pytz
from django.core.files.uploadedfile import SimpleUploadedFile

from evaluation_registry.evaluations.models import (
    Department,
    Evaluation,
    EvaluationDepartmentAssociation,
    EvaluationDesignType,
    EvaluationDesignTypeDetail,
    PdfEvaluationFile,
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
def pdf_evaluation_file():
    pdf = SimpleUploadedFile("report.pdf", open("tests/report.pdf", "rb").read())
    file = PdfEvaluationFile(pdf=pdf)
    yield file


@pytest.fixture
def pdf_evaluation_file_with_text():
    structured_text = {
        "title": "Research into the Behavioural Effects of building in Risk Triggers to Third Party Software",
        "status": "complete",
        "lead_department": "HM Revenue and Customs",
        "brief_description": "This research report explores ... returns.",
        "evaluation_design_types": ["qualitative"],
    }
    pdf = SimpleUploadedFile("report.pdf", open("tests/report.pdf", "rb").read())
    file = PdfEvaluationFile(pdf=pdf, structured_text=structured_text)
    yield file
