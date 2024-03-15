from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from emotions import views
from . views import (Home,Dash,create_checkout_session,
	success,cancel,home,detect_face_emotion,detect_voice,
	detect_pose,ProfileUpdateView, email_history)

app_name = 'emotions'

urlpatterns = [
	path('', views.Home, name='homepage'),
	path('detect_face_emotion/', views.detect_face_emotion, name='detect_face_emotion'),
	path('detect_face/', views.detect_face_emotion, name='detect_face'),
	path('detect_voice/', views.detect_voice, name='detect_voice'),
	path('detect_pose/', views.detect_pose, name='detect_pose'),
	path('dashboard/', views.Dash, name='dashboard'),
	path('home', views.home, name='home'),
    path('create_checkout_session/', views.create_checkout_session, name='checkout'),
    path('success.html/', views.success, name='success'),
    path('cancel.html/', views.cancel, name='cancel'),
	path('update_profile/', ProfileUpdateView.as_view(), name='update_profile'),
    path('email_history/', views.email_history, name='email_history'),
    path('stream_video_feed/', views.stream_video_feed, name='stream_video_feed')

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)