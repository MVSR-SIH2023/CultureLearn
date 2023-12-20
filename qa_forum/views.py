import operator
from functools import reduce
from accounts.models import User
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.urls import reverse
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, ListView, UpdateView, View


from .models import (Answer, AnswerVote, Question)
from django.views.generic import DetailView
from accounts.models import Profile
from taggit.models import Tag, TaggedItem
from django.http import JsonResponse
import json
from django.contrib import messages
from django.urls import reverse
from .forms import QuestionForm
from django.contrib.auth.mixins import LoginRequiredMixin
from .mixins import AuthorRequiredMixin
# from .utils import question_score
from django.contrib.auth.decorators import login_required
try:
    qa_messages = 'django.contrib.messages' in settings.INSTALLED_APPS and\
        settings.QA_SETTINGS['qa_messages']

except AttributeError:  # pragma: no cover
    qa_messages = False

if qa_messages:
    from django.contrib import messages


def question_index_view(request):
    all_questions = Question.objects.all().select_related('user')
    noans = Question.objects.filter(answer__isnull=True).order_by('-pub_date').select_related('user')
    
    question_data = {}
    for question in all_questions:
        # Get answer count for each question
        answer_count = Answer.objects.filter(question=question).count()
        
     

        # Get tags related to each question
        question_tags = question.tags.all()  # Assuming the tags are obtained from a ManyToManyField
        
        question_data[question.id]={
            'question': question,
            'answer_count': answer_count,
            
            'question_tags': question_tags,
        }
        
    noans_data = {}
    for question in noans:
        print(question.title)
        # Get answer count for each question
        answer_count = Answer.objects.filter(question=question).count()
        
       

        # Get tags related to each question
        question_tags = question.tags.all()  # Assuming the tags are obtained from a ManyToManyField
        
        noans_data[question.id]={
            'question': question,
            'answer_count': answer_count,
            'hit_count': hit_count_value,
            'question_tags': question_tags,
        }
        
        

    # Get all tags related to questions
    question_content_type = ContentType.objects.get_for_model(Question)
    items = TaggedItem.objects.filter(content_type=question_content_type)
    all_tags = Tag.objects.filter(taggit_taggeditem_items__in=items).distinct()

    context = {
        'question_data': question_data,
        'questions':all_questions,
        'tags': all_tags,
        'noans':noans,
        'noans_data':noans_data,
        'totalcount' : Question.objects.count(),
        'anscount' : Answer.objects.count(),
    }

    return render(request, 'qa/index.html', context)





@login_required(login_url ='accounts:login')
def create_question(request):
    if request.method == 'POST':
        title = request.POST.get('title') 
        
        # Process tags input and save tags associated with the post
        tags_data = request.POST.get('tags')  
        tags_list = [tag.strip() for tag in tags_data.split(',') if tag.strip()]  # Clean up tags data

            # Add tags to the post using the TaggableManager
            
        user = request.user

        # Create a new question object
        question = Question.objects.create(title=title, user=user)
        question.tags.add(*tags_list)
        
        question.save()
        print("question created")
        num_answers =0
        hit_count =0
        question_data = {
            'id': question.id,
            'pub_date': question.pub_date.strftime('%Y-%m-%d %H:%M:%S'), 
            # Include other necessary fields here
        }
        if qa_messages:
            messages.success(request, _('Thank you! Your question has been created.'))

        return JsonResponse({'success': True, 'message': _('Question created successfully'),'question':question_data,'num_answers':num_answers,'hit_count':hit_count })

    return JsonResponse({'success': False, 'message': _('Invalid Request')})

@login_required(login_url ='accounts:login')
def create_answer(request, id):
    if request.method == 'POST':
        answer_text = request.POST.get('body')
        
        if answer_text:
            user = request.user
            question = Question.objects.get(id=id)
            avatar_url = None
            if user.profile.image:  # Checking if the profile has an image associated with it
                avatar_url = user.profile.avatar
            answer = Answer.objects.create(answer_text=answer_text, user=user, question=question)
            profile = get_object_or_404(Profile,user=user)
            user = (User.objects.filter(pk=request.user.pk).values(
                        "username",
                        "email",
                        "first_name",
                        "last_name",
                        "last_login",
                        "is_superuser",
                        "is_active",
                        
                        
                    )
                    .first()
                )
            answer_list =[]
            answer_data = {
                'id': answer.id,
                'pub_date': answer.pub_date.strftime('%Y-%m-%d %H:%M:%S'),
                'user': user,
                'avatar':avatar_url,
                'contributions':profile.contributions,
                'answer': answer.answer_text,
                
           
            }
            answer_list.append(answer_data)
            
    
            return JsonResponse({'success': True, 'message': _('Answer created successfully'), 'answer': answer_list})
        else:
            return JsonResponse({'success': False, 'message': _('Invalid Answer')})
    return JsonResponse({'success': False, 'message': _('Invalid Request')})


def search_question(request):
    if request.method == "POST":
        search_term = request.POST.get('search', '')
        print(search_term)
        # Filter posts based on title, username, and tags
        filtered_questions = Question.objects.filter(
            Q(title__icontains=search_term) | 
            Q(tags__name__icontains=search_term)
        ).distinct()
        
    
        questions_data = []
        for question in filtered_questions:
            # Get the number of answers for each question
            num_answers = Answer.objects.filter(question=question).count()
            
            # Get the hit count for each question
           
            tags = list(question.tags.all().values_list('name', flat=True))
            question_data = {
                'id': question.id,
                'title': question.title,
                'user': question.user.username,  # Extract the username from the User object
                'tags' : tags,
                'num_answers':num_answers,
                
                'pub_date': question.pub_date.strftime('%Y-%m-%d %H:%M:%S'),  # Format date as needed
               
            }
            questions_data.append(question_data)

        return JsonResponse({'questions': questions_data}, safe=False)
    else:
        return JsonResponse({'success': False, 'message': _('Invalid method')})

def search_by_tag(request,tag):
    if request.method == "POST":
        tag_value = request.POST.get('tag_value', '')
        
        # Filter posts based on title, username, and tags
        filtered_questions = Question.objects.filter( tags__name__icontains=tag_value)
        
    
        questions_data = []
        for question in filtered_questions:
            # Get the number of answers for each question
            num_answers = Answer.objects.filter(question=question).count()
            
            # Get the hit count for each question
           
            tags = list(question.tags.all().values_list('name', flat=True))
            question_data = {
                'id': question.id,
                'title': question.title,
                'user': question.user.username,  # Extract the username from the User object
                'tags' : tags,
                'num_answers':num_answers,
                
                'pub_date': question.pub_date.strftime('%Y-%m-%d %H:%M:%S'),  # Format date as needed
               
            }
            questions_data.append(question_data)

        return JsonResponse({'questions': questions_data}, safe=False)
    else:
        return JsonResponse({'success': False, 'message': _('Invalid method')})




@login_required(login_url ='accounts:login')
def update_question(request,id):
    if request.method == "POST":
        question = get_object_or_404(Question,id=id)
        new_question = request.POST.get("title")
        tags = request.POST.get("tags")
        question.title = new_question
        new_tags_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
         # Get the existing tags as a list of tag names
        existing_tags_list = list(question.tags.values_list('name', flat=True))

        # Remove tags that are not in the updated list
        tags_to_remove = list(set(existing_tags_list) - set(new_tags_list))
        question.tags.remove(*tags_to_remove)

        # Add new tags to the question
        tags_to_add = list(set(new_tags_list) - set(existing_tags_list))
        question.tags.add(*tags_to_add)
        question.save()
        
       
        tags = list(question.tags.all().values_list('name', flat=True))
        question_data = {
                'title':question.title,
                'user': question.user.username,
                'pub_date':question.pub_date.strftime('%Y-%m-%d %H:%M:%S'),
            }
       
        
        return JsonResponse({'success': True, 'message': _('Answer updated successfully'), 'question': question_data})
   
    else:
        return JsonResponse({'success': False, 'message': _('Invalid Request')})
        


@login_required(login_url ='accounts:login')
def update_answer(request,id):
    if request.method == "POST":
        answer = get_object_or_404(Answer,id=id)
        new_answer = request.POST.get("answer_text")
        if new_answer:
            answer.answer_text = new_answer
            answer.save()
            user = request.user
            avatar_url = None
            if user.profile.image: 
                avatar_url = user.profile.avatar
            profile = get_object_or_404(Profile,user=user)
            
            user = (User.objects.filter(pk=request.user.pk).values("username").first())
            answer_list =[]
            answer_data = {
                'id': answer.id,
                'pub_date': answer.pub_date.strftime('%Y-%m-%d %H:%M:%S'),
                'user': user,
                'avatar':avatar_url,
                'contributions':profile.contributions,
                'answer': answer.answer_text,
            }
            answer_list.append(answer_data)
            
    
            return JsonResponse({'success': True, 'message': _('Answer updated successfully'), 'answer': answer_list})
        else:
            return JsonResponse({'success': False, 'message': _('Invalid Answer')})
    else:
        return JsonResponse({'success': False, 'message': _('Invalid Request')})
        
    
@login_required(login_url ='accounts:login')
def ans_delete_view(request,id):
    ans = get_object_or_404(Answer, id=id, user=request.user)
    
    if request.method == "POST":
        ans.delete()
        
        return JsonResponse({'message': 'Answer deleted'})
        
    return JsonResponse({'error': 'Invalid request'})
  
  
from django.db.models import F
def question_detail_view(request, id):
    question = get_object_or_404(Question, id=id)
    answers = Answer.objects.filter(question=question)
    

    
    answer_details = {}
    
    if request.user.is_authenticated:
        for answer in answers:
            answer_vote = AnswerVote.objects.filter(user=request.user, answer=answer).first()
            upvoted = False
            downvoted = False
            
            if answer_vote:
                upvoted = answer_vote.upvote_value
                downvoted = answer_vote.downvote_value
            
            answer_details[answer.id] = {
                
                'upvote_count': answer.positive_votes,
                'downvote_count': answer.negative_votes,
                'upvoted': upvoted,
                'downvoted': downvoted,
                'username':answer.user.username,
                'contributions':answer.user.profile.contributions,
                'avatar':answer.user.profile.avatar,
            }

    context = {
        'question': question,
        'answers':answers,
        'answer_details': answer_details,
        'user':request.user,
       
    }

    return render(request, 'qa/detail_question.html', context)


@login_required(login_url ='accounts:login')
def toggle_answer_vote(request, id):
    if request.method == 'POST' and request.user.is_authenticated:
        vote_value = request.POST.get('value')
        answer = Answer.objects.get(id=id)
        
        # Fetch the QuestionVote object associated with the question
        answer_vote, created = AnswerVote.objects.get_or_create(user=request.user, answer=answer)
        
        if vote_value == "upvote":
            
            if answer_vote.upvote_value:
                # If the user already upvoted, remove the upvote
                answer_vote.upvote_value = False
                answer_vote.save()
                answer.positive_votes -= 1
                voted = False
            else:
                # If the user hasn't upvoted, add the upvote
                answer_vote.upvote_value = True
                answer_vote.downvote_value = False  # Remove downvote if any
                answer_vote.save()
                answer.positive_votes += 1
                if answer.negative_votes !=0:
                    answer.negative_votes -= 1  
                voted = True
            
            answer.save()
            return JsonResponse({'answer': id, 'upvoted': voted, 'upvote_count': answer.positive_votes,'downvote_count': answer.negative_votes})
        else:
            if answer_vote.downvote_value:
                # If the user already downvoted, remove the downvote
                answer_vote.downvote_value = False
                answer_vote.save()
                answer.negative_votes -= 1
                voted = False
            else:
                # If the user hasn't downvoted, add the downvote
                answer_vote.downvote_value = True
                answer_vote.upvote_value = False  # Remove upvote if any
                answer_vote.save()
                answer.negative_votes += 1
                if answer.positive_votes !=0:
                    answer.positive_votes -= 1  
                voted = True
            
            answer.save()
            return JsonResponse({'answer': id, 'downvoted': voted, 'upvote_count':answer.positive_votes,'downvote_count': answer.negative_votes})
    
    return JsonResponse({'error': 'Invalid request or user not authenticated'})

def filter_answer(request, id):
    question = get_object_or_404(Question, id=id)
    filter_value = request.POST.get('filter_value')
    
    if filter_value == "latest":
        answers = Answer.objects.filter(question=question).order_by('-pub_date')
    else:
        answers = Answer.objects.filter(question=question).order_by('-positive_votes')
    
    answer_data = []
    user = (User.objects.filter(id=request.user.id).values("username").first())
    for answer in answers:
        answer_vote = AnswerVote.objects.filter(user=request.user, answer=answer).first()
        upvoted = False
        downvoted = False
        
        if answer_vote:
            upvoted = answer_vote.upvote_value
            downvoted = answer_vote.downvote_value
        
        answer_details = {
           
            'upvote_count': answer.positive_votes,
            'downvote_count': answer.negative_votes,
            'upvoted': upvoted,
            'downvoted': downvoted,
            'answer_text':answer.answer_text,
            'username': answer.user.username,
            'contributions': answer.user.profile.contributions,
            'avatar': answer.user.profile.avatar,
            'ruser':user #request user
        }
        answer_data.append(answer_details)
    
    context = {
        'answer_data': answer_data,
    }
    
    return JsonResponse(context, status=200)
