from django.db import models
from accounts.models import User
from taggit.managers import TaggableManager
from django.urls import reverse

from PIL import Image
from django.utils.text import slugify
from django.conf import settings

# Create your models here.

#HitCountMixin need to know abt this mixin it was inherited by question class

class Question(models.Model):
    """Model class to contain every question in the forum"""
    
    title = models.CharField(max_length=200, blank=False) #title of question
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    tags = TaggableManager()
    reward = models.IntegerField(default=0)   #remove this field
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    closed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-pub_date']

    def get_question_url(self):
        return reverse('question-details', kwargs={'id': self.id})

    def __str__(self):
        return self.title
    
    

class Answer(models.Model):
    """Model class to contain every answer in the forum and to link it
    to the proper question."""
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.TextField()
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    updated = models.DateTimeField('date updated', auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.BooleanField(default=False)
    positive_votes = models.IntegerField(default=0)
    negative_votes = models.IntegerField(default=0)
    total_points = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        try:
            points = settings.QA_SETTINGS['reputation']['CREATE_ANSWER']

        except KeyError:
            points = 0

        self.user.profile.modify_reputation(points)
        self.total_points = self.positive_votes - self.negative_votes
        super(Answer, self).save(*args, **kwargs)

    def __str__(self):  # pragma: no cover
        return self.answer_text

    class Meta:
        ordering = ['-answer', '-pub_date']
    
        
class VoteParent(models.Model):
    """Abstract model to define the basic elements to every single vote."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    upvote_value = models.BooleanField(default=False)
    downvote_value = models.BooleanField(default=False)

    class Meta:
        abstract = True


class AnswerVote(VoteParent):
    """Model class to contain the votes for the answers."""
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('user', 'answer'),)

