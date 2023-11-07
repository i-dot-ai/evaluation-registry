import logging

from django.contrib.auth import get_user_model, login, logout
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.views.decorators.http import require_http_methods

from evaluation_registry.evaluations import email_handler, models
from evaluation_registry.evaluations.forms import EmailForm

logger = logging.getLogger(__name__)

UserModel = get_user_model()


def _strip_microseconds(dt):
    if not dt:
        return None
    return dt.replace(microsecond=0, tzinfo=None)


class CustomLoginView(View):
    template_name = "login.html"
    error_message = "Something has gone wrong.  Please try again."

    def get(self, request):
        if request.user.is_authenticated:
            return redirect(reverse("index"))
        form = EmailForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = EmailForm(request.POST)
        if form.is_valid():
            try:
                user = UserModel.objects.get(email=form.cleaned_data["email"])
                email_handler.send_verification_email(user)
            except UserModel.DoesNotExist:
                user = UserModel.objects.create_user(email=form.cleaned_data["email"])
                email_handler.send_register_email(user)
            return redirect(reverse("email-sent"))
        else:
            return render(request, "login.html", {"form": form})


def email_sent_view(request):
    return render(request, "email-sent.html")


def register_email_view(request):
    return verify_email_view(request, register=True)


@require_http_methods(["GET"])
def verify_email_view(request, register=False):
    if request.user.is_authenticated:
        logout(request)
    user_id = request.GET.get("user_id")
    token = request.GET.get("code")
    if not models.User.objects.filter(pk=user_id).exists():
        return render(request, "login-failure.html")
    verify_result = email_handler.verify_token(user_id, token, "email-verification")

    if not verify_result:
        return render(request, "login-failure.html")
    else:
        user = models.User.objects.get(pk=user_id)
        if not user.verified:
            user.verified = True
            user.save()
        login(request, user)
        return redirect(reverse("post-login"))


def post_login_view(request):
    return redirect(reverse("index"))


class LogoutView(View):
    template_name = "logout.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        logout(request)
        return redirect("login")
