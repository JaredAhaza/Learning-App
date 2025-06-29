from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'students', views.StudentViewSet)
router.register(r'student-profiles', views.StudentProfileViewSet)
router.register(r'teachers', views.TeacherViewSet)
router.register(r'teacher-profiles', views.TeacherProfileViewSet)
router.register(r'courses', views.CourseViewSet)
router.register(r'cohorts', views.CohortViewSet)
router.register(r'enrollments', views.EnrollmentViewSet)
router.register(r'enrollment-requests', views.EnrollmentRequestViewSet)
router.register(r'units', views.UnitViewSet)
router.register(r'lessons', views.LessonViewSet)
router.register(r'topics', views.TopicViewSet)
router.register(r'quizzes', views.QuizViewSet)
router.register(r'questions', views.QuestionViewSet)
router.register(r'answers', views.AnswerViewSet)
router.register(r'quiz-submissions', views.StudentQuizSubmissionViewSet)
router.register(r'projects', views.ProjectViewSet)
router.register(r'project-submissions', views.ProjectSubmissionViewSet)
router.register(r'lesson-progress', views.LessonProgressViewSet)
router.register(r'topic-progress', views.TopicProgressViewSet)
router.register(r'online-classes', views.OnlineClassViewSet)
router.register(r'time-slots', views.TimeSlotViewSet)

# The API URLs are now determined automatically by the router
urlpatterns = [
    # Authentication
    path('auth/login/', views.LoginView.as_view(), name='api_login'),
    
    # Dashboard endpoints
    path('dashboard/student/<str:student_id>/', views.StudentDashboardView.as_view(), name='api_student_dashboard'),
    path('dashboard/teacher/<str:teacher_id>/', views.TeacherDashboardView.as_view(), name='api_teacher_dashboard'),
    
    # Student-specific endpoints
    path('students/<str:student_id>/enrollments/', views.StudentEnrollmentsView.as_view(), name='api_student_enrollments'),
    path('students/<str:student_id>/units/', views.StudentUnitsView.as_view(), name='api_student_units'),
    path('students/<str:student_id>/lessons/', views.StudentLessonsView.as_view(), name='api_student_lessons'),
    
    # Teacher-specific endpoints
    path('teachers/<str:teacher_id>/units/', views.TeacherUnitsView.as_view(), name='api_teacher_units'),
    path('teachers/<str:teacher_id>/lessons/', views.TeacherLessonsView.as_view(), name='api_teacher_lessons'),
    
    # Include router URLs
    path('', include(router.urls)),
] 