from django.conf.urls import url

from . import views
from qa.views import LoginView, RegisterView, LogoutView, AskView, ProfileView

app_name = 'qa'
urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name='home'),
    url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    url(r'^login/$', LoginView.as_view()),
    url(r'^register/$', RegisterView.as_view()),
    url(r'^logout/$', LogoutView.as_view()),
    url(r'^ask/$', AskView.as_view()),
    url(r'^profile/$', ProfileView.as_view()),
    url(r'^delete/$', ProfileView.as_view()),
]
