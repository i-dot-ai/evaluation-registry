import pytest

from evaluation_registry.evaluations.filters import EvaluationFilter
from evaluation_registry.evaluations.models import Evaluation


@pytest.mark.django_db
@pytest.mark.parametrize(
    "params, count",
    [
        ({}, 3),
        ({"departments": ["cabinet-office"]}, 2),
        ({"departments": ["cabinet-office", "home-office"]}, 3),
        ({"departments": ["foreign-commonwealth-development-office"]}, 0),
        ({"departments": ["home-office"]}, 2),
        ({"departments": ["department-of-social-affairs-and-citizenship"]}, 3),
    ],
)
def tests_evaluation_filter(
    multi_department_evaluation,
    cabinet_office_led_evaluation,
    home_office_led_evaluation,
    foreign_office,
    params,
    count,
):
    evaluation_list = EvaluationFilter(data=params, queryset=Evaluation.objects.all())
    assert evaluation_list.qs.count() == count
