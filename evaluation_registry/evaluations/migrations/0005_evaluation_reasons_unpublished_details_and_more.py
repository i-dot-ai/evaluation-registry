# Generated by Django 4.2.7 on 2023-11-28 14:05

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("evaluations", "0004_remove_evaluation_other_reasons_unpublished_description_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="evaluation",
            name="reasons_unpublished_details",
            field=models.TextField(blank=True, max_length=4096, null=True),
        ),
        migrations.AddField(
            model_name="historicalevaluation",
            name="reasons_unpublished_details",
            field=models.TextField(blank=True, max_length=4096, null=True),
        ),
    ]
