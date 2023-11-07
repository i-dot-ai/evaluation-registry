from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError


class EmailForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=100, widget=forms.EmailInput(attrs={"class": "govuk-input"}))

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email is None:
            return email

        if email.endswith(".gov.uk"):
            return email

        domain = email.split("@")[-1]  # Extract the domain part of the email
        if domain not in settings.ALLOWED_DOMAINS:
            raise ValidationError("This email domain is not allowed.")

        return email
