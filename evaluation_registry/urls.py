from django.contrib import admin
from django.urls import include, path

from evaluation_registry.evaluations import info_views, views

info_urlpatterns = [
    path("privacy-notice/", info_views.privacy_notice_view, name="privacy-notice"),
    path("accessibility-statement/", info_views.accessibility_statement_view, name="accessibility-statement"),
    path("support/", info_views.support_view, name="support"),
]

other_urlpatterns = [
    path("", views.index_view, name="index"),
    path("home/", views.homepage_view, name="homepage"),
    path("admin/", admin.site.urls),
    path("search/", views.evaluation_list_view, name="search"),
    path("evaluation/<uuid:uuid>/", views.evaluation_detail_view, name="evaluation-detail"),
    path("accounts/", include("allauth.urls")),
]

urlpatterns = info_urlpatterns + other_urlpatterns
