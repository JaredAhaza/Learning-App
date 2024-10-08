from django.contrib import admin
from .models import *
from django.utils.html import format_html

# Register your models here.
class StudentAdmin(admin.ModelAdmin):
    pass
admin.site.register(Student, StudentAdmin)

class StudentProfileAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if not obj.name:
            try:
                student = Student.objects.get(user=request.user)
                obj.name = student.user.get_full_name()
            except Student.DoesNotExist:
                pass
        super().save_model(request, obj, form, change)
admin.site.register(StudentProfile, StudentProfileAdmin)


class TeacherAdmin(admin.ModelAdmin):
    pass
admin.site.register(Teacher, TeacherAdmin)

class TeacherProfileAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if not obj.name:
            try:
                teacher = Student.objects.get(user=request.user)
                obj.name = teacher.user.get__full__name()
            except Teacher.DoesNotExist:
                pass    
        super().save_model(request, obj, form, change)
admin.site.register(TeacherProfile, TeacherProfileAdmin)