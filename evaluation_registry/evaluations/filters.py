import django_filters

from evaluation_registry.evaluations.models import Department, Evaluation
from django.db.models import Q


class EvaluationFilter(django_filters.FilterSet):
    departments = django_filters.ModelMultipleChoiceFilter(
        field_name="departments__code",
        to_field_name="code",
        queryset=Department.objects.all(),
    )

    class Meta:
        model = Evaluation
        fields = ['is_process_type', 'is_impact_type', 'is_economic_type', 'is_other_type', 'departments']

    @property
    def qs(self):
        if self.request is None:
            return super().qs

        qs = super().qs
        evaluation_types = self.request.getlist("evaluation_types")

        query = Q()
        if Evaluation.EvaluationType.PROCESS in evaluation_types:
            query |= Q(is_process_type=True)
        if Evaluation.EvaluationType.IMPACT in evaluation_types:
            query |= Q(is_impact_type=True)
        if Evaluation.EvaluationType.ECONOMIC in evaluation_types:
            query |= Q(is_economic_type=True)
        if Evaluation.EvaluationType.OTHER in evaluation_types:
            query |= Q(is_other_type=True)

        return qs.filter(query)
