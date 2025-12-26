"""Django admin"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from core import models

class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users."""
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None, {'fields': ('email', 'password','role')}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }
        ),
        (_('Important dates'), {'fields':('last_login',)}),
    )
    readonly_fields = ['last_login']
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'name',
                'is_active',
                'is_staff',
                'is_superuser',
                'affiliation',
                'background_user',
                'role',
                'phone_number',
             )
        }),
    )

admin.site.register(models.User, UserAdmin)
admin.site.register(models.Event)
admin.site.register(models.Topic)
admin.site.register(models.Paper)
admin.site.register(models.EventRegistration)
admin.site.register(models.EventSchedule)
admin.site.register(models.ContactUs)