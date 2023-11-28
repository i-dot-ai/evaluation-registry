from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    SearchVector,
)
from django.core.paginator import Paginator
from django.db.models import QuerySet
from django.forms import modelform_factory, modelformset_factory
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from evaluation_registry.evaluations.forms import (
    EvaluationDesignTypeDetailForm,
    EventDateForm,
)
from evaluation_registry.evaluations.models import (
    Department,
    Evaluation,
    EvaluationDesignType,
    EvaluationDesignTypeDetail,
    EventDate,
)


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


def full_text_search(search_term: str) -> QuerySet:
    """search title and brief-description using PG full-text-search"""
    if not search_term:
        return Evaluation.objects.all()

    search_title = SearchVector("title", weight="A")
    description_search = SearchVector("brief_description", weight="B")
    search_vector = search_title + description_search
    search_query = SearchQuery(search_term)
    evaluation_list = (
        Evaluation.objects.annotate(
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

    evaluation_list = filter_by_department_and_types(
        full_text_search(search_term),
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
def evaluation_update_type_view(request, uuid, parent=None):
    try:
        evaluation = Evaluation.objects.get(id=uuid)
    except Evaluation.DoesNotExist:
        raise Http404("No %(verbose_name)s found matching the query" % {"verbose_name": Evaluation._meta.verbose_name})

    return evaluation_type_view(request, evaluation, parent=parent)


def evaluation_update_description(request, evaluation, next_page=None):
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
def evaluation_update_view(request, uuid):
    try:
        evaluation = Evaluation.objects.get(id=uuid)
    except Evaluation.DoesNotExist:
        raise Http404("No %(verbose_name)s found matching the query" % {"verbose_name": Evaluation._meta.verbose_name})

    return evaluation_update_description(request, evaluation)


@require_http_methods(["GET", "POST"])
def evaluation_update_dates_view(request, uuid):
    try:
        evaluation = Evaluation.objects.get(id=uuid)
    except Evaluation.DoesNotExist:
        raise Http404("No %(verbose_name)s found matching the query" % {"verbose_name": Evaluation._meta.verbose_name})

    form_fields = ["evaluation", "month", "year", "other_description", "category"]
    existing_date_count = EventDate.objects.filter(evaluation=evaluation).count()
    DateFormset = modelformset_factory(  # noqa: N806
        EventDate,
        form=EventDateForm,
        fields=form_fields,
        extra=1 if existing_date_count else 3,
    )

    if request.method == "POST":
        formset = DateFormset(request.POST, queryset=EventDate.objects.filter(evaluation=evaluation))

        for form in formset:
            form.initial["evaluation"] = evaluation  # required so the blank form is ignored if unchanged

        if formset.is_valid():
            formset.save()

            if request.POST.get("addanother"):
                return redirect("evaluation-update-dates", uuid=evaluation.id)

            return redirect("evaluation-detail", uuid=evaluation.id)  # TODO: redirect to next page of form

    else:
        formset = DateFormset(queryset=EventDate.objects.filter(evaluation=evaluation))

    return render(
        request,
        "share-form/evaluation-dates.html",
        {
            "evaluation": evaluation,
            "formset": formset,
            "errors": formset.errors,
            "categories": EventDate.Category,
            "existing_date_count": existing_date_count,
        },
    )
