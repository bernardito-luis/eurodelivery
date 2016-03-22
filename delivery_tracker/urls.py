from django.conf.urls import url

from delivery_tracker import views


urlpatterns = [
    url(r'^register/$', views.register, name='register'),
    url(r'^finish_registration/(?P<slug>\w+)/$',
        views.finish_registration, name='finish_registration'),
    url(r'^forgot_password/$',
        views.forgot_password, name='forgot_password'),
    url(r'^login/$',
        views.user_login, name='login'),
    url(r'^cabinet/$',
        views.cabinet, name='cabinet'),
]
