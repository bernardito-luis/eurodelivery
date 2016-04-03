import datetime
from uuid import uuid4

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import (
    authenticate, login, logout, update_session_auth_hash
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import HttpResponseNotFound, HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string

from delivery_tracker.forms import UserForm, ForgotPasswordForm, UserInfoForm
from delivery_tracker.models import (
    UserRegistrationLink, PurchaseOrder, Product, PurchaseOrderStatus)
from delivery_tracker.models import CURRENT_FEE, PURCHASE_ORDER_STATUS
from delivery_tracker.utils import generate_password


def home_page(request):
    return redirect('cabinet')


def register(request):
    registered = False

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)

        if user_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.is_active = 0
            user.save()
            registered = True

            new_slug = str(uuid4()).replace('-', '')
            while UserRegistrationLink.objects.filter(slug=new_slug).count():
                new_slug = str(uuid4()).replace('-', '')
            UserRegistrationLink.objects.create(
                user=user,
                slug=new_slug,
                created_date=datetime.datetime.now()
            )

            # TODO: fix texts and link
            link = ('%s/tracker/finish_registration/%s/' %
                    (request.get_host(), new_slug, ))
            text_msg = render_to_string(
                'delivery_tracker/email/finish_registration.txt',
                {'registration_link': link}
            )
            html_msg = render_to_string(
                'delivery_tracker/email/finish_registration.html',
                {'registration_link': link}
            )
            send_mail(
                'Finish your registration at EuroDelivery',
                text_msg,
                settings.EMAIL_HOST_USER,
                [user.username, ],
                fail_silently=False,
                html_message=html_msg
            )

    else:
        user_form = UserForm()

    return render(
        request,
        'delivery_tracker/register.html',
        {'user_form': user_form, 'registered': registered}
    )


def finish_registration(request, slug):
    try:
        link = UserRegistrationLink.objects.get(slug=slug)
        link.user.is_active = 1
        link.user.save()
        return HttpResponse('Congratz! Registration finished!')
    except UserRegistrationLink.DoesNotExist:
        return HttpResponse('Sorry, but your link is incorrect.')


def forgot_password(request):
    password_restore_message = ''
    if request.method == 'POST':
        forgot_password_form = ForgotPasswordForm(data=request.POST)
        if forgot_password_form.is_valid():
            username = forgot_password_form.data.get('registered_email')
            try:
                user = User.objects.get(username=username)
                new_password = generate_password()
                text_msg = render_to_string(
                    'delivery_tracker/email/restore_password.txt',
                    {'new_password': new_password}
                )
                html_msg = render_to_string(
                    'delivery_tracker/email/restore_password.html',
                    {'new_password': new_password}
                )
                send_mail(
                    'Your new password at EuroDelivery',
                    text_msg,
                    settings.EMAIL_HOST_USER,
                    [user.username, ],
                    fail_silently=False,
                    html_message=html_msg
                )
                user.set_password(new_password)
                user.save()
                password_restore_message = (
                    'We have sent a new password to the specified email'
                )
            except User.DoesNotExist:
                password_restore_message = 'No user with such email'
        else:
            pass
    else:
        forgot_password_form = ForgotPasswordForm()

    context = {
        'forgot_password_form': forgot_password_form,
        'password_restore_message': password_restore_message
    }
    return render(
        request,
        'delivery_tracker/forgot_password.html',
        context
    )


def user_login(request):
    context = dict()
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return redirect('cabinet')
            else:
                context['status_message'] = 'Your account has been expired'
        else:
            context['status_message'] = 'Invalid username or password'

    return render(request, 'delivery_tracker/login.html', context)


@login_required
def user_logout(request):
    logout(request)
    return redirect('home_page')


@login_required
def cabinet(request):
    return render(request, 'delivery_tracker/cabinet.html')


@login_required
def personal_data(request):
    context = dict()
    context['messages'] = messages.get_messages(request)
    if request.method == "POST" and 'profile_changes' in request.POST:
        form = UserInfoForm(data=request.POST)
        if form.is_valid():
            request.user.first_name = form.data['first_name']
            request.user.last_name = form.data['last_name']
            if request.user.username != form.data['email']:
                messages.add_message(
                    request,
                    messages.INFO,
                    u'Внимание! логин изменен на %s' % (form.data['email'], )
                )
            request.user.username = form.data['email']
            request.user.save()
            messages.add_message(
                request,
                messages.INFO,
                u'Изменения сохранены'
            )
            return redirect('cabinet_personal_data')
    elif request.method == "POST" and 'password_change' in request.POST:
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_new_password = request.POST.get('confirm_new_password')

        if not request.user.check_password(old_password):
            messages.add_message(
                request,
                messages.INFO,
                u'Неверно введен текущий пароль'
            )
            return redirect('cabinet_personal_data')
        if new_password != confirm_new_password:
            messages.add_message(
                request,
                messages.INFO,
                u'Введенные пароли не совпадают'
            )
            return redirect('cabinet_personal_data')

        request.user.set_password(new_password)
        request.user.save()
        update_session_auth_hash(request, request.user)
        messages.add_message(
            request,
            messages.INFO,
            u'Пароль изменен'
        )
        return redirect('cabinet_personal_data')
    else:
        init_values = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.username,
            'password': '******',
        }
        form = UserInfoForm(initial=init_values)
    context = {'form': form, 'masked_password': '******'}
    return render(request, 'delivery_tracker/personal_data.html', context)


@login_required
def orders_and_bills(request):
    return redirect('new_order')


@login_required
def new_order(request):
    context = dict()
    context['current_fee'] = CURRENT_FEE
    if request.method == 'POST':
        new_purchase_order = PurchaseOrder.objects.create(
            user=request.user,
            status=PurchaseOrderStatus.objects.get(
                id=PURCHASE_ORDER_STATUS['ordered']
            ),
            shipping_cost=request.POST['shipping_cost'] or 0,
            coupon=request.POST['coupon'],
            discount=request.POST['discount'] or 0,
            user_comment=request.POST['user_comment']
        )
        i = 0
        print(request.POST)
        while True:
            i += 1
            try:
                prod_link = request.POST['product_link_%d' % (i, )]
            except KeyError:
                break
            if (not request.POST.get('product_link_%d' % (i, )) or
                not request.POST.get('color_%d' % (i, )) or
                not request.POST.get('size_%d' % (i, )) or
                not request.POST.get('quantity_%d' % (i, )) or
                not request.POST.get('price_%d' % (i, )) or
                request.POST.get('discount_in_shop_%d' % (i, )) is None
            ):
                messages.add_message(
                    request,
                    messages.INFO,
                    u'Не заполнены обязательные поля у товаров!'
                )
                return redirect('new_order')
            try:
                Product.objects.create(
                    purchase_order=new_purchase_order,
                    user=request.user,
                    shop_link=request.POST['shop_link_%d' % (i, )],
                    product_link=request.POST['product_link_%d' % (i, )],
                    vendor_code=request.POST['vendor_code_%d' % (i, )],
                    name=request.POST['name_%d' % (i, )],
                    color=request.POST['color_%d' % (i, )],
                    size=request.POST['size_%d' % (i, )],
                    quantity=request.POST['quantity_%d' % (i, )],
                    price=request.POST['price_%d' % (i, )],
                    discount_code=request.POST['discount_code_%d' % (i, )],
                    discount_in_shop=request.POST['discount_in_shop_%d' % (i, )],
                    note=request.POST['note_%d' % (i, )]
                )
            except KeyError:
                break
    return render(request, 'delivery_tracker/new_order.html', context)


@login_required
def my_orders(request, status):
    context = dict()
    if status == 'active':
        cur_status = (
            PURCHASE_ORDER_STATUS['ordered'],
            PURCHASE_ORDER_STATUS['waits_for_payment'],
            PURCHASE_ORDER_STATUS['in_progress'],
            PURCHASE_ORDER_STATUS['coming_to_storage'],
            PURCHASE_ORDER_STATUS['received_partially'],
        )
    elif status == 'draft':
        cur_status = (
            PURCHASE_ORDER_STATUS['draft'],
        )
    elif status == 'archive':
        cur_status = (
            PURCHASE_ORDER_STATUS['canceled'],
            PURCHASE_ORDER_STATUS['received_to_stock'],
        )
    else:
        return HttpResponseNotFound('<h1>Страница не найдена</h1>')
    context['active_tab'] = status

    context['orders'] = PurchaseOrder.objects.filter(
        user=request.user,
        status_id__in=cur_status
    )


    return render(request, 'delivery_tracker/my_orders.html', context)
