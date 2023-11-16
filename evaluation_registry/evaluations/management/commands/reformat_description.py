from django.core.management import BaseCommand
from openai import OpenAI
from tqdm import tqdm

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


class Command(BaseCommand):
    help = "Use ChatGPT to reformat evaluation descriptions"

    def add_arguments(self, parser):
        parser.add_argument("api_key", type=str)
        parser.add_argument("max_number_to_process", type=int)

    def handle(self, *args, **options):
        api_key = options["api_key"]
        max_number_to_process = options["max_number_to_process"] or Evaluation.objects.count()

        client = OpenAI(
            api_key=api_key,
        )

        progress_bar = tqdm(desc="Processing", total=max_number_to_process)
        for evaluation in Evaluation.objects.all()[:max_number_to_process]:
            progress_bar.set_description(f"updating rsm-evaluation-id: {evaluation.rsm_evaluation_id}")
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": CHATGPT_ROLE},
                    {"role": "user", "content": evaluation.brief_description},
                ],
                model="gpt-3.5-turbo",
            )

            evaluation.brief_description = chat_completion.choices[0].message.content
            evaluation.save()

            progress_bar.update(1)

        progress_bar.close()
        self.stdout.write(self.style.SUCCESS("reformatting text complete"))
