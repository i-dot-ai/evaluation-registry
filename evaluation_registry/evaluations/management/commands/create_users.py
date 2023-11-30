import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.management import BaseCommand
from tqdm import tqdm

from evaluation_registry import settings
from evaluation_registry.evaluations.models import Evaluation

cognito_client = boto3.client("cognito-idp", region_name=settings.AWS_REGION_NAME)


def create_user(email: str) -> None:
    name = email.split("@")[0]
    given_name, family_name = name.split(".", 1)

    user_attributes = [
        {"Name": "given_name", "Value": given_name},
        {"Name": "family_name", "Value": family_name},
        {"Name": "email", "Value": email},
        {"Name": "email_verified", "Value": "true"},
    ]

    cognito_client.admin_create_user(
        UserPoolId=settings.COLA_COGNITO_USER_POOL_ID,
        Username=email,
        UserAttributes=user_attributes,
        MessageAction="SUPPRESS",
    )

    cognito_client.admin_set_user_password(
        UserPoolId=settings.COLA_COGNITO_USER_POOL_ID,
        Username=email,
        Password=settings.EVAREG_COGNITO_FIXED_PASSWORD,
        Permanent=True,
    )


class Command(BaseCommand):
    help = "Create users in cognito user pool"

    def add_arguments(self, parser):
        parser.add_argument("emails", type=str, nargs="+")

    def handle(self, *args, **options):
        progress_bar = tqdm(desc="Processing", total=len(options["emails"]))
        for email in options["emails"]:
            progress_bar.set_description(f"creating user: {email}")
            try:
                cognito_client.admin_get_user(
                    UserPoolId=settings.COLA_COGNITO_USER_POOL_ID,
                    Username=email,
                )
                self.stdout.write(self.style.SUCCESS("user already exists"))
            except ClientError:
                create_user(email)
                self.stdout.write(self.style.SUCCESS("created user"))

            progress_bar.update(1)

        progress_bar.close()
        self.stdout.write(self.style.SUCCESS("reformatting text complete"))
