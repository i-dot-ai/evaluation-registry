import factory

from evaluation_registry.evaluations.models import Evaluation


class EvaluationFactory(factory.Factory):
    class Meta:
        model = Evaluation
