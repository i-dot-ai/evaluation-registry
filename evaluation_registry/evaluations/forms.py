from django.forms import (
    BooleanField,
    CharField,
    Form,
    ModelChoiceField,
    ModelForm,
    ModelMultipleChoiceField,
    MultipleChoiceField,
    URLField,
)

from evaluation_registry.evaluations import models
from evaluation_registry.evaluations.models import (
    Department,
    Evaluation,
    EvaluationDesignType,
    EventDate,
)


class NullableModelMultipleChoiceField(ModelMultipleChoiceField):
    # Because Django doesn't allow for an empty_label in multiple choice fields
    def clean(self, value):
        if value:
            value = [v for v in value if v != ""]
        return super().clean(value)


class NamedErrorsModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(NamedErrorsModelForm, self).__init__(*args, **kwargs)

        for field in self.fields.values():
            field.error_messages["required"] = f"{field.label} is required"


class EvaluationBasicDetailsForm(NamedErrorsModelForm):
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
        queryset=EvaluationDesignType.objects.all(), label="Evaluation type", to_field_name="code", required=False
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


class EvaluationShareForm(Form):
    is_final_report_published = BooleanField(label="Is final report published?", required=True)
    link_to_published_evaluation = URLField(max_length=1024, label="Link to published evaluation", required=False)
    plan_link = URLField(required=False)
    reasons_unpublished = MultipleChoiceField(choices=models.Evaluation.UnpublishedReason.choices, required=False)
    reasons_unpublished_details = CharField(
        label="Please specify additional details about the reasons this evaluation is unpublished",
        required=False,
        max_length=2096,
    )

    def __init__(self, *args, **kwargs):
        super(EvaluationShareForm, self).__init__(*args, **kwargs)

    def clean(self):
        super().clean()
        is_final_report_published = self.data.get("is_final_report_published")

        self.cleaned_data["is_final_report_published"] = is_final_report_published == "1"
        is_final_report_published = self.cleaned_data["is_final_report_published"]
        if is_final_report_published:
            link_to_published_evaluation = self.cleaned_data.get("link_to_published_evaluation")
            plan_link = self.cleaned_data.get("plan_link")
            if not (plan_link or link_to_published_evaluation):
                self.add_error("plan_link", "Please provide at least one link to an evaluation document")
                self.add_error(
                    "link_to_published_evaluation",
                    "Please provide at least one link to an evaluation document",
                )
        else:
            reasons_unpublished = self.cleaned_data.get("reasons_unpublished")
            if not reasons_unpublished:
                self.add_error("reasons_unpublished", "Please provide a reason this evaluation is unpublished")
                fields_that_requires_other_info = ["other", "quality"]
                if any(field in reasons_unpublished for field in fields_that_requires_other_info):
                    self.add_error(
                        "reasons_unpublished_details",
                        "Please enter details about the reasons this evaluation is unpublished",
                    )


class EventDateForm(NamedErrorsModelForm):
    def __init__(self, *args, **kwargs):
        super(EventDateForm, self).__init__(*args, **kwargs)
        self.fields["month"].error_messages["invalid_choice"] = "Please enter a month number from 1-12"

    def clean(self):
        super().clean()
        category = self.cleaned_data.get("category")
        other_description = self.cleaned_data.get("other_description")

        if (category == "other") and not other_description:
            self.add_error("other_description", "Please provide additional description for the 'Other' choice")

    class Meta:
        model = EventDate
        fields = ["evaluation", "category", "other_description", "month", "year"]


class EvaluationVisibilityForm(NamedErrorsModelForm):
    is_sharing_permission_obtained = BooleanField()

    def __init__(self, *args, **kwargs):
        super(EvaluationVisibilityForm, self).__init__(*args, **kwargs)
        self.fields["is_sharing_permission_obtained"].error_messages[
            "required"
        ] = "Please confirm that you have permission to share this data"

    def clean(self):
        super().clean()
        is_sharing_permission_obtained = self.data.get("is_sharing_permission_obtained")

        self.cleaned_data["is_sharing_permission_obtained"] = is_sharing_permission_obtained == "1"
        is_sharing_permission_obtained = self.cleaned_data["is_sharing_permission_obtained"]

    class Meta:
        model = Evaluation
        fields = ["is_sharing_permission_obtained"]
