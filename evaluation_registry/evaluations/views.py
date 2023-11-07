from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.tokens import default_token_generator
from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    SearchVector,
)
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from django.views.generic import DetailView

from evaluation_registry.evaluations.forms import EmailForm
from evaluation_registry.evaluations.models import Department, Evaluation, User

UserModel = get_user_model()


class UUIDDetailView(DetailView):
    uuid_url_kwarg = "id"

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        uuid = self.kwargs.get(self.uuid_url_kwarg)
        if uuid is not None:
            queryset = queryset.filter(id=uuid)

        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(
                "No %(verbose_name)s found matching the query" % {"verbose_name": queryset.model._meta.verbose_name}
            )
        return obj


@require_http_methods(["GET"])
def index_view(request):
    return render(
        request,
        template_name="index.html",
        context={"request": request},
    )


@require_http_methods(["GET"])
def homepage_view(request):
    return render(
        request,
        template_name="homepage.html",
        context={"request": request},
    )


@require_http_methods(["GET"])
def evaluation_list_view(request):
    search_term = request.GET.get("search_term") or ""
    selected_departments = request.GET.getlist("departments")
    selected_types = request.GET.getlist("evaluation_types")

    # TODO: include evaluation visibility for version for CS
    search_choices = {}
    search_choices["departments"] = Department.objects.filter(code__in=selected_departments).all()
    search_choices["evaluation_types"] = list(
        filter(lambda x: x[0] in selected_types, Evaluation.EvaluationType.choices)
    )

    department_query = Q()
    if selected_departments:
        department_query = Q(departments__in=search_choices["departments"])

    type_query = Q()
    if Evaluation.EvaluationType.PROCESS in selected_types:
        type_query |= Q(is_process_type=True)
    if Evaluation.EvaluationType.IMPACT in selected_types:
        type_query |= Q(is_impact_type=True)
    if Evaluation.EvaluationType.ECONOMIC in selected_types:
        type_query |= Q(is_economic_type=True)
    if Evaluation.EvaluationType.OTHER in selected_types:
        type_query |= Q(is_other_type=True)

    if search_term:
        search_title = SearchVector("title", weight="A")
        description_search = SearchVector("brief_description", weight="B")
        search_vector = search_title + description_search
        search_query = SearchQuery(search_term)
        evaluation_list = (
            Evaluation.objects.annotate(search=search_vector, rank=SearchRank(search_vector, search_query))
            .filter(Q(search=search_query) & department_query & type_query)
            .order_by("-rank")
        )
    else:
        evaluation_list = Evaluation.objects.filter(department_query & type_query)

    paginator = Paginator(evaluation_list, 25)
    page_number = request.GET.get("page") or 1
    page_obj = paginator.get_page(page_number)
    pages_list = paginator.get_elided_page_range(page_number, on_each_side=1, on_ends=1)
    return render(
        request,
        "evaluation_list.html",
        {
            "evaluations": evaluation_list,
            "page_obj": page_obj,
            "pages_list": pages_list,
            "search_term": search_term,
            "departments": Department.objects.all(),
            "evaluation_types": Evaluation.EvaluationType.choices,
            "selected_departments": selected_departments,
            "selected_types": selected_types,
            "search_choices": search_choices,
        },
    )


@require_http_methods(["GET"])
def evaluation_detail_view(request, uuid):
    try:
        evaluation = Evaluation.objects.get(id=uuid)
    except Evaluation.DoesNotExist:
        raise Http404("No %(verbose_name)s found matching the query" % {"verbose_name": Evaluation._meta.verbose_name})

    dates = evaluation.event_dates.all()
    return render(request, "evaluation_detail.html", {"evaluation": evaluation, "dates": dates})


@require_http_methods(["GET", "POST"])
def send_login_link(request):
    if request.method == "POST":
        form = EmailForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.get(email=form.cleaned_data["email"])
            except User.DoesNotExist:
                user = User.objects.create_user(email=form.cleaned_data["email"])

            # Generate a unique token and create a LoginToken object
            login_token = default_token_generator.make_token(user)

            # Send the login link to the user's email
            login_url = request.build_absolute_uri(f"/verify-login-link/?token={login_token}&email={user.email}")
            send_mail(
                "Login Link",
                f"Click the following link to log in: {login_url}",
                "from@example.com",
                [user.email],
                fail_silently=False,
            )
            # redirect to success
            return render(request, "email_sent.html")
        else:
            return render(request, "login.html", {"form": form})

    form = EmailForm()
    return render(request, "login.html", {"form": form})


@require_http_methods(["GET"])
def verify_login_link(request):
    token = request.GET.get("token")
    email = request.GET.get("email")

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        messages.warning(request, "User not found, please try again.")
        return redirect("login")

    if default_token_generator.check_token(user, token):
        login(request, user)
        return redirect(settings.LOGIN_REDIRECT_URL)

    messages.warning(request, "Invalid token, please try again.")
    return redirect("login")
