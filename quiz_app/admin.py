from django.contrib import admin
from .models import QuizQuestion, Topic, CompetitionEntry, TopicQuestion, UserTopicScore

# Register your models here.
admin.site.register(Topic)

# @admin.register(QuizQuestion)
# class QuizAdmin(admin.ModelAdmin):
#     list_display = ['truncated_question', 'correct_option']

#     def truncated_question(self, obj):
#         return obj.question_with_choices.split('?')[0] + '?'
    
#     truncated_question.short_description = 'Question'

@admin.register(TopicQuestion)
class TopicQuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'topic', 'correct_answer']

@admin.register(CompetitionEntry)
class CompetitionEntryAdmin(admin.ModelAdmin):
    list_display = ['user', 'topic', 'timestamp']

@admin.register(UserTopicScore)
class UserTopicScoreAdmin(admin.ModelAdmin):
    list_display = ['user', 'topic', 'score']

