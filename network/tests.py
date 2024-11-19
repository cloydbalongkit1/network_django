import json

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import User, Post, Comment, Like


class UserModelTestCase(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass123')
        self.user2 = User.objects.create_user(username='user2', password='pass123')

        self.user1.following.add(self.user2)

    def test_user_creation(self):
        self.assertEqual(User.objects.count(), 2)

    def test_followers_and_following(self):
        self.assertEqual(self.user1.following.count(), 1)
        self.assertEqual(self.user2.followers.count(), 1)


class PostModelTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='post_user', password='pass123')
        
        self.post1 = Post.objects.create(new_post="First Post", created_by=self.user)
        self.post2 = Post.objects.create(new_post="Second Post", created_by=self.user)

    def test_post_creation(self):
        self.assertEqual(Post.objects.count(), 2)
        self.assertEqual(self.post1.new_post, "First Post")
        self.assertEqual(self.post1.created_by, self.user)

    def test_post_string_representation(self):
        self.assertEqual(str(self.post1), "First Post... - post_user")


class CommentModelTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='comment_user', password='pass123')
        self.post = Post.objects.create(new_post="A post for comments", created_by=self.user)
        
        self.comment = Comment.objects.create(
            post=self.post, comment="This is a comment", commented_by=self.user
        )

    def test_comment_creation(self):
        self.assertEqual(self.post.comments.count(), 1)
        self.assertEqual(self.comment.comment, "This is a comment")

    def test_comment_string_representation(self):
        self.assertEqual(str(self.comment), "This is a comment - comment_user")


class LikeModelTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='like_user', password='pass123')
        self.post = Post.objects.create(new_post="A post for likes", created_by=self.user)
        
        self.like = Like.objects.create(post=self.post, user=self.user)

    def test_like_creation(self):
        self.assertEqual(self.post.post_likes.count(), 1)
        self.assertEqual(self.user.user_likes.count(), 1)

    def test_like_string_representation(self):
        self.assertEqual(str(self.like), "like_user likes A post for... - like_user")

    def test_like_uniqueness(self):
        with self.assertRaises(Exception):
            Like.objects.create(post=self.post, user=self.user)


class ClientTestCase(TestCase):
    
    def setUp(self):
        self.user1 = get_user_model().objects.create_user(username='user1', password='password123')
        self.user2 = get_user_model().objects.create_user(username='user2', password='password123')

        self.post = Post.objects.create(new_post="A test post", created_by=self.user1)
        self.client = Client()

    def test_user_registration(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com', 
            'password': 'password123', 
            'confirmation': 'password123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(get_user_model().objects.filter(username='newuser').exists())

    def test_create_post(self):
        self.client.login(username='user1', password='password123')
        response = self.client.post(reverse('post'), {'compose': "This is a new post"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Post.objects.filter(new_post="This is a new post").exists())

    def test_like_post(self):
        self.client.login(username='user2', password='password123')
        response = self.client.post(
            reverse('liked_button'),
            json.dumps({'post_id': self.post.id}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.post.refresh_from_db()
        self.assertEqual(self.post.likes, 1)

    def test_user_cannot_like_own_post(self):
        self.client.login(username='user1', password='password123')
        response = self.client.post(
            reverse('liked_button'),
            json.dumps({'post_id': self.post.id}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)
        self.post.refresh_from_db()
        self.assertEqual(self.post.likes, 0)


