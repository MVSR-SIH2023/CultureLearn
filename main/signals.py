# from django.dispatch import receiver
# from django.db.models.signals import post_save
# from main.models import *
# from accounts.models import notification,User

# @receiver(post_save, sender=Festival)
# def create_festival_notification(sender, instance, created, **kwargs):
#     if created:
       
#         users = User.objects.all() 

#         # Create a notification for each user
#         for user in users:
#             notify = notification.objects.create(
#                 user=user,
#                 following_user=None, 
#                 notification_type=5,  
#                 content_id=instance.id, 
#                 is_viewed=False,  
#             )
           
#             notify.save()