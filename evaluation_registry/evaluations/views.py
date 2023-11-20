from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    SearchVector,
)
from django.core.paginator import Paginator
from django.db.models import QuerySet
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from evaluation_registry.evaluations.forms import (
    EvaluationCreateForm,
    EvaluationDesignTypeDetailForm,
)
from evaluation_registry.evaluations.models import (
    Department,
    Evaluation,
    EvaluationDepartmentAssociation,
    EvaluationDesignType,
    EvaluationDesignTypeDetail,
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


@require_http_methods(["GET", "POST"])
def start_form_view(request):
    options = Evaluation.Status.choices
    if request.method == "GET":
        return render(request, "share-form/evaluation-status.html", {"options": options, "error": False})
    status = request.POST.get("status")
    if not status:
        return render(request, "share-form/evaluation-status.html", {"options": options, "error": True})
    return redirect("evaluation-create", status=status)


@require_http_methods(["GET", "POST"])
def evaluation_create_view(request, status):
    errors = {}
    departments = Department.objects.all()
    if request.method == "POST":
        form = EvaluationCreateForm(request.POST)

        form_complete = request.POST.get("form_complete")
        selected_departments = request.POST.getlist("departments")
        selected_lead = request.POST.get("lead_department")
        department_to_remove = request.POST.get("remove_department")

        if form_complete:
            if form.is_valid():
                new_evaluation = form.save()
                EvaluationDepartmentAssociation.objects.create(
                    evaluation=new_evaluation, department=form.cleaned_data["lead_department"], is_lead=True
                )
                if form.cleaned_data["departments"]:
                    for department in form.cleaned_data["departments"]:
                        EvaluationDepartmentAssociation.objects.create(
                            evaluation=new_evaluation,
                            department=department,
                        )

                return redirect("evaluation-detail", uuid=new_evaluation.id)  # TODO: redirect to next page of form
            errors = form.errors.as_data()

        if department_to_remove and (department_to_remove in selected_departments):
            selected_departments.remove(department_to_remove)

        data = {
            "title": request.POST.get("title"),
            "lead_department": selected_lead,
            "departments": Department.objects.filter(code__in=selected_departments).all(),
        }

    else:
        # create a blank form
        form = EvaluationCreateForm()
        data = {"title": "", "lead_department": "", "departments": []}

    return render(
        request,
        "share-form/evaluation-create.html",
        {"form": form, "status": status, "departments": departments, "data": data, "errors": errors},
    )


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
        for dt in existing_objects.filter(design_type=design_type):
            dt.delete()

    if should_update_text:  # handles the case where the 'Other' text has been updated
        for dt in existing_objects.filter(design_type__collect_description=True):
            dt.text = form.cleaned_data["text"]
            dt.save()


@require_http_methods(["GET", "POST"])
def evaluation_update_type_view(request, uuid, parent=None):
    try:
        evaluation = Evaluation.objects.get(id=uuid)
    except Evaluation.DoesNotExist:
        raise Http404("No %(verbose_name)s found matching the query" % {"verbose_name": Evaluation._meta.verbose_name})

    if parent:
        parent_type = EvaluationDesignType.objects.get(code=parent)
        options = EvaluationDesignType.objects.filter(parent=parent_type)
        if options.count() == 0:
            raise Http404(
                "No %(verbose_name)s found matching the query"
                % {"verbose_name": EvaluationDesignType._meta.verbose_name}
            )
    else:
        options = EvaluationDesignType.root_objects.all()
        parent_type = None

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

            return redirect(
                "evaluation-detail", uuid=form.cleaned_data["evaluation"].id
            )  # TODO: redirect to next page of form

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
            "parent": parent_type,
        },
    )
