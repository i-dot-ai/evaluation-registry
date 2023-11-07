from django.contrib import admin
from django.urls import include, path

from evaluation_registry.evaluations import (
    authentication_views,
    decorators,
    info_views,
    views,
)
from evaluation_registry.evaluations.decorators import login_required

info_urlpatterns = [
    path("privacy-notice/", info_views.privacy_notice_view, name="privacy-notice"),
    path("accessibility-statement/", info_views.accessibility_statement_view, name="accessibility-statement"),
]

other_urlpatterns = [
    path("", views.homepage_view, name="index"),
    path("login", authentication_views.CustomLoginView.as_view(), name="login"),
    path("unauthorised/", decorators.unauthorised_view, name="unauthorised"),
    path("evaluations/", views.evaluation_list_view, name="list-evaluations"),
    path("health/", include("health_check.urls")),
    path("admin/", admin.site.urls),
    path("evaluation/<uuid:uuid>/", views.evaluation_detail_view, name="evaluation-detail"),
    path("logout/", login_required(authentication_views.LogoutView.as_view()), name="logout"),
    path("email-sent/", authentication_views.email_sent_view, name="email-sent"),
    path("post-login/", authentication_views.post_login_view, name="post-login"),
    path("verify-register/", authentication_views.register_email_view, name="verify-email-register"),
    path("verify/", authentication_views.verify_email_view, name="verify-email"),
]

urlpatterns = info_urlpatterns + other_urlpatterns
