import pytest
from django.db import IntegrityError

from evaluation_registry.evaluations.models import (
    Evaluation,
    EvaluationDepartmentAssociation,
)


@pytest.mark.django_db
def test_evaluation(cabinet_office_led_evaluation, cabinet_office, home_office):
    EvaluationDepartmentAssociation.objects.create(
        evaluation=cabinet_office_led_evaluation, department=home_office, is_lead=False
    )

    assert cabinet_office_led_evaluation.departments.count() == 2
    assert cabinet_office_led_evaluation.lead_department == cabinet_office
    assert cabinet_office_led_evaluation.visibility == Evaluation.Visibility.PUBLIC.value


@pytest.mark.django_db
def test_evaluation_lead_constraint(cabinet_office_led_evaluation, home_office):
    with pytest.raises(IntegrityError) as error:
        EvaluationDepartmentAssociation.objects.create(
            evaluation=cabinet_office_led_evaluation, department=home_office, is_lead=True
        )

    assert 'duplicate key value violates unique constraint "unique-lead-department"' in error.value.args[0]


@pytest.mark.django_db
def test_evaluation_no_lead_constraint(basic_evaluation, cabinet_office, home_office):
    EvaluationDepartmentAssociation.objects.create(
        evaluation=basic_evaluation, department=cabinet_office, is_lead=False
    )
    EvaluationDepartmentAssociation.objects.create(evaluation=basic_evaluation, department=home_office, is_lead=False)

    assert basic_evaluation.lead_department is None


@pytest.mark.django_db
def test_evaluation_duplicate_constraint(cabinet_office_led_evaluation, cabinet_office):
    with pytest.raises(IntegrityError) as error:
        EvaluationDepartmentAssociation.objects.create(
            evaluation=cabinet_office_led_evaluation, department=cabinet_office, is_lead=False
        )

    assert 'duplicate key value violates unique constraint "unique-evaluation-department"' in error.value.args[0]


@pytest.mark.pdf_to_json
@pytest.mark.django_db
def test_extract_plain_text(pdf_evaluation_file):
    pdf_evaluation_file.extract_plain_text()
    assert pdf_evaluation_file.plain_text == "Dummy PDF file"


@pytest.mark.pdf_to_json
@pytest.mark.django_db
def test_build_evaluation(pdf_evaluation_file_with_text):
    """here we test that chatGPT's guesses for:
    * department 'HM Revenue and Customs' gets mapped to `hm-revenue-customs`
    * design-type 'qualitative' gets mapped to `qualitative_process`
    using the unsung hero of NLP: postgres full text search
    """
    pdf_evaluation_file_with_text.build_evaluation()
    assert list(pdf_evaluation_file_with_text.evaluation.departments.values_list("code", flat=True)) == [
        "hm-revenue-customs"
    ]
    assert list(pdf_evaluation_file_with_text.evaluation.evaluation_design_types.values_list("code", flat=True)) == [
        "qualitative_process"
    ]
