from django.contrib import admin

from . import models

admin_site = admin.AdminSite()


class EventDateAdmin(admin.ModelAdmin):
    list_display = ["__str__", "category", "status", "evaluation"]
    list_filter = ["category", "status"]


class EvaluationAdmin(admin.ModelAdmin):
    list_display = ["title", "lead_department", "visibility"]
    list_filter = ["lead_department", "visibility"]


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ["code", "display"]


admin.site.register(models.EventDate, EventDateAdmin)
admin.site.register(models.Evaluation, EvaluationAdmin)
admin.site.register(models.Department, DepartmentAdmin)
admin.site.register(models.User)
