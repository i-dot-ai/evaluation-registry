from automatilib.cola.urls import url_patterns as cola_url_patterns
from django.contrib import admin
from django.urls import include, path

from evaluation_registry.evaluations import info_views, share_views, views

info_urlpatterns = [
    path("privacy-notice/", info_views.privacy_notice_view, name="privacy-notice"),
    path("accessibility-statement/", info_views.accessibility_statement_view, name="accessibility-statement"),
    path("faq/", info_views.faq_view, name="faq"),
]

share_urlpatterns = [
    path("evaluation/<uuid:uuid>/", views.evaluation_detail_view, name="evaluation-detail"),
    path("evaluation/<uuid:uuid>/update-type/", views.evaluation_update_type_view, name="evaluation-update-type"),
    path(
        "evaluation/<uuid:uuid>/update-type/<str:parent>",
        views.evaluation_update_type_view,
        name="evaluation-update-type-child",
    ),
    path("evaluation/<uuid:uuid>/update-description/", views.evaluation_update_view, name="evaluation-update"),
    path("evaluation/<uuid:uuid>/update-dates/", views.evaluation_update_dates_view, name="evaluation-update-dates"),
    path("evaluation/<uuid:uuid>/update-links/", views.evaluation_update_links_view, name="evaluation-share"),
    path("evaluation/<uuid:uuid>/update-policies/", views.evaluation_update_policies_view, name="evaluation-policies"),
    path("evaluation/<uuid:uuid>/update-cost/", views.evaluation_update_cost_view, name="evaluation-cost"),
    path(
        "evaluation/<uuid:uuid>/update-title-departments/",
        views.evaluation_update_title_department_view,
        name="evaluation-title-departments",
    ),
    path("evaluation/create", share_views.create_view, name="create"),
    path("evaluation/create/<int:page_number>/", share_views.create_view, name="create"),
    path("evaluation/create/<int:page_number>/<str:status>", share_views.create_view, name="create"),
    path("evaluation/<uuid:uuid>/share/<int:page_number>/", share_views.share_view, name="share"),
]

other_urlpatterns = [
    path("", views.homepage_view, name="homepage"),
    path("health/", include("health_check.urls")),
    path("login/", views.login_to_cola_view, name="login"),
    path("search/", views.evaluation_list_view, name="search"),
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
]

development_urlpatterns = [path("__debug__/", include("debug_toolbar.urls"))]

urlpatterns = info_urlpatterns + share_urlpatterns + other_urlpatterns + cola_url_patterns + development_urlpatterns
