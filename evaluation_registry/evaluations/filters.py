import django_filters

from evaluation_registry.evaluations.models import Department, Evaluation


class EvaluationFilter(django_filters.FilterSet):
    departments = django_filters.ModelMultipleChoiceFilter(
        field_name="departments__code",
        to_field_name="code",
        queryset=Department.objects.all(),
    )

    class Meta:
        model = Evaluation
        fields = ["departments"]
