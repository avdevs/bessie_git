from django.db import models
from users.models import User

class Response(models.Model):
    question_number = models.IntegerField()
    score = models.IntegerField()

    def __str__(self):
        return f"Q{self.question_number}: {self.score}"
    
class QuizResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    physical_health = models.FloatField()
    mental_health = models.FloatField()
    self_care = models.FloatField()
    emotional_health = models.FloatField()
    emotional_distress = models.FloatField()

class QuizResultComments(models.Model):
    quiz = models.ForeignKey(QuizResult, on_delete=models.CASCADE)
    physical_health = models.TextField()
    mental_health = models.TextField()
    self_care = models.TextField()
    emotional_health = models.TextField()
    emotional_distress = models.TextField()    
