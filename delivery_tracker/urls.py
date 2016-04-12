from django.conf.urls import url
from django.shortcuts import redirect

from delivery_tracker import views


urlpatterns = [
    # TODO: convention trailing slash means no modification to DB
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
    url(r'^tracker/orders_and_bills/$',
        views.orders_and_bills, name='orders_and_bills'),
    url(r'^tracker/new_order/$', views.new_order, name='new_order'),
    url(r'^tracker/my_orders/(?P<status>\w+)$',
        views.my_orders, name='my_orders'),
    url(r'^tracker/order/(?P<order_id>\w+)/details/$',
        views.purchase_order, name='order'),

    url(r'^tracker/ajax/my_orders/get_linked_shops/$',
        views.ajax_linked_shops, name='ajax_linked_shops'),
    url(r'^tracker/ajax/my_orders/get_status_log/$',
        views.ajax_status_log, name='ajax_status_log'),
    url(r'^tracker/ajax/my_orders/get_linked_bills/$',
        views.ajax_linked_bills, name='ajax_linked_bills'),
    url(r'^tracker/ajax/my_orders/get_linked_in_parcels/$',
        views.ajax_linked_incoming_parcels, name='ajax_linked_in_parcels'),
    url(r'^tracker/ajax/my_orders/get_linked_out_parcels/$',
        views.ajax_linked_outcoming_parcels, name='ajax_linked_out_parcels'),
]



