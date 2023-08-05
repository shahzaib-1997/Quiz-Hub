from django.contrib import admin
from .models import Topic, TopicQuestion, UserTopicScore, Room

# Register your models here.
@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'user']

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['topic', 'room']


@admin.register(TopicQuestion)
class TopicQuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'topic', 'correct_answer']

@admin.register(UserTopicScore)
class UserTopicScoreAdmin(admin.ModelAdmin):
    list_display = ['user', 'topic', 'score']

