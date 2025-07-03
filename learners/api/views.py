from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from accounts.models import Student, StudentProfile, Teacher, TeacherProfile
from coursework.models import (
    Course, Cohort, Enrollment, EnrollmentRequest, Unit, Lesson, Topic,
    Quiz, Question, Answer, StudentQuizSubmission, StudentAnswer,
    Project, ProjectSubmission, LessonProgress, TopicProgress,
    QuizItemProgress, OnlineClass, TimeSlot
)
from .serializers import (
    UserSerializer, StudentSerializer, StudentProfileSerializer, StudentDetailSerializer,
    TeacherSerializer, TeacherProfileSerializer, TeacherDetailSerializer,
    CourseSerializer, CohortSerializer, EnrollmentSerializer, EnrollmentRequestSerializer,
    UnitSerializer, TopicSerializer, LessonSerializer, AnswerSerializer, QuestionSerializer,
    QuizSerializer, StudentAnswerSerializer, StudentQuizSubmissionSerializer,
    ProjectSerializer, ProjectSubmissionSerializer, LessonProgressSerializer,
    TopicProgressSerializer, QuizItemProgressSerializer, OnlineClassSerializer,
    TimeSlotSerializer, UnitWithProgressSerializer, StudentDashboardSerializer,
    TeacherDashboardSerializer
)


# Authentication Views
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                login(request, user)
                # Check if user is a student or teacher
                try:
                    student = Student.objects.get(user=user)
                    return Response({
                        'user_type': 'student',
                        'user_id': user.id,
                        'username': user.username,
                        'student_id': student.student_id
                    })
                except Student.DoesNotExist:
                    try:
                        teacher = Teacher.objects.get(user=user)
                        return Response({
                            'user_type': 'teacher',
                            'user_id': user.id,
                            'username': user.username,
                            'teacher_id': teacher.teacher_id
                        })
                    except Teacher.DoesNotExist:
                        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


# Student Views
class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return StudentDetailSerializer
        return StudentSerializer


class StudentProfileViewSet(viewsets.ModelViewSet):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer


# Teacher Views
class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TeacherDetailSerializer
        return TeacherSerializer


class TeacherProfileViewSet(viewsets.ModelViewSet):
    queryset = TeacherProfile.objects.all()
    serializer_class = TeacherProfileSerializer


# Coursework Views
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class CohortViewSet(viewsets.ModelViewSet):
    queryset = Cohort.objects.all()
    serializer_class = CohortSerializer
    
    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        cohort = self.get_object()
        enrollments = Enrollment.objects.filter(cohort=cohort, status='active')
        students = [enrollment.student for enrollment in enrollments]
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    
    def get_queryset(self):
        queryset = Enrollment.objects.all()
        student_id = self.request.query_params.get('student', None)
        cohort_id = self.request.query_params.get('cohort', None)
        status_filter = self.request.query_params.get('status', None)
        
        if student_id:
            queryset = queryset.filter(student__student_id=student_id)
        if cohort_id:
            queryset = queryset.filter(cohort__cohort_id=cohort_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        return queryset


class EnrollmentRequestViewSet(viewsets.ModelViewSet):
    queryset = EnrollmentRequest.objects.all()
    serializer_class = EnrollmentRequestSerializer
    
    def get_queryset(self):
        queryset = EnrollmentRequest.objects.all()
        student_id = self.request.query_params.get('student', None)
        cohort_id = self.request.query_params.get('cohort', None)
        status_filter = self.request.query_params.get('status', None)
        
        if student_id:
            queryset = queryset.filter(student__student_id=student_id)
        if cohort_id:
            queryset = queryset.filter(cohort__cohort_id=cohort_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        return queryset


class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    
    def get_queryset(self):
        queryset = Unit.objects.all()
        cohort_id = self.request.query_params.get('cohort', None)
        teacher_id = self.request.query_params.get('teacher', None)
        
        if cohort_id:
            queryset = queryset.filter(cohort__cohort_id=cohort_id)
        if teacher_id:
            queryset = queryset.filter(teacher__teacher_id=teacher_id)
            
        return queryset
    
    @action(detail=True, methods=['get'])
    def lessons(self, request, pk=None):
        unit = self.get_object()
        lessons = unit.lessons.all()
        serializer = LessonSerializer(lessons, many=True)
        return Response(serializer.data)


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    
    def get_queryset(self):
        queryset = Lesson.objects.all()
        unit_id = self.request.query_params.get('unit', None)
        teacher_id = self.request.query_params.get('teacher', None)
        class_type = self.request.query_params.get('class_type', None)
        
        if unit_id:
            queryset = queryset.filter(unit__unit_id=unit_id)
        if teacher_id:
            queryset = queryset.filter(teacher__teacher_id=teacher_id)
        if class_type:
            queryset = queryset.filter(class_type=class_type)
            
        return queryset
    
    @action(detail=True, methods=['get'])
    def topics(self, request, pk=None):
        lesson = self.get_object()
        topics = lesson.topic_set.all()
        serializer = TopicSerializer(topics, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def quiz(self, request, pk=None):
        lesson = self.get_object()
        try:
            quiz = lesson.quiz
            serializer = QuizSerializer(quiz)
            return Response(serializer.data)
        except Quiz.DoesNotExist:
            return Response({'error': 'No quiz found for this lesson'}, status=status.HTTP_404_NOT_FOUND)


class TopicViewSet(viewsets.ModelViewSet):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    
    def get_queryset(self):
        queryset = Topic.objects.all()
        lesson_id = self.request.query_params.get('lesson', None)
        
        if lesson_id:
            queryset = queryset.filter(lesson_id=lesson_id)
            
        return queryset


class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        quiz = self.get_object()
        student_id = request.data.get('student_id')
        
        try:
            student = Student.objects.get(student_id=student_id)
            student_profile = StudentProfile.objects.get(student=student)
        except (Student.DoesNotExist, StudentProfile.DoesNotExist):
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Create submission
        submission = StudentQuizSubmission.objects.create(
            student=student_profile,
            quiz=quiz
        )
        
        # Process answers
        answers_data = request.data.get('answers', [])
        for answer_data in answers_data:
            question_id = answer_data.get('question_id')
            selected_answer_id = answer_data.get('selected_answer_id')
            text_answer = answer_data.get('text_answer')
            
            try:
                question = Question.objects.get(id=question_id)
                selected_answer = None
                if selected_answer_id:
                    selected_answer = Answer.objects.get(id=selected_answer_id)
                
                StudentAnswer.objects.create(
                    submission=submission,
                    question=question,
                    selected_answer=selected_answer,
                    text_answer=text_answer
                )
            except (Question.DoesNotExist, Answer.DoesNotExist):
                continue
        
        # Auto-mark the submission
        submission.auto_mark()
        
        serializer = StudentQuizSubmissionSerializer(submission)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    
    def get_queryset(self):
        queryset = Question.objects.all()
        quiz_id = self.request.query_params.get('quiz', None)
        
        if quiz_id:
            queryset = queryset.filter(quiz_id=quiz_id)
            
        return queryset


class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    
    def get_queryset(self):
        queryset = Answer.objects.all()
        question_id = self.request.query_params.get('question', None)
        
        if question_id:
            queryset = queryset.filter(question_id=question_id)
            
        return queryset


class StudentQuizSubmissionViewSet(viewsets.ModelViewSet):
    queryset = StudentQuizSubmission.objects.all()
    serializer_class = StudentQuizSubmissionSerializer
    
    def get_queryset(self):
        queryset = StudentQuizSubmission.objects.all()
        student_id = self.request.query_params.get('student', None)
        quiz_id = self.request.query_params.get('quiz', None)
        
        if student_id:
            queryset = queryset.filter(student__student__student_id=student_id)
        if quiz_id:
            queryset = queryset.filter(quiz_id=quiz_id)
            
        return queryset


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    
    def get_queryset(self):
        queryset = Project.objects.all()
        lesson_id = self.request.query_params.get('lesson', None)
        
        if lesson_id:
            queryset = queryset.filter(lesson_id=lesson_id)
            
        return queryset


class ProjectSubmissionViewSet(viewsets.ModelViewSet):
    queryset = ProjectSubmission.objects.all()
    serializer_class = ProjectSubmissionSerializer
    
    def get_queryset(self):
        queryset = ProjectSubmission.objects.all()
        project_id = self.request.query_params.get('project', None)
        student_id = self.request.query_params.get('student', None)
        
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if student_id:
            queryset = queryset.filter(student__student__student_id=student_id)
            
        return queryset


class LessonProgressViewSet(viewsets.ModelViewSet):
    queryset = LessonProgress.objects.all()
    serializer_class = LessonProgressSerializer
    
    def get_queryset(self):
        queryset = LessonProgress.objects.all()
        student_id = self.request.query_params.get('student', None)
        lesson_id = self.request.query_params.get('lesson', None)
        
        if student_id:
            queryset = queryset.filter(student__student_id=student_id)
        if lesson_id:
            queryset = queryset.filter(lesson_id=lesson_id)
            
        return queryset


class TopicProgressViewSet(viewsets.ModelViewSet):
    queryset = TopicProgress.objects.all()
    serializer_class = TopicProgressSerializer
    
    def get_queryset(self):
        queryset = TopicProgress.objects.all()
        student_id = self.request.query_params.get('student', None)
        topic_id = self.request.query_params.get('topic', None)
        
        if student_id:
            queryset = queryset.filter(student__student__student_id=student_id)
        if topic_id:
            queryset = queryset.filter(topic_id=topic_id)
            
        return queryset


class OnlineClassViewSet(viewsets.ModelViewSet):
    queryset = OnlineClass.objects.all()
    serializer_class = OnlineClassSerializer
    
    def get_queryset(self):
        queryset = OnlineClass.objects.all()
        unit_id = self.request.query_params.get('unit', None)
        
        if unit_id:
            queryset = queryset.filter(unit__unit_id=unit_id)
            
        return queryset


class TimeSlotViewSet(viewsets.ModelViewSet):
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer
    
    def get_queryset(self):
        queryset = TimeSlot.objects.all()
        teacher_id = self.request.query_params.get('teacher', None)
        lesson_id = self.request.query_params.get('lesson', None)
        day = self.request.query_params.get('day', None)
        
        if teacher_id:
            queryset = queryset.filter(teacher__teacher_id=teacher_id)
        if lesson_id:
            queryset = queryset.filter(lesson_id=lesson_id)
        if day:
            queryset = queryset.filter(day=day)
            
        return queryset


# Dashboard Views
class StudentDashboardView(APIView):
    def get(self, request, student_id):
        try:
            student = Student.objects.get(student_id=student_id)
            serializer = StudentDashboardSerializer(student)
            return Response(serializer.data)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)


class TeacherDashboardView(APIView):
    def get(self, request, teacher_id):
        try:
            teacher = Teacher.objects.get(teacher_id=teacher_id)
            serializer = TeacherDashboardSerializer(teacher)
            return Response(serializer.data)
        except Teacher.DoesNotExist:
            return Response({'error': 'Teacher not found'}, status=status.HTTP_404_NOT_FOUND)


# Custom API Views
class StudentEnrollmentsView(APIView):
    def get(self, request, student_id):
        try:
            student = Student.objects.get(student_id=student_id)
            enrollments = Enrollment.objects.filter(student=student)
            serializer = EnrollmentSerializer(enrollments, many=True)
            return Response(serializer.data)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)


class StudentUnitsView(APIView):
    def get(self, request, student_id):
        try:
            student = Student.objects.get(student_id=student_id)
            enrollments = Enrollment.objects.filter(student=student, status='active')
            units = []
            for enrollment in enrollments:
                units.extend(enrollment.cohort.units.all())
            serializer = UnitSerializer(units, many=True)
            return Response(serializer.data)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)


class StudentLessonsView(APIView):
    def get(self, request, student_id):
        try:
            student = Student.objects.get(student_id=student_id)
            enrollments = Enrollment.objects.filter(student=student, status='active')
            units = []
            for enrollment in enrollments:
                units.extend(enrollment.cohort.units.all())
            lessons = Lesson.objects.filter(unit__in=units)
            serializer = LessonSerializer(lessons, many=True)
            return Response(serializer.data)
        except Student.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)


class TeacherUnitsView(APIView):
    def get(self, request, teacher_id):
        try:
            teacher = Teacher.objects.get(teacher_id=teacher_id)
            units = Unit.objects.filter(teacher=teacher)
            serializer = UnitSerializer(units, many=True)
            return Response(serializer.data)
        except Teacher.DoesNotExist:
            return Response({'error': 'Teacher not found'}, status=status.HTTP_404_NOT_FOUND)


class TeacherLessonsView(APIView):
    def get(self, request, teacher_id):
        try:
            teacher = Teacher.objects.get(teacher_id=teacher_id)
            lessons = Lesson.objects.filter(teacher=teacher)
            serializer = LessonSerializer(lessons, many=True)
            return Response(serializer.data)
        except Teacher.DoesNotExist:
            return Response({'error': 'Teacher not found'}, status=status.HTTP_404_NOT_FOUND)


@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        logout(request)
        response = Response({'success': 'Logged out successfully.'}, status=status.HTTP_200_OK)
        response.delete_cookie('sessionid')
        response.delete_cookie('csrftoken')
        return response 