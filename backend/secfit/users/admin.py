from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Offer, AthleteFile
from django.contrib.auth import get_user_model
from .forms import CustomUserChangeForm, CustomUserCreationForm

# Register your models here.


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = get_user_model()
    # list_display = UserAdmin.list_display + ('coach',)
    fieldsets = UserAdmin.fieldsets + ((None, {"fields": ("coach",)}),)
    add_fieldsets = UserAdmin.add_fieldsets + ((None, {"fields": ("coach",)}),)


admin.site.register(get_user_model(), CustomUserAdmin)
admin.site.register(Offer)
admin.site.register(AthleteFile)
