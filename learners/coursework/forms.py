from django import forms
from .models import *

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['course_id', 'course_name', 'course_code', 'description', 'instructions', 'credits']

class CohortForm(forms.ModelForm):
    class Meta:
        model = Cohort
        fields = ['cohort_id', 'course', 'name', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'})
        }

class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ['unit_id', 'cohort', 'unit_name', 'unit_code', 'description']