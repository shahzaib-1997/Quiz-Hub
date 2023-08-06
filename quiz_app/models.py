from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class RoomManager(models.Manager):
    def user_rooms(self, user):
        return self.filter(user=user)
        

class Room(models.Model):

    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rooms')

    objects = RoomManager()

    def __str__(self):
        return f"{self.name}"


class Topic(models.Model):

    topic = models.CharField(max_length=255)
    room = models.ForeignKey(Room, related_name='topics', on_delete=models.CASCADE)

    def __str__(self):
        return self.topic


class TopicQuestion(models.Model):
    question_text = models.TextField()
    options = models.TextField() 
    correct_answer = models.CharField(max_length=255)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)

    def __str__(self):
        return self.question_text
    

class UserTopicScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    score = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.user.username} - {self.topic} - Score: {self.score}"
    
