from django.contrib import admin

from users.models import Subscribe, User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'email',
        'username',
        'first_name',
        'last_name',
        'get_recipes_count',
        'get_subscribers_count',
    )
    search_fields = (
        'email',
        'username',
        'first_name',
        'last_name',
    )
    list_filter = (
        'email',
        'username',
        'first_name',
        'last_name',
    )
    empty_value_display = '-пусто-'

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    get_recipes_count.short_description = 'Количество рецептов'

    def get_subscribers_count(self, obj):
        return obj.subscribed.count()

    get_subscribers_count.short_description = 'Количество подписчиков'


admin.site.register(User, UserAdmin)
admin.site.register(Subscribe)
