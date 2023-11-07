from django.db import migrations

def print_success(str):
    # prints in green
    print(f'\033[1;32;40m{str}\033[m')

def print_warning(str):
    # prints in yellow
    print(f'\033[1;33;40m{str}\033[m')


def update_evaluation_types(apps, schema_editor):
    Evaluation = apps.get_model("evaluations", "Evaluation")
    print("Updating evaluation types for all evaluations")

    for e in Evaluation.objects.all():
        if e.evaluation_types:
            print_warning(f"Skipping {e.title}: evaluation_types field already exists")
            continue

        choices = []
        if e.is_process_type:
            choices.append(Evaluation.EvaluationType.PROCESS)
        if e.is_impact_type:
            choices.append(Evaluation.EvaluationType.IMPACT)
        if e.is_economic_type:
            choices.append(Evaluation.EvaluationType.ECONOMIC)
        if e.is_other_type:
            choices.append(Evaluation.EvaluationType.OTHER)

        e.evaluation_types = choices
        e.save()

        print_success(f"Added evaluation types to {e.title}")



class Migration(migrations.Migration):
    dependencies = [
        ("evaluations", "0003_evaluation_evaluation_types"),
    ]

    operations = [
        migrations.RunPython(update_evaluation_types),
    ]
