from django.contrib import admin
from .models import *


admin.site.register(Post)
admin.site.register(Comment)

admin.site.register(LikedPost)
admin.site.register(LikedComment)

admin.site.register(MainPodcast)
admin.site.register(Podcast)
admin.site.register(LikedPodcast)
# Register your models here.
