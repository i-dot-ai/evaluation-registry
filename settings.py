import ast
import os
import socket
import subprocess



LOCALHOST = socket.gethostbyname(socket.gethostname())


def get_environ_vars() -> dict:
    """get env-vars for EC2"""
    completed_process = subprocess.run(
        ["/opt/elasticbeanstalk/bin/get-config", "environment"], stdout=subprocess.PIPE, text=True, check=True
    )

    return ast.literal_eval(completed_process.stdout)


if "DB_HOST" in os.environ:
    env_vars = os.environ
else:
    env_vars = get_environ_vars()


ALLOWED_HOSTS = [
    LOCALHOST,  # https://stackoverflow.com/a/35728155
    "localhost",
    "127.0.0.1",
    # TODO: add when these are known
    # "dev.<YOUR-DNS>.cabinetoffice.gov.uk",
    # "<YOUR-DNS>.cabinetoffice.gov.uk",
    "evalaution-registry-dev.eba-2mmghbpu.eu-west-2.elasticbeanstalk.com",
    "evalaution-registry-prod.eba-2mmghbpu.eu-west-2.elasticbeanstalk.com",
]

if env_vars.get("AWS_STORAGE_BUCKET_NAME"):
    STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

    AWS_STORAGE_BUCKET_NAME = env_vars["AWS_STORAGE_BUCKET_NAME"]
    AWS_S3_REGION_NAME = env_vars["AWS_S3_REGION_NAME"]
else:
    DEFAULT_FILE_STORAGE = "inmemorystorage.InMemoryStorage"
