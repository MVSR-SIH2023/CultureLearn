from django.contrib import admin
from .models import *
from django import forms
from django.contrib.auth.admin import UserAdmin


     
    
admin.site.register(User),
admin.site.register(Profile),  
admin.site.register(Follow) 
admin.site.register(Pending),
admin.site.register(Workshop),
admin.site.register(Workshop_register),
admin.site.register(Workshop_messeges),
admin.site.register(notification),
admin.site.register(static_pages),
    
# Register your models here.
