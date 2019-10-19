from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
import uuid
import os
import datetime


def get_file_path(instance, filename):
    filename, ext = filename.split('.')[-2:]
    filename = "%s.%s.%s" % (str(uuid.uuid4().hex)[:10], filename, ext)
    today = datetime.datetime.today()
    return os.path.join('uploads', str(today.year), str(today.month), str(today.day), filename)

# Create your models here.


class Channel(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    is_user_self_channel = models.BooleanField(default=False)
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=256)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.constraints.UniqueConstraint(
                fields=['owner'],
                condition=Q(is_user_self_channel=True),
                name='user_self_channel',
            ),
        ]


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, null=False)
    followed_on = models.DateTimeField(auto_now_add=True)


class Post(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, null=False)
    text = models.TextField(max_length=1000, null=True)
    file = models.FileField(upload_to=get_file_path)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.constraints.CheckConstraint(
                check=~Q(Q(file='') & Q(text='')),
                name='text_or_file_must_filled'
            ),
        ]



class Seen(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=False)
    created_on = models.DateTimeField(auto_now_add=True)


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=False)
    created_on = models.DateTimeField(auto_now_add=True)


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=False)
    created_on = models.DateTimeField(auto_now_add=True)

