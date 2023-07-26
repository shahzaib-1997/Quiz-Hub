from rest_framework import serializers
from .models import QuizQuestion, Topic

class QuizQuestionSerializer(serializers.ModelSerializer):

    class Meta:
        model = QuizQuestion
        exclude = 'topic'


class TopicSerializer(serializers.ModelSerializer):

    class Meta:
        model = Topic
        fields = '__all__'
