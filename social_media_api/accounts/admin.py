from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser


class CustomUserAdmin(BaseUserAdmin):
    """
    Custom User Admin for managing CustomUser model.
    Extends Django's default UserAdmin.
    """
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('bio', 'profile_picture', 'followers')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at')
    list_display = ('username', 'email', 'first_name', 'last_name', 'created_at')
    list_filter = BaseUserAdmin.list_filter + ('created_at', 'updated_at')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'bio')


admin.site.register(CustomUser, CustomUserAdmin)


