from django.urls import path
from . import views
from .views import teacher_timetable, student_timetable, add_time_slot, remove_time_slot

urlpatterns = [
    # ... existing urls ...
    
    # Timetable URLs
    path('teacher/timetable/', teacher_timetable, name='teacher_timetable'),
    path('student/timetable/', student_timetable, name='student_timetable'),
    path('lesson/<int:lesson_id>/add-time-slot/', add_time_slot, name='add_time_slot'),
    path('time-slot/<int:time_slot_id>/remove/', remove_time_slot, name='remove_time_slot'),
    # Quiz URLs
    path('lesson/<int:lesson_id>/quiz/create/', views.create_quiz, name='create_quiz'),
    path('quiz/<int:quiz_id>/edit/', views.edit_quiz, name='edit_quiz'),
    path('quiz/<int:quiz_id>/add-question/', views.add_question, name='add_question'),
    path('question/<int:question_id>/add-answer/', views.add_answer, name='add_answer'),
    path('lesson/<int:lesson_id>/quiz/take/', views.take_quiz, name='take_quiz'),
    path('quiz/submission/<int:submission_id>/result/', views.quiz_result, name='quiz_result'),
    path('quiz/review/explanatory/', views.review_explanatory_answers, name='review_explanatory_answers'),
    path('quiz/review/explanatory/<int:submission_id>/', views.review_explanatory_detail, name='review_explanatory_detail'),
    # Project URLs
    path('lesson/<int:lesson_id>/project/create/', views.create_project, name='create_project'),
    path('project/<int:project_id>/submit/', views.submit_project, name='submit_project'),
    path('project/review/', views.review_projects, name='review_projects'),
    path('project/review/<int:submission_id>/', views.review_project_detail, name='review_project_detail'),
    path('project/submission/<int:submission_id>/result/', views.project_result, name='project_result'),
]