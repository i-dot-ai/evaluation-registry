import calendar
import uuid
from typing import Optional

from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.query import QuerySet
from django_use_email_as_username.models import BaseUser, BaseUserManager
from simple_history.models import HistoricalRecords


class UUIDPrimaryKeyBase(models.Model):
    class Meta:
        abstract = True

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


class TimeStampedModel(UUIDPrimaryKeyBase):
    created_at = models.DateTimeField(editable=False, auto_now_add=True)
    modified_at = models.DateTimeField(editable=False, auto_now=True)

    class Meta:
        abstract = True


class User(BaseUser, UUIDPrimaryKeyBase):
    objects = BaseUserManager()
    username = None

    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        super().save(*args, **kwargs)


class Department(TimeStampedModel):
    code = models.SlugField(
        max_length=128,
        unique=True,
        help_text="unique identifier, containing only letters, numbers, underscores or hyphens",
    )
    display = models.CharField(max_length=512, help_text="display name")

    def __str__(self):
        return self.display


class RootDesignTypeManager(models.Manager):
    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(parent__isnull=True)


class AbstractChoice(TimeStampedModel):
    code = models.SlugField(
        max_length=128,
        unique=True,
        help_text="unique identifier, containing only letters, numbers, underscores or hyphens",
    )
    display = models.CharField(max_length=512, help_text="display name")
    parent = models.ForeignKey("self", related_name="children", on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.display

    class Meta:
        abstract = True


class EvaluationDesignType(AbstractChoice):
    collect_description = models.BooleanField(
        default=False, help_text="Use for 'other' types to prompt further information"
    )

    objects = models.Manager()
    root_objects = RootDesignTypeManager()


class Taxonomy(AbstractChoice):
    def __str__(self):
        return f"{self.parent} > {self.display}" if self.parent else self.display


class Evaluation(TimeStampedModel):
    class Visibility(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLIC = "public", "Public"

    class Status(models.TextChoices):
        PLANNED = "planned", "A planned evaluation"
        ONGOING = "ongoing", "An ongoing evaluation"
        COMPLETE = "complete", "A complete evaluation report"

    class UnpublishedReason(models.TextChoices):
        SIGNOFF = "signoff", "Sign-off delays"
        PROCUREMENT = "procurement", "Procurement delays"
        RESOURCE = "resource", "Resource constraints"
        QUALITY = "quality", "Quality issues (please specify)"
        CHANGES = "changes", "Changes in the policy/programme being evaluated"
        OTHER = "other", "Other (please specify)"

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    title = models.CharField(max_length=1024, null=True)
    departments = models.ManyToManyField(  # type: ignore
        Department,
        through="EvaluationDepartmentAssociation",
        help_text="departments involved in this evaluation",
    )
    status = models.CharField(max_length=512, choices=Status.choices, blank=True, null=True)
    # For matching with initial data upload from RSM - evaluation id
    rsm_evaluation_id = models.SmallIntegerField(blank=True, null=True, unique=True)

    evaluation_design_types = models.ManyToManyField(  # type: ignore
        EvaluationDesignType, through="EvaluationDesignTypeDetail", help_text="add more text for 'Other' Design Types"
    )

    brief_description = models.TextField(blank=True, null=True)
    # In the future, there may be canonical lists to select from for these
    has_grant_number = models.BooleanField(default=False)
    grant_number = models.CharField(max_length=256, blank=True, null=True)
    has_major_project_number = models.BooleanField(default=False)
    major_project_number = models.CharField(max_length=256, blank=True, null=True)
    policies = models.ManyToManyField(  # type: ignore
        Taxonomy, help_text="policy areas covered by this evaluation", blank=True
    )

    visibility = models.CharField(max_length=512, choices=Visibility.choices, default=Visibility.DRAFT)
    is_final_report_published = models.BooleanField(null=True, blank=True)
    link_to_published_evaluation = models.URLField(max_length=1024, blank=True, null=True)
    plan_link = models.URLField(max_length=1024, blank=True, null=True)
    reasons_unpublished = ArrayField(
        models.CharField(max_length=256, choices=UnpublishedReason.choices), blank=True, null=True
    )
    reasons_unpublished_details = models.TextField(blank=True, null=True, max_length=4096)

    history = HistoricalRecords()

    @property
    def lead_department(self) -> Optional[Department]:
        try:
            return self.departments.get(evaluationdepartmentassociation__is_lead=True)
        except ObjectDoesNotExist:
            return None

    @property
    def other_departments(self):
        try:
            return self.departments.filter(evaluationdepartmentassociation__is_lead=False)
        except ObjectDoesNotExist:
            return None

    @property
    def types_text_list(self):
        return [t.display for t in self.evaluation_design_types.filter(parent__isnull=True)]

    @property
    def reports_with_links(self):
        return self.report_set.exclude(link="")

    @property
    def other_design_types(self):
        return self.evaluationdesigntypedetail_set.filter(design_type__code="other")

    def get_reasons_unpublished_text(self) -> list[str]:
        if not self.reasons_unpublished:
            return []
        return [choice[1] for choice in Evaluation.UnpublishedReason.choices if choice[0] in self.reasons_unpublished]

    def get_policies_text_list(self):
        return [t.display for t in self.policies.all()]

    def __str__(self):
        return str(self.title)


class EvaluationDepartmentAssociation(models.Model):
    """association model for evaluations & departments, with a
    flag to identify whether this is the primary association
    """

    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    is_lead = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["evaluation", "department"], name="unique-evaluation-department"),
            models.UniqueConstraint(
                fields=["evaluation"], condition=models.Q(is_lead=True), name="unique-lead-department"
            ),
        ]


class EvaluationDesignTypeDetail(models.Model):
    """additional user-created text to describe evaluation designs
    that do not fit standard types
    """

    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE)
    design_type = models.ForeignKey(EvaluationDesignType, on_delete=models.CASCADE)
    text = models.CharField(max_length=1024, blank=True, null=True)


class Report(TimeStampedModel):
    title = models.CharField(max_length=1024, blank=True, null=True)
    link = models.URLField(max_length=1024, blank=True, null=True)
    rsm_report_id = models.SmallIntegerField(blank=True, null=True)
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE)


class EventDate(TimeStampedModel):
    class Category(models.TextChoices):
        EVALUATION_START = "eval_start", "Evaluation start"
        EVALUATION_END = "eval_end", "Evaluation end"
        FIRST_PARTICIPANT_RECRUITED = "first_recruit", "First participant recruited"
        LAST_PARTICIPANT_RECRUITED = "last_recruit", "Last participant recruited"
        INTERVENTION_START_DATE = "intervention_start", "Intervention start date"
        INTERVENTION_END_DATE = "intervention_end", "Intervention end date"
        INTERIM_DATA_EXTRACTION_DATE = "interim_extract", "Interim data extraction date"
        INTERIM_DATA_ANALYSIS_START = "interim_analysis_start", "Interim data analysis start"
        INTERIM_DATA_ANALYSIS_END = "interim_analysis_end", "Interim data analysis end"
        PUBLICATION_INTERIM_RESULTS = "pub_interim", "Publication of interim results"
        FINAL_DATA_EXTRACTION_DATE = "final_extract", "Final data extraction date"
        FINAL_DATA_ANALYSIS_START = "final_analysis_start", "Final data analysis start"
        FINAL_DATA_ANALYSIS_END = "final_analysis_end", "Final data analysis end"
        PUBLICATION_FINAL_RESULTS = "pub_final", "Publication of final results"
        OTHER = "other", "Other"
        NOT_SET = "not set", "Not Set"

    class Status(models.TextChoices):
        INTENDED = "intended", "Intended"
        ACTUAL = "actual", "Actual"
        NOT_SET = "not set", "Not Set"

    class Month(models.IntegerChoices):
        JANUARY = 1
        FEBRUARY = 2
        MARCH = 3
        APRIL = 4
        MAY = 5
        JUNE = 6
        JULY = 7
        AUGUST = 8
        SEPTEMBER = 9
        OCTOBER = 10
        NOVEMBER = 11
        DECEMBER = 12

    evaluation = models.ForeignKey(Evaluation, related_name="event_dates", on_delete=models.CASCADE)
    month = models.PositiveSmallIntegerField(null=True, blank=True, choices=Month.choices)
    year = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(2100)],
    )
    other_description = models.CharField(max_length=256, blank=True, null=True)
    category = models.CharField(max_length=25, choices=Category.choices, default=Category.NOT_SET)
    status = models.CharField(max_length=25, choices=Status.choices, default=Status.NOT_SET)

    def __str__(self):
        if self.month:
            return f"{calendar.month_name[self.month]} {self.year}"
        return f"{self.year}"


class RSMFile(TimeStampedModel):
    """raw RSM data files"""

    csv = models.FileField(upload_to="rsm_csv_files/")
    last_successfully_loaded_at = models.DateTimeField(null=True, blank=True)
