
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout,login,authenticate
from django.urls import reverse
from django.contrib import messages
from django.db.models import Count
from django.contrib import messages
from articles.models import Post,MainPodcast
from django.http import HttpResponse
from .models import *
from .forms import *
from .decorators import *
from django.core.paginator import Paginator
from django.utils import timezone
from django.utils.timezone import activate
from django.core.serializers import serialize
from django.http import JsonResponse
import pytz
from django.core.mail import send_mail
from django.conf import settings
from openai import OpenAI
import wikipedia
import requests
import datetime
from qa_forum.models import Question
# from allauth.account.utils import send_email_confirmation
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode , urlsafe_base64_decode
from django.utils.encoding import force_bytes , force_str
from  accounts.tokens import generate_token
from environ import Env


env = Env()
Env.read_env()

UserModel = get_user_model()


def send_welcome_mail(current_site,user, first_name, last_name, email):
    subject = "Welcome to CultureLearn"
    from_email = settings.EMAIL_HOST_USER
    
    #link_app = "http://localhost:8000/home"
    
    message2=render_to_string('registration/email.html',{
        'first_name': first_name,
        'last_name': last_name,
        'email': email,  
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.id)),
        'token':generate_token.make_token(user),
    })
    
    email=EmailMessage(
            subject,
            message2,
            settings.EMAIL_HOST_USER,
            [email],
        )
    email.content_subtype = "html" 
    email.send(fail_silently= True)





def password_reset_mail(user,request):
    subject = "Reset CultureLearn Password"
    
    token = generate_token.make_token(user)

    # Build the password reset link
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    password_reset_link = request.build_absolute_uri(f'/reset-password/{uid}/{token}/') 
    #link_app = "http://localhost:8000/home"
    
    message2=render_to_string('registration/password_reset_email.html',{
        'first_name': user.first_name,  
        'reset_link': password_reset_link,
        
    })
    
    email=EmailMessage(
            subject,
            message2,
            settings.EMAIL_HOST_USER,
            [user.email],
        )
    email.content_subtype = "html" 
    email.send(fail_silently= True)
    
    
def activate_user(request, uidb64, token):
    try:
        uid= force_str(urlsafe_base64_decode(uidb64))
        user=User.objects.get(id=uid)
    except(TypeError,ValueError,OverflowError,User.DoesNotExist):
        user= None
    if user is not None and generate_token.check_token(user,token):
        user.is_active=True
        user.save()
        login(request, user,backend='django.contrib.auth.backends.ModelBackend')
        return redirect("/home")
    else:
        return render(request,"registration/activation_failed.html")


from django.shortcuts import redirect
from django.urls import reverse



def forgot_password(request):
    if request.method == 'POST':
        user_email = request.POST.get('email')
        
        user = User.objects.filter(email=user_email).first()
        
        if user is not None:
            password_reset_mail(user,request)
            
            return redirect('{}?forgot_password=True'.format('/forgot-password/'))
        else:
            return JsonResponse({'error': 'Email not found.'})

    return render(request, 'registration/forgot_password.html')



def reset_password(request, uidb64, token):
    try:
        uid= force_str(urlsafe_base64_decode(uidb64))
        user=User.objects.get(id=uid)
        if user is not None and generate_token.check_token(user,token):
            if request.method == 'POST':
                password = request.POST.get('password')
                confirm_password = request.POST.get('confirm_password')

                if password == confirm_password:
                    # Set the new password
                    user.set_password(password)
                    user.save()
                        
                    return redirect('/login')  
                else:
                    
                    return redirect(request.path_info)
                
            return render(request, 'registration/reset_password.html')
        else:
            messages.error(request, 'Invalid token.')
            return redirect('/forgot-password')  # Redirect to forgot password page if token is invalid
    except(TypeError,ValueError,OverflowError,User.DoesNotExist):
        user= None
        return redirect('/forgot-password')

   
def signup(request):
    if request.method == 'POST' :
        try: 
            username=request.POST.get('username')
            print(username)
            first_name=request.POST.get('fname')
            last_name=request.POST.get('lname')
            email=request.POST.get('email')
            password =request.POST.get('pass1')
            confirm_password =request.POST.get('pass2')
            
            
            validate_password(password)
            
            if User.objects.filter(username=username):
                messages.error(request,"Username already Exist! please try some other Username")
                return redirect('/signup')

            if User.objects.filter(email=email):
                messages.error(request,'Email already registered! please try some other Email ')
                return redirect('/signup')
        

            if len(username)<5:
                messages.error(request,'Username must be greater than 4 characters')
                return redirect('/signup')
        
            if password != confirm_password:
                messages.error(request,"Passwords didn't match!")
                return redirect('/signup')

            if not username.isalnum():
                messages.error(request,"Username must be Alpha-Numeric!")
                return redirect('/signup')
            user = User.objects.create_user(username,email,password)
            user.first_name=first_name
            user.last_name=last_name
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            send_welcome_mail(current_site,user, first_name, last_name, email)
            
            
            return redirect('/home?activation_sent=true')
        except Exception and ValidationError as e:
            return render(request,'registration/signup.html',{'errors':e})
    else:
        pass
        return render(request, 'registration/signup.html')

def logout_user(request):
    logout(request)
    return redirect("/home")

    
        

class UsernameOrEmailBackend(object):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if username is None or password is None:
            return
        try:
            user = UserModel.objects.get(
                Q(username=username) | Q(email=username))
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user

    def user_can_authenticate(self, user):
        """
        Reject users with is_active=False. Custom user models that don't have
        that attribute are allowed.
        """
        is_active = getattr(user, 'is_active', None)
        return is_active or is_active is None

    def get_user(self, user_id):
        try:
            user = UserModel._default_manager.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
        return user if self.user_can_authenticate(user) else None

def login_user(request):
    if request.method == 'POST':
        username_or_email= request.POST['username_or_email']
        password = request.POST['password']

        
        user = authenticate(request,username=username_or_email, password=password)

        if user is not None :
            
            if user.is_active==True :
                login(request, user)
            
                return redirect('/home')  
        else:
            messages.error(request, 'username and password are incorrect')
            return render(request, 'registration/login.html')

    return render(request, 'registration/login.html')


    
@login_required
def profile_view(request,user_id=None):
    
    if user_id:
        profile = get_object_or_404(User, id= user_id).profile
    else:
        profile = request.user.profile #current user goes from homepage 
    
    followers_count=Follow.objects.filter(following=profile.user).count
    following_count=Follow.objects.filter(follower=profile.user).count
    written_articles=Post.objects.filter(author=profile.user.id)
    published_podcast=MainPodcast.objects.filter(author=profile.user.id)
    held_workshop=Workshop.objects.filter(organiser=profile.user.id)
    qas = Question.objects.filter(user = profile.user.id)
    
   
    context = {
        'profile' : profile,
        'followers_count':followers_count, 
        'following_count':following_count,
        'posts':written_articles,
        'main_podcasts':published_podcast,
        'workshops':held_workshop,
        'qas':qas,
        'user':request.user
    
    }
    
    return render(request, 'u_profile/profile.html', context)



@login_required
def update_profile(request):
    user = request.user
    profile = Profile.objects.get(user=user)

    if request.method == 'POST':
        if 'delete' in request.POST:  
            user.delete()  
            logout(request)  
            return redirect('/home')  
        else:
            if request.FILES.get('image'):  
                profile.image = request.FILES['image'] 
            if request.POST.get('bio'): 
                profile.bio = request.POST['bio']  

            profile.save()  
            
            return redirect("/profile")

    return render(request, 'u_profile/profile_edit.html', {'profile': profile})






@login_required
def profile_delete_view(request):
    user = request.user
    
    if request.method == 'POST':
        logout(request)
        user.delete()
        messages.success(request, 'Account deleted')
        return redirect('/home')
    
    return render(request, 'u_profile/profile_delete.html' )

def follow_user(request,id):
    if request.user.is_authenticated:
        if request.method=="GET":
            if Follow.objects.filter(follower = request.user ,following = User.objects.get(id=id)).exists():  
                return JsonResponse({'status':'UnFollow'})
            else:
                return JsonResponse({'status':'Follow'})
        else:
            print(request.POST.get('user_id'))
            if Follow.objects.filter(follower = request.user ,following = User.objects.get(id=id)).exists():  #unfollow
                Follow.objects.filter(
                follower=request.user,
                following=User.objects.get(id=id)
                ).delete()
                print("unfollowed")
                notification.objects.filter(notification_type=4,following_user=request.user,user=User.objects.get(id=id)).delete()
                return JsonResponse({'unfollowed':True},safe=False)
            else: # follow
                follow_object = Follow.objects.create(
                follower=request.user,
                following=User.objects.get(id=id)
                )
                print("followed")
                notification.objects.create(user=follow_object.following,
                                            notification_type=4,
                                            content_id=follow_object.follower.id,
                                            is_viewed=False,
                                            following_user =follow_object.follower)
                return JsonResponse({'followed':True},safe=False)
    else:
        
        return redirect("/login")

def show_users(request):
    users=Profile.objects.all()
    if request.user.is_authenticated:
        status = []
        users=list(users)
        for profile in users :
            if Follow.objects.filter(follower=request.user,following=profile.user).exists():
                status.append("Unfollow")
            else:
                status.append("Follow")

        context={'users':zip(users,status)}
        return render(request, "u_profile/show_users.html",context)
    else:
        context={"users":users}
        return render(request, "u_profile/show_users.html",context)

def become_expert(request):
    if User.objects.get(id=request.user.id).profile.role=='expert':
        return HttpResponse("you are alredy an Expert User")
    user = Pending.objects.filter(applicant=request.user)
    if user:
        return HttpResponse("yet to become a expert")
    form = ExpertUserForm(request.POST,request.FILES or None)
    if request.method == 'POST':
            resume = request.FILES.get('resume')
            letter = request.POST.get('letter')
            
            application = Pending.objects.create(resume = resume, letter = letter, applicant = request.user , status ='pending' )
            application.save()
            
            # popup # become expert in profile
            return redirect('/home')
    return render(request, 'become_expert.html')

def get_articles(Question):
    print(Question)
    return wikipedia.search(Question,results=3)
def ai_assisstant(request):
    if request.method=="POST":
        form_identifier = request.POST.get('form_identifier', None)
        if form_identifier == 'form1':
            Question = request.POST.get('Question')
            articles = get_articles(Question=Question)
            article_titles = []
            for article in articles :
                article_titles.append(article.title)
            print(article_titles)
            client = OpenAI(api_key="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")
            response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an Expert in Indian Culture.Explain clearly covering varoius aspects.Give response in three paragraphs only,only in 150 words,separate each paragragh with &&&"},
                {"role": "user", "content": "Give response in three paragraphs only each separated by &&& ,only in 150 words:"+ Question },
            ]
            )
            response = (response.choices[0].message).content
            answer_list = response.split("&&&")

            response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an Expert in Indian Culture.Pick related topics and 10 keywords for the Question in context of India"},
                {"role": "user", "content": "Pick keywords which are related to India .Each keyword should be separated by comma :"+ Question },
            ]
            )
            response = (response.choices[0].message).content
            keywords = response.split(',')

            YT_api_key="AIzaSyDBTe3DiwKuKMDJfCWv1V0nglyAVzX8cy4"
            api_url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&q={Question}&key={YT_api_key}'
            response = requests.get(api_url)
            data = response.json()
            videos = data['items']
            video_title=[]
            video_thumbnail_url=[]
            video_url=[]
            for video in videos:
                video_title.append(video['snippet']['title'])
                video_thumbnail_url.append(video['snippet']['thumbnails']['default']['url'])
                video_url.append(video['id']['videoId'])

            videos=zip(video_title,video_thumbnail_url,video_url)
            context = {'Question':Question,
                       'answer_list':answer_list,
                       'keywords' : keywords,
                       'articles_titles':article_titles,
                       'videos':videos}
            return render(request,"Ai/ai_assisstant.html",context)
        
        if form_identifier == 'form2':
            selected_keywords = [key for key in request.POST if request.POST[key] == 'on']
            Question = ""
            for keyword in selected_keywords:
                Question = Question+" "+keyword 

            articles = get_articles(Question=Question)
            article_titles = []
            for article in articles :
                article_titles.append(article.title)
            print(article_titles)

            client = OpenAI(api_key="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")
            response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an Expert in Indian Culture.Explain clearly covering varoius aspects.Give response in three paragraphs only,only in 150 wordsseparate each paragragh with &&&"},
                {"role": "user", "content": "Give response in three paragraphs only each separated by &&& ,only in 150 words:"+ Question },
            ]
            )
            response = (response.choices[0].message).content
            answer_list = response.split("&&&")
            
            response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an Expert in Indian Culture.Pick related topics and 10 keywords from the given words in context of India and Indian Culture"},
                {"role": "user", "content": "Pick keywords which are related to India .Each keyword should be separated by comma :"+ Question },
            ]
            )
            response = (response.choices[0].message).content
            keywords = response.split(',')
            articles = wikipedia.search(Question,results=3)
            print(articles)

            YT_api_key="AIzaSyDBTe3DiwKuKMDJfCWv1V0nglyAVzX8cy4"
            api_url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&q={Question}&key={YT_api_key}'
            response = requests.get(api_url)
            data = response.json()
            videos = data['items']
            video_title=[]
            video_thumbnail_url=[]
            video_url=[]
            for video in videos:
                video_title.append(video['snippet']['title'])
                video_thumbnail_url.append(video['snippet']['thumbnails']['default']['url'])
                video_url.append(video['id']['videoId'])

            videos=zip(video_title,video_thumbnail_url,video_url)
            context = {'Question':Question,
                       'answer_list':answer_list,
                       'keywords' : keywords,
                       'articles_titles':article_titles,
                       'videos':videos}
            return render(request,"ai_assisstant.html",context)
    return render(request,"Ai/ai_assisstant.html")

def quiz(request):
    if request.method == "POST":
        description = request.POST.get('description')
        client = OpenAI(api_key="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")
        response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an Expert in Indian Culture.Generate a only 10 Quiz questions in JSON Format for the specific topic related to Indian Culture and traditions ,dont use "" in the response  "},
            {"role": "assistant", "content": "I will generate quiz of 10 questions in JSON format only " + '{"name":"Title of Quiz","quiz": [{"question": "question1","options": ["option1","option2","option3","option4"],"correct_answer": "correct option"},{"question": "question2","options": ["option1","option2","option3","option4"],"correct_answer": "correct option"},{"question": "question3","options": ["option1","option2","option3","option4"],"correct_answer": "correct option"}],dont use "" in the response '
     },
            {"role": "user", "content":  "quiz: [ question: question,options: {Option1, Option2, Option3, Option4},correct_answer: Correct Option ] on  "
                        + description + "related to Indian Culture and traditions only in JSON format only,dont use "" in the response "}]
            )
        response = (response.choices[0].message).content
        print(response)
        return JsonResponse(response,safe=False)
    else:
        return render(request,"Ai/quiz.html")

@login_required(login_url='login_user')
def search_users(request):
    if request.method == "POST":
        query =  request.POST.get('query')
        users = User.objects.filter(username__icontains=query)
        users_with_profile = []
        for user in users:
            profile = Profile.objects.get(user = user)
            if Follow.objects.filter(follower = request.user ,following = User.objects.get(id=profile.user.id)).exists():
                status = "Unfollow"
            else:
                status = "Follow"
            data ={
                "name" : user.username,
                "id" :user.id,
                "image": profile.avatar,
                "status":status
            }
            users_with_profile.append(data)
        return JsonResponse(users_with_profile,safe=False)
    else:
        
        return JsonResponse({'status':"invalid request"})

@login_required(login_url='login_user')
def search_experts(request):
    if request.method == "POST":
        query =  request.POST.get('query')
        users = User.objects.filter(username__icontains=query,role="expert")
        users_with_profile = []
        for user in users:
            profile = Profile.objects.get(user = user)
            if Follow.objects.filter(follower = request.user ,following = User.objects.get(id=profile.user.id)).exists():
                status = "Unfollow"
            else:
                status = "Follow"
            data ={
                "name" : user.username,
                "id" :user.id,
                "image": profile.avatar,
                "status":status
            }
            users_with_profile.append(data)
        return JsonResponse(users_with_profile,safe=False)
    else:
        
        return JsonResponse({'status':"invalid request"})


def show_experts(request):
    users=Profile.objects.filter(role="expert")
    if request.user.is_authenticated:
        status = []
        users=list(users)
        for profile in users :
            if Follow.objects.filter(follower=request.user,following=profile.user).exists():
                status.append("Unfollow")
            else:
                status.append("Follow")

        context={'users':zip(users,status)}
        return render(request, "u_profile/show_experts.html",context)
    else:
        context={"users":users}
        return render(request, "u_profile/show_experts.html",context)


@login_required(login_url='login_user')
@expert_user_required
def create_workshop(request):
    if request.method =="POST":
        name= request.POST.get('title')
        start_date = request.POST.get('s_date')
        end_date = request.POST.get('e_date') 
        address = request.POST.get('address')
        description = request.POST.get('description')
        content = request.POST.get('content')
        image = request.FILES.get('u_image')
        mode = request.POST.get("mode")
        r_start = request.POST.get("r_start")
        r_end = request.POST.get("r_end")
        platform = request.POST.get('platform')
        duration = request.POST.get("duration")
        organiser = request.user
        workshop = Workshop.objects.create(name=name,description=description,image=image,organiser=organiser,mode=mode,start_date=start_date,end_date=end_date,r_opening_date=r_start,r_closing_date=r_end,duration=duration,Address=address,Platform=platform,wyl=content)
        id = workshop.id
        follow =  Follow.objects.filter(following=workshop.organiser)
        for f in follow:
            current_datetime = datetime.now()
            print("created notification")
            notification.objects.create(user=f.follower,
                                         notification_type=3, #workshop notification type
                                         content_id=workshop.id,
                                         is_viewed=False,
                                         date_time=current_datetime,
                                         following_user = workshop.organiser)
        return redirect(reverse('accounts:workshop' , kwargs={'id':id}))
   
    return render(request, "workshop/create_workshop.html")

def get_workshop_status(current_date, start_date, end_date):
    if current_date > end_date:
        return "past"
    elif current_date >= start_date and current_date <= end_date:
        return "ongoing"
    else:
        return "future"
    

def show_workshops(request):
    ist = pytz.timezone('Asia/Kolkata')
    activate(ist)
    current_datetime = timezone.now()  
    current_date = current_datetime.date()

    all_work = Workshop.objects.all()
    work = Paginator(all_work,1) #no of workshops in each page
    page = request.GET.get('page')
    no_of_pages=work.num_pages
    print()
    workshops = []
    status = []
    if page == None:
        page=1
        items = work.page(page)
        print(items)
        for w in items:
            status.append(get_workshop_status(current_date, w.start_date, w.end_date))
        workshops=zip(items,status)

        context = {'workshops':workshops,'no_of_pages':no_of_pages}
        return render(request,"workshop/show_workshops.html",context)
    else :
        if int(page) > work.num_pages:
            page=work.num_pages
        items = work.page(page)
        workshops_data=[]
        for w in items:
            workshop_data = {
                'id':w.id,
            'name': w.name,
            'start_date': str(w.start_date),
            'end_date': str(w.end_date),
            'image' : w.image.url,
            'status': get_workshop_status(current_date, w.start_date, w.end_date)
            }
            workshops_data.append(workshop_data)
        print(workshops_data)
        return JsonResponse(workshops_data,safe=False)


def search_workshop(request):
    
    search_term = request.POST.get('search', '')
    print(search_term)
    # Filter posts based on title, username, and tags
    filtered_workshops = Workshop.objects.filter(name__icontains=search_term).distinct()
    
    print(filtered_workshops)
    
    ist = pytz.timezone('Asia/Kolkata')
    activate(ist)
    current_datetime = timezone.now()  
    current_date = current_datetime.date()
    
    
    workshops_data = []
    for workshop in filtered_workshops:
        workshop_data = {
            'id': workshop.id,
            'name': workshop.name,
            'organiser': workshop.organiser.username,  # Extract the username from the User object
            'start_date': workshop.start_date,
            'image': workshop.image.url,
            'end_date': workshop.end_date,  # Format date as needed
            'status': get_workshop_status(current_date, workshop.start_date,workshop.end_date)
            # Add more fields as needed
        }
        workshops_data.append(workshop_data)

    return JsonResponse({'workshops': workshops_data}, safe=False)

def workshop_details(request,id):
   
    work = Workshop.objects.get(id=id)
    context = {'workshop':work}
    return render(request,"workshop/workshop.html",context)

@login_required(login_url='login')
def register_workshop(request,id):
    if request.method=="POST":
        work = Workshop.objects.get(id=id)
        if Workshop_register.objects.filter(workshop=work,registered_user=request.user).exists():
            #pop up sending 
            return JsonResponse({'status':'already registered'})
        if request.user == work.organiser: # checking if the organiser is registering for his own workshop
            return JsonResponse({'status':'You are the organizer, You cannot register'})
         
        ist = pytz.timezone('Asia/Kolkata')
        activate(ist)
        current_datetime = timezone.now()  
        current_date = current_datetime.date()
        status = get_workshop_status(current_date, work.r_opening_date, work.r_closing_date)
        if status =="ongoing":
            if request.user.is_authenticated:
                register = Workshop_register.objects.create(
                    registered_user=request.user,
                    workshop=Workshop.objects.get(id=id),
                    registered_date=current_date
                )
                return JsonResponse({"status":"Registered Successfully."})
            else :
                return HttpResponse("/login_user")
        elif status == "future":
            return JsonResponse({"status":"Registration not open yet."})
        else:
            return JsonResponse({"status":"Registration closed."})
    
@login_required(login_url='login_user')
def organiser_view(request,id):
    work =  Workshop.objects.get(id=id)
    
    workRegister_objs = Workshop_register.objects.filter(workshop=work)
    users=[]
    for work in workRegister_objs :
        users.append(work.registered_user)
    context = {"users":users,"workshopid":Workshop.objects.get(id=id).id}
    return render(request,"workshop/organiser_view.html",context)


def workshop_messages(request,id):
    if request.method=="POST":
        ist = pytz.timezone('Asia/Kolkata')
        activate(ist)
        current_datetime = timezone.now()  
        current_date = current_datetime.date()
        content_ =  request.POST.get('content')
        print(content_)
        work = Workshop.objects.get(id=id)
        status = get_workshop_status(current_date, work.start_date,work.end_date)
        if status != "past" :
            messege = Workshop_messeges.objects.create(
                workshop = work,
                content = content_,
                created = current_datetime
            )
            return JsonResponse({'status':'messege added'})
        else:
            return JsonResponse({'status':'The workshop has been completed.'})
    else:
        if Workshop_register.objects.filter(workshop=Workshop.objects.get(id=id),registered_user=request.user).exists() or Workshop.objects.get(id=id).organiser==request.user:
            #CHECKING USER IS REGISTERED OR ORGANISER
            workshop=Workshop.objects.get(id=id)
            messages = Workshop_messeges.objects.filter(workshop=workshop).order_by('created')
            data = serialize("json",messages)
            return JsonResponse(data,safe=False)
        else:
            return JsonResponse({'status':'not registered'})
        
def send_mail_after_registration(user_email,user_name,content):
    subject = "New Message from " + user_name
    # message = "Hello "+ first_name + "!! \n"+"Welcome to Project12 !! \nThankyou for visiting our website \nWe have also sent a confirmation email to admin, if he confirms it your account will be activated \n\n Thanking You\n Project12 Admin"
    from_email = settings.EMAIL_HOST_USER
    to_list= [user_email]
    send_mail(subject, content, from_email, to_list, fail_silently=True)


def send_mails(request,id):
    ist = pytz.timezone('Asia/Kolkata')
    activate(ist)
    current_datetime = timezone.now()  
    current_date = current_datetime.date()
    work = Workshop.objects.get(id=id)
    status = get_workshop_status(current_date,work.start_date,work.end_date)
    if status != "past":
        if work.organiser==request.user:
            content = request.POST.get('content')
            users = Workshop_register.objects.filter(workshop=work)
            for user in users:
                send_mail_after_registration(user.registered_user.email,user.registered_user.username,content)
            return JsonResponse({"status":"mails sent"})
        else:
            return JsonResponse({"status":"not organiser"})
    
def notifications(request):
    if not request.user.is_authenticated:
        return render(request,"u_profile/notifications.html")
        
    all_notifications = (notification.objects.filter(user=request.user).order_by('-date_time')) # notifications to current user 
   
    all_notifications_ = Paginator(all_notifications,1) #change no of notifications in one page
    page = request.GET.get('page')
    no_of_pages=all_notifications_.num_pages
  

    if page == None:
        page=1
        items = all_notifications_.page(page)
        list_items = []
        for w in items:
            data = {
                'user':w.user.username,
                'following_user': (w.following_user.username),
                'notification_type':w.notification_type,
                'content_id':w.content_id,
                'is_viewed':'yes' if w.is_viewed else 'no',
                'date_time':w.date_time                
            }
            w.is_viewed = True 
            w.save()
            list_items.append(data)
        return render(request,"u_profile/notifications.html",{'notifications':list_items,'no_of_pages':no_of_pages})
    else:
        if int(page) > no_of_pages:
            page = no_of_pages 
        items = all_notifications_.page(page)
        json_data=[]
        for w in items:
            data = {
                'user':w.user.username,
                'following_user': (w.following_user.username),
                'notification_type':w.notification_type,
                'content_id':w.content_id,
                'is_viewed':'yes' if w.is_viewed else 'no',
                'date_time':w.date_time                
            }
            w.is_viewed = True
            w.save()
            json_data.append(data)

    return JsonResponse(json_data,safe=False)

def real_search(request):
    if 'term' in request.GET:
        qs = static_pages.objects.filter(name__istartswith=request.GET.get('term'))
        names = []
        for name in qs:
            names.append(name.name)
        return JsonResponse(names,safe=False)
    else:
        return JsonResponse({'status':400})

def give_url(request):
    query = request.POST.get('query')
    if static_pages.objects.filter(name=query).exists():
        page = static_pages.objects.get(name=query)
        url = page.url
        return JsonResponse({"url":url,"status":"found"})
    else:
        return JsonResponse({"status":"not found"})