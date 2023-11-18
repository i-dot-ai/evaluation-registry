import pytest
from django.forms import Form

from evaluation_registry.evaluations.models import EvaluationDesignTypeDetail
from evaluation_registry.evaluations.views import (
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
