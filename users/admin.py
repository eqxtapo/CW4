from django.contrib import admin

from users.models import User

# Register your models here.


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "avatar",
        "email",
        "first_name",
        "last_name",
        "middle_name",
        "phone",
        "country",
    )
    search_fields = ("email",)
    list_filter = ("email",)
