import os

import pytest
from django.core.management import call_command

from evaluation_registry.evaluations.factories import EvaluationFactory
from evaluation_registry.evaluations.models import Evaluation


@pytest.mark.django_db
def test_load_rsm_csv():
    initial_evaluation_count = Evaluation.objects.count()
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rsm-data-2023-07-21.scsv")
    call_command("load_rsm_csv", file_path)
    final_evaluation_count = Evaluation.objects.count()
    assert final_evaluation_count - initial_evaluation_count == 3


@pytest.mark.django_db
@pytest.mark.parametrize(
    "is_process, is_impact, is_economic, is_other",
    [
        (True, False, False, False),
        (False, True, False, False),
        (False, False, True, False),
        (False, False, False, True),
        (True, True, True, True),  # can handle multiple given types
        (False, False, False, False)  # can handle no given types
    ]
)
def test_update_evaluation_types(is_process, is_impact, is_economic, is_other):
    evaluation = EvaluationFactory(
        is_process_type=is_process,
        is_impact_type=is_impact,
        is_economic_type=is_economic,
        is_other_type=is_other
    )
    evaluation.save()
    assert not Evaluation.objects.get(id=evaluation.id).evaluation_types
    call_command("update_evaluation_types")

    assert (
        Evaluation.EvaluationType.PROCESS in Evaluation.objects.get(id=evaluation.id).evaluation_types
        ) is is_process
    assert (
        Evaluation.EvaluationType.IMPACT in Evaluation.objects.get(id=evaluation.id).evaluation_types
        ) is is_impact
    assert (
        Evaluation.EvaluationType.ECONOMIC in Evaluation.objects.get(id=evaluation.id).evaluation_types
        ) is is_economic
    assert (
        Evaluation.EvaluationType.OTHER in Evaluation.objects.get(id=evaluation.id).evaluation_types
        ) is is_other
