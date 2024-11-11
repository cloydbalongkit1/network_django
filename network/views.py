import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .models import User, Post, Comment, Like
from .form import EditProfile




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
        try:
            data = json.loads(request.body)
            post_id = data.get('post_id')
            if post_id:
                post = get_object_or_404(Post, id=post_id)
                if post.created_by != request.user:
                    already_liked = Like.objects.filter(post=post, user=request.user).exists()
                    if not already_liked:
                        Like.objects.create(post=post, user=request.user)
                        post.likes += 1
                        post.save()
                        return JsonResponse({'success': True, 'likes': post.likes})
                    else:
                        return JsonResponse({'success': False, 'message': 'You have already liked this post.'})
                else:
                    return JsonResponse({'success': False, 'message': 'You cannot like your own post.'})
        except (json.JSONDecodeError, KeyError):
            return JsonResponse({'success': False, 'message': 'Invalid data.'})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})



@login_required
def profile(request):
    id = request.user.id
    user_profile = get_object_or_404(User, id=id)
    form = EditProfile(instance=user_profile)

    if request.method == 'POST':
        form = EditProfile(request.POST, instance=user_profile)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            bio = form.cleaned_data['bio']
            location = form.cleaned_data['location']
            work = form.cleaned_data['work']
            user_profile.first_name = first_name
            user_profile.last_name = last_name 
            user_profile.bio = bio 
            user_profile.location = location 
            user_profile.work = work
            user_profile.save()

            redirect('user_profile')
    
    return render(request, "network/profile.html", {
        'user': user_profile, 
        'form': form
        })


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
