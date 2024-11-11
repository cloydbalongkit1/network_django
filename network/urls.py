
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("post", views.post, name="post"),
    path("liked", views.liked, name="liked_button"),
    path("profile/<int:id>/", views.profile, name="user_profile"),
    path("follow", views.follow, name="follow"),
    
]   

