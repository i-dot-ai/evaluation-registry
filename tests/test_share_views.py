from unittest.mock import patch

import pytest
from django.http import HttpResponse, HttpResponseForbidden

from evaluation_registry.evaluations import share_views


@pytest.mark.django_db
def test_create_view(alice, client):
    client.force_login(user=alice)
    with patch.object(share_views, "before_create_view", return_value=HttpResponse()) as mock_first_view:
        client.get("/evaluation/create")
    mock_first_view.assert_called_once()

    with (
        patch.object(share_views, "choose_evaluation_status_view", return_value=HttpResponse()) as mock_status_view,
        patch.object(share_views, "evaluation_create_view", return_value=HttpResponse()) as mock_create_view,
    ):
        client.get("/evaluation/create/3/")
    mock_status_view.assert_called_once()
    mock_create_view.assert_not_called()

    with patch.object(share_views, "evaluation_create_view", return_value=HttpResponse()) as mock_create_view:
        client.get("/evaluation/create/3/test")
    mock_create_view.assert_called_once()
    assert mock_create_view.call_args[1]["status"] == "test"


@pytest.mark.django_db
def test_share_view_no_design_types(alice, client, basic_evaluation):
    client.force_login(user=alice)
    with patch.object(share_views, "evaluation_type_view", return_value=HttpResponse()) as mock_type_view:
        client.get(f"/evaluation/{basic_evaluation.id}/share/1/")
    mock_type_view.assert_called_once()
    assert len(mock_type_view.call_args) == 2

    with patch.object(share_views, "evaluation_type_view", return_value=HttpResponse()) as mock_type_view:
        client.get(f"/evaluation/{basic_evaluation.id}/share/2/")
    mock_type_view.assert_not_called()


@pytest.mark.django_db
def test_share_view_with_impact_type(alice, client, impact_evaluation):
    client.force_login(user=alice)
    with patch.object(share_views, "evaluation_type_view", return_value=HttpResponse()) as mock_type_view:
        client.get(f"/evaluation/{impact_evaluation.id}/share/2/")
    mock_type_view.assert_called_once()


@pytest.mark.django_db
def test_share_view_different_user(client, basic_evaluation, create_user):
    baljit = create_user("baljit@example.com")
    client.force_login(user=baljit)

    response = client.get(f"/evaluation/{basic_evaluation.id}/share/1/")
    assert isinstance(response, HttpResponseForbidden)
