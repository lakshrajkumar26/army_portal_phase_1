from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from .models import User

# ✅ Hide Groups from admin
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "role", "is_staff", "center")
    list_filter = ("role", "is_staff", "is_superuser", "center")

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email")}),
        ("Role & Center", {"fields": ("role", "center")}),
        ("Permissions", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    # 🔥 THIS LINE HIDES "Users" FROM SIDEBAR
    def has_module_permission(self, request):
        return False
