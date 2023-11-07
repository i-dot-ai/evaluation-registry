import calendar
import uuid
from datetime import datetime, timedelta
from typing import Optional

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

    class EvaluationType(models.TextChoices):
        PROCESS = "process", "Process evaluation"
        IMPACT = "impact", "Impact evaluation"
        ECONOMIC = "economic", "Economic evaluation"
        OTHER = "other", "Other"

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    title = models.CharField(max_length=1024, blank=True, null=True)
    departments = models.ManyToManyField(  # type: ignore
        Department,
        through="EvaluationDepartmentAssociation",
        help_text="departments involved in this evaluation",
    )

    is_process_type = models.BooleanField(default=False, help_text="evaluation is a process type?")
    is_impact_type = models.BooleanField(default=False, help_text="evaluation is an impact type?")
    is_economic_type = models.BooleanField(default=False, help_text="evaluation is an economic type?")
    is_other_type = models.BooleanField(default=False, help_text="evaluation is an other type?")
    other_evaluation_type_description = models.TextField(
        null=True, blank=True, help_text="optional description of other evaluation type"
    )

    brief_description = models.TextField(blank=True, null=True)
    # In the future, there may be canonical lists to select from for these
    grant_number = models.CharField(max_length=256, blank=True, null=True)
    major_project_number = models.CharField(max_length=256, blank=True, null=True)

    plan_link = models.URLField(max_length=1024, blank=True, null=True)
    published_evaluation_link = models.URLField(max_length=1024, blank=True, null=True)
    visibility = models.CharField(max_length=512, choices=Visibility.choices, default=Visibility.DRAFT)

    @property
    def lead_department(self) -> Optional[Department]:
        try:
            return self.departments.get(evaluationdepartmentassociation__is_lead=True)
        except ObjectDoesNotExist:
            return None

    @property
    def evaluation_types(self):
        type_list = []
        if self.is_process_type:
            type_list.append(self.EvaluationType.PROCESS)
        if self.is_impact_type:
            type_list.append(self.EvaluationType.IMPACT)
        if self.is_economic_type:
            type_list.append(self.EvaluationType.ECONOMIC)
        if self.is_other_type:
            type_list.append(self.EvaluationType.OTHER)
        return type_list

    @property
    def evaluation_type_text(self):
        return list(map(lambda x: x.label, self.evaluation_types))

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


class LoginToken(TimeStampedModel):
    """A one time token to authenticate a user"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, help_text="a user may have many tokens")
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, help_text="each token is unique")

    def has_expired(self) -> bool:
        """has the link expired?"""
        age = datetime.now() - self.created_at.replace(tzinfo=None)
        return age > timedelta(hours=1)
