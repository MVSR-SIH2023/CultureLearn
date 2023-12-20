from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from django.http import  JsonResponse, Http404
from django.contrib import messages
from .models import *
from .forms import *
from taggit.models import Tag

from django.core.paginator import Paginator
from django.db.models import Q

from collections import defaultdict
from datetime import datetime
from accounts.models import Follow, notification

@login_required
def create_post_view(request):
    
    if request.method == 'POST':
        form = PostContentForm(request.POST, request.FILES)
        
        title = request.POST.get('title')
        if form.is_valid():
            
            new_post = form.save(commit=False)
            new_post.author = request.user  
            new_post.title = title
            new_post.save()
            # Process tags input and save tags associated with the post
            tags_data = request.POST.get('tags')  # Assuming tags are provided as a comma-separated string
            tags_list = [tag.strip() for tag in tags_data.split(',') if tag.strip()]  # Clean up tags data
            new_post.tags.add(*tags_list)
            follow =  Follow.objects.filter(following=new_post.author)
            for f in follow:
                current_datetime = datetime.now()
                print("created notification")
                notification.objects.create(user=f.follower,
                                            notification_type=1, #workshop notification type
                                            content_id=new_post.id,
                                            is_viewed=False,
                                            date_time=current_datetime,
                                            following_user = new_post.author)
            # Add tags to the post using the TaggableManager
            

            return redirect('/all-posts')  # Redirect to the post detail page after successful creation
    else:
        form = PostContentForm()
        
    
    return render(request, 'articles/create_post.html', {'form': form})

def all_post_view(request): 
    posts = Post.objects.all()[:3]
    num_posts = Post.objects.all().count()
    context = {
        'posts' : posts, 
        'num_posts':num_posts,
        
    } 
    return render(request, 'articles/all_posts.html', context)




def load_more_articles_view(request):
    loaded_item = request.GET.get('offset')
    loaded_item_int = int(loaded_item) if loaded_item.isdigit() else 0
    limit = 3
    last_limit = loaded_item_int + limit
    post_objects = Post.objects.all()[loaded_item_int:last_limit]
    num_posts = Post.objects.all().count()
    posts_data = []
    for post in post_objects:
        post_data = {
            'id': post.id,
            'title': post.title,
            'author': post.author.username,  # Extract the username from the User object
            'url': post.get_absolute_url(),
            'content': post.content,
            'image': post.image.url,
            'date': post.date.strftime('%Y-%m-%d %H:%M:%S'),# Format date as needed
            'num_posts':num_posts,
            'last_limit':last_limit,
            # Add more fields as needed
        }
        posts_data.append(post_data)
    
    
    
    return JsonResponse({'posts':posts_data}, safe=False)






@login_required
def post_delete_view(request,id):
    post = get_object_or_404(Post, id=id, author=request.user)
    
    if request.method == "POST":
        post.delete()
        
        return JsonResponse({'message': 'Post deleted'})
        
    return JsonResponse({'error': 'Invalid request'})


@login_required
def post_edit_view(request, id):
    post = get_object_or_404(Post, id=id, author=request.user)
    form = PostForm(instance=post)
    
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid:
            form.save()
            messages.success(request, 'Post updated')
            return redirect('/all-posts')
    
    context = {
        'post' : post,
        'form' : form
    }
    return render(request, 'articles/edit_post.html', context)

from django.db.models import Count
#particular post details 
def post_page_view(request, id):
    post = get_object_or_404(Post, id=id)
    tag_names = post.tags.values_list('name', flat=True)

    # Find recommended articles based on these tags, order by likes count, and retrieve only 3 articles
    recommended_articles = (
        Post.objects
        .filter(tags__name__in=tag_names)
        .exclude(id=post.id)
        .annotate(like_count=Count('likes'))
        .order_by('-like_count')[:3]
    )
    
    comment_count = Comment.objects.filter(parent_post=post).count()
    
    liked = post.likes.filter(id=request.user.id).exists()
    likes_count = post.likes.count()
    context = {
        'post' : post,
        'id':id,
        'likes':likes_count,
        'liked':liked,
        'request':request,
        'comment_count':comment_count,
        'recommended_articles':recommended_articles
        
    }
    
    return render(request, 'articles/post_detail.html', context)


    

def search_posts(request):
    
    search_term = request.POST.get('search', '')
    print(search_term)
    # Filter posts based on title, username, and tags
    filtered_posts = Post.objects.filter(
        Q(title__icontains=search_term) | 
        Q(author__username__icontains=search_term) | 
        Q(tags__name__icontains=search_term)
    ).distinct()
    


    posts_data = []
    for post in filtered_posts:
        post_data = {
            'id': post.id,
            'title': post.title,
            'author': post.author.username,  # Extract the username from the User object
            'url': post.get_absolute_url(),
            'content': post.content,
            'image': post.image.url,
            'date': post.date.strftime('%Y-%m-%d %H:%M:%S'),  # Format date as needed
            # Add more fields as needed
        }
        posts_data.append(post_data)

    return JsonResponse({'posts': posts_data}, safe=False)
    


def post_filter(request):
    filter_value = request.POST.get('filter_value')
        
    # Latest created post
    if filter_value == "latest":
        queryset = Post.objects.all().order_by('-date')  # Use '-' to get the latest first
        posts_data = []
        for post in queryset:
            post_data = {
                    'id': post.id,
                    'title': post.title,
                    'author': post.author.username,  # Extract the username from the User object
                    'url': post.get_absolute_url(),
                    'content': post.content,
                    'image': post.image.url,
                    'date': post.date.strftime('%Y-%m-%d %H:%M:%S'),  # Format date as needed
                    # Add more fields as needed
            }
            posts_data.append(post_data)
        return JsonResponse({"posts": posts_data}, status=200)
        
        # Top liked post
    elif filter_value == "liked":
        queryset = Post.objects.all().order_by('likes')  # Assuming 'likes' is a field in the Post model
        posts_data = []
        for post in queryset:
            post_data = {
                    'id': post.id,
                    'title': post.title,
                    'author': post.author.username,  # Extract the username from the User object
                    'url': post.get_absolute_url(),
                    'content': post.content,
                    'image': post.image.url,
                    'date': post.date.strftime('%Y-%m-%d %H:%M:%S'),  # Format date as needed
                    # Add more fields as needed
                }
            posts_data.append(post_data)
        return JsonResponse({"posts": posts_data}, status=200)
        
        # Lexicographic order
    else:
        queryset = Post.objects.all().order_by('title')
        posts_data = []
        for post in queryset:
            post_data = {
                    'id': post.id,
                    'title': post.title,
                    'author': post.author.username,  # Extract the username from the User object
                    'url': post.get_absolute_url(),
                    'content': post.content,
                    'image': post.image.url,
                    'date': post.date.strftime('%Y-%m-%d %H:%M:%S'),  # Format date as needed
                    # Add more fields as needed
                }
            posts_data.append(post_data)
        return JsonResponse({"posts": posts_data}, status=200)
    

    
    
            
        

    




@login_required
@require_POST #this decorator ensures that incomming method is post method
def create_comment_view(request, id):
  
    
    # Retrieve the post for which the comment is being created
    post = get_object_or_404(Post, id=id)
    
    comment_count = Comment.objects.filter(parent_post=post).count()
    
    body = request.POST.get('body')  
    
    if body:
        # Create the comment
        new_comment = Comment.objects.create(
            author=request.user,
            parent_post=post,
            body=body
        )
        
        
        liked = False
        
        is_post_author = new_comment.parent_post.author == request.user
        # Return a JSON response with the newly created comment details
        return JsonResponse({
            'id': new_comment.id,
            'author': new_comment.author.username,
            'body': new_comment.body,
            'likes': new_comment.likes.count(),
            'liked':liked,
            'created': new_comment.created.strftime('%Y-%m-%d %H:%M:%S'),
            'is_post_author':is_post_author,
            'comment_count' : comment_count,
        })
    else:
        # If the 'body' parameter is missing in the request, return an error JSON response
        return JsonResponse({'error': 'Comment body is required'}, status=400)









@login_required
def comment_delete_view(request, id):
    try:
        comment =  get_object_or_404(Comment, id=id)
    except Comment.DoesNotExist:
        raise Http404("Comment does not exist or you don't have permission to delete it.")

    if request.method == "POST":
        parent_post_id = comment.parent_post.id  # Save the parent post ID before deletion
        comment.delete()
        
        
        return JsonResponse({'success': True, 'post_id': parent_post_id})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)









@login_required
def toggle_post_like(request, id):
    if request.method == 'POST' and request.user.is_authenticated:
        post = Post.objects.get(id=id)
        
        user_liked = post.likes.filter(id=request.user.id).exists()
        
        if user_liked:
            post.likes.remove(request.user)
            liked = False
        else:
            post.likes.add(request.user)
            liked = True
        
        likes_count = post.likes.count()
        
        return JsonResponse({'post': id, 'liked': liked, 'likes': likes_count})
    
    return JsonResponse({'error': 'Invalid request or user not authenticated'})

@login_required
def toggle_comment_like(request, id):
    if request.method == 'POST' and request.user.is_authenticated:
        comment = Comment.objects.get(id=id)
        
        
        user_liked = comment.likes.filter(id=request.user.id).exists()
       
        if user_liked:
            comment.likes.remove(request.user)
            liked = False
        else:
            comment.likes.add(request.user)
            liked = True
        
        likes_count = comment.likes.count()
        
        return JsonResponse({'id': id,'liked': liked, 'likes': likes_count})
    
    return JsonResponse({'error': 'Invalid request or user not authenticated'})





    


@login_required
def upload_main_podcast(request):
    if request.method=="POST":
        name = request.POST.get('name')
        image = request.FILES.get("templates")
        # audio = request.FILES.get("audio")
        description = request.POST.get("content")
        
        p=MainPodcast.objects.create(title=name,description=description,author=request.user)
        image.name=str(p.id)
        p.image=image
        p.save()
        return redirect('/all-podcasts/create-main/create-single')

    return render(request, "articles/createPodcast.html")

@login_required
def upload_single_podcast(request):
    main_podcasts=MainPodcast.objects.filter(author=request.user)
    
    
    if request.method=="POST":
        
        name = request.POST.get('name')
        image = request.FILES.get("templates")
        audio = request.FILES.get("audio")
        description = request.POST.get("content")
        main_podcast_id= request.POST.get("main_podcasts")
        main_podcast = get_object_or_404(MainPodcast, pk=main_podcast_id)
        p=Podcast.objects.create(name=name,description=description,main_podcast = main_podcast,author=request.user)
        audio.name = str(p.id)
        image.name =str(p.id)
        p.audio = audio
        p.image =image
        p.save()
        follow =  Follow.objects.filter(following=p.author)
        print("created notification")
        for f in follow:
            current_datetime = datetime.now()
            notification.objects.create(user=f.follower,
                                        notification_type=2, #workshop notification type
                                        content_id=p.main_podcast.id,
                                        is_viewed=False,
                                        date_time=current_datetime,
                                        following_user = p.author)
        
        return redirect('/all-podcasts')

    return render(request, "articles/sequencePodcast.html", {'main_podcasts':main_podcasts})

def show_main_podcasts(request):
    main_podcasts = MainPodcast.objects.all()[:3] #if limit need to be changed change here also in all-post js and load more function
    num_podcasts = MainPodcast.objects.all().count()
    context={'main_podcasts':main_podcasts,"num_podcasts":num_podcasts}
    return render(request, "articles/allMainPodcast.html",context)


def load_more_podcasts_view(request):
    loaded_item = request.GET.get('offset')
    loaded_item_int = int(loaded_item) if loaded_item.isdigit() else 0
    limit = 3
    last_limit = loaded_item_int + limit
    num_podcasts = Post.objects.all().count()
    podcast_objects = MainPodcast.objects.all()[loaded_item_int:last_limit]
    
    podcasts_data = []
    for podcast in podcast_objects:
        podcast_data = {
            'id': podcast.id,
            'title': podcast.title,
            'author_id':podcast.author.id,
            'author': podcast.author.username,  # Extract the username from the User object
            'url': podcast.get_absolute_url(),
            'description': podcast.description,
            'image': podcast.image.url,
            'created': podcast.created.strftime('%Y-%m-%d %H:%M:%S'),
            'num_podcasts':num_podcasts,                                        
            'last_limit':last_limit,
            # Add more fields as needed
        }
        podcasts_data.append(podcast_data)
    
    
    
    return JsonResponse({'podcasts':podcasts_data}, safe=False)

def search_podcast(request):
    
    search_term = request.POST.get('search', '')
    print(search_term)
    # Filter posts based on title, username, and tags
    filtered_podcasts = MainPodcast.objects.filter(
        Q(title__icontains=search_term) | 
        Q(author__username__icontains=search_term)
    ).distinct()
    print(filtered_podcasts)
    
    
    podcasts_data = []
    for podcast in filtered_podcasts:
        podcast_data = {
            'id': podcast.id,
            'url': podcast.get_absolute_url(),
            'title': podcast.title,
            'author_id':podcast.author.id,
            'author': podcast.author.username,  # Extract the username from the User object
            'description': podcast.description,
            'image': podcast.image.url,
            'created': podcast.created.strftime('%Y-%m-%d %H:%M:%S'),  # Format date as needed
            # Add more fields as needed
        }
        podcasts_data.append(podcast_data)

    return JsonResponse({'podcasts': podcasts_data}, safe=False)


def podcast_filter(request):
    filter_value = request.POST.get('filter_value')
        
    # Latest created post
    if filter_value == "latest":
        queryset = MainPodcast.objects.all().order_by('-created')  # Use '-' to get the latest first
        podcasts_data = []
        for podcast in queryset:
            podcast_data = {
                'id': podcast.id,
                'title': podcast.title,
                'url': podcast.get_absolute_url(),
                'author_id':podcast.author.id,
                'author': podcast.author.username,  # Extract the username from the User object
                'description': podcast.description,
                'image': podcast.image.url,
                'created': podcast.created.strftime('%Y-%m-%d %H:%M:%S'),  # Format date as needed
                # Add more fields as needed
            }
            podcasts_data.append(podcast_data)

        return JsonResponse({'podcasts': podcasts_data}, status=200)
        
        # Lexicographic order
    else:
        queryset = MainPodcast.objects.all().order_by('title')
        podcasts_data = []
        for podcast in queryset:
            podcast_data = {
                'id': podcast.id,
                'title': podcast.title,
                'author': podcast.author.username,  # Extract the username from the User object
                'description': podcast.description,
                'image': podcast.image.url,
                'created': podcast.created.strftime('%Y-%m-%d %H:%M:%S'),  # Format date as needed
                # Add more fields as needed
            }
            podcasts_data.append(podcast_data)

        return JsonResponse({'podcasts': podcasts_data}, status=200)




def show_main_podcast_detail(request, id):
    main_podcast = MainPodcast.objects.get(id=id)
    ordered_podcasts = main_podcast.main_podcast.order_by('order').all()
    
    podcasts = Podcast.objects.filter(main_podcast=main_podcast)
    
    liked = defaultdict(bool)  # Default all to False
    likes_count = defaultdict(int)  # Default all to 0
    
    for podcast in podcasts:
        likes_count[podcast.id] = podcast.likes.count()
        if request.user.is_authenticated:
            user_liked = podcast.likes.filter(id=request.user.id).exists()
            liked[podcast.id] = user_liked
    
    context = {
        'podcasts': ordered_podcasts,
        'main_podcast': main_podcast,
        'user': request.user,
        'likes': dict(likes_count),
        'liked': dict(liked),
    }
    return render(request, "articles/podcast_episodes.html", context)



@login_required
def podcast_delete_view(request,id):
    podcast = get_object_or_404(Podcast, id=id, author=request.user)
    
    if request.method == "POST":
        podcast.delete()
        
        return JsonResponse({'message': 'Podcast deleted'})
        
    return JsonResponse({'error': 'Invalid request'})


@login_required
def toggle_podcast_like(request, id):
    if request.method == 'POST' and request.user.is_authenticated:
        podcast = Podcast.objects.get(id=id)
        
        user_liked = podcast.likes.filter(id=request.user.id).exists()
        
        if user_liked:
            podcast.likes.remove(request.user)
            liked = False
        else:
            podcast.likes.add(request.user)
            liked = True
        
        likes_count = podcast.likes.count()
        
        return JsonResponse({'id': id, 'liked': liked, 'likes': likes_count})
    
    return JsonResponse({'error': 'Invalid request or user not authenticated'})    


