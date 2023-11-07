from django.contrib import admin
from django.urls import include, path

from evaluation_registry.evaluations import info_views, views
from evaluation_registry.evaluations.views import send_login_link

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
    path("accounts/", include("allauth.urls")),
    path("login/", views.send_login_link, name="login"),
    path("verify-login-link/", views.verify_login_link, name="verify_login_link"),
]

urlpatterns = info_urlpatterns + other_urlpatterns
