from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
import re

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Only @gmail.com or @csucc.edu.ph emails allowed")
    role = forms.ChoiceField(
        choices=[('', '-- Select Role --')] + list(User.ROLE_CHOICES),
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control ps-5 rounded-pill'
        })
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "role")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'role':  # role already has its class
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
    
    def clean_role(self):
        role = self.cleaned_data.get("role")
        if not role:
            raise forms.ValidationError("Please select a role.")
        return role