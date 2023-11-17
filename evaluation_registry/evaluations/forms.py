from django.core.exceptions import ValidationError
from django.forms import ModelChoiceField, ModelForm, ModelMultipleChoiceField 


from evaluation_registry.evaluations.models import Department, Evaluation


class NullableModelMultipleChoiceField(ModelMultipleChoiceField):
    # Because Django doesn't allow for an empty_label in multiple choice fields
    def clean(self, value):
        updated_value = [v for v in value if v != '']
        super().clean(updated_value)


class EvaluationCreateForm(ModelForm):
    lead_department = ModelChoiceField(queryset=Department.objects.all(), empty_label='', to_field_name='code')
    departments = NullableModelMultipleChoiceField(queryset=Department.objects.all(), to_field_name='code', required=False)

    def clean(self):
        cleaned_data = super().clean()
        lead_department = cleaned_data.get("lead_department")
        departments = cleaned_data.get("departments")

        all_departments = [lead_department] + [departments]

        for idx, department in enumerate(all_departments):
            if len(set(all_departments[:idx+1])) < len(all_departments[:idx+1]):
                raise ValidationError(
                    'This department has been listed more than once: %(department)s',
                    code='invalid',
                    params={'department': department.display},
                )

    class Meta:
        model = Evaluation
        fields = ["status", "title"]
