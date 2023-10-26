from django.contrib import admin

from . import models

admin_site = admin.AdminSite()


class EventDateAdmin(admin.ModelAdmin):
    list_display = ["__str__", "category", "status", "evaluation"]
    list_filter = ["category", "status"]


class EvaluationAdmin(admin.ModelAdmin):
    list_display = ["title", "visibility"]
    list_filter = ["visibility"]


admin.site.register(models.EventDate, EventDateAdmin)
admin.site.register(models.Evaluation, EvaluationAdmin)
admin.site.register(models.User)
