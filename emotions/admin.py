from django.contrib import admin
from . models import Profile, Emotion, Plans,EmailHist

admin.site.register(Emotion)
admin.site.register(Profile)
admin.site.register(Plans)
admin.site.register(EmailHist)
