from django import forms

from evaluation_registry.evaluations.models import Evaluation


class EvaluationCreateForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        fields = ["status", "title"]
