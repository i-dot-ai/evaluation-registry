import environ
from django.core.management import BaseCommand, call_command

env = environ.Env()


class Command(BaseCommand):
    help = "Generates an Entity Relationship Diagram for the repository’s README"

    def handle(self, *args, **options):
        if env.str("ENVIRONMENT", None) != "LOCAL":
            raise Exception("This command only works in the LOCAL env")

        call_command("graph_models", ["-a", "-g", "-o", "docs/erd.png"])
