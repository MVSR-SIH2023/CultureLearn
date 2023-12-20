
    
    
from django.urls import path,include
from .views import *

app_name = 'accounts'  # Define the app_name or namespace for the app

urlpatterns = [
    
    path('profile/', profile_view, name="profile"), 
    path('profile/<int:user_id>/', profile_view, name="profile"),
    path('profile-edit/', update_profile , name="profile-edit"), 
    
   
    
    path('signup/', signup,name="signup"),
    path('login/', login_user ,name="login"),
    path('logout/', logout_user ,name="logout"),
    path('activate/<uidb64>/<token>',activate_user, name="activate"),
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('reset-password/<str:uidb64>/<str:token>/', reset_password, name='reset_password'),
    
    # path('real_search/',real_search,name="real_search"),
    # path('give_url/',give_url,name="give_url"),
    
    
    path('all_quiz/',show_quiz,name="show_quiz"),
    path('take_quiz/<int:id>',take_quiz,name="take_quiz"),
    path('get_quiz/',get_quiz,name="get_quiz"),
    path('submit_score/',submit_score,name="submit_score"),
    path('get_leaderboard/',get_leaderboard,name="get_leaderboard"),
    path('get_user_score/',get_user_score,name="get_user_score"),
    
    
    path('gallery/<int:id>/',gallery,name="gallery"),
    path('upload_gallery/<int:id>/',upload_gallery,name="upload_gallery"),
    path('search-workshops/',search_workshop,name="search_workshop"),
    path('create_workshop/',create_workshop,name="create_workshop"),
    path('show_users/',show_users,name="show_users"),
    path('show_experts/',show_experts,name="show_experts"),
    path('search_users/',search_users,name="search_users"),
    path('search_experts/',search_experts,name="search_experts"),
    path('follow_user/<int:id>/',follow_user,name="follow_user"),
    path('quiz/',create_quiz,name="quiz"),
    path('become_expert/',become_expert,name="become_expert"),
    path('ai_assisstant/',ai_assisstant,name="ai_assisstant"),
    path('show_workshops/',show_workshops,name="show_workshops"),
    path('workshop/register_workshop/<int:id>/', register_workshop, name="register_workshop"),
    path('organiser_view/<int:id>/',organiser_view,name="organiser_view"),
    path('workshop/<int:id>/',workshop_details,name="workshop"),
    path('organizer_view/workshop_messages/<int:id>/',workshop_messages,name="workshop_messages"),
    path('send_mails/<int:id>/',send_mails,name="send_mails"),
    
    path('notifications/', notifications, name='notifications'),
   
]