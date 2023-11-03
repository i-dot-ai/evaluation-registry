from django.contrib import admin
from django.urls import include, path

from evaluation_registry.evaluations import info_views, views, authentication_views, decorators

info_urlpatterns = [
    path("privacy-notice/", info_views.privacy_notice_view, name="privacy-notice"),
    path("accessibility-statement/", info_views.accessibility_statement_view, name="accessibility-statement"),
]

other_urlpatterns = [
    path("", authentication_views.CustomLoginView.as_view(), name="index"),
    path("unauthorised/", decorators.unauthorised_view, name="unauthorised"),
    path("evaluations/", views.evaluation_list_view, name="list-evaluations"),
    path("health/", include("health_check.urls")),
    path("home/", views.homepage_view, name="homepage"),
    path("admin/", admin.site.urls),
    path("evaluation/<uuid:uuid>/", views.evaluation_detail_view, name="evaluation-detail"),
    path("logout/", authentication_views.LogoutView.as_view(), name="logout"),
    path("email-sent/", authentication_views.email_sent_view, name="email-sent"),
    path("post-login/", authentication_views.post_login_view, name="post-login"),
    path("verify-register/", authentication_views.register_email_view, name="verify-email-register"),
    path("verify/", authentication_views.verify_email_view, name="verify-email"),
]

urlpatterns = info_urlpatterns + other_urlpatterns
