from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
#   still allowing.....tracks//777 through although track_id is still correctly
#   identified as 777
    url(r'^\/api\/v1.0\/tracks\/?(\/(\d+))?$', views.tracks, name='Tracks'),
    url(r'^\/api\/v1.0\/trackdetails\/?(\/(\d+))?$', views.trackdetails, name='Tracks'),
    url(r'^\/api\/v1.0\/users\/?(\/(.+))?$', views.users, name='Users'),
    url(r'^\/api\/v1.0\/images\/?(\/(.+))?$', views.images, name='Images'),
    url(r'^\/api\/v1.0\/login\/?$', views.login, name='Login')

]