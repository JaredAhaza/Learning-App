from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
from . import models
from django.core.exceptions import ValidationError
from django.forms import DateInput

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


class StudentProfileForm(forms.ModelForm):
    date_of_birth = forms.DateField(widget=DateInput(format='%Y-%m-%d'))  # Use consistent format

    class Meta:
        model = models.StudentProfile
        fields = ['date_of_birth', 'phone_number', 'bio', 'profile_picture', 'gender']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'class': 'input--style-4 js-datepicker', 'type': 'text', 'placeholder': 'YYYY-MM-DD'}),
            'gender': forms.RadioSelect
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['profile_picture'].required = False

    
    