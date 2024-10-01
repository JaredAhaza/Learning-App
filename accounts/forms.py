from django import forms
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.forms import UserCreationForm
from . import models
from django.core.exceptions import ValidationError
from django.forms import DateInput
from django.contrib.contenttypes.models import ContentType

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
        superuser_group = Group.objects.get_or_create(name='SUPERUSER')
        user.groups.add(superuser_group)

        view_student_permission, created = Permission.objects.get_or_create(
            codename='view_student',
            name = 'Can view student group',
            content_type = ContentType.objects.get_for_model(Group)
        )

        manage_student_permission, created = Permission.objects.get_or_create(
            codename='manage_student',
            name = 'Can manage student group',
            content_type = ContentType.objects.get_for_model(Group)
        )

        view_steacher_permission, created = Permission.objects.get_or_create(
            codename='view_teacher',
            name = 'Can view teacher group',
            content_type = ContentType.objects.get_for_model(Group)
        )

        manage_teacher_permission, created = Permission.objects.get_or_create(
            codename='manage_teacher',
            name = 'Can manage teacher group',
            content_type = ContentType.objects.get_for_model(Group)
        )

        superuser_group.permissions.add(view_student_permission)
        superuser_group.permissions.add(manage_student_permission)
        superuser_group.permissions.add(view_steacher_permission)
        superuser_group.permissions.add(manage_teacher_permission)

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


class TeacherUserForm(UserCreationForm):
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
        group = Group.objects.get(name='TEACHER')
        user.groups.add(group)
        return user
    

class TeacherForm(forms.ModelForm):
    class Meta:
        model = models.Teacher
        fields = [ 'email']


class TeacherProfileForm(forms.ModelForm):
    date_of_birth = forms.DateField(widget=DateInput(format='%Y-%m-%d'))  # Use consistent format

    class Meta:
        model = models.TeacherProfile
        fields = ['date_of_birth', 'phone_number', 'bio', 'profile_picture', 'gender']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'class': 'input--style-4 js-datepicker', 'type': 'text', 'placeholder': 'YYYY-MM-DD'}),
            'gender': forms.RadioSelect
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['profile_picture'].required = False