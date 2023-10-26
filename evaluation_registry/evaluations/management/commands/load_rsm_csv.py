import json

from django.core.management import BaseCommand

from evaluation_registry.evaluations.models import (
    Department,
    Evaluation,
    EventDate,
)


def parse_row(text):
    return json.loads(f"[{text}]")


MONTHS = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "Jul": 7,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "Oct": 10,
    "November": 10,
    "December": 12,
}


def make_event_date(evaluation, kvp, category, key):
    pub_month = MONTHS.get(kvp[f"{key} (Month)"])
    if year := kvp[f"{key} (Year)"]:
        try:
            EventDate.objects.create(
                evaluation=evaluation,
                month=pub_month,
                year=int(year),
                category=category,
            )
        except ValueError:
            pass


class Command(BaseCommand):
    help = "Load RSM data from CSV"

    def add_arguments(self, parser):
        parser.add_argument("file", type=str)

    def handle(self, *args, **options):
        file = options["file"]
        self.stdout.write(self.style.SUCCESS('loading "%s"' % file))

        with open(file) as f:
            header = parse_row(next(f))
            for row in f:
                record = dict(zip(header, parse_row(row)))
                if lead_department_code := record["Client"]:
                    lead_department, _ = Department.objects.get_or_create(
                        code=lead_department_code[:128], display=lead_department_code[:512]
                    )
                    published_evaluation_link = record["gov_uk_link"]
                    if len(published_evaluation_link or "") > 1024:
                        published_evaluation_link = None

                    evaluation = Evaluation.objects.create(
                        title=record["Evaluation title"],
                        lead_department=lead_department,
                        brief_description=record["Evaluation summary"],
                        major_project_number=record["Major projects identifier"],
                        visibility=Evaluation.EvaluationVisibility.PUBLIC,
                        published_evaluation_link=published_evaluation_link,
                    )

                    make_event_date(
                        evaluation,
                        record,
                        EventDate.EventDateCategory.INTERVENTION_START_DATE,
                        "Intervention start date",
                    )
                    make_event_date(
                        evaluation, record, EventDate.EventDateCategory.INTERVENTION_END_DATE, "Intervention end date"
                    )
                    make_event_date(
                        evaluation, record, EventDate.EventDateCategory.PUBLICATION_FINAL_RESULTS, "Publication date"
                    )
                    make_event_date(evaluation, record, EventDate.EventDateCategory.OTHER, "Event start date")
