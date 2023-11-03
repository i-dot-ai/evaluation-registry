from django.shortcuts import render


def unauthorised_view(request):
    return render(request, "unauthorised.html", {}, status=401)


def login_required(func):
    def _inner(request, *args, **kwargs):
        if request.user.is_authenticated:
            return func(request, *args, **kwargs)
        else:
            return unauthorised_view(request)

    return _inner
