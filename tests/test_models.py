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
