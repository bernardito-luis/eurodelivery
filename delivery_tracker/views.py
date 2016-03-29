import datetime
from uuid import uuid4

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect, HttpResponse
from django.template.loader import render_to_string

from delivery_tracker.forms import UserForm, ForgotPasswordForm, UserInfoForm
from delivery_tracker.models import UserRegistrationLink
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
    if request.method == "POST":
        form = UserInfoForm(data=request.POST)
    else:
        init_values = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.username,
            'password': '******',
        }
        form = UserInfoForm(initial=init_values)
    context = {'form': form}
    return render(request, 'delivery_tracker/personal_data.html', context)
