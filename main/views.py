from django.shortcuts import render, redirect,get_object_or_404
from articles.models import Post
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives , EmailMessage, send_mail

from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

from django.http import HttpResponseRedirect
from django.urls import reverse
# Create your views here.

def home(request):

    
    return render(request, 'base.html')


    










  