from django.urls import path
from . import views

urlpatterns = [
    path('redirect_to_dashboard', views.redirect_to_dashboard, name='redirect_to_dashboard'),
    
    # Student URLs
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('update_student_profile/', views.update_student_profile, name='update_student_profile'),
    path('request_enrollment/<str:cohort_id>/', views.request_enrollment, name='request_enrollment'),
    path('unit/<str:unit_id>/lessons/', views.unit_lessons, name='unit_lessons'),
    path('unit/<str:unit_id>/online-classes/', views.unit_online_classes, name='unit_online_classes'),
    path('lesson/<int:lesson_id>/', views.student_lesson_view, name='student_lesson_view'),
    path('complete-lesson/<int:lesson_id>/', views.complete_lesson, name='complete_lesson'),
    
    # Teacher URLs
    path('teacher_dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('update_teacher_profile/', views.update_teacher_profile, name='update_teacher_profile'),
    path('teacher_courses/', views.teacher_courses, name='teacher_courses'),
    path('add_course/', views.add_course, name='add_course'),
    path('edit_course/<str:course_id>/', views.edit_course, name='edit_course'),
    path('edit_cohort/<str:cohort_id>/', views.edit_cohort, name='edit_cohort'),
    path('edit_unit/<str:unit_id>/', views.edit_unit, name='edit_unit'),    
    path('manage_enrollment_request/', views.manage_enrollment_requests, name='manage_enrollment_requests'),
    path('lesson/<int:lesson_id>/manage/', views.teacher_lesson_view, name='teacher_lesson_view'),
    path('lesson/<int:lesson_id>/delete/', views.delete_lesson, name='delete_lesson'),
    path('online-class/<int:class_id>/delete/', views.delete_online_class, name='delete_online_class'),
]