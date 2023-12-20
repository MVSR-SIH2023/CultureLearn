from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from django.db.models.signals import post_save


from .models import *
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.core.files.storage import default_storage
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

@receiver(post_save, sender=User)  
def create_profile(sender, instance, created, **kwargs):
    user = instance
    if created:
        Profile.objects.create(
            user = user,
            email = user.email
        )
    else:
        profile = get_object_or_404(Profile, user=user)
        profile.email = user.email
        profile.save()
        
        
        
@receiver(post_save, sender=Profile)
def update_user(sender, instance, created, **kwargs):
    profile = instance
    if created == False:
        user = get_object_or_404(User, id=profile.user.id)
        if user.email != profile.email:
            user.email = profile.email
            user.save()




@receiver(post_save, sender=Pending)
def update_applicant_role(sender, instance, created, **kwargs):
    applicant = instance
    if not created:  # Check if the instance was not just created
        if applicant.status == 'accepted':  # Assuming 'accepted' is the status indicating approval
            user_profile = get_object_or_404(Profile, user=applicant.id)
            if user_profile.role == 'normal':
                user_profile.role = 'expert'
                user_profile.save()

                # Send congratulatory email
                send_congratulatory_email(user_profile)

def send_congratulatory_email(request, user_profile):
    subject = "Congratulations on becoming an expert!"
    
    from_email = settings.EMAIL_HOST_USER
    to_email = user_profile.user.email
    link_app = "http://localhost:8000/home"
    
    
    message2 = render_to_string('registration/email.html', {
        'name': user_profile.realname,
        'email': to_email,  
        'link_app': link_app,
    })
    
    email = EmailMessage(
        subject,
        message2,
        settings.EMAIL_HOST_USER,
        [to_email],
    )
    email.content_subtype = "html" 
    email.send(fail_silently=True)
    


@receiver(post_save, sender=Profile)
def update_account_email(sender, instance, created, **kwargs):
    profile = instance
    if not created:
        try:
            user = profile.user
            if profile.email != user.email:
                user.email = profile.email
                user.save()
        except User.DoesNotExist:
            pass
        
# Signal to delete profile picture and resume file before deleting the user
# @receiver(pre_delete, sender=User)
# def delete_user_related_files(sender, instance, **kwargs):
#     try:
#         profile = Profile.objects.get(user=instance)
#         if profile.image :
#             default_storage.delete(profile.image.path)
#     except Profile.DoesNotExist:
#         pass

#     # Check if the user has any pending items and delete associated resume files
#     try:
#         pending_items = Pending.objects.filter(user=instance)
#         file = pending_items.get_file()
#         default_storage.delete(file.path)
#         Pending.objects.filter(user=instance).delete()
#     except:
#         pass