import pytest

from evaluation_registry.evaluations.models import Evaluation


@pytest.mark.django_db
def test_evaluation(alice, cabinet_office):
    evaluation = Evaluation.objects.create(
        created_by=alice,
        lead_department=cabinet_office,
        visibility=Evaluation.EvaluationVisibility.PUBLIC,
    )
    assert evaluation.created_by == alice
    assert evaluation.lead_department == cabinet_office
    assert evaluation.visibility == Evaluation.EvaluationVisibility.PUBLIC.value
