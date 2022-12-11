from django.contrib import admin

from users.models import Subscribe, User

admin.site.register(User)
admin.site.register(Subscribe)
