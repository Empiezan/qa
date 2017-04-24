# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

import datetime

from django.db.models import Sum
from django.contrib.auth.models import User

from django.utils.encoding import python_2_unicode_compatible
# Create your models here.

class Post(models.Model):
    post_text = models.TextField()
    author = models.CharField(max_length=200,default='Guest')
    pub_date = models.DateTimeField('date published')
    vote_count = models.IntegerField(default=0)
    def __str__(self):
        return self.post_text

# class Person(models.Model):
#     name = models.CharField(max_length=200,default='Guest', primary_key=True)
#     post = models.ForeignKey(Post)
#     reputation = models.BigIntegerField()
#
#     def save(self, *args, **kwargs):
#         self.reputation = self.post.objects.aggregate(Sum('vote_count'))
#         super(Person, self).save(*args, **kwargs)

class Comment(models.Model):
     comment = models.ForeignKey(Post, on_delete=models.CASCADE)
     author = models.CharField(max_length=200)
     pub_date = models.DateTimeField('date published')
     vote_count = models.IntegerField(default=0)
     def __str__(self):
        return self.comment_text
