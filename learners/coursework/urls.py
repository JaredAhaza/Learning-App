from django.urls import path
from . import views
from .views.timetable import teacher_timetable, student_timetable, add_time_slot, remove_time_slot

urlpatterns = [
    # ... existing urls ...
    
    # Timetable URLs
    path('teacher/timetable/', teacher_timetable, name='teacher_timetable'),
    path('student/timetable/', student_timetable, name='student_timetable'),
    path('lesson/<int:lesson_id>/add-time-slot/', add_time_slot, name='add_time_slot'),
    path('time-slot/<int:time_slot_id>/remove/', remove_time_slot, name='remove_time_slot'),
]