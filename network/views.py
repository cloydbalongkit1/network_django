import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .models import User, Post, Comment
from django.http import JsonResponse



def index(request):
    user_posts = Post.objects.all()[::-1]
    return render(request, "network/index.html", {"posts": user_posts})


@login_required
def post(request):
    if request.method == "POST":
        composed_post = request.POST.get('compose')
        created_by = request.user
        user_post = Post(new_post=composed_post, created_by=created_by)
        user_post.save()
        return redirect('index')
    return redirect('index')



@login_required
def liked(request):
    if request.method == "POST":
        data = json.loads(request.body)  # Parses the JSON body of the request
        print(data)
        post_id = data.get('post_id')
        if post_id:
            post = get_object_or_404(Post, id=post_id)  # Safely retrieves the Post object
            post.likes += 1  # Increments the likes count
            post.save()  # Saves the updated Post
            return JsonResponse({'success': True, 'likes': post.likes})  # Returns a JSON response with success status and updated like count
    return JsonResponse({'success': False})  # Returns a JSON response with failure status if something goes wrong



def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
