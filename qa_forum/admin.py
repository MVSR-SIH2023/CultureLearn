from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Question)
admin.site.register(Answer)
#admin.site.register(AnswerComment)
#admin.site.register(QuestionComment)
admin.site.register(AnswerVote)