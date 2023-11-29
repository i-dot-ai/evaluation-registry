from django.core.management import BaseCommand
from openai import OpenAI
from tqdm import tqdm

from evaluation_registry import settings
from evaluation_registry.evaluations.models import Evaluation

CHATGPT_ROLE = """
You are a plain text formatter.

You will receive badly formatted text and reformat it with:
* proper capitalization of abbreviations, proper nouns and sentences
* sensible whitespace

Do not:
* remove or add words
* change the tone of the text

Please return the reformatted text without explanation.
"""

client = OpenAI(api_key=settings.OPENAI_KEY)


def reformat_evaluation(evaluation: Evaluation):
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": CHATGPT_ROLE},
            {"role": "user", "content": evaluation.brief_description},
        ],
        model="gpt-3.5-turbo",
    )

    evaluation.brief_description = chat_completion.choices[0].message.content
    evaluation.save()


class Command(BaseCommand):
    help = "Use ChatGPT to reformat evaluation descriptions"

    def add_arguments(self, parser):
        parser.add_argument("max_number_to_process", type=int, nargs="?", default=None)

    def handle(self, *args, **options):
        max_number_to_process = options["max_number_to_process"] or Evaluation.objects.count()

        progress_bar = tqdm(desc="Processing", total=max_number_to_process)
        for evaluation in Evaluation.objects.all().order_by("rsm_evaluation_id")[:max_number_to_process]:
            progress_bar.set_description(f"updating rsm-evaluation-id: {evaluation.rsm_evaluation_id}")
            reformat_evaluation(evaluation)
            progress_bar.update(1)

        progress_bar.close()
        self.stdout.write(self.style.SUCCESS("reformatting text complete"))
