
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("post", views.post, name="post"),
    path("view/post/<int:id>/", views.view_post, name="view_post"),
    path("liked", views.liked, name="liked_button"),
    path("profile/<int:id>/", views.profile, name="user_profile"),
    path('view/profile/<int:id>/', views.view_profile, name="view_profile"),
    path('follow', views.follow, name="follow"),
    path('following', views.following, name="following"),
    path('all/posts', views.all_posts, name="all_posts"),
    path('edit/posts/<int:id>', views.edit_post, name="edit_post"),
]   

