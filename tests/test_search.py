import pytest

from evaluation_registry.evaluations.models import (
    Evaluation,
    EvaluationDepartmentAssociation,
)
from evaluation_registry.evaluations.views import (
    authorised_base_evaluation_queryset,
    filter_by_department_and_types,
    full_text_search,
)


@pytest.fixture
def evaluations(alice, cabinet_office, home_office, impact, other):
    e1 = Evaluation.objects.create(title="summaries of policies", created_by=alice)
    e2 = Evaluation.objects.create(
        title="public transport", brief_description="to long to detail here", visibility=Evaluation.Visibility.PUBLIC
    )
    e2.evaluation_design_types.add(impact)

    e3 = Evaluation.objects.create(title="details of something or other", visibility=Evaluation.Visibility.DRAFT)
    e3.evaluation_design_types.add(impact)
    e3.evaluation_design_types.add(other)

    for dept in cabinet_office, home_office:
        EvaluationDepartmentAssociation.objects.create(
            evaluation=e1,
            department=dept,
            is_lead=False,
        )

    EvaluationDepartmentAssociation.objects.create(
        evaluation=e2,
        department=cabinet_office,
        is_lead=True,
    )
    yield Evaluation.objects.all()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "show_public, show_user, expected_number_of_results",
    [
        (True, True, 2),
        (True, False, 1),
        (False, True, 1),
        (False, False, 0),
    ],
)
def test_authorised_base_evaluation_queryset(alice, evaluations, show_public, show_user, expected_number_of_results):
    results = authorised_base_evaluation_queryset(show_public=show_public, show_user=show_user, user=alice)
    assert len(results) == expected_number_of_results


@pytest.mark.django_db
@pytest.mark.parametrize(
    "search_term, expected_number_of_results, expected_lead_title",
    [
        ("policies", 1, "summaries of policies"),  # match one word
        ("policies summaries", 1, "summaries of policies"),  # match wrong word order
        ("policy summary", 1, "summaries of policies"),  # stemming, policies == policy
        ("detail", 2, "details of something or other"),  # find same word in both title and description
    ],
)
def test_full_text_search(evaluations, search_term, expected_number_of_results, expected_lead_title):
    results = full_text_search(Evaluation.objects.all(), search_term)
    assert len(results) == expected_number_of_results
    assert results[0].title == expected_lead_title


@pytest.mark.django_db
@pytest.mark.parametrize(
    "departments, types, expected_number_of_results",
    [
        ([], [], 3),
        (["cabinet-office", "home-office"], [], 2),
        (["cabinet-office"], [], 2),
        (["home-office"], [], 1),
        ([], ["impact", "other"], 2),
        ([], ["impact"], 2),
        ([], ["other"], 1),
        ([], ["some-new-type-i-just-invented"], 0),
        (["cabinet-office"], ["impact", "other"], 1),
    ],
)
def test_filter_evaluations(evaluations, departments, types, expected_number_of_results):
    results = filter_by_department_and_types(evaluations, departments, types)
    assert len(results) == expected_number_of_results
