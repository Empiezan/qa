from django.conf.urls import url

from . import views

from django.conf import settings
from django.conf.urls.static import static

# slugs are for passing variables between views
# static media refers to the css files
app_name = 'qa'
urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name='home'),
    url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    url(r'^reply/(?P<slug>.*)/$', views.ReplyView.as_view(), name='reply'),
    url(r'^replying/(?P<slug>.*)$', views.replying, name='replying'),
    url(r'^login/$', views.LoginView.as_view()),
    url(r'^register/$', views.RegisterView.as_view()),
    url(r'^logout/$', views.LogoutView.as_view()),
    url(r'^ask/$', views.AskView.as_view()),
    url(r'^profile/$', views.ProfileView.as_view(), name='profile'),
    url(r'^home/$', views.GoHome, name='GoHome'),
    url(r'^(?P<slug>.*)/vote/$', views.vote, name='vote'),
    url(r'^(?P<slug>.*)/comment/$', views.comment, name='comment'),
    url(r'^(?P<slug>.*)/delComment/$', views.delComment, name='delComment'),
    url(r'^(?P<slug>.*)/delReply/$', views.delReply, name='delReply'),
    url(r'^(?P<slug>.*)/favorite/$', views.favorite, name='favorite'),
    url(r'^(?P<slug>.*)/report/$', views.report, name='report'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
