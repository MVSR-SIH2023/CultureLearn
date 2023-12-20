from django import forms
from .models import Question,Answer
from ckeditor_uploader.widgets import CKEditorUploadingWidget

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['title',  'tags']

    def __init__(self, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)


