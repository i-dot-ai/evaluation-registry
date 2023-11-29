# Generated by Django 4.2.7 on 2023-11-22 10:52

import uuid

import django.contrib.postgres.fields
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
import django_use_email_as_username.models
import simple_history.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                ("first_name", models.CharField(blank=True, max_length=150, verbose_name="first name")),
                ("last_name", models.CharField(blank=True, max_length=150, verbose_name="last name")),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                ("date_joined", models.DateTimeField(default=django.utils.timezone.now, verbose_name="date joined")),
                ("email", models.EmailField(max_length=254, unique=True, verbose_name="email address")),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            managers=[
                ("objects", django_use_email_as_username.models.BaseUserManager()),
            ],
        ),
        migrations.CreateModel(
            name="Department",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "code",
                    models.SlugField(
                        help_text="unique identifier, containing only letters, numbers, underscores or hyphens",
                        max_length=128,
                        unique=True,
                    ),
                ),
                ("display", models.CharField(help_text="display name", max_length=512)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Evaluation",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=1024, null=True)),
                (
                    "status",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("planned", "A planned evaluation"),
                            ("ongoing", "An ongoing evaluation"),
                            ("complete", "A complete evaluation report"),
                        ],
                        max_length=512,
                        null=True,
                    ),
                ),
                ("rsm_evaluation_id", models.SmallIntegerField(blank=True, null=True, unique=True)),
                ("brief_description", models.TextField(blank=True, null=True)),
                ("has_grant_number", models.BooleanField(default=False)),
                ("grant_number", models.CharField(blank=True, max_length=256, null=True)),
                ("has_major_project_number", models.BooleanField(default=False)),
                ("major_project_number", models.CharField(blank=True, max_length=256, null=True)),
                ("plan_link", models.URLField(blank=True, max_length=1024, null=True)),
                (
                    "visibility",
                    models.CharField(
                        choices=[("draft", "Draft"), ("civil_service", "Civil Service"), ("public", "Public")],
                        default="draft",
                        max_length=512,
                    ),
                ),
                (
                    "reasons_unpublished",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(
                            choices=[
                                ("signoff", "Sign-off delays"),
                                ("procurement", "Procurement delays"),
                                ("resource", "Resource constraints"),
                                ("quality", "Quality issues (please specify)"),
                                ("changes", "Changes in the policy/programme being evaluated"),
                                ("other", "Other (please specify)"),
                            ],
                            max_length=256,
                        ),
                        blank=True,
                        null=True,
                        size=None,
                    ),
                ),
                (
                    "quality_reasons_unpublished_description",
                    models.TextField(
                        blank=True, help_text="description of quality issues preventing publication", null=True
                    ),
                ),
                (
                    "other_reasons_unpublished_description",
                    models.TextField(
                        blank=True, help_text="description of other issues preventing publication", null=True
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="EvaluationDesignType",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "code",
                    models.SlugField(
                        help_text="unique identifier, containing only letters, numbers, underscores or hyphens",
                        max_length=128,
                        unique=True,
                    ),
                ),
                ("display", models.CharField(help_text="display name", max_length=512)),
                (
                    "collect_description",
                    models.BooleanField(default=False, help_text="Use for 'other' types to prompt further information"),
                ),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="children",
                        to="evaluations.evaluationdesigntype",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Taxonomy",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "code",
                    models.SlugField(
                        help_text="unique identifier, containing only letters, numbers, underscores or hyphens",
                        max_length=128,
                        unique=True,
                    ),
                ),
                ("display", models.CharField(help_text="display name", max_length=512)),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="children",
                        to="evaluations.taxonomy",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Report",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(blank=True, max_length=1024, null=True)),
                ("link", models.URLField(blank=True, max_length=1024, null=True)),
                ("rsm_report_id", models.SmallIntegerField(blank=True, null=True)),
                (
                    "evaluation",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="evaluations.evaluation"),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="HistoricalEvaluation",
            fields=[
                ("id", models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)),
                ("created_at", models.DateTimeField(blank=True, editable=False)),
                ("modified_at", models.DateTimeField(blank=True, editable=False)),
                ("title", models.CharField(max_length=1024, null=True)),
                (
                    "status",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("planned", "A planned evaluation"),
                            ("ongoing", "An ongoing evaluation"),
                            ("complete", "A complete evaluation report"),
                        ],
                        max_length=512,
                        null=True,
                    ),
                ),
                ("rsm_evaluation_id", models.SmallIntegerField(blank=True, db_index=True, null=True)),
                ("brief_description", models.TextField(blank=True, null=True)),
                ("has_grant_number", models.BooleanField(default=False)),
                ("grant_number", models.CharField(blank=True, max_length=256, null=True)),
                ("has_major_project_number", models.BooleanField(default=False)),
                ("major_project_number", models.CharField(blank=True, max_length=256, null=True)),
                ("plan_link", models.URLField(blank=True, max_length=1024, null=True)),
                (
                    "visibility",
                    models.CharField(
                        choices=[("draft", "Draft"), ("civil_service", "Civil Service"), ("public", "Public")],
                        default="draft",
                        max_length=512,
                    ),
                ),
                (
                    "reasons_unpublished",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(
                            choices=[
                                ("signoff", "Sign-off delays"),
                                ("procurement", "Procurement delays"),
                                ("resource", "Resource constraints"),
                                ("quality", "Quality issues (please specify)"),
                                ("changes", "Changes in the policy/programme being evaluated"),
                                ("other", "Other (please specify)"),
                            ],
                            max_length=256,
                        ),
                        blank=True,
                        null=True,
                        size=None,
                    ),
                ),
                (
                    "quality_reasons_unpublished_description",
                    models.TextField(
                        blank=True, help_text="description of quality issues preventing publication", null=True
                    ),
                ),
                (
                    "other_reasons_unpublished_description",
                    models.TextField(
                        blank=True, help_text="description of other issues preventing publication", null=True
                    ),
                ),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")], max_length=1),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "historical evaluation",
                "verbose_name_plural": "historical evaluations",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name="EventDate",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "month",
                    models.PositiveSmallIntegerField(
                        blank=True,
                        choices=[
                            (1, "January"),
                            (2, "February"),
                            (3, "March"),
                            (4, "April"),
                            (5, "May"),
                            (6, "June"),
                            (7, "July"),
                            (8, "August"),
                            (9, "September"),
                            (10, "October"),
                            (11, "November"),
                            (12, "December"),
                        ],
                        null=True,
                    ),
                ),
                (
                    "year",
                    models.PositiveSmallIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(1900),
                            django.core.validators.MaxValueValidator(2100),
                        ]
                    ),
                ),
                ("other_description", models.CharField(blank=True, max_length=256, null=True)),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("eval_start", "Evaluation start"),
                            ("eval_end", "Evaluation end"),
                            ("first_recruit", "First participant recruited"),
                            ("last_recruit", "Last participant recruited"),
                            ("intervention_start", "Intervention start date"),
                            ("intervention_end", "Intervention end date"),
                            ("interim_extract", "Interim data extraction date"),
                            ("interim_analysis_start", "Interim data analysis start"),
                            ("interim_analysis_end", "Interim data analysis end"),
                            ("pub_interim", "Publication of interim results"),
                            ("final_extract", "Final data extraction date"),
                            ("final_analysis_start", "Final data analysis start"),
                            ("final_analysis_end", "Final data analysis end"),
                            ("pub_final", "Publication of final results"),
                            ("other", "Other"),
                            ("not set", "Not Set"),
                        ],
                        default="not set",
                        max_length=25,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("intended", "Intended"), ("actual", "Actual"), ("not set", "Not Set")],
                        default="not set",
                        max_length=25,
                    ),
                ),
                (
                    "evaluation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="event_dates",
                        to="evaluations.evaluation",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="EvaluationDesignTypeDetail",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("text", models.CharField(blank=True, max_length=1024, null=True)),
                (
                    "design_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="evaluations.evaluationdesigntype"
                    ),
                ),
                (
                    "evaluation",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="evaluations.evaluation"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="EvaluationDepartmentAssociation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("is_lead", models.BooleanField(default=False)),
                (
                    "department",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="evaluations.department"),
                ),
                (
                    "evaluation",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="evaluations.evaluation"),
                ),
            ],
        ),
        migrations.AddField(
            model_name="evaluation",
            name="departments",
            field=models.ManyToManyField(
                help_text="departments involved in this evaluation",
                through="evaluations.EvaluationDepartmentAssociation",
                to="evaluations.department",
            ),
        ),
        migrations.AddField(
            model_name="evaluation",
            name="evaluation_design_types",
            field=models.ManyToManyField(
                help_text="add more text for 'Other' Design Types",
                through="evaluations.EvaluationDesignTypeDetail",
                to="evaluations.evaluationdesigntype",
            ),
        ),
        migrations.AddConstraint(
            model_name="evaluationdepartmentassociation",
            constraint=models.UniqueConstraint(
                fields=("evaluation", "department"), name="unique-evaluation-department"
            ),
        ),
        migrations.AddConstraint(
            model_name="evaluationdepartmentassociation",
            constraint=models.UniqueConstraint(
                condition=models.Q(("is_lead", True)), fields=("evaluation",), name="unique-lead-department"
            ),
        ),
    ]
