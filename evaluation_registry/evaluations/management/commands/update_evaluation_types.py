from django.core.management import BaseCommand

from evaluation_registry.evaluations.models import Evaluation


class Command(BaseCommand):
    help = "Populate evaluation_types field using boolean evaluation type fields"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Updating all Evaluations"))

        for e in Evaluation.objects.all():
            if e.evaluation_types:
                self.stdout.write(self.style.NOTICE(f"Skipping {e.title}: evaluation_types field already exists"))
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

            self.stdout.write(self.style.SUCCESS(f"Added evaluation types to {e.title}"))
