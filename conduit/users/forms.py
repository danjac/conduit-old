# Django
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm as BaseUserChangeForm
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm

# Third Party Libraries
from allauth.account.adapter import get_adapter
from allauth.account.forms import PasswordField, PasswordVerificationMixin

User = get_user_model()


class UserChangeForm(BaseUserChangeForm):
    class Meta(BaseUserChangeForm.Meta):
        model = User


class UserCreationForm(BaseUserCreationForm):
    class Meta(BaseUserCreationForm.Meta):
        model = User


class UserForm(PasswordVerificationMixin, forms.ModelForm):

    password1 = PasswordField(label="New Password", required=False)
    password2 = PasswordField(label="New Password (again)", required=False)

    class Meta:
        model = User
        fields = ("name", "image", "bio", "email")

    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        if password:
            get_adapter().clean_password(password, self.instance)
        return password

    def save(self):
        instance = super().save(commit=False)
        password = self.cleaned_data.get("password1")
        if password:
            get_adapter().set_password(instance, password)
        else:
            instance.save()
        return instance
