from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
from . import models
from django.core.exceptions import ValidationError

class StudentUserForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already exists")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.save()
        group = Group.objects.get(name='STUDENT')
        user.groups.add(group)
        return user

class SuperUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_superuser = True
        user.save()
        group = Group.objects.get(name='STUDENT')
        group.user_set.remove(user)
        return user

class StudentForm(forms.ModelForm):
    class Meta:
        model = models.Student
        fields = [ 'email']