from django.contrib.auth.models import AbstractUser
from django.db import models



class User(AbstractUser):
    pass


class Post(models.Model):
    new_post = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_posts')
    date_created = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.new_post[:50]} - {self.created_by}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    commented_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_comments')
    commented_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.comment[:50]} - {self.commented_by}"
