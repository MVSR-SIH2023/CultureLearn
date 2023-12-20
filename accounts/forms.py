from django.forms import ModelForm
from django import forms
from .models import *

class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        exclude = ['user','role','contributions','created','notification']
        labels = {
            'realname' : 'Name'
        }
        widgets = {
            'image': forms.FileInput(),
            'bio' : forms.Textarea(attrs={'rows':3})
        }
        
        
        
class ExpertUserForm(forms.ModelForm):
    class Meta:
        model = Pending
        fields = ['resume', 'letter']

class CreateWorkshopForm(forms.ModelForm):
    class Meta:
        model = Workshop
        fields = ['name',
                'description',
                'image' ,
                'mode' ,
                'start_date' ,
                'end_date' ,
                'duration' ,
                'Address' ,
                'Platform' ]