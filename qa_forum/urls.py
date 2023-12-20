from django.urls import path
from .views import *

urlpatterns = [
    path('question', question_index_view, name='qa_index'),
    path('question/<int:id>/',question_detail_view , name='qa_detail'),
  
    
   
    path('new-question/', create_question, name='qa_create_question'),
    path('answersent/<int:id>/', create_answer, name='qa_create_answer'),
    path('answer/edit/<int:id>/', update_answer, name='qa_update_answer'),
    path('vote/answer/<int:id>/',toggle_answer_vote , name='qa_answer_vote'),
    path('answer/delete/<int:id>/', ans_delete_view , name='ans_delete'),
    path('question/<int:id>/filter/',filter_answer, name="filter_answer"),
    path("editquestion/<int:id>/",update_question ,name="update_question"),
    path('search-questions/', search_question, name='qa_search'),
    path('tag/<str:tag>/',search_by_tag , name='qa_tag'),
]