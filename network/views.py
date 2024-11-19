import json
import random

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core.paginator import Paginator

from .models import User, Like, Post, Comment
from .form import EditProfile, EditPost



def index(request):
    all_posts = Post.objects.all()[::-1]
    if request.user.is_authenticated:
        selected_posts = all_posts[:10]
    else:
        selected_posts = random.sample(list(all_posts), 8) if len(all_posts) >= 8 else all_posts
         
    paginator = Paginator(selected_posts, 4)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, "network/index.html", {"page_obj": page_obj})


@login_required
def all_posts(request):
    all_posts = Post.objects.all()[::-1]

    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, "network/index.html", {"page_obj": page_obj})


@login_required
def edit_post(request, id):
    post = get_object_or_404(Post, id=id, created_by=request.user)

    if request.method == 'GET':
        form = EditPost(initial={'content': post.new_post})
        return render(request, 'network/edit_post.html', {'form': form, 'post': post})
    
    elif request.method == 'POST':
        data = json.loads(request.body)
        new_content = data.get('editPost')

        if new_content:
            post.new_post = new_content
            post.save()
            return JsonResponse({'status': 'success', 'message': 'Post updated successfully!'})

        return JsonResponse({'status': 'error', 'message': 'Invalid data submitted.'}, status=400)



@login_required
def post(request):
    if request.method == "POST":
        composed_post = request.POST.get('compose')
        created_by = request.user
        user_post = Post(new_post=composed_post, created_by=created_by)
        user_post.save()

        source = request.POST.get('source')
        if source == 'profile':
            return redirect('user_profile', id=request.user.id)
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
            viewed_user_id = data.get('viewed_user')
            logged_user = request.user

            print(logged_user)
            print(logged_user.following.all())

            viewed_user = get_object_or_404(User, id=viewed_user_id)

            if viewed_user in logged_user.following.all():
                logged_user.following.remove(viewed_user)
                following = False
            else:
                logged_user.following.add(viewed_user)
                following = True

            response_data = {
                "success": True,
                "following": following,
                "following_count": logged_user.following_count,
                "followers_count": viewed_user.followers_count,
            }

            return JsonResponse(response_data)
        except (ValueError, KeyError) as error:
            return JsonResponse({'success': False, 'message': str(error)}, status=400)
        except (json.JSONDecodeError):
            return JsonResponse({'success': False, 'message': 'Invalid data.'})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)




@login_required
def profile(request, id):
    user_profile = get_object_or_404(User, id=id)
    user_posts = Post.objects.filter(created_by=request.user).order_by('-date_created')
    form = EditProfile(instance=user_profile)

    followers = user_profile.followers.all()  
    following = user_profile.following.all()

    paginator = Paginator(user_posts, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST':
        form = EditProfile(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            redirect('user_profile', id=user_profile.id)
        
    return render(request, "network/profile.html", {
        'user': user_profile, 
        'form': form,
        'posts': page_obj,
        'followers': followers,
        'following': following,
        })



@login_required
def view_profile(request, id):
    if request.method == 'POST':
        viewed_profile = get_object_or_404(User, id=id)
        viewed_profile_posts = Post.objects.filter(created_by=viewed_profile).order_by('-date_created')

        page_number = int(request.POST.get('page', 1))
        paginator = Paginator(viewed_profile_posts, 5)  # Adjust number of posts per page as needed
        page_obj = paginator.get_page(page_number)

        is_following = request.user in viewed_profile.followers.all()
        profile_data = {
           'id': viewed_profile.id,
           'first_name': viewed_profile.first_name,
           'last_name': viewed_profile.last_name,
           'username': viewed_profile.username,
           'bio': viewed_profile.bio,
           'work': viewed_profile.work,
           'location': viewed_profile.location,
           'date_joined': viewed_profile.date_joined.strftime('%B %Y'),
           'following': len([user.username for user in viewed_profile.following.all()]),  # Serialize following
           'followers': len([user.username for user in viewed_profile.followers.all()]),  # Serialize followers
           'is_following': is_following, 
           'posts': [{
               'created_by': post.created_by.username,
               'new_post': post.new_post,
               'date_created': post.date_created.strftime('%Y-%m-%d %H:%M:%S'),
               'created_by_id': post.created_by.id,
               'id': post.id,
               'likes': post.likes,
                } for post in page_obj.object_list],
           'has_next': page_obj.has_next(),
           'has_previous': page_obj.has_previous(),
           'page_number': page_obj.number,
           'total_pages': paginator.num_pages,
        }
        return JsonResponse({'success': True, 'profile': profile_data, 'logged_in_user_id': request.user.id})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})



@login_required
def following(request):
    user = get_object_or_404(User, id=request.user.id)
    following_users = user.following.all()
    following_posts = Post.objects.filter(created_by__in=following_users).order_by('-date_created')

    paginator = Paginator(following_posts, 5)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, "network/index.html", {"page_obj": page_obj})



@login_required
def post_comments(request, post_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        comment_text = data.get('comment', '').strip()
        
        if not comment_text:
            return JsonResponse({'status': 'error', 'message': 'Comment cannot be empty'}, status=400)

        post = get_object_or_404(Post, id=post_id)
        comment = Comment.objects.create(post=post, comment=comment_text, commented_by=request.user)

        return JsonResponse({
            'status': 'success',
            'message': 'Comment posted successfully!',
            'comment': {
                'id': comment.id,
                'comment': comment.comment,
                'commented_by': comment.commented_by.username,
                'commented_date': comment.commented_date.strftime('%B %d, %Y %H:%M'),
            }
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)




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
