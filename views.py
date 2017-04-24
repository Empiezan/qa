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
from django.contrib.auth.models import User
from django.views import View

import datetime

import logging

from .forms import LogForm, LogoutForm, AskForm, DeleteForm
from .models import Post, Comment


class HomeView(generic.ListView):
    template_name = 'qa/index.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        """Return the last twenty-five published questions."""
        return Post.objects.order_by('-vote_count')[:25]

class DetailView(generic.DetailView):
    model = Post
    template_name = 'qa/detail.html'

class LoginView(View):
    form_class = LogForm
    initial = {'username': '','password': ''}
    template_name = 'qa/login.html'
    # m = Member.objects.get(username=request.POST['username'])

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

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

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            # process the data in form.cleaned_data as required
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # Return an 'invalid registration' error message.
                return HttpResponseRedirect('/qa/register')
            else:
                user = User.objects.create_user(username, 'example@wustl.edu', password)
                user.save()
                # Redirect to a success page.
                login(request, user)
                return HttpResponseRedirect('/qa/')

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
        # return render(request, self.template_name, {'form': form}

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

    def get_queryset(self):
        """Return the last ten published questions."""
        return Post.objects.filter(author=self.request.user).order_by('-vote_count')[:10]

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            post_id = request.POST['hidden']
            if request.user.is_authenticated():
                Post.objects.get(id = int(post_id)).delete()
            return HttpResponseRedirect('/qa/profile/')
        # process the data in form.cleaned_data as required
        return render(request, self.template_name, {'form': form})
