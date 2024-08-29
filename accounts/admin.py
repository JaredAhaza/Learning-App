from django.contrib import admin
from .models import *
from django.utils.html import format_html

# Register your models here.
class StudentAdmin(admin.ModelAdmin):
    pass
admin.site.register(Student, StudentAdmin)

class StudentProfileAdmin(admin.ModelAdmin):
    pass
admin.site.register(StudentProfile, StudentProfileAdmin)