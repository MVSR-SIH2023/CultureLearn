from django.forms import ModelForm
from django import forms
from .models import *

from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget

from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content','image','tags']
        labels = {
            'tags' : 'Category'
        }
        
class PostContentForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget())
    class Meta:
        model = Post
        fields = ['content','image'] 
        

        

