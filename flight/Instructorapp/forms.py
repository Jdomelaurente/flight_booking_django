# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
import re

User = get_user_model()  # ✅ use your custom user model

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Only @gmail.com or @csucc.edu.ph emails allowed")

    class Meta:
        model = User  # ✅ now it uses master.User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control ps-5 rounded-pill'
            field.widget.attrs['placeholder'] = field.label

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if username.isupper():
            raise forms.ValidationError("Username cannot be all uppercase letters.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not (email.endswith("@gmail.com") or email.endswith("@csucc.edu.ph")):
            raise forms.ValidationError("Email must be @gmail.com or @csucc.edu.ph")
        return email

    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        if not re.search(r'\d', password) or not re.search(r'[A-Za-z]', password):
            raise forms.ValidationError("Password must contain both letters and numbers.")
        return password
