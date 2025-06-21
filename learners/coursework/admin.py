# coursework/admin.py
from django.contrib import admin
from tinymce.widgets import TinyMCE
from .models import *

class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_name', 'course_code', 'credits')
    list_filter = ('credits',)
    search_fields = ('course_name', 'course_code', 'description')
    fieldsets = (
        ('Basic Information', {
            'fields': ('course_id', 'course_name', 'course_code', 'credits')
        }),
        ('Course Details', {
            'fields': ('description', 'instructions')
        })
    )

    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()}
    }

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('day', 'start_time', 'end_time', 'lesson', 'teacher', 'is_booked')
    list_filter = ('day', 'is_booked', 'teacher')
    search_fields = ('lesson__title', 'teacher__user__username', 'teacher__user__email')
    ordering = ('day', 'start_time')
    raw_id_fields = ('lesson', 'teacher')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('lesson', 'teacher', 'teacher__user')

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'unit', 'class_type', 'teacher', 'get_status_display', 'created_at')
    list_filter = ('class_type', 'teacher', 'unit__cohort')
    search_fields = ('title', 'description', 'unit__unit_name', 'teacher__user__username')
    raw_id_fields = ('unit', 'teacher')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'unit', 'teacher', 'description', 'class_type')
        }),
        ('Content', {
            'fields': ('content', 'reading_materials', 'video_url')
        }),
        ('Online Class Settings', {
            'fields': ('meeting_link', 'meeting_platform', 'start_time', 'duration'),
            'classes': ('collapse',),
            'description': 'Settings for online classes'
        }),
        ('Time Management', {
            'fields': ('estimated_completion_time',)
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('unit', 'unit__cohort', 'teacher', 'teacher__user')

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 1

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('name', 'lesson', 'number_of_questions', 'time')
    list_filter = ('lesson',)
    search_fields = ('name', 'lesson__title')
    inlines = [QuestionInline]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_content', 'quiz', 'question_type')
    list_filter = ('quiz', 'question_type')
    search_fields = ('question_content', 'quiz__name')
    inlines = [AnswerInline]

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('content', 'question', 'correct')
    list_filter = ('correct', 'question__quiz')
    search_fields = ('content', 'question__question_content')

@admin.register(StudentQuizSubmission)
class StudentQuizSubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz', 'score', 'reviewed', 'submitted_at')
    list_filter = ('reviewed', 'quiz')
    search_fields = ('student__user__username', 'quiz__name')

@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ('submission', 'question', 'selected_answer', 'text_answer')
    list_filter = ('question__quiz',)
    search_fields = ('submission__student__user__username', 'question__question_content')

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'due_date')
    list_filter = ('lesson', 'due_date')
    search_fields = ('title', 'lesson__title')

@admin.register(ProjectSubmission)
class ProjectSubmissionAdmin(admin.ModelAdmin):
    list_display = ('project', 'student', 'grade', 'reviewed', 'submitted_at')
    list_filter = ('reviewed', 'project')
    search_fields = ('student__user__username', 'project__title')

class UnitInline(admin.TabularInline):
    model = Unit
    extra = 1
    fields = ('unit_id', 'unit_name', 'unit_code', 'teacher')

@admin.register(Cohort)
class CohortAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'start_date', 'end_date', 'get_student_count')
    list_filter = ('course', 'start_date', 'end_date')
    search_fields = ('name', 'course__course_name', 'course__course_code')
    date_hierarchy = 'start_date'
    inlines = [UnitInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('cohort_id', 'name', 'course')
        }),
        ('Schedule', {
            'fields': ('start_date', 'end_date')
        })
    )

    def get_student_count(self, obj):
        return obj.enrollment_set.count()
    get_student_count.short_description = 'Students'

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('unit_name', 'unit_code', 'cohort', 'teacher', 'get_lesson_count')
    list_filter = ('cohort', 'teacher')
    search_fields = ('unit_name', 'unit_code', 'description', 'learning_outcomes')
    fieldsets = (
        ('Basic Information', {
            'fields': ('unit_id', 'unit_name', 'unit_code', 'cohort', 'teacher')
        }),
        ('Content', {
            'fields': ('description', 'learning_outcomes')
        })
    )

    def get_lesson_count(self, obj):
        return obj.lessons.count()
    get_lesson_count.short_description = 'Lessons'

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'cohort', 'status', 'progress', 'enrolled_at')
    list_filter = ('status', 'cohort', 'enrolled_at')
    search_fields = ('student__user__username', 'cohort__name')

@admin.register(EnrollmentRequest)
class EnrollmentRequestAdmin(admin.ModelAdmin):
    list_display = ('student', 'cohort', 'status', 'requested_at', 'reviewed_at')
    list_filter = ('status', 'cohort', 'requested_at')
    search_fields = ('student__user__username', 'cohort__name')

@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'lesson', 'opened', 'completed', 'created_at')
    list_filter = ('opened', 'completed', 'created_at')
    search_fields = ('student__user__username', 'lesson__title')

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'content_type', 'created_at')
    list_filter = ('content_type', 'lesson')
    search_fields = ('title', 'lesson__title')

@admin.register(TopicProgress)
class TopicProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'topic', 'opened', 'completed', 'created_at')
    list_filter = ('opened', 'completed', 'created_at')
    search_fields = ('student__user__username', 'topic__title')

@admin.register(QuizItemProgress)
class QuizItemProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz_item', 'answered', 'correct', 'created_at')
    list_filter = ('answered', 'correct', 'created_at')
    search_fields = ('student__user__username', 'quiz_item__topic__title')

@admin.register(OnlineClass)
class OnlineClassAdmin(admin.ModelAdmin):
    list_display = ('title', 'unit', 'meeting_platform', 'start_time', 'duration')
    list_filter = ('meeting_platform', 'unit', 'start_time')
    search_fields = ('title', 'unit__unit_name')
    readonly_fields = ('created_at', 'updated_at')

# Register remaining models
admin.site.register(Course, CourseAdmin)