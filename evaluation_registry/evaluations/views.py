from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    SearchVector,
)
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import QuerySet
from django.forms import modelform_factory, modelformset_factory
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from evaluation_registry.evaluations.forms import (
    EvaluationDesignTypeDetailForm,
    EvaluationShareForm,
    EventDateForm,
)
from evaluation_registry.evaluations.models import (
    Department,
    Evaluation,
    EvaluationDesignType,
    EvaluationDesignTypeDetail,
    EventDate,
    Taxonomy,
    User,
)


def check_evaluation_and_user(request, uuid):
    evaluation = get_object_or_404(Evaluation, id=uuid)
    if evaluation.created_by != request.user:
        raise PermissionDenied("You do not have permission to edit this evaluation")
    return evaluation


@require_http_methods(["GET"])
def login_to_cola_view(request):
    if request.user.id:
        return redirect(reverse("homepage"))
    cola_url = settings.COLA_LOGIN_URL
    return render(request, "auth/login.html", {"cola_url": cola_url})


@require_http_methods(["GET"])
@login_required
def homepage_view(request):
    return render(
        request,
        template_name="homepage.html",
        context={"request": request},
    )


def authorised_base_evaluation_queryset(show_public: bool, show_user: bool, user: User) -> QuerySet:
    if show_public:
        if show_user:
            return Evaluation.objects.filter(visibility=Evaluation.Visibility.PUBLIC) | Evaluation.objects.filter(
                created_by=user
            )
        return Evaluation.objects.filter(visibility=Evaluation.Visibility.PUBLIC)
    if show_user:
        return Evaluation.objects.filter(created_by=user)
    return Evaluation.objects.none()


def full_text_search(base_queryset: QuerySet, search_term: str) -> QuerySet:
    """search title and brief-description using PG full-text-search"""
    if not search_term:
        return base_queryset

    search_title = SearchVector("title", weight="A")
    description_search = SearchVector("brief_description", weight="B")
    search_vector = search_title + description_search
    search_query = SearchQuery(search_term)
    evaluation_list = (
        base_queryset.annotate(
            search=search_vector,
            rank=SearchRank(search_vector, search_query),
        )
        .filter(search=search_query)
        .order_by("-rank")
    )

    return evaluation_list


def filter_by_department_and_types(evaluations: QuerySet, departments: list[str], types: list[str]) -> QuerySet:
    """filter query set on department-codes and evaluation-types"""

    if departments:
        evaluations = evaluations.filter(departments__code__in=departments)

    if types:
        evaluations = evaluations.filter(evaluation_design_types__code__in=types)

    return evaluations.distinct()


@require_http_methods(["GET"])
def evaluation_list_view(request):
    search_term = request.GET.get("search_term")
    selected_departments = request.GET.getlist("departments")
    selected_types = request.GET.getlist("evaluation_types")
    evaluations_to_show = request.GET.getlist("evaluations_to_show")

    if request.user.is_authenticated:
        base_evaluation_queryset = authorised_base_evaluation_queryset(
            show_public=("public" in evaluations_to_show), show_user=("user" in evaluations_to_show), user=request.user
        )
    else:
        base_evaluation_queryset = Evaluation.objects.filter(visibility=Evaluation.Visibility.PUBLIC)

    evaluation_list = filter_by_department_and_types(
        full_text_search(base_evaluation_queryset, search_term),
        selected_departments,
        selected_types,
    )

    search_choices = {
        "departments": Department.objects.filter(code__in=selected_departments).all(),
        "evaluation_types": [
            (e.code, e.display) for e in EvaluationDesignType.root_objects.filter(code__in=selected_types)
        ],
    }

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
            "search_term": search_term if search_term else "",
            "departments": Department.objects.all(),
            "evaluation_types": EvaluationDesignType.root_objects.all(),
            "selected_departments": selected_departments,
            "selected_types": selected_types,
            "search_choices": search_choices,
            "is_authenticated": request.user.is_authenticated,
            "evaluations_to_show": evaluations_to_show,
        },
    )


@require_http_methods(["GET"])
def evaluation_detail_view(request, uuid):
    evaluation = get_object_or_404(Evaluation, id=uuid)

    dates = evaluation.event_dates.all()
    return render(request, "evaluation_detail.html", {"evaluation": evaluation, "dates": dates})


def update_evaluation_design_objects(existing_objects, existing_design_types, form):
    should_update_text = "text" in form.changed_data
    to_add = set(form.cleaned_data["design_types"]).difference(existing_design_types)
    for design_type in to_add:
        EvaluationDesignTypeDetail.objects.create(
            evaluation=form.cleaned_data["evaluation"],
            design_type=design_type,
            text=form.cleaned_data["text"] if design_type.collect_description else None,
        )
        if design_type.collect_description:
            should_update_text = False  # text has been updated by creating this new object

    to_remove = set(existing_design_types).difference(form.cleaned_data["design_types"])
    for design_type in to_remove:
        existing_objects.filter(design_type=design_type).delete()

    if should_update_text:  # handles the case where the 'Other' text has been updated
        existing_objects.filter(design_type__collect_description=True).update(text=form.cleaned_data["text"])


def evaluation_type_view(request, evaluation, parent=None, next_page=None):
    if parent:
        parent_object = EvaluationDesignType.objects.get(code=parent)
        options = EvaluationDesignType.objects.filter(parent__code=parent)
        if not options.exists():
            raise Http404(
                "No %(verbose_name)s found matching the query"
                % {"verbose_name": EvaluationDesignType._meta.verbose_name}
            )
    else:
        options = EvaluationDesignType.root_objects.all()
        parent_object = None
    options = list(options)
    if any(option.display.lower() == "other" for option in options):
        other_option = next(option for option in options if option.display.lower() == "other")
        options.append(options.pop(options.index(other_option)))
    data = {"evaluation": evaluation, "design_types": [], "design_types_codes": [], "text": ""}
    existing_links = EvaluationDesignTypeDetail.objects.filter(evaluation=evaluation, design_type__in=options)

    for existing_link in existing_links:
        data["design_types"].append(existing_link.design_type)
        data["design_types_codes"].append(existing_link.design_type.code)
        if existing_link.design_type.collect_description and existing_link.text:
            data["text"] = existing_link.text

    errors = {}

    if request.method == "POST":
        form = EvaluationDesignTypeDetailForm(request.POST, initial=data)

        if not parent and not form["design_types"].value():
            form.add_error("design_types", "Please select at least one evaluation type")

        if form.is_valid():
            if form.has_changed():
                update_evaluation_design_objects(
                    existing_objects=existing_links,
                    existing_design_types=data["design_types"],
                    form=form,
                )

            if next_page:
                return redirect("share", uuid=form.cleaned_data["evaluation"].id, page_number=next_page)

            return redirect("evaluation-detail", uuid=form.cleaned_data["evaluation"].id)

        else:
            errors = form.errors.as_data().values()

            data["design_types_codes"] = request.POST.get("design_types") or []
            data["text"] = request.POST.get("text") or ""

    else:
        form = EvaluationDesignTypeDetailForm()

    return render(
        request,
        "share-form/evaluation-update-type.html",
        {
            "evaluation": evaluation,
            "options": options,
            "errors": errors,
            "data": data,
            "parent": parent_object,
        },
    )


@require_http_methods(["GET", "POST"])
@login_required
def evaluation_update_type_view(request, uuid, parent=None):
    evaluation = check_evaluation_and_user(request, uuid)

    return evaluation_type_view(request, evaluation, parent=parent)


def evaluation_description_view(request, evaluation, next_page=None):
    errors = {}
    form_fields = [
        "brief_description",
        "grant_number",
        "has_grant_number",
        "major_project_number",
        "has_major_project_number",
    ]
    EvaluationForm = modelform_factory(Evaluation, fields=form_fields)  # noqa: N806

    if request.method == "POST":
        form = EvaluationForm(request.POST, instance=evaluation)

        if form.is_valid():
            for field in form_fields:
                setattr(evaluation, field, form.cleaned_data[field])
            evaluation.save(update_fields=form_fields)

            if next_page:
                return redirect("share", uuid=evaluation.id, page_number=next_page)
            return redirect("evaluation-detail", uuid=evaluation.id)

        else:
            errors = form.errors.as_data()

    else:
        form = EvaluationForm(instance=evaluation)

    return render(
        request,
        "share-form/evaluation-description.html",
        {
            "evaluation": evaluation,
            "form": form,
            "errors": errors,
        },
    )


@require_http_methods(["GET", "POST"])
@login_required
def evaluation_update_view(request, uuid):
    evaluation = check_evaluation_and_user(request, uuid)

    return evaluation_description_view(request, evaluation)


def evaluation_dates_view(request, evaluation, next_page=None):
    form_fields = ["evaluation", "month", "year", "other_description", "category"]
    existing_date_count = EventDate.objects.filter(evaluation=evaluation).count()
    other_errors = {}

    DateFormset = modelformset_factory(  # noqa: N806
        EventDate,
        form=EventDateForm,
        fields=form_fields,
        extra=1 if existing_date_count else 3,
    )

    initial_formset_data = (
        [
            {"evaluation": evaluation, "category": EventDate.Category.EVALUATION_START},
            {"evaluation": evaluation, "category": EventDate.Category.EVALUATION_END},
            {"evaluation": evaluation, "category": EventDate.Category.PUBLICATION_FINAL_RESULTS},
        ]
        if not existing_date_count
        else None
    )

    if request.method == "POST":
        formset = DateFormset(
            request.POST, queryset=EventDate.objects.filter(evaluation=evaluation), initial=initial_formset_data
        )

        for form in formset:
            form.initial["evaluation"] = evaluation  # required so the blank form is ignored if unchanged

        if formset.is_valid():
            formset.save()

            new_date_requested = request.POST.get("addanother") == "date"
            formset_changed = any(form.has_changed() for form in formset)

            if new_date_requested:
                if formset_changed:
                    if next_page:
                        return redirect("share", uuid=evaluation.id, page_number=(next_page - 1))
                    return redirect("evaluation-update-dates", uuid=evaluation.id)
                other_errors = ["Please add information for one date before selecting 'Save and add another'"]

            else:
                if next_page:
                    return redirect("share", uuid=evaluation.id, page_number=next_page)
                return redirect("evaluation-detail", uuid=evaluation.id)

    else:
        formset = DateFormset(queryset=EventDate.objects.filter(evaluation=evaluation), initial=initial_formset_data)

    return render(
        request,
        "share-form/evaluation-dates.html",
        {
            "evaluation": evaluation,
            "formset": formset,
            "errors": {"formset": formset.errors, "other": other_errors},
            "categories": EventDate.Category,
            "existing_date_count": existing_date_count,
        },
    )


@require_http_methods(["GET", "POST"])
@login_required
def evaluation_update_dates_view(request, uuid):
    evaluation = check_evaluation_and_user(request, uuid)

    return evaluation_dates_view(request, evaluation)


def evaluation_links_view(request, evaluation, next_page=None):
    errors = {}
    if request.method == "POST":
        instance = evaluation
        form_data = request.POST.dict()
        form_data["reasons_unpublished"] = request.POST.getlist("reasons_unpublished[]")
        form = EvaluationShareForm(form_data)
        data = {}
        if form.is_valid():
            if form.has_changed():
                if form.cleaned_data["is_final_report_published"]:
                    instance.plan_link = form.cleaned_data["plan_link"]
                    instance.link_to_published_evaluation = form.cleaned_data["link_to_published_evaluation"]
                else:
                    instance.reasons_unpublished = list(form.cleaned_data["reasons_unpublished"])
                    instance.reasons_unpublished_details = form.cleaned_data["reasons_unpublished_details"]
                instance.is_final_report_published = form.cleaned_data["is_final_report_published"]
                instance.save()

            if next_page:
                return redirect("share", uuid=evaluation.id, page_number=next_page)
            return redirect("evaluation-detail", uuid=evaluation.id)

        else:
            errors = form.errors.as_data()

            data["is_final_report_published"] = request.POST.get("is_final_report_published") or None
            data["link_to_published_evaluation"] = request.POST.get("link_to_published_evaluation") or None
            data["plan_link"] = request.POST.get("plan_link") or None
            data["reasons_unpublished"] = request.POST.get("reasons_unpublished") or []
        return render(
            request,
            "share-form/share-evaluation.html",
            {
                "errors": errors,
                "data": data,
                "options": Evaluation.UnpublishedReason.choices,
            },
        )
    else:
        return render(
            request,
            "share-form/share-evaluation.html",
            {
                "errors": errors,
                "options": Evaluation.UnpublishedReason.choices,
            },
        )


@require_http_methods(["GET", "POST"])
@login_required
def evaluation_update_links_view(request, uuid):
    evaluation = check_evaluation_and_user(request, uuid)

    return evaluation_links_view(request, evaluation)


def evaluation_policies_view(request, evaluation, next_page=None):
    EvaluationForm = modelform_factory(Evaluation, fields=["policies"])  # noqa: N806
    EvaluationForm.base_fields["policies"].to_field_name = "code"
    policies = Taxonomy.objects.order_by("code")

    selected_policies = list(map(lambda p: p.code, evaluation.policies.all()))

    if request.method == "POST":
        form = EvaluationForm(request.POST, instance=evaluation)

        if form.is_valid():
            form.save()

            if next_page:
                return redirect("share", uuid=evaluation.id, page_number=next_page)
            return redirect("evaluation-detail", uuid=evaluation.id)

        else:
            errors = form.errors.as_data()
            selected_policies = request.POST.getlist("selected_policies")

    else:
        form = EvaluationForm(instance=evaluation)
        errors = {}

    return render(
        request,
        "share-form/evaluation-policies.html",
        {
            "evaluation": evaluation,
            "form": form,
            "errors": errors,
            "policies": policies,
            "selected_policies": selected_policies,
        },
    )


@require_http_methods(["GET", "POST"])
@login_required
def evaluation_update_policies_view(request, uuid):
    evaluation = check_evaluation_and_user(request, uuid)

    return evaluation_policies_view(request, evaluation)
