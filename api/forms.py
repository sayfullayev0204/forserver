from django import forms
from django.contrib.auth.models import User


class ChangeLoginPasswordForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    username = forms.CharField(max_length=150, required=True)

    class Meta:
        model = User
        fields = ["username", "password"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


from django import forms
from django.contrib.auth.forms import AuthenticationForm


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
