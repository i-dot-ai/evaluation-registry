import pytest

from evaluation_registry.evaluations.forms import (
    EvaluationBasicDetailsForm,
    EvaluationDesignTypeDetailForm,
    EvaluationShareForm,
    EventDateForm,
    NullableModelMultipleChoiceField,
)
from evaluation_registry.evaluations.models import Department, EventDate


@pytest.mark.django_db
def test_nullable_model_multiple_choice_field(cabinet_office):
    department_field = NullableModelMultipleChoiceField(queryset=Department.objects.all(), to_field_name="code")

    assert department_field.clean(["", cabinet_office.code]).count() == 1


@pytest.mark.django_db
def test_evaluation_basic_details_form(cabinet_office):
    form = EvaluationBasicDetailsForm(
        data={
            "title": "",
            "departments": [cabinet_office.code],
            "lead_department": cabinet_office.code,
        }
    )

    assert form.errors["title"] == ["Title is required"]
    assert form.errors["departments"] == [f"This department has been listed more than once: {cabinet_office.display}"]


@pytest.mark.django_db
def test_evaluation_basic_details_update_form_update(cabinet_office_led_evaluation, home_office):
    form = EvaluationBasicDetailsForm(
        instance=cabinet_office_led_evaluation,
        data={
            "title": "test",
            "lead_department": home_office.code,
        },
    )

    assert not form.errors
    assert form.cleaned_data["lead_department"] == home_office


@pytest.mark.django_db
def test_evaluation_design_type_detail_form(impact, other):
    form = EvaluationDesignTypeDetailForm(data={"design_types": [impact.code, other.code], "text": ""})

    assert form.errors["evaluation"] == ["Evaluation is required"]
    assert form.errors["text"] == ["Please provide additional description for the 'Other' choice"]


@pytest.mark.django_db
def test_event_date_form(basic_evaluation):
    form = EventDateForm(data={"evaluation": basic_evaluation, "category": EventDate.Category.OTHER, "month": "1234"})

    assert form.errors["other_description"] == ["Please provide additional description for the 'Other' choice"]
    assert form.errors["month"] == ["Please enter a month number from 1-12"]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "plan_link, evaluation_link, expected_number_of_errors",
    [
        ("test.com", "test.com", 0),
        ("test.com", "", 0),
        ("", "test.com", 0),
        ("", "", 2),
    ],
)
def test_evaluation_share_form(basic_evaluation, plan_link, evaluation_link, expected_number_of_errors):
    form = EvaluationShareForm(
        data={
            "evaluation": basic_evaluation,
            "is_final_report_published": "1",
            "plan_link": plan_link,
            "link_to_published_evaluation": evaluation_link,
        }
    )

    assert len(form.errors) == expected_number_of_errors
