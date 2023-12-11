import os

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from evaluation_registry.evaluations.models import Evaluation, RSMFile


@pytest.mark.django_db
def test_rsm_upload(admin_client):
    """this test is in two parts:
    1. upload a new RSM csv
    2. call the import_csv action on it
    """
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rsm-data-2023-07-21.csv")

    with open(file_path, "rb") as file:
        file_data = file.read()

    uploaded_file = SimpleUploadedFile("test_file.txt", file_data, "text/plain")

    response = admin_client.post(
        "/admin/evaluations/rsmfile/add/",
        {
            "csv": uploaded_file,
        },
        follow=True,
    )

    assert response.status_code == 200
    file = RSMFile.objects.last()

    initial_count = Evaluation.objects.count()

    response = admin_client.post(
        "/admin/evaluations/rsmfile/",
        {
            "action": "import_csv",
            "_selected_action": [file.pk],
        },
        follow=True,
    )

    assert response.status_code == 200
    assert Evaluation.objects.count() - initial_count == 3


@pytest.mark.django_db
def test_evaluation_admin_performance(impact_evaluation, admin_client, django_assert_max_num_queries):
    with django_assert_max_num_queries(20):
        admin_client.get(f"/admin/evaluations/evaluation/{impact_evaluation.pk}/change/")
