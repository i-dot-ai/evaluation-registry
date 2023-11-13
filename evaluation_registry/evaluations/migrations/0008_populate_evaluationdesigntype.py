import json
import os

from django.db import migrations, models

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "design_types.csv")) as f:
    rows = [json.loads(f"[{row}]") for row in f.readlines()]
    DESIGN_TYPES = rows[1:]


def populate_evaluation_design_type_model(apps, schema_editor):
    EvaluationDesignType = apps.get_model("evaluations", "EvaluationDesignType")

    for code, display, parent, collect_description in DESIGN_TYPES:
        EvaluationDesignType.objects.get_or_create(
            code=code,
            display=display,
            collect_description=(collect_description == "true"),
        )


def update_evaluation_design_type_parents(apps, schema_editor):
    EvaluationDesignType = apps.get_model("evaluations", "EvaluationDesignType")

    for code, display, parent, _ in DESIGN_TYPES:
        if parent:
            parent_instance = EvaluationDesignType.objects.get(code=parent)


            EvaluationDesignType.objects.filter(code=code).update(
                parent=parent_instance,
            )


class Migration(migrations.Migration):
    dependencies = [
        ("evaluations", "0007_evaluationdesigntype_and_more"),
    ]

    operations = [
        migrations.RunPython(populate_evaluation_design_type_model),
        migrations.RunPython(update_evaluation_design_type_parents),
    ]
