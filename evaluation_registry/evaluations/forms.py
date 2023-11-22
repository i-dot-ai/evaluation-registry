from django.forms import (
    CharField,
    Form,
    ModelChoiceField,
    ModelForm,
    ModelMultipleChoiceField,
)

from evaluation_registry.evaluations.models import (
    Department,
    Evaluation,
    EvaluationDesignType,
)


class NullableModelMultipleChoiceField(ModelMultipleChoiceField):
    # Because Django doesn't allow for an empty_label in multiple choice fields
    def clean(self, value):
        if value:
            value = [v for v in value if v != ""]
        return super().clean(value)


class BetterErrorsModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(BetterErrorsModelForm, self).__init__(*args, **kwargs)

        for field in self.fields.values():
            field.error_messages = {"required": f"{field.label} is required"}


class EvaluationCreateForm(BetterErrorsModelForm):
    lead_department = ModelChoiceField(queryset=Department.objects.all(), to_field_name="code", label="Lead Department")
    departments = NullableModelMultipleChoiceField(
        queryset=Department.objects.all(), to_field_name="code", required=False
    )

    def clean(self):
        super().clean()
        lead_department = self.cleaned_data.get("lead_department")
        departments = self.cleaned_data.get("departments")

        if departments:
            if departments.filter(id=lead_department.id).exists():
                self.add_error(
                    "departments", f"This department has been listed more than once: {lead_department.display}"
                )

    class Meta:
        model = Evaluation
        fields = ["status", "title"]


class EvaluationDesignTypeDetailForm(Form):
    evaluation = ModelChoiceField(queryset=Evaluation.objects.all(), label="Evaluation")
    design_types = ModelMultipleChoiceField(
        queryset=EvaluationDesignType.objects.all(), label="Evaluation type", to_field_name="code"
    )
    text = CharField(max_length=1024, required=False)

    def __init__(self, *args, **kwargs):
        super(EvaluationDesignTypeDetailForm, self).__init__(*args, **kwargs)

        for field in self.fields.values():
            field.error_messages = {"required": f"{field.label} is required"}

    def clean(self):
        super().clean()
        design_types = self.cleaned_data.get("design_types")
        text = self.cleaned_data.get("text")

        if design_types:
            if design_types.filter(collect_description=True).exists() and not text:
                self.add_error("text", "Please provide additional description for the 'Other' choice")


class EventDateForm(BetterErrorsModelForm):
    pass
