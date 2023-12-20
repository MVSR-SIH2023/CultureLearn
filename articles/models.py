from django.db import models
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from accounts.models import User
from taggit.managers import TaggableManager
from django.urls import reverse
from ckeditor_uploader.fields import RichTextUploadingField
from PIL import Image
import uuid

# Create your models here.

class FeaturedPostManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(featured=True)

class Post(models.Model):
    title = models.CharField(max_length=100)
    content = RichTextUploadingField()
    date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE , null=True,related_name ="posts")
    image = models.ImageField(upload_to='blog/images/%Y-%m-%d/')
    featured = models.BooleanField(default=False)
    tags = TaggableManager()
    objects = models.Manager()
    featured_post = FeaturedPostManager()
    likes = models.ManyToManyField(User, related_name="likedposts", through="LikedPost",blank = True)
    
    def save(self, *args, **kwargs):

        if self.image:  # Check if an image is present
            img = Image.open(self.image)
            max_size = (600, 600)  # Define maximum dimensions (width, height)
            img.thumbnail(max_size)
            img.save(self.image.path)

        super().save(*args, **kwargs)

        
    def get_absolute_url(self):
        return reverse('articles:post', kwargs={'id': self.id})
    
    class Meta:
        ordering = ["-date"]
    def __str__(self):
        return 'Post {} by {}'.format(self.title, self.author)

class LikedPost(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.user.username} : {self.post.title}'
        

        
        
class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='comments')
    parent_post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    body = models.CharField(max_length=150)
    likes = models.ManyToManyField(User, related_name='likedcomments', through='LikedComment',blank = True)
    created = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        try:
            return f'{self.author.username} : {self.body[:30]}' 
        except:
            return f'no author : {self.body[:30]}' 
        
    class Meta:
        ordering = ['-created']

        
        
class LikedComment(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.user.username} : {self.comment.body[:30]}'
        
        

        

    
def validate_audio_file_extension(value):
    if not value.name.endswith('.mp3'):
        raise ValidationError("Only MP3 files are allowed.") 
    
class Podcast(models.Model):
    name = models.CharField(unique=True,max_length=50)
    description = models.CharField(max_length=255)
    hindi_audio = models.FileField(upload_to="podcast_audios",validators=[FileExtensionValidator(['mp3']), validate_audio_file_extension])
    english_audio = models.FileField(upload_to="podcast_audios",validators=[FileExtensionValidator(['mp3']), validate_audio_file_extension])
    telugu_audio = models.FileField(upload_to="podcast_audios",validators=[FileExtensionValidator(['mp3']), validate_audio_file_extension])
    image = models.ImageField(upload_to="podcast_images")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authored_podcasts')
    created = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_podcasts', through='LikedPodcast',blank=True)
    main_podcast = models.ForeignKey('MainPodcast', on_delete=models.CASCADE, related_name='main_podcast') #need to change this default 
    
    
    def __str__(self):
        return  f'{self.author.username} : {self.name}'

    
class MainPodcast(models.Model):
    title = models.CharField(unique=True,max_length=50)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_main_podcasts')
    image = models.ImageField(upload_to="main_podcast_images")
    description = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return  f'{self.author.username} : {self.title}'
    
    def get_absolute_url(self):
        return reverse('articles:single-podcasts', kwargs={'id': self.id})
    
class LikedPodcast(models.Model):
    podcast = models.ForeignKey(Podcast, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.user.username} : {self.podcast.name}'



