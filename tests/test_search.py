import pytest

from evaluation_registry.evaluations.models import (
    Evaluation,
    EvaluationDepartmentAssociation,
)
from evaluation_registry.evaluations.views import (
    filter_by_department_and_types,
    full_text_search,
)


@pytest.fixture
def evaluations(cabinet_office, home_office):
    e1 = Evaluation.objects.create(title="summaries of policies")
    e2 = Evaluation.objects.create(
        title="how to cover up a large scandal",
        brief_description="to long to detail here",
        evaluation_types=[Evaluation.EvaluationType.IMPACT],
    )
    Evaluation.objects.create(
        title="details of something or other",
        evaluation_types=[Evaluation.EvaluationType.IMPACT, Evaluation.EvaluationType.OTHER],
    )

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
    "search_term, expected_number_of_results, expected_lead_title",
    [
        ("policies", 1, "summaries of policies"),  # match one word
        ("policies summaries", 1, "summaries of policies"),  # match wrong word order
        ("policy summary", 1, "summaries of policies"),  # stemming, policies == policy
        ("detail", 2, "details of something or other"),  # find same word in both title and description
    ],
)
def test_full_text_search(evaluations, search_term, expected_number_of_results, expected_lead_title):
    results = full_text_search(search_term)
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
