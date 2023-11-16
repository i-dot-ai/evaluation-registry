import os

import pytest
from django.core.management import call_command

from evaluation_registry.evaluations.models import Evaluation


@pytest.mark.django_db
def test_load_rsm_csv():
    initial_evaluation_count = Evaluation.objects.count()
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rsm-data-2023-07-21.scsv")
    call_command("load_rsm_csv", file_path)
    final_evaluation_count = Evaluation.objects.count()
    assert final_evaluation_count - initial_evaluation_count == 3
