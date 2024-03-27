"""
URL configuration for Emocom project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from emotions import views
from chat import views_chat
from django.conf.urls.i18n import i18n_patterns

urlpatterns = i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('emotions.urls')),
    path('chat/', include('chat.urls')),
    path('accounts/', include('allauth.urls')),
    
    path('voice_auth/', views.voice_auth, name='voice_auth'),
    path('enroll/', views.enroll_route, name='enroll'),
    path('recognize/', views.recognize_route, name='recognize'),

    path('voice_emotion/', views.voice_emotion, name='voice_emotion'),
    path('detect_voice_emotion/', views.classify, name= 'detect_voice_emotion' ),


    path('home_room/',views_chat.home , name='home_room'),
    path('<str:room>/', views_chat.room, name='room'),
    path('checkview', views_chat.checkview, name='checkview'),
    path('send', views_chat.send, name='send'),
    path('getMessages/<str:room>/', views_chat.getMessages, name='getMessages'),


)