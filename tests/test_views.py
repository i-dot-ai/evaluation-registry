from unittest.mock import patch

import pytest
from django.forms import Form
from django.http import HttpResponseForbidden

from evaluation_registry.evaluations.models import (
    EvaluationDepartmentAssociation,
    EvaluationDesignTypeDetail,
    EventDate,
    Report,
)
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
def test_evaluation_update_type_view(
    mock_render, client, basic_evaluation, impact, alice, django_assert_max_num_queries
):
    client.force_login(user=alice)
    with django_assert_max_num_queries(5):
        client.get(f"/evaluation/{basic_evaluation.id}/update-type/")
    _, _, data = mock_render.call_args[0]
    assert data["evaluation"] == basic_evaluation
    assert all([eval_type.parent is None for eval_type in data["options"]])

    with django_assert_max_num_queries(7):
        client.get(f"/evaluation/{basic_evaluation.id}/update-type/impact")
    _, _, data = mock_render.call_args[0]
    assert data["evaluation"] == basic_evaluation
    assert all([eval_type.parent == impact for eval_type in data["options"]])


@pytest.mark.django_db
def test_update_view_different_user(client, basic_evaluation, create_user, django_assert_max_num_queries):
    baljit = create_user("baljit@example.com")
    client.force_login(user=baljit)

    with django_assert_max_num_queries(7):
        response = client.get(f"/evaluation/{basic_evaluation.id}/update-type/")
    assert isinstance(response, HttpResponseForbidden)


@pytest.mark.django_db
def test_evaluation_update_policies_view(client, basic_evaluation, alice, django_assert_max_num_queries):
    """right now this query is only testing the performance of the get route"""
    client.force_login(user=alice)
    with django_assert_max_num_queries(8):
        client.get(f"/evaluation/{basic_evaluation.id}/update-policies/")


@pytest.mark.django_db
def test_evaluation_detail_view_performance(
    client,
    child_policy,
    parent_policy,
    home_office,
    cabinet_office,
    impact,
    other,
    basic_evaluation,
    alice,
    django_assert_max_num_queries,
):
    """right now this query is only testing the performance of the get route.

    We extend the basic-evaluation with as many related objects as possible"""
    client.force_login(user=alice)

    for design_type in impact, other:
        EvaluationDesignTypeDetail.objects.create(
            evaluation=basic_evaluation,
            design_type=design_type,
            text=str(design_type),
        )

    for department, is_lead in (cabinet_office, True), (home_office, False):
        EvaluationDepartmentAssociation.objects.create(
            evaluation=basic_evaluation,
            department=department,
            is_lead=is_lead,
        )

    for policy in child_policy, parent_policy:
        basic_evaluation.policies.add(policy)

    for rsm_report_id in 1, 2, 3:
        Report.objects.create(evaluation=basic_evaluation, rsm_report_id=rsm_report_id)

    for year, month in (2000, 1), (2010, 2), (2020, None):
        EventDate.objects.create(evaluation=basic_evaluation, year=year, month=month)

    basic_evaluation.save()

    with django_assert_max_num_queries(9):
        client.get(f"/evaluation/{basic_evaluation.id}/")
