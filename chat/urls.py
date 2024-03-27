from django.urls import path
from chat import views_chat

urlpatterns = ( 
    path('home/', views_chat.home, name='home'),
    path('<str:room>/', views_chat.room, name='room'),
    path('checkview', views_chat.checkview, name='checkview'),
    path('send', views_chat.send, name='send'),
    path('getMessages/<str:room>/', views_chat.getMessages, name='getMessages'),
)