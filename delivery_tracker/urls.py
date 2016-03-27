from django.conf.urls import url

from delivery_tracker import views


urlpatterns = [
    url(r'^$', views.home_page, name='home_page'),
    url(r'^tracker/register/$', views.register, name='register'),
    url(r'^tracker/finish_registration/(?P<slug>\w+)/$',
        views.finish_registration, name='finish_registration'),
    url(r'^tracker/forgot_password/$',
        views.forgot_password, name='forgot_password'),
    url(r'^tracker/login/$',
        views.user_login, name='login'),
    url(r'^tracker/logout/$',
        views.user_logout, name='logout'),
    url(r'^tracker/cabinet/$',
        views.cabinet, name='cabinet'),
    url(r'^tracker/cabinet/personal_data/$',
        views.personal_data, name='cabinet_personal_data'),
]
