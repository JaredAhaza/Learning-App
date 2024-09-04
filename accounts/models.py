from django.db import models
from django.contrib.auth.models import User
import uuid

class Student(models.Model):
    email = models.EmailField(unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student')
    groups = models.ManyToManyField(User, related_name='student_groups')
    user_permissions = models.ManyToManyField(User, related_name='student_permissions')
    student_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


class StudentProfile(models.Model):
    Gender = (
        ('Male', 'M'),
        ('Female', 'F'),
        ('Rather not say', 'RNS'),
    )
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=False, null=False)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    gender = models.CharField(choices=Gender, max_length=20)

    
    def __str__(self):
        return self.name
