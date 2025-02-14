from logging import PlaceHolder
from typing_extensions import Self
from django.contrib.auth.models import AbstractUser
from django.db import models
from pytz import timezone
from .util import resize_image
from django_countries.fields import CountryField
from flatpickr import DatePickerInput


class User(AbstractUser):
    pass

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    name = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    about = models.TextField(blank=True, null=True)
    country = CountryField(blank=True, null=True)
    image = models.ImageField(default='media/profile_pics/default.png', upload_to="profile_pics", blank=True, null=True)
    
    
    def __str__(self):
        return f"{self.user.username}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        resize_image(self.image.path, 300, 300)
    

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE , related_name="posts", verbose_name="posted by")
    content = models.CharField(max_length=500, null=True, blank=False)
    date = models.DateTimeField(auto_now_add=True)
    categ=models.CharField(max_length=255,null=True, blank=False)
    liked = models.ManyToManyField(UserProfile, blank=True, related_name='likes',editable=True)
    
    def num_likes(self):
        return self.liked.all().count()
    
    def __str__(self):
        return f"Post {self.id} made by {self.user} on {self.date.strftime('%d %b %Y %H:%M:%S')}"
    
    class Meta:
        verbose_name = "post"
        verbose_name_plural = "posts"
        
class Comment(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="commented by")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField(blank=False)
    date = models.DateTimeField(auto_now_add=True, null=False, blank=True, verbose_name="commented on")
    
    class Meta:
        verbose_name = "comment"
        verbose_name_plural = "comments"
        ordering = ["date"]
    
    def __str__(self):
            return f"Comment {self.id} made by {self.user} on post {self.post_id} on {self.date.strftime('%d %b %Y %H:%M:%S')}"
        

class Following(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")
    user_followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers" )
    
    class Meta:
        verbose_name = "following"
        verbose_name_plural = "followings"
        unique_together = ['user', 'user_followed']
    
    def __str__(self):
        return f"{self.user} is following {self.user_followed}"

    def get_user_followed_posts(self):
        return self.user_followed.posts.order_by("-date").all()


LIKE_CHOICES = (
    ('Like', 'Like'),
    ('Unlike', 'Unlike'),
)

class Like(models.Model): 
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_like")
    value = models.CharField(choices=LIKE_CHOICES, max_length=8)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "likes"
    
    def __str__(self):
        return f"{self.user}-{self.post}-{self.value}"
    
    def val_likes(self):
            return self.value
