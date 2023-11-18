from django.contrib import admin
from django.urls import include, path

from evaluation_registry.evaluations import info_views, views

info_urlpatterns = [
    path("privacy-notice/", info_views.privacy_notice_view, name="privacy-notice"),
    path("accessibility-statement/", info_views.accessibility_statement_view, name="accessibility-statement"),
]

other_urlpatterns = [
    path("", views.evaluation_list_view, name="index"),
    path("health/", include("health_check.urls")),
    path("home/", views.homepage_view, name="homepage"),
    path("admin/", admin.site.urls),
    path("evaluation/<uuid:uuid>/", views.evaluation_detail_view, name="evaluation-detail"),
    path("evaluation/<uuid:uuid>/update-type/", views.evaluation_update_type_view, name="evaluation-update-type"),
    path("evaluation/create", views.start_form_view, name="start-form"),
    path("evaluation/create/<str:status>", views.evaluation_create_view, name="evaluation-create"),
    path("accounts/", include("allauth.urls")),
]

urlpatterns = info_urlpatterns + other_urlpatterns
