# Generated by Django 4.2.7 on 2023-11-16 12:01

import uuid

import django.contrib.postgres.fields
import django.db.models.deletion
import simple_history.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("evaluations", "0004_populate_designtype"),
    ]

    operations = [
        migrations.CreateModel(
            name="HistoricalEvaluation",
            fields=[
                ("id", models.UUIDField(db_index=True, default=uuid.uuid4, editable=False)),
                ("created_at", models.DateTimeField(blank=True, editable=False)),
                ("modified_at", models.DateTimeField(blank=True, editable=False)),
                ("title", models.CharField(blank=True, max_length=1024, null=True)),
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
                ("grant_number", models.CharField(blank=True, max_length=256, null=True)),
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
    ]
