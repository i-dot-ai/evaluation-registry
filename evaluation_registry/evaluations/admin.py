import csv
import datetime

from django.contrib import admin
from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    SearchVector,
)
from simple_history.admin import SimpleHistoryAdmin

from . import models
from .management.commands import load_rsm_csv
from .models import (
    Evaluation,
    EvaluationDepartmentAssociation,
    EvaluationDesignTypeDetail,
    EventDate,
    Report,
)

admin_site = admin.AdminSite()


def import_csv(modeladmin, request, queryset):
    if queryset.count() > 1:
        modeladmin.message_user(request, "Please select exactly one file to import.", level="ERROR")
        return

    file = queryset.first()
    records = list(csv.DictReader(file))
    cmd = load_rsm_csv.Command()
    cmd.process_tabular_data(records)
    file.last_successfully_loaded_at = datetime.datetime.now()
    file.save()


import_csv.short_description = "Import selected CSV file"  # type: ignore


class RSMFileAdmin(admin.ModelAdmin):
    actions = [import_csv]
    list_display = ["id", "csv", "last_successfully_loaded_at"]
    readonly_fields = ["last_successfully_loaded_at"]


class EventDateInline(admin.TabularInline):
    model = EventDate
    extra = 0


class EvaluationDepartmentAssociationInline(admin.TabularInline):
    model = EvaluationDepartmentAssociation
    extra = 0


class ReportInline(admin.TabularInline):
    model = Report
    extra = 0


class EvaluationDesignTypeDetailInline(admin.TabularInline):
    model = EvaluationDesignTypeDetail
    extra = 0


class EvaluationAdmin(SimpleHistoryAdmin):
    list_display = ["rsm_evaluation_id", "title", "lead_department", "visibility"]
    list_filter = ["visibility", "evaluation_design_types__display"]
    search_fields = ("title", "brief_description")
    inlines = [ReportInline, EventDateInline, EvaluationDepartmentAssociationInline, EvaluationDesignTypeDetailInline]

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


class EvaluationDesignTypeAdmin(admin.ModelAdmin):
    list_display = ["code", "display", "parent", "collect_description"]
    list_filter = ["parent"]


class TaxonomyAdmin(admin.ModelAdmin):
    list_display = ["code", "display", "parent"]
    list_filter = ["parent"]


admin.site.register(models.Evaluation, EvaluationAdmin)
admin.site.register(models.Department, DepartmentAdmin)
admin.site.register(models.EvaluationDesignType, EvaluationDesignTypeAdmin)
admin.site.register(models.RSMFile, RSMFileAdmin)
admin.site.register(models.Taxonomy, TaxonomyAdmin)
admin.site.register(models.User)
