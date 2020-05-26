from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


class UserAdmin(UserAdmin):
    #inlines = (,)
    fieldsets = (
        (None, {'fields': (
            'first_name', 'last_name',
            'phone', 'email',
            'passcode', 'password',
        )}),
        (_('Permissions'), {'fields': (
            'is_active', 'is_staff', 'is_superuser',
            'is_phone_verified', 'is_email_verified',
            'groups', 'user_permissions',
        )}),
        (_('Important dates'), {'fields': (
            'last_login', 'date_joined'
        )}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'first_name', 'last_name',
                'phone', 'email',
                'password1', 'password2'
            ),
        }),
    )

    list_display = (
        'first_name', 'last_name',
        'phone', 'email', 'is_active',
        'date_joined', 'last_login',
    )

    search_fields = ('phone', 'email',)
    ordering = ('phone', 'email',)

    # RESERVED
    # actions = ['verification']

    # def verification(delf, request, queryset):
    #     for user in queryset:
    #         user.verify() # verify(request)

    # verification.short_description = 'Send verification request'


admin.site.register(User, UserAdmin)
