# Generated by Django 4.2.7 on 2023-12-04 13:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("evaluations", "0006_evaluation_policies"),
    ]

    operations = [
        migrations.AddField(
            model_name="evaluation",
            name="report_title",
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
        migrations.AddField(
            model_name="evaluation",
            name="rsm_report_id",
            field=models.SmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="historicalevaluation",
            name="report_title",
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
        migrations.AddField(
            model_name="historicalevaluation",
            name="rsm_report_id",
            field=models.SmallIntegerField(blank=True, null=True),
        ),
        migrations.DeleteModel(
            name="Report",
        ),
    ]
