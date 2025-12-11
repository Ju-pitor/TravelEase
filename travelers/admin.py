from django.contrib import admin
from .models import TravelerProfile
from .models import User
from django.contrib.auth.admin import UserAdmin

admin.site.register(TravelerProfile)


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'email', 'user_type', 'is_traveler', 'is_agency', 'is_app_admin', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('user_type', 'is_traveler', 'is_agency', 'is_app_admin')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('user_type', 'is_traveler', 'is_agency', 'is_app_admin')}),
    )

admin.site.register(User, CustomUserAdmin)