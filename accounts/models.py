from django.db import models
from django.contrib.auth.models import User
import uuid

class Student(models.Model):
    email = models.EmailField(unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student')
    groups = models.ManyToManyField(User, related_name='student_groups')
    user_permissions = models.ManyToManyField(User, related_name='student_permissions')
    student_id = models.CharField(max_length=3, primary_key=True)

    def save(self, *args, **kwargs):
        if not self.student_id:
            last_student = Student.objects.order_by('student_id').last()
            if last_student:
                next_id = int(last_student.student_id[2:]) + 1
            else:
                next_id = 1
            self.student_id = f"IL{next_id:03d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}"


class StudentProfile(models.Model):
    Gender = (
        ('Male', 'M'),
        ('Female', 'F'),
        ('Rather not say', 'RNS'),
    )
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    gender = models.CharField(blank=True, choices=Gender, max_length=20)

    
    def __str__(self):
        return f"Student Profile for {self.student.user}"