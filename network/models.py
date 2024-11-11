from django.contrib.auth.models import AbstractUser
from django.db import models



class User(AbstractUser):
    followers = models.IntegerField(default=0)
    following = models.IntegerField(default=0)
    bio = models.CharField(max_length=500, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    work = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.username




class Post(models.Model):
    new_post = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_posts')
    date_created = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.new_post[:10]}... - {self.created_by}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    commented_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_comments')
    commented_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.comment[:50]} - {self.commented_by}"



class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_likes')

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return f"{self.user} likes {self.post}"
    


class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='following_set', on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name='followers_set', on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"

