from django import forms
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']

    # NB: you'll need to set auth_user username to VARCHAR(75)
    username = forms.EmailField(max_length=75, help_text="Enter your email")
    password = forms.CharField(widget=forms.PasswordInput())

    buf_username = None

    def clean_email(self):
        email = self.cleaned_data['username']
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        self.buf_username = username
        if not username:
            raise forms.ValidationError("Empty username is not allowed")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Such user already exists")

        return username

    def full_clean(self):
        super(UserForm, self).full_clean()
        if (self.buf_username and 'username' in self._errors and
                'at most 30' in self._errors['username']):
            del self._errors['username']
            if len(self.buf_username) > 75:
                raise forms.ValidationError(
                    "Ensure this value has at most 75 characters (it has %d)" %
                    (len(self.buf_username), )
                )


class ForgotPasswordForm(forms.Form):
    registered_email = forms.EmailField(
        max_length=75, help_text="Enter your registered email"
    )


# class UserAdmin(UserAdmin):
#     form = UserForm
#     list_display = ('email', 'first_name', 'last_name', 'is_staff')
#     list_filter = ('is_staff', )
#     search_fields = ('email', )
#
# admin.site.unregister(User)
# admin.site.register(User, UserAdmin)

