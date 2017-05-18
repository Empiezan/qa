# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

import datetime

# Sum will be used to tally up the total number of votes a user has received
from django.db.models import Sum
from django.contrib.auth.models import User

from django.db.models.signals import post_save
from django.dispatch import receiver

from django.utils.encoding import python_2_unicode_compatible
# Create your models here.

# Profile is a class derived from the User class
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, primary_key=True)
    photo = models.ImageField(upload_to='', default = 'default/no-img.png')
    reputation = models.BigIntegerField(default=0)
    reported = models.BooleanField(default=False)

    def __str__(self):
        return self.image.url

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, name=instance.username)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Post(models.Model):
    post_text = models.TextField()
    author = models.CharField(max_length=200,default='guest')
    pub_date = models.DateTimeField('date published')
    vote_count = models.IntegerField(default=0)
    # a post can be favorited by many users and a user can favorite many posts
    favorited_by = models.ManyToManyField(Profile)
    def __str__(self):
        return self.post_text

class Comment(models.Model):
    comment_text = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    vote_count = models.IntegerField(default=0)
    def __str__(self):
        return self.comment_text

class Reply(models.Model):
    reply_text = models.TextField()
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    author = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    def __str__(self):
        return self.reply_text
