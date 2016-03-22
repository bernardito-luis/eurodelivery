from django.db import models


class UserRegistrationLink(models.Model):
    created_date = models.DateTimeField()
    user = models.ForeignKey('auth.User')
    slug = models.CharField(max_length=32, unique=True)

    class Meta:
        db_table = 'user_registration_link'
