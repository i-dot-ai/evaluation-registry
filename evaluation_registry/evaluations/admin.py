import json
from io import BytesIO

import pdfplumber
import requests
from django.conf import settings
from django.contrib import admin
from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    SearchVector,
)
from openai import OpenAI
from simple_history.admin import SimpleHistoryAdmin

from . import models
from .auto_fill import evaluation_initial_data_schema
from .models import (
    Department,
    Evaluation,
    EvaluationDepartmentAssociation,
    EvaluationDesignType,
    EvaluationDesignTypeDetail,
    EventDate,
    Report,
)

client = OpenAI(api_key="settings.OPENAI_KEY")

admin_site = admin.AdminSite()


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


@admin.action(description="Generate plain text")
def generate_plain_text(modeladmin, request, queryset):
    for item in queryset:
        response = requests.get(item.url)
        pdf_content = BytesIO(response.content)

        with pdfplumber.open(pdf_content) as pdf:
            item.plain_text = "".join(page.extract_text() for page in pdf.pages)

        item.save()


@admin.action(description="Generate AI data")
def generate_ai_data(modeladmin, request, queryset):
    prompt = {
        "name": "extract_evaluation_info",
        "description": "Extract evaluation information from the body of the input text",
        "type": "object",
        "parameters": evaluation_initial_data_schema,
    }

    for item in queryset:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": " ".join(item.plain_text.split(" ")[:2500])}],
            tools=[{"type": "function", "function": prompt}],
            tool_choice="auto",
        )

        item.ai_generated_data = json.loads(response.choices[0].message.tool_calls[0].function.arguments)
        item.save()


@admin.action(description="Clean AI data")
def clean_ai_data(modeladmin, request, queryset):
    for item in queryset:
        item.cleaned_data = dict(item.ai_generated_data)
        if lead_department := item.cleaned_data["lead_department"]:
            item.cleaned_data["lead_department"] = (
                Department.objects.annotate(search=SearchVector("code", "display"))
                .filter(search=lead_department)
                .first()
                .code
            )

        for i, evaluation_design_type in enumerate(item.cleaned_data["evaluation_design_types"]):
            item.cleaned_data["evaluation_design_types"][i] = (
                EvaluationDesignType.objects.annotate(search=SearchVector("code", "display"))
                .filter(search=evaluation_design_type)
                .first()
                .code
            )

        item.save()


class AutoGeneratedEvaluationAdmin(admin.ModelAdmin):
    actions = [generate_plain_text, generate_ai_data, clean_ai_data]


admin.site.register(models.Evaluation, EvaluationAdmin)
admin.site.register(models.Department, DepartmentAdmin)
admin.site.register(models.EvaluationDesignType, EvaluationDesignTypeAdmin)
admin.site.register(models.AutoGeneratedEvaluation, AutoGeneratedEvaluationAdmin)
admin.site.register(models.User)
