# Generated by Django 4.2.7 on 2023-12-04 09:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("evaluations", "0007_alter_evaluation_visibility_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="evaluation",
            name="cost",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name="historicalevaluation",
            name="cost",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
