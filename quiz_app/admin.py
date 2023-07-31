from django.contrib import admin
from .models import Topic, TopicQuestion, UserTopicScore

# Register your models here.
admin.site.register(Topic)

@admin.register(TopicQuestion)
class TopicQuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'topic', 'correct_answer']

@admin.register(UserTopicScore)
class UserTopicScoreAdmin(admin.ModelAdmin):
    list_display = ['user', 'topic', 'score']

