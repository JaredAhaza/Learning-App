from django import forms
from django.contrib.auth.models import User
from . import models
from django.core.exceptions import ValidationError

class StudentUserForm(forms.ModelForm):
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already exists")
        return email
    

class StudentForm(forms.ModelForm):
    class Meta:
        model = models.Student
        fields = ['groups', 'user', 'email']