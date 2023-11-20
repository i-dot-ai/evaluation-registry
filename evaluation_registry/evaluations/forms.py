from django.forms import ModelChoiceField, ModelForm, ModelMultipleChoiceField

from evaluation_registry.evaluations.models import (
    Department,
    Evaluation,
    EvaluationFile,
)


class NullableModelMultipleChoiceField(ModelMultipleChoiceField):
    # Because Django doesn't allow for an empty_label in multiple choice fields
    def clean(self, value):
        if value:
            value = [v for v in value if v != ""]
        return super().clean(value)


class EvaluationCreateForm(ModelForm):
    lead_department = ModelChoiceField(queryset=Department.objects.all(), to_field_name="code", label="Lead Department")
    departments = NullableModelMultipleChoiceField(
        queryset=Department.objects.all(), to_field_name="code", required=False
    )

    def __init__(self, *args, **kwargs):
        super(EvaluationCreateForm, self).__init__(*args, **kwargs)

        for field in self.fields.values():
            field.error_messages = {"required": f"{field.label} is required"}

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


class EvaluationFileForm(ModelForm):
    class Meta:
        model = EvaluationFile
        fields = ["file"]
