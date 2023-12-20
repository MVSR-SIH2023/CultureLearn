from django.urls import path,include
from .views import *

app_name = 'articles'  # Define the app_name or namespace for the app

urlpatterns = [
    
    path('all-posts/create/',create_post_view,name="post-create"),
    path('all-posts', all_post_view, name='all-posts'),
    path('load-more-articles/', load_more_articles_view, name='load_more_articles'),
    path('load-more-podcasts/', load_more_podcasts_view, name='load_more_podcasts_view'),
    path('post/<int:id>/', post_page_view, name="post"),
    path('post/edit/<int:id>', post_edit_view, name="post-edit"),
    path('post/delete/<int:id>/', post_delete_view, name='post-delete'),
    
    path('post/like/<int:id>/', toggle_post_like, name="like-post"), 
    path('comment/like/<int:id>/', toggle_comment_like , name="like-comment"), 
    path('search-posts/',search_posts,name="search_posts"),
    path('post-filter/',post_filter,name="post_filter"),
    path('search-podcasts/',search_podcast,name="search_podcast"),
    path('podcast-filter/',podcast_filter,name="podcast_filter"),
    path('all-podcasts/',show_main_podcasts,name="all-podcasts"),
    path('all-podcasts/create-main/',upload_main_podcast, name="create-main-podcast"),
    path('all-podcasts/create-main/create-single/',upload_single_podcast,name="create-single-podcast"),
    path('all-podcasts/<int:id>/',show_main_podcast_detail,name="single-podcasts"),
    path('all-podcasts/delete/<int:id>/', podcast_delete_view, name='podcast-delete'),
    path('all-podcasts/like/<int:id>/', toggle_podcast_like, name="like-podcast"),
    path('commentsent/<int:id>/', create_comment_view , name='comment-sent'), 
    path('comment/delete/<int:id>/', comment_delete_view, name='comment-delete'),
    
    
    
    
]