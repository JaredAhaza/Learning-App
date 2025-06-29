from rest_framework import serializers
from accounts.models import Student, StudentProfile, Teacher, TeacherProfile
from coursework.models import (
    Course, Cohort, Enrollment, EnrollmentRequest, Unit, Lesson, Topic,
    Quiz, Question, Answer, StudentQuizSubmission, StudentAnswer,
    Project, ProjectSubmission, LessonProgress, TopicProgress,
    QuizItemProgress, OnlineClass, TimeSlot
)
from django.contrib.auth.models import User


# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


# Student Serializers
class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Student
        fields = ['student_id', 'email', 'user']


class StudentProfileSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    
    class Meta:
        model = StudentProfile
        fields = [
            'id', 'student', 'profile_picture', 'phone_number', 
            'date_of_birth', 'bio', 'gender'
        ]


class StudentDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    profile = StudentProfileSerializer(source='studentprofile', read_only=True)
    
    class Meta:
        model = Student
        fields = ['student_id', 'email', 'user', 'profile']


# Teacher Serializers
class TeacherSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Teacher
        fields = ['teacher_id', 'email', 'user']


class TeacherProfileSerializer(serializers.ModelSerializer):
    teacher = TeacherSerializer(read_only=True)
    
    class Meta:
        model = TeacherProfile
        fields = [
            'id', 'teacher', 'profile_picture', 'phone_number', 
            'date_of_birth', 'bio', 'gender'
        ]


class TeacherDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    profile = TeacherProfileSerializer(source='teacherprofile', read_only=True)
    
    class Meta:
        model = Teacher
        fields = ['teacher_id', 'email', 'user', 'profile']


# Coursework Serializers
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            'course_id', 'course_name', 'course_code', 'description', 
            'instructions', 'credits'
        ]


class CohortSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    
    class Meta:
        model = Cohort
        fields = [
            'cohort_id', 'course', 'name', 'start_date', 'end_date'
        ]


class EnrollmentSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    cohort = CohortSerializer(read_only=True)
    
    class Meta:
        model = Enrollment
        fields = [
            'id', 'student', 'cohort', 'enrolled_at', 'status', 'progress'
        ]


class EnrollmentRequestSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    cohort = CohortSerializer(read_only=True)
    reviewed_by = TeacherSerializer(read_only=True)
    
    class Meta:
        model = EnrollmentRequest
        fields = [
            'id', 'student', 'cohort', 'requested_at', 'status', 
            'notes', 'reviewed_by', 'reviewed_at'
        ]


class UnitSerializer(serializers.ModelSerializer):
    cohort = CohortSerializer(read_only=True)
    teacher = TeacherSerializer(read_only=True)
    
    class Meta:
        model = Unit
        fields = [
            'unit_id', 'cohort', 'unit_name', 'unit_code', 
            'description', 'learning_outcomes', 'teacher'
        ]


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = [
            'id', 'lesson', 'title', 'content_type', 'content_text',
            'content_pdf', 'content_video', 'created_at'
        ]


class LessonSerializer(serializers.ModelSerializer):
    unit = UnitSerializer(read_only=True)
    teacher = TeacherSerializer(read_only=True)
    topics = TopicSerializer(many=True, read_only=True)
    
    class Meta:
        model = Lesson
        fields = [
            'id', 'unit', 'title', 'description', 'class_type', 'content',
            'meeting_link', 'meeting_platform', 'start_time', 'duration',
            'video_url', 'reading_materials', 'estimated_completion_time',
            'created_at', 'updated_at', 'teacher', 'topics'
        ]


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'question', 'content', 'correct']


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model = Question
        fields = [
            'id', 'quiz', 'question_content', 'question_type', 'answers'
        ]


class QuizSerializer(serializers.ModelSerializer):
    lesson = LessonSerializer(read_only=True)
    questions = QuestionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Quiz
        fields = [
            'id', 'lesson', 'name', 'desc', 'number_of_questions', 
            'time', 'questions'
        ]


class StudentAnswerSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(read_only=True)
    selected_answer = AnswerSerializer(read_only=True)
    
    class Meta:
        model = StudentAnswer
        fields = [
            'id', 'submission', 'question', 'selected_answer', 'text_answer'
        ]


class StudentQuizSubmissionSerializer(serializers.ModelSerializer):
    student = StudentProfileSerializer(read_only=True)
    quiz = QuizSerializer(read_only=True)
    answers = StudentAnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model = StudentQuizSubmission
        fields = [
            'id', 'student', 'quiz', 'submitted_at', 'score', 
            'reviewed', 'feedback', 'answers'
        ]


class ProjectSerializer(serializers.ModelSerializer):
    lesson = LessonSerializer(read_only=True)
    
    class Meta:
        model = Project
        fields = [
            'id', 'lesson', 'title', 'description', 'due_date'
        ]


class ProjectSubmissionSerializer(serializers.ModelSerializer):
    project = ProjectSerializer(read_only=True)
    student = StudentProfileSerializer(read_only=True)
    
    class Meta:
        model = ProjectSubmission
        fields = [
            'id', 'project', 'student', 'file', 'text', 'submitted_at',
            'reviewed', 'feedback', 'grade'
        ]


class LessonProgressSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    lesson = LessonSerializer(read_only=True)
    
    class Meta:
        model = LessonProgress
        fields = [
            'id', 'student', 'lesson', 'opened', 'completed', 'created_at'
        ]


class TopicProgressSerializer(serializers.ModelSerializer):
    student = StudentProfileSerializer(read_only=True)
    topic = TopicSerializer(read_only=True)
    
    class Meta:
        model = TopicProgress
        fields = [
            'id', 'student', 'topic', 'opened', 'completed', 'created_at'
        ]


class QuizItemProgressSerializer(serializers.ModelSerializer):
    student = StudentProfileSerializer(read_only=True)
    quiz_item = QuizSerializer(read_only=True)
    
    class Meta:
        model = QuizItemProgress
        fields = [
            'id', 'student', 'quiz_item', 'answered', 'correct', 'created_at'
        ]


class OnlineClassSerializer(serializers.ModelSerializer):
    unit = UnitSerializer(read_only=True)
    
    class Meta:
        model = OnlineClass
        fields = [
            'id', 'unit', 'title', 'description', 'meeting_link',
            'meeting_platform', 'start_time', 'duration', 'created_at', 'updated_at'
        ]


class TimeSlotSerializer(serializers.ModelSerializer):
    lesson = LessonSerializer(read_only=True)
    teacher = TeacherSerializer(read_only=True)
    
    class Meta:
        model = TimeSlot
        fields = [
            'id', 'day', 'start_time', 'end_time', 'lesson', 'teacher', 'is_booked'
        ]


# Nested Serializers for Dashboard
class UnitWithProgressSerializer(serializers.ModelSerializer):
    cohort = CohortSerializer(read_only=True)
    teacher = TeacherSerializer(read_only=True)
    lessons = LessonSerializer(many=True, read_only=True)
    
    class Meta:
        model = Unit
        fields = [
            'unit_id', 'cohort', 'unit_name', 'unit_code', 
            'description', 'learning_outcomes', 'teacher', 'lessons'
        ]


class StudentDashboardSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    profile = StudentProfileSerializer(source='studentprofile', read_only=True)
    enrollments = EnrollmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Student
        fields = ['student_id', 'email', 'user', 'profile', 'enrollments']


class TeacherDashboardSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    profile = TeacherProfileSerializer(source='teacherprofile', read_only=True)
    
    class Meta:
        model = Teacher
        fields = ['teacher_id', 'email', 'user', 'profile'] 