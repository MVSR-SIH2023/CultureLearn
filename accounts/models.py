from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.templatetags.static import static
from PIL import Image
from django.contrib.auth.models import AbstractUser
from django.db.models import F
from datetime import date
from datetime import datetime
class User(AbstractUser):
    email = models.EmailField(unique=True,null = False, blank = False)
    



def user_profile_path(instance, filename):
    #file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'profile/user_{0}/{1}'.format(instance.user.id, filename)

class Profile(models.Model):
    
    # Choices for language preferences field
    ROLE_CHOICES = [
        ("normal", "Normal"),
        ("expert", "Expert"),
        ("admin", "Admin"),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    image = models.ImageField(upload_to=user_profile_path, null=True, blank=True )              
    realname = models.CharField(max_length=25, null=True, blank=True)
    email = models.EmailField(unique=True, null=True)
    bio = models.TextField(null=True, blank=True) 
    created = models.DateTimeField(auto_now_add=True)
    notification = models.BooleanField(default=False)
    contributions = models.IntegerField(default=0)
    
    def __str__(self):
        return str(self.user.username)
    
    @property
    def avatar(self):
        try:
            avatar = self.image.url
        except:
            avatar = None
        return avatar
    @property
    def name(self):
        if self.realname:
            full_name = f"{self.user.first_name} {self.user.last_name}"
        else:
            full_name = self.user.username
        return full_name
    
    
    def modify_reputation(self, added_points):
        """Core function to modify the reputation of the user profile."""
        try:
            self.contributions += added_points
            self.save()
        except:
            pass
        
    
    def save(self, *args, **kwargs):

        if self.image:  # Check if an image is present
            img = Image.open(self.image)
            max_size = (500, 500)  # Define maximum dimensions (width, height)
            img.thumbnail(max_size)
            img.save(self.image.path)

        super().save(*args, **kwargs)
        
def validate_pdf_file_extension(value):
    if not value.name.endswith('.pdf'):
        raise ValidationError("Only pdf files are allowed.") 
    
class Pending(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"), 
    ]
    applicant = models.ForeignKey(User, related_name="applicant", on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    resume = models.FileField(upload_to="resume/",validators=[FileExtensionValidator(['pdf']), validate_pdf_file_extension]) 
    letter = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name_plural = 'applicants'
    def __str__(self):
        return f"{self.applicant} - {self.created}"
    
    #function te retrieve the stored resumes 
    def get_file(self):
        try:
            file = open(self.resume.path,'r').readlines()
            return file
        except Exception as e:
            print("Error in retrieving files")
            
            

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"
        
   
    
class Workshop(models.Model):
    MODE = [
        ('Online','Online'),
        ('Offline','Offline'),
        ('Hybrid','Hybrid'),
    ]
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to="workshop_images/")
    organiser = models.ForeignKey(User,on_delete=models.CASCADE,related_name='workshops')
    mode = models.CharField(max_length=7,choices=MODE)
    start_date = models.DateField()
    end_date = models.DateField()
    r_opening_date = models.DateField(default=date(2023, 11, 1)) #registration opening date
    r_closing_date = models.DateField(default=date(2023, 11, 1))
    duration = models.CharField(max_length=100)
    Address = models.TextField(max_length=200)
    Platform = models.TextField(max_length=50)  #What you will Learn
    wyl = models.TextField(max_length=200,default="hello")
    created = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        follow =  Follow.objects.filter(following=self.organiser)
        for f in follow:
            current_datetime = datetime.now()
            print("created notification")
            notification.objects.create(user=f.follower,
                                         notification_type=3, #workshop notification type
                                         content_id=self.id,
                                         is_viewed=False,
                                         date_time=current_datetime,
                                         following_user = self.organiser.username)
    
    
class Workshop_register(models.Model):
    registered_user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='registered')
    workshop=models.ForeignKey(Workshop,on_delete=models.CASCADE)
    registered_date=models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('registered_user', 'workshop')

    def __str__(self):
        return self.registered_user.username+" registered for " + self.workshop.name
    
    
class Workshop_messeges(models.Model):
    workshop=models.ForeignKey(Workshop,on_delete=models.CASCADE,related_name='messages')
    content=models.TextField(max_length=500)
    created=models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.workshop.name  
    
class notification(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='notifications')
    following_user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='notification_by')
    notification_type = models.IntegerField() # articles --> 1, podcast -->2, workshop -->3,follow -->4,festival -->5
    content_id = models.IntegerField()
    is_viewed = models.BooleanField()
    date_time = models.DateTimeField(auto_now_add=True)

class static_pages(models.Model):
    name = models.CharField(max_length=100,unique=True)
    url = models.CharField(max_length=100,unique=True)

    def _str_(self):
        return self.name