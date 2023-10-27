import pytest

from evaluation_registry.evaluations.models import (
    Evaluation,
    EvaluationDepartmentAssociation,
)


@pytest.mark.django_db
def test_evaluation(alice, cabinet_office, home_office):
    evaluation = Evaluation.objects.create(
        created_by=alice,
        visibility=Evaluation.EvaluationVisibility.PUBLIC,
    )
    EvaluationDepartmentAssociation.objects.create(evaluation=evaluation, department=cabinet_office, is_lead=True)
    EvaluationDepartmentAssociation.objects.create(evaluation=evaluation, department=home_office, is_lead=False)

    assert evaluation.created_by == alice
    assert evaluation.departments.count() == 2
    assert evaluation.lead_department == cabinet_office
    assert evaluation.visibility == Evaluation.EvaluationVisibility.PUBLIC.value
