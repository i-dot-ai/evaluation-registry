# Generated by Django 3.2.22 on 2023-10-26 15:19
import json
import os

from django.db import migrations, models

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "departments.csv")) as f:
    rows = [json.loads(f"[{row}]") for row in f.readlines()]
    DEPARTMENTS = rows[1:]


def populate_department_model(apps, schema_editor):
    Department = apps.get_model("evaluations", "Department")

    for code, display, _, _, _ in DEPARTMENTS:
        Department.objects.get_or_create(code=code, display=display)


class Migration(migrations.Migration):
    dependencies = [
        ("evaluations", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(populate_department_model),
    ]
