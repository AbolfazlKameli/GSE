from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import UserChangeForm, UserCreationForm
from .models import User, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('first_name', 'last_name', 'email', 'id', 'is_active', 'is_superuser')
    list_filter = ('is_superuser',)
    readonly_fields = ('last_login',)

    fieldsets = (
        ('Main', {'fields': ('first_name', 'last_name', 'email', 'password', 'last_login')}),
        ('Permissions', {'fields': ('is_active', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {'fields': ('first_name', 'last_name', 'email', 'password1', 'password2')}),
    )

    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('first_name', 'last_name')
    filter_horizontal = ('groups', 'user_permissions')

    inlines = [UserProfileInline]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        if not is_superuser:
            form.base_fields['is_superuser'].disabled = True
        return form


admin.site.register(User, UserAdmin)
