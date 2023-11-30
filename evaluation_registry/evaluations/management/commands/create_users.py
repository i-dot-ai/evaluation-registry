import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from django.core.management import BaseCommand
from tqdm import tqdm

cognito_client = boto3.client("cognito-idp", region_name=settings.AWS_REGION_NAME)


def user_exists(email: str) -> bool:
    try:
        cognito_client.admin_get_user(
            UserPoolId=settings.COLA_COGNITO_USER_POOL_ID,
            Username=email,
        )
        return True
    except ClientError:
        return False


def create_user(
    email: str,
    given_name: str,
    family_name: str,
    is_admin: bool | None = False,
    phone_number: str | None = None,
) -> None:
    user_attributes = [
        {"Name": "given_name", "Value": given_name},
        {"Name": "family_name", "Value": family_name},
        {"Name": "email", "Value": email},
        {"Name": "email_verified", "Value": "true"},
        {"Name": "custom:isAdmin", "Value": is_admin},
        {"Name": "custom:phoneNumber", "Value": phone_number},
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
            if not user_exists(email):
                name = email.split("@")[0]
                given_name, family_name = name.split(".", 1)
                create_user(email, given_name, family_name)
            progress_bar.update(1)

        progress_bar.close()
        self.stdout.write(self.style.SUCCESS("reformatting text complete"))
