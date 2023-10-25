import uuid
from typing import Any

from django.db import models
from django_use_email_as_username.models import BaseUser, BaseUserManager


class UUIDPrimaryKeyBase(models.Model):
    class Meta:
        abstract = True

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


class TimeStampedModel(models.Model):
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


class Department(UUIDPrimaryKeyBase, TimeStampedModel):
    code = models.SlugField(
        max_length=128,
        unique=True,
        help_text="unique identifier, containing only letters, numbers, underscores or hyphens",
    )
    display = models.CharField(max_length=128, help_text="display name")

    @classmethod
    def choices(cls) -> list[tuple[Any, Any]]:
        return [(x.code, x.display) for x in cls.objects.all()]

    def __str__(self):
        return self.display

    class Meta:
        abstract = True


class Evaluation(UUIDPrimaryKeyBase, TimeStampedModel):
    class EvaluationType(models.TextChoices):
        IMPACT = "impact", "Impact evaluation"
        PROCESS = "process", "Process evaluation"
        ECONOMIC = "economic", "Economic evaluation"
        OTHER = "other", "Other"
        NOT_SET = "not set", "Not Set"

    class EvaluationVisibility(models.TextChoices):
        DRAFT = "draft", "Draft"
        CIVIL_SERVICE = "civil_service", "Civil Service"
        PUBLIC = "public", "Public"

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    title = models.CharField(max_length=1024, blank=True, null=True)
    lead_department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='led_evaluations')
    departments = models.ManyToManyField(Department, related_name="+")

    evaluation_type = models.CharField(
        max_length=25,
        choices=EvaluationType.choices,
        default=EvaluationType.NOT_SET
    )
    evaluation_type_other = models.CharField(max_length=256, blank=True, null=True)

    # TODO: confirm whether this should be a CharField with design team
    brief_description = models.TextField(blank=True, null=True)
    # In the future, there may be canonical lists to select from for these
    grant_number = models.CharField(max_length=256, blank=True, null=True)
    major_project_number = models.CharField(max_length=256, blank=True, null=True)

    # TODO: there is a standard max_length of 200 for URL Fields - will that be enough?
    plan_link = models.URLField(blank=True, null=True)
    published_evaluation_link = models.URLField(blank=True, null=True)
    visibility = models.CharField(
        max_length=25,
        choices=EvaluationVisibility.choices,
        default=EvaluationVisibility.DRAFT
    )


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
    date = models.DateField(blank=True, null=True)
    other_description = models.CharField(max_length=256, blank=True, null=True)
    category = models.CharField(
        max_length=25,
        choices=EventDateCategory.choices,
        default=EventDateCategory.NOT_SET
    )
    status = models.CharField(
        max_length=25,
        choices=EventDateStatus.choices,
        default=EventDateStatus.NOT_SET
    )
