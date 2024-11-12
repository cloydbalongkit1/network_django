import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .models import User, Like, Post, Follow, Comment
from .form import EditProfile




def index(request):
    all_posts = Post.objects.all()[::-1]
    return render(request, "network/index.html", {"posts": all_posts})


@login_required
def post(request):
    if request.method == "POST":
        composed_post = request.POST.get('compose')
        created_by = request.user
        user_post = Post(new_post=composed_post, created_by=created_by)
        user_post.save()

        source = request.POST.get('source')
        if source == 'profile':
            return redirect('user_profile')
        else:
            return redirect('index')
    return redirect('index')


# use javascript ---- OK
@login_required
def view_post(request, id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            post_id = id
            user_id = data.get('user_id')

            post = get_object_or_404(Post, id=post_id, created_by_id=user_id)
            post_details = {
                'id': post.id,
                'created_by': post.created_by.username,
                'created_by_id': post.created_by.id,  # Add this line to include author ID
                'new_post': post.new_post,
                'date_created': post.date_created,
                'likes': post.likes
            }
            return JsonResponse({'success': True, 'post': post_details})

        except (json.JSONDecodeError, KeyError, Post.DoesNotExist):
            return JsonResponse({'success': False, 'message': 'Invalid data or post not found.'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})






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
def follow(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            if user_id:
                user_to_follow = get_object_or_404(User, id=user_id)
                if user_to_follow != request.user:  # Ensure the user is not trying to follow themselves
                    # Check if the user is already following the specified user
                    is_following = Follow.objects.filter(follower=request.user, following=user_to_follow).exists()
                    if is_following:
                        # Unfollow the user
                        Follow.objects.filter(follower=request.user, following=user_to_follow).delete()
                        user_to_follow.followers -= 1
                        request.user.following -= 1
                        user_to_follow.save()
                        request.user.save()
                        return JsonResponse({'success': True, 'message': 'Unfollowed successfully.', 'followers': user_to_follow.followers})
                    else:
                        # Follow the user
                        Follow.objects.create(follower=request.user, following=user_to_follow)
                        user_to_follow.followers += 1
                        request.user.following += 1
                        user_to_follow.save()
                        request.user.save()
                        return JsonResponse({'success': True, 'message': 'Followed successfully.', 'followers': user_to_follow.followers})
                else:
                    return JsonResponse({'success': False, 'message': 'You cannot follow yourself.'})
        except (json.JSONDecodeError, KeyError):
            return JsonResponse({'success': False, 'message': 'Invalid data.'})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})



@login_required
def profile(request, id):
    user_profile = get_object_or_404(User, id=id)
    user_posts = Post.objects.filter(created_by=request.user).order_by('-date_created')
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

            redirect('user_profile', id=user_profile.id)
    
    return render(request, "network/profile.html", {
        'user': user_profile, 
        'form': form,
        'posts': user_posts,
        })



@login_required
def view_profile(request, id):
    if request.method == 'POST':
        # Extract data from the request body
        # user_id = request.data.get('user_id')  # Get the user ID from the POST body
        user_profile = get_object_or_404(User, id=id)

        # Fetch user posts
        user_posts = Post.objects.filter(created_by=user_profile).order_by('-date_created')

        # Construct profile data
        profile_data = {
            'id': user_profile.id,
            'first_name': user_profile.first_name,
            'last_name': user_profile.last_name,
            'username': user_profile.username,
            'bio': user_profile.bio,
            'work': user_profile.work,
            'location': user_profile.location,
            'date_joined': user_profile.date_joined.strftime('%B %Y'),
            'following': user_profile.following,
            'followers': user_profile.followers,
            'posts': [{
                'created_by': post.created_by.username,
                'new_post': post.new_post,
                'date_created': post.date_created.strftime('%Y-%m-%d %H:%M:%S'),
                'created_by_id': post.created_by.id,
                'id': post.id,
                'likes': post.likes,
            } for post in user_posts],
        }

        return JsonResponse({'success': True, 'profile': profile_data})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})




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
