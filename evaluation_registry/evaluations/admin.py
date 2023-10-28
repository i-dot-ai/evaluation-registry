from django.contrib import admin
from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    SearchVector,
)

from . import models
from .models import Evaluation, EvaluationDepartmentAssociation

admin_site = admin.AdminSite()


class EventDateAdmin(admin.ModelAdmin):
    list_display = ["__str__", "category", "status", "evaluation"]
    list_filter = ["category", "status", "year"]


class EvaluationDepartmentAssociationInline(admin.TabularInline):
    model = EvaluationDepartmentAssociation
    extra = 1


class EvaluationAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "lead_department",
        "visibility",
        "is_process_type",
        "is_impact_type",
        "is_economic_type",
        "is_other_type",
    ]
    list_filter = ["visibility", "is_process_type", "is_impact_type", "is_economic_type", "is_other_type"]
    search_fields = ("title", "brief_description")
    inlines = [EvaluationDepartmentAssociationInline]

    def get_search_results(self, request, queryset, search_term):
        if not search_term:
            return super().get_search_results(request, queryset, search_term)

        search_title = SearchVector("title", weight="A")
        description_search = SearchVector("brief_description", weight="B")
        search_vector = search_title + description_search

        search_query = SearchQuery(search_term)
        queryset = (
            Evaluation.objects.annotate(search=search_vector, rank=SearchRank(search_vector, search_query))
            .filter(search=search_query)
            .order_by("-rank")
        )
        return queryset, False


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ["code", "display"]


admin.site.register(models.EventDate, EventDateAdmin)
admin.site.register(models.Evaluation, EvaluationAdmin)
admin.site.register(models.Department, DepartmentAdmin)
admin.site.register(models.User)
