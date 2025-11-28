from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.loginRoom, name="login"),
    path('logout/', views.logoutRoom, name="logout"),
    path('register/', views.registerRoom, name="register"),
    path('user-profile/<str:pk>', views.userProfile, name="user-profile"),

    path('', views.home, name="home"),
    path('room/<str:pk>/', views.room, name="room"),
    path('delete-message/<str:pk>', views.deleteMessage, name="delete-message"),

    path('create-room', views.createRoom, name="create-room"),
    path('edit-room/<str:pk>', views.editRoom, name="edit-room"),
    path('delete-room/<str:pk>', views.deleteRoom, name="delete-room")
]