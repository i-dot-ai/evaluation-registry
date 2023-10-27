import uuid
from typing import Any

from django.core.exceptions import ValidationError
from django.db import models
from django_use_email_as_username.models import BaseUser, BaseUserManager


def month_validator(value):
    if value < 1 or value > 12:
        raise ValidationError(
            "The month should be a value between 1 and 12",
        )


def year_validator(value):
    if value < 1900 or value > 2100:
        raise ValidationError(
            "The year should be between 1900 and 2100",
            params={"value": value},
        )


class UUIDPrimaryKeyBase(models.Model):
    class Meta:
        abstract = True

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(editable=False, auto_now_add=True)
    modified_at = models.DateTimeField(editable=False, auto_now=True)

    class Meta:
        abstract = True


class ChoicesModel(models.Model):
    code = models.SlugField(
        max_length=128,
        unique=True,
        help_text="unique identifier, containing only letters, numbers, underscores or hyphens",
    )
    display = models.CharField(max_length=512, help_text="display name")

    class Meta:
        abstract = True

    @classmethod
    def choices(cls) -> list[tuple[Any, Any]]:
        return [(x.code, x.display) for x in cls.objects.all()]

    def __str__(self):
        return self.display


class User(BaseUser, UUIDPrimaryKeyBase):
    objects = BaseUserManager()
    username = None

    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        super().save(*args, **kwargs)


class Department(UUIDPrimaryKeyBase, TimeStampedModel, ChoicesModel):
    pass


class Evaluation(UUIDPrimaryKeyBase, TimeStampedModel):
    class EvaluationVisibility(models.TextChoices):
        DRAFT = "draft", "Draft"
        CIVIL_SERVICE = "civil_service", "Civil Service"
        PUBLIC = "public", "Public"

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    title = models.CharField(max_length=1024, blank=True, null=True)
    departments = models.ManyToManyField(
        Department, through="EvaluationDepartmentAssociation", help_text="departments involved in this evaluation"
    )

    is_process_type = models.BooleanField(default=False, help_text="evaluation is a process type?")
    is_impact_type = models.BooleanField(default=False, help_text="evaluation is a impact type?")
    is_economic_type = models.BooleanField(default=False, help_text="evaluation is a economic type?")
    is_other_type = models.BooleanField(default=False, help_text="evaluation is a other type?")
    other_evaluation_type_description = models.TextField(
        null=True, blank=True, help_text="optional description of other evaluation type"
    )

    brief_description = models.TextField(blank=True, null=True)
    # In the future, there may be canonical lists to select from for these
    grant_number = models.CharField(max_length=256, blank=True, null=True)
    major_project_number = models.CharField(max_length=256, blank=True, null=True)

    plan_link = models.URLField(max_length=1024, blank=True, null=True)
    published_evaluation_link = models.URLField(max_length=1024, blank=True, null=True)
    visibility = models.CharField(
        max_length=512, choices=EvaluationVisibility.choices, default=EvaluationVisibility.DRAFT
    )

    @property
    def lead_department(self):
        return self.departments.filter(evaluationdepartmentassociation__is_lead=True).first()

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
            models.UniqueConstraint(fields=["evaluation", "department"], name="unique-evaluation-department")
        ]


class EventDate(UUIDPrimaryKeyBase, TimeStampedModel):
    class EventDateCategory(models.TextChoices):
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

    class EventDateStatus(models.TextChoices):
        INTENDED = "intended", "Intended"
        ACTUAL = "actual", "Actual"
        NOT_SET = "not set", "Not Set"

    evaluation = models.ForeignKey(Evaluation, related_name="event_dates", on_delete=models.CASCADE)
    month = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[year_validator],
    )
    year = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[year_validator],
    )
    other_description = models.CharField(max_length=256, blank=True, null=True)
    category = models.CharField(max_length=25, choices=EventDateCategory.choices, default=EventDateCategory.NOT_SET)
    status = models.CharField(max_length=25, choices=EventDateStatus.choices, default=EventDateStatus.NOT_SET)

    def __str__(self):
        if self.month:
            return f"{self.year}-{self.month:02}"
        return f"{self.year}"
