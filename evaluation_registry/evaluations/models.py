import calendar
import uuid
from typing import Optional

from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django_use_email_as_username.models import BaseUser, BaseUserManager


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


class Evaluation(TimeStampedModel):
    class Visibility(models.TextChoices):
        DRAFT = "draft", "Draft"
        CIVIL_SERVICE = "civil_service", "Civil Service"
        PUBLIC = "public", "Public"

    class Status(models.TextChoices):
        PLANNED = "planned", "A planned evaluation"
        ONGOING = "ongoing", "An ongoing evaluation"
        COMPLETE = "complete", "A complete evaluation report"

    class EvaluationType(models.TextChoices):
        IMPACT = "impact", "Impact evaluation"
        PROCESS = "process", "Process evaluation"
        ECONOMIC = "economic", "Value for money evaluation"
        OTHER = "other", "Other"

    class ImpactType(models.TextChoices):
        RCT = "rct", "Randomised controlled trial (RCT)"
        QUASI_EXPERIMENTAL = "quasi_experimental", "Quasi-experimental method"
        THEORY = "theory", "Theory-based method"
        GENERIC = "generic", "Generic research method"
        OTHER = "other", "Other"

    class ProcessType(models.TextChoices):
        INDIVIDUAL = "individual", "Individual interviews"
        GROUP = "group", "Focus groups or group interviews"
        CASE_STUDY = "case_study", "Case studies"
        SURVEYS = "surveys", "Surveys and polling"
        OUTPUT = "output", "Output or performance modelling"
        QUALITATIVE = "qualitative", "Qualitative observational studies"
        CONSULTATIVE = "consultative", "Consultative/deliberative methods"
        OTHER = "other", "Other"

    class EconomicType(models.TextChoices):
        MINIMISATION = "minimisation", "Cost minimisation"
        EFFECTIVENESS = "effectiveness", "Cost-effectiveness analysis"
        BENEFIT = "benefit", "Cost-benefit analysis"
        UTILITY = "utility", "Cost-utility analysis"
        OTHER = "other", "Other"

    class RCTType(models.TextChoices):
        CLUSTER = "cluster", "Cluster RCT"
        STEPPED = "stepped", "Stepped wedge RCT"
        WAITLIST = "waitlist", "Wait list RCT"
        OTHER = "other", "Other"

    class QuasiExperimentalType(models.TextChoices):
        PROPENSITY = "propensity", "Propensity score matching"
        TIMING = "timing", "Timing of events"
        INTERRUPTED = "interrupted", "Interrupted time series analysis"
        INSTRUMENTAL = "instrumental", "Instrumental variables"
        SYNTHETIC = "synthetic", "Synthetic control variables"
        DIFFERENCE = "difference", "Difference-in-difference"
        REGRESSION = "regression", "Regression discontinuity"
        OTHER = "other", "Other"

    class TheoryType(models.TextChoices):
        QCA = "qca", "Qualitative comparative analysis (QCA)"
        REALIST = "realist", "Realist evaluation"
        PROCESS = "process", "Process tracing"
        CONTRIBUTION_ANALYSIS = "contribution_analysis", "Contribution analysis"
        BAYESIAN = "bayesian", "Bayesian updating"
        CONTRIBUTION_TRACING = "contribution_tracing", "Contribution tracing"
        SIGNIFICANT = "significant", "Most significant change"
        OUTCOME = "outcome", "Outcome harvesting"
        SIMULATION = "simulation", "Simulation modelling"
        OTHER = "other", "Other"

    class GenericType(models.TextChoices):
        INDIVIDUAL = "individual", "Individual interviews"
        GROUP = "group", "Focus groups or group interviews"
        CASE_STUDY = "case_study", "Case studies"
        SURVEYS = "surveys", "Surveys and polling"
        OUTPUT = "output", "Output or performance modelling"
        QUALITATIVE = "qualitative", "Qualitative observational studies"
        CONSULTATIVE = "consultative", "Consultative/deliberative methods"
        OTHER = "other", "Other"

    class UnpublishedReason(models.TextChoices):
        SIGNOFF = "signoff", "Sign-off delays"
        PROCUREMENT = "procurement", "Procurement delays"
        RESOURCE = "resource", "Resource constraints"
        QUALITY = "quality", "Quality issues (please specify)"
        CHANGES = "changes", "Changes in the policy/programme being evaluated"
        OTHER = "other", "Other (please specify)"

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    title = models.CharField(max_length=1024, blank=True, null=True)
    departments = models.ManyToManyField(  # type: ignore
        Department,
        through="EvaluationDepartmentAssociation",
        help_text="departments involved in this evaluation",
    )
    status = models.CharField(max_length=512, choices=Status.choices, blank=True, null=True)

    evaluation_types = ArrayField(
        models.CharField(max_length=256, choices=EvaluationType.choices), blank=True, null=True
    )
    other_evaluation_type_description = models.TextField(
        null=True, blank=True, help_text="optional description of other evaluation type"
    )

    impact_types = ArrayField(models.CharField(max_length=256, choices=ImpactType.choices), blank=True, null=True)
    other_impact_type_description = models.TextField(
        null=True, blank=True, help_text="optional description of other impact evaluation type"
    )
    process_types = ArrayField(models.CharField(max_length=256, choices=ProcessType.choices), blank=True, null=True)
    other_process_type_description = models.TextField(
        null=True, blank=True, help_text="optional description of other process evaluation type"
    )
    economic_types = ArrayField(models.CharField(max_length=256, choices=EconomicType.choices), blank=True, null=True)
    other_economic_type_description = models.TextField(
        null=True, blank=True, help_text="optional description of other economic evaluation type"
    )

    rct_types = ArrayField(models.CharField(max_length=256, choices=RCTType.choices), blank=True, null=True)
    other_rct_type_description = models.TextField(
        null=True, blank=True, help_text="optional description of other RCT method type"
    )
    quasi_experimental_types = ArrayField(
        models.CharField(max_length=256, choices=QuasiExperimentalType.choices), blank=True, null=True
    )
    other_quasi_experimental_type_description = models.TextField(
        null=True, blank=True, help_text="optional description of other quasi-experimental method type"
    )
    theory_types = ArrayField(models.CharField(max_length=256, choices=TheoryType.choices), blank=True, null=True)
    other_theory_type_description = models.TextField(
        null=True, blank=True, help_text="optional description of other theory based method type"
    )
    generic_types = ArrayField(models.CharField(max_length=256, choices=GenericType.choices), blank=True, null=True)
    other_generic_type_description = models.TextField(
        null=True, blank=True, help_text="optional description of other generic based method type"
    )

    brief_description = models.TextField(blank=True, null=True)
    # In the future, there may be canonical lists to select from for these
    grant_number = models.CharField(max_length=256, blank=True, null=True)
    major_project_number = models.CharField(max_length=256, blank=True, null=True)

    plan_link = models.URLField(max_length=1024, blank=True, null=True)
    published_evaluation_link = models.URLField(max_length=1024, blank=True, null=True)
    visibility = models.CharField(max_length=512, choices=Visibility.choices, default=Visibility.DRAFT)
    reasons_unpublished = ArrayField(
        models.CharField(max_length=256, choices=UnpublishedReason.choices), blank=True, null=True
    )
    quality_reasons_unpublished_description = models.TextField(
        null=True, blank=True, help_text="description of quality issues preventing publication"
    )
    other_reasons_unpublished_description = models.TextField(
        null=True, blank=True, help_text="description of other issues preventing publication"
    )

    @property
    def lead_department(self) -> Optional[Department]:
        try:
            return self.departments.get(evaluationdepartmentassociation__is_lead=True)
        except ObjectDoesNotExist:
            return None

    def get_array_field_text(self, values, choices) -> list[str]:
        if not values:
            return []
        return [choice[1] for choice in choices if choice[0] in values]

    def get_evaluation_types_text(self) -> list[str]:
        return self.get_array_field_text(self.evaluation_types, Evaluation.EvaluationType.choices)

    def get_impact_types_text(self) -> list[str]:
        return self.get_array_field_text(self.impact_types, Evaluation.ImpactType.choices)

    def get_process_types_text(self) -> list[str]:
        return self.get_array_field_text(self.process_types, Evaluation.ProcessType.choices)

    def get_economic_types_text(self) -> list[str]:
        return self.get_array_field_text(self.economic_types, Evaluation.EconomicType.choices)

    def get_rct_types_text(self) -> list[str]:
        return self.get_array_field_text(self.rct_types, Evaluation.RCTType.choices)

    def get_quasi_experimental_text(self) -> list[str]:
        return self.get_array_field_text(self.quasi_experimental_types, Evaluation.QuasiExperimentalType.choices)

    def get_theory_types_text(self) -> list[str]:
        return self.get_array_field_text(self.theory_types, Evaluation.TheoryType.choices)

    def get_generic_types_text(self) -> list[str]:
        return self.get_array_field_text(self.generic_types, Evaluation.GenericType.choices)

    def get_reasons_unpublished_text(self) -> list[str]:
        return self.get_array_field_text(self.reasons_unpublished, Evaluation.UnpublishedReason.choices)

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
