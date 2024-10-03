# coursework/admin.py
from django.contrib import admin
from .models import *

class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title',)



class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'created_at')
    search_fields = ('title', 'course__title')

class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'created_at')
    search_fields = ('title', 'lesson__title')

class QuizAdmin(admin.ModelAdmin):
    list_display = ('topic', 'name')
    search_fields = ('topic', 'topic__title')

class TopicProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'topic', 'opened', 'completed', 'created_at')
    search_fields = ('student__name', 'topic__title')

class QuizItemProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz_item', 'answered', 'correct', 'created_at')
    search_fields = ('student__name', 'quiz_item__question')


admin.site.register(Quiz, verbose_name='Quiz', verbose_name_plural='Quizzes')

class AnswerInLine(admin.TabularInline):
    model = Answer
    
class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInLine]
    
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer)
admin.site.register(Marks_Of_User)
admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(TopicProgress, TopicProgressAdmin)
admin.site.register(QuizItemProgress, QuizItemProgressAdmin)