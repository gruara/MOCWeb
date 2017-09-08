from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^\/api\/v1.0\/tracks\/$', views.tracks, name='Tracks')
]