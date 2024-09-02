from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    email = models.EmailField(unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student')
    groups = models.ManyToManyField(User, related_name='student_groups')
    user_permissions = models.ManyToManyField(User, related_name='student_permissions')


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

class Enrollment(models.Model):
    """Represents a student's enrollment in a course."""
    enr_student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    course = models.ForeignKey('coursework.Course', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.enr_student.name} - {self.course.title}"

class LessonProgress(models.Model):
    """Represents a student's progress on a lesson."""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    lesson = models.ForeignKey('coursework.Lesson', on_delete=models.CASCADE)
    opened = models.BooleanField(default=False)  # Has the student opened the lesson?
    completed = models.BooleanField(default=False)  # Has the student completed the lesson?
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.name} - {self.lesson.title}"