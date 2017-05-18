# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Create your views here.

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Sum
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.models import User
from django.views import View

import datetime

import logging

from .forms import SearchForm, LogForm, LogoutForm, AskForm, DeleteForm, VoteForm, CommentForm, ReplyForm, ImageUploadForm
from .models import Post, Comment, Reply, Profile


class HomeView(generic.ListView):
    form_class = SearchForm
    initial = {'keyword' : ''}
    template_name = 'qa/index.html'
    context_object_name = 'post_list'
    model = Post

    def get(self, request, *args, **kwargs):
        vote_count = request.GET.get('vote_count', None)
        pub_date = request.GET.get('pub_date', None)
        keyword = request.GET.get('keyword', None)
        post = Post.objects.all()

        if keyword and keyword != '':
            post = post.filter(post_text=keyword)
        elif pub_date:
            post = post.order_by('-pub_date')
        else:
            post = post.order_by('-vote_count')
        # Show 25 posts per page
        paginator = Paginator(post, 25)

        page = request.GET.get('page')
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            posts = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            posts = paginator.page(paginator.num_pages)

        # form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'post_list': posts})


class DetailView(generic.DetailView):
    form_class = CommentForm
    initial= {'comment' : 'some comment'}
    model = Post
    template_name = 'qa/detail.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        # get the numeric id of the post being viewed from the url
        postid = request.get_full_path().split('/')[-2]
        post = Post.objects.get(id=postid)
        return render(request, self.template_name, {'form': form, 'post': post})


class LoginView(View):
    form_class = LogForm
    initial = {'username': '','password': ''}
    template_name = 'qa/login.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            # process the data in form.cleaned_data as required
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                request.session['authenticated'] = True
                login(request, user)
                # Redirect to a success page.
                return HttpResponseRedirect('/qa/')
            else:
                # Return an 'invalid login' error message.
                return HttpResponseRedirect('/qa/login/')

        return render(request, self.template_name, {'form': form})

class RegisterView(View):
    form_class = LogForm
    initial = {'username' : '', 'password': ''}
    template_name = 'qa/register.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            # process the data in form.cleaned_data as required
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # Return an 'invalid registration' error message.
                return HttpResponseRedirect(reverse('qa:home'))
            else:
                user = User.objects.create_user(username, 'example@wustl.edu', password)
                user.save()
                login(request, user)
                # Redirect to a success page.
                return HttpResponseRedirect(reverse('qa:home'))

        return render(request, self.template_name, {'form': form})

class LogoutView(View):
    form_class = LogoutForm
    initial = {'filler':'filled'}
    template_name = 'qa/logout.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect('/qa/')

class AskView(View):
    form_class = AskForm
    initial = {'question': 'e.g., What is the best way to stay awake?'}
    template_name = 'qa/ask.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            text = request.POST['question']
            p = Post(post_text = text, pub_date = datetime.datetime.now())
            if request.user.is_authenticated():
                p.author = request.user.username
            p.save()
            return HttpResponseRedirect('/qa/')
        # process the data in form.cleaned_data as required
        return render(request, self.template_name, {'form': form})

class ProfileView(generic.ListView):
    form_class = DeleteForm
    initial = {'hidden':''}
    template_name = 'qa/profile.html'
    context_object_name = 'post_list'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProfileView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        prof = get_object_or_404(Profile, name=request.user.username)
        # add up all of the upvotes and downvotes a user has received to represent their reputation
        prof.reputation = Post.objects.filter(author=request.user.username).aggregate(Sum('vote_count'))
        reputation = prof.reputation['vote_count__sum']
        photo = prof.photo
        reply = Comment.objects.filter(author=self.request.user.username).order_by('-pub_date')
        comment = Comment.objects.filter(author=self.request.user.username).order_by('-pub_date')
        post = Post.objects.filter(author=self.request.user.username).order_by('-vote_count')
        favorites = prof.post_set.all()
        progress = 0
        if reputation > 100:
            progress = 100
        else:
            progress = reputation
        # if the user has not reached 100 net upvotes, then the text will indicate how many more points the user needs
        progress_text = str(100-progress) + ' more points to next badge!'

        if progress == 100:
            progress_text = str(progress) + ' point milestone reached!'

        reportees = Profile.objects.filter(reported=True)

        return render(request, self.template_name, {'post_list': post, 'photo': photo, 'reply': reply, 'comment': comment, 'reputation':reputation, 'favorites':favorites, 'progress':progress, 'progress_text':progress_text, 'reportees':reportees})

    # receives post data for users uploading profile pictures and deleting their own posts from the profile page
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        p = Profile.objects.get(name = request.user.username)
        image_form = ImageUploadForm(request.POST, request.FILES)
        if image_form.is_valid():
            p.photo = image_form.cleaned_data['image']
            p.save()
        if form.is_valid():
            post_id = request.POST['hidden']
            if request.user.is_authenticated():
                Post.objects.get(id = int(post_id)).delete()
        return HttpResponseRedirect(reverse('qa:profile'))

def GoHome(request):
    return HttpResponseRedirect('/qa/')

def vote(request, slug):
    post = get_object_or_404(Post, pk=slug)
    selected_choice = request.POST['choice']
    if selected_choice == 'upvote':
        post.vote_count += 1
    else:
        post.vote_count -= 1
    post.save()
    # Always return an HttpResponseRedirect after successfully dealing
    # with POST data. This prevents data from being posted twice if a
    # user hits the Back button.
    return HttpResponseRedirect(reverse('qa:detail', args=(post.id,)))

def comment(request, slug):
    # get the Post to which the user is attempted to comment on
    p = get_object_or_404(Post, pk=slug)
    # create a Comment associated with that Post
    c = Comment(comment_text=request.POST['comment'],author=request.user.username,pub_date=datetime.datetime.now(),post=p)
    c.save()
    return HttpResponseRedirect(reverse('qa:detail', args=(p.id,)))

class ReplyView(generic.DetailView):
    form_class = ReplyForm
    initial = {'reply': 'i agree'}
    model = Comment
    template_name = 'qa/reply.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        comment_id = request.get_full_path().split('/')[-2]
        comment = Comment.objects.get(id=comment_id)
        return render(request, self.template_name, {'form': form, 'comm':comment})

def replying(request, slug):
    c = get_object_or_404(Comment, pk=slug)
    r = Reply(reply_text=request.POST['reply'],author=request.user.username,pub_date=datetime.datetime.now(),comment=c)
    r.save()
    p = get_object_or_404(Post, pk=c.post.id)
    return HttpResponseRedirect(reverse('qa:detail', args=(p.id,)))

def delComment(request, slug):
    c = get_object_or_404(Comment, pk=slug)
    c.delete()
    p = get_object_or_404(Post, pk=c.post.id)
    return HttpResponseRedirect(reverse('qa:detail', args=(p.id,)))

def delReply(request, slug):
    r = get_object_or_404(Reply, pk=slug)
    r.delete()
    c = get_object_or_404(Comment, pk=r.comment.id)
    p = get_object_or_404(Post, pk=c.post.id)
    return HttpResponseRedirect(reverse('qa:detail', args=(p.id,)))

def favorite(request, slug):
    p = get_object_or_404(Post, pk=slug)
    prof = get_object_or_404(Profile, name=request.user.username)
    p.favorited_by.add(prof)
    return HttpResponseRedirect(reverse('qa:detail', args=(p.id,)))

def report(request, slug):
    p = get_object_or_404(Post, pk=slug)
    prof = get_object_or_404(Profile, name=p.author)
    prof.reported = True
    prof.save()
    return HttpResponseRedirect(reverse('qa:detail', args=(p.id,)))
