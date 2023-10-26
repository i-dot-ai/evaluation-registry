from django.contrib import admin

from . import models

admin_site = admin.AdminSite()
admin.site.register(models.User)
