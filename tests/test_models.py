@pytest.mark.django_db
def test_evaluation(alice):
    evaluation = Evaluation.objects.create(created_by=alice)
    assert True