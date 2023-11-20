# Generated by Django 4.2.7 on 2023-11-20 08:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("evaluations", "0006_alter_evaluation_title_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="EvaluationFile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("file", models.FileField(upload_to="evaluation_uploads")),
                ("plain_text", models.TextField(blank=True, null=True)),
                ("structured_text", models.JSONField(blank=True, null=True)),
            ],
        ),
    ]
