from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from .models import *

def expert_user_required(view_func):
    def wrapper(request, *args, **kwargs):
        print("wrapper called")
        if request.user.is_authenticated :
            if request.user.profile.role == 'expert':
                return view_func(request, *args, **kwargs)
            
            else:
                return redirect(reverse('accounts:become_expert')) 
    return wrapper

def access_messeges(view_func):
    def wrapper(request, id, *args, **kwargs):
        if request.method=="POST" and request.user.is_authenticated and request.user==Workshop.objects.get(id=id).organiser:
            return view_func(request, id, *args, **kwargs)
        elif request.method=="GET" and Workshop_register.objects.filter(registered_user=request.user,workshop=Workshop.objects.get(id=id)).exists():
            return view_func(request, id, *args, **kwargs)
        else:
            return redirect("/workshop/"+str(id)+"/")
    return wrapper

def is_user_registered(view_func):
    def wrapper(request, id, *args, **kwargs):
        print("wrapper called with workshop_id:", id)
        if request.user.is_authenticated and Workshop_register.objects.filter(registered_user=request.user,workshop=Workshop.objects.get(id=id)).exists():
            return view_func(request, id, *args, **kwargs)
        elif Workshop.objects.get(id=id).organiser==request.user:
            return view_func(request, id, *args, **kwargs)
        else:
            return HttpResponse("not registered") 
    return wrapper
