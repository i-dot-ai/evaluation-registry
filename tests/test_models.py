import pytest

from evaluation_registry.evaluations.models import Evaluation


@pytest.mark.django_db
def test_evaluation(alice, cabinet_office, public):
    evaluation = Evaluation.objects.create(created_by=alice, lead_department=cabinet_office, visibility=public)
    assert evaluation.created_by == alice
    assert evaluation.lead_department == cabinet_office
    assert evaluation.visibility == public
