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

class OnlineClassForm(forms.ModelForm):
    class Meta:
        model = OnlineClass
        fields = ['title', 'description', 'meeting_link', 'meeting_platform', 'start_time', 'duration']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = [
            'title', 'description', 'class_type', 'content',
            'meeting_link', 'meeting_platform', 'start_time', 'duration',
            'video_url', 'reading_materials', 'estimated_completion_time'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'content': forms.Textarea(attrs={'rows': 6}),
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make online class fields required only when class_type is ONLINE
        self.fields['meeting_link'].required = False
        self.fields['meeting_platform'].required = False
        self.fields['start_time'].required = False
        self.fields['duration'].required = False
        self.fields['video_url'].required = False

    def clean(self):
        cleaned_data = super().clean()
        class_type = cleaned_data.get('class_type')
        
        if class_type == 'ONLINE':
            if not cleaned_data.get('meeting_link'):
                self.add_error('meeting_link', 'Meeting link is required for online classes')
            if not cleaned_data.get('meeting_platform'):
                self.add_error('meeting_platform', 'Meeting platform is required for online classes')
            if not cleaned_data.get('start_time'):
                self.add_error('start_time', 'Start time is required for online classes')
            if not cleaned_data.get('duration'):
                self.add_error('duration', 'Duration is required for online classes')
        elif class_type == 'PRERECORDED':
            if not cleaned_data.get('video_url'):
                self.add_error('video_url', 'Video URL is required for pre-recorded lessons')
        
        return cleaned_data