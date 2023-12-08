from unittest.mock import patch

import pytest
from django.forms import Form
from django.http import HttpResponseForbidden

from evaluation_registry.evaluations.models import EvaluationDesignTypeDetail
from evaluation_registry.evaluations.views import (
    render,
    update_evaluation_design_objects,
)


@pytest.mark.django_db
def test_update_evaluation_design_objects(impact, other, basic_evaluation, evaluation_other_type_link):
    existing_evaluation_links = EvaluationDesignTypeDetail.objects.filter(id=evaluation_other_type_link.id)

    form = Form
    form.cleaned_data = {"design_types": [impact], "evaluation": basic_evaluation}
    form.changed_data = ["design_types"]

    update_evaluation_design_objects(existing_evaluation_links, [other], form)
    assert EvaluationDesignTypeDetail.objects.filter(design_type=other).count() == 0
    assert EvaluationDesignTypeDetail.objects.filter(design_type=impact).count() == 1


@pytest.mark.django_db
def test_update_evaluation_design_objects_text_only(other, basic_evaluation, evaluation_other_type_link):
    update_text = "updated text"
    existing_evaluation_links = EvaluationDesignTypeDetail.objects.filter(id=evaluation_other_type_link.id)

    form = Form
    form.cleaned_data = {"design_types": [other], "evaluation": basic_evaluation, "text": update_text}
    form.changed_data = ["text"]

    update_evaluation_design_objects(existing_evaluation_links, [other], form)
    assert EvaluationDesignTypeDetail.objects.filter(design_type=other).count() == 1
    assert EvaluationDesignTypeDetail.objects.get(design_type=other).id == existing_evaluation_links.first().id
    assert EvaluationDesignTypeDetail.objects.get(design_type=other).text == update_text


@pytest.mark.django_db
@patch("evaluation_registry.evaluations.views.render", side_effect=render)
def test_evaluation_update_type_view(mock_render, client, basic_evaluation, impact, alice):
    client.force_login(user=alice)
    client.get(f"/evaluation/{basic_evaluation.id}/update-type/")
    _, _, data = mock_render.call_args[0]
    assert data["evaluation"] == basic_evaluation
    assert all([eval_type.parent is None for eval_type in data["options"]])

    client.get(f"/evaluation/{basic_evaluation.id}/update-type/impact")
    _, _, data = mock_render.call_args[0]
    assert data["evaluation"] == basic_evaluation
    assert all([eval_type.parent == impact for eval_type in data["options"]])


@pytest.mark.django_db
def test_update_view_different_user(client, basic_evaluation, create_user):
    baljit = create_user("baljit@example.com")
    client.force_login(user=baljit)

    response = client.get(f"/evaluation/{basic_evaluation.id}/update-type/")
    assert isinstance(response, HttpResponseForbidden)
