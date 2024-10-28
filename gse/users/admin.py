from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import UserChangeForm, UserCreationForm
from .models import User, UserProfile, Address


class UserProfileInline(admin.StackedInline):
    model = UserProfile


class UserAddressInline(admin.StackedInline):
    model = Address


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('email', 'id', 'is_active', 'is_superuser', 'role')
    list_filter = ('is_superuser',)
    readonly_fields = ('last_login',)

    fieldsets = (
        ('Main', {'fields': ('email', 'password', 'role', 'last_login')}),
        ('Permissions', {'fields': ('is_active', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {'fields': ('email', 'password1', 'password2')}),
    )

    search_fields = ('email',)
    ordering = ('email',)

    inlines = [UserProfileInline, UserAddressInline]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        if not is_superuser:
            form.base_fields['is_superuser'].disabled = True
        return form


admin.site.register(User, UserAdmin)
