from django.db import models
from django.contrib.auth.models import AbstractUser, User

class Student(models.Model):
    email = models.EmailField(unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student')
    groups = models.ManyToManyField(User, related_name='student_groups')
    user_permissions = models.ManyToManyField(User, related_name='student_permissions')

class StudentProfile(models.Model):
    Edu_level = (
        ('Primary', 'PRI'),
        ('High School', 'HS'),
        ('University', 'UNI'),
    )
    Gender = (
        ('Male', 'M'),
        ('Female', 'F'),
        ('Rather not say', 'RNS'),
    )
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    mode_of_learning = models.CharField(max_length=20, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    education_level = models.CharField(choices=Edu_level, max_length=100, blank=True)
    gender = models.CharField(choices=Gender, max_length=20)