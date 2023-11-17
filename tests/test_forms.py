import pytest

from evaluation_registry.evaluations.forms import EvaluationCreateForm, NullableModelMultipleChoiceField
from evaluation_registry.evaluations.models import Department


@pytest.mark.django_db
def test_nullable_model_multiple_choice_field(cabinet_office):
    department_field = NullableModelMultipleChoiceField(queryset=Department.objects.all(), to_field_name="code")

    assert department_field.clean(["", cabinet_office.code]).count() == 1


@pytest.mark.django_db
def test_evaluation_create_form(cabinet_office):
    form = EvaluationCreateForm(
        data={
            "title": "",
            "departments": [cabinet_office.code],
            "lead_department": cabinet_office.code,
        }
    )

    assert form.errors["title"] == ["Title is required"]
    assert form.errors["departments"] == [f"This department has been listed more than once: {cabinet_office.display}"]
