from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import User


# Register your models here.
class UserAdmin(UserAdmin):
	add_form = CustomUserCreationForm
	form = CustomUserChangeForm
	model = User
	list_display = (
		"email",
		"first_name",
		"last_name",
		"user_type",
		"bessie_admin",
		"is_staff",
		"is_active",
	)
	list_filter = (
		"email",
		"first_name",
		"last_name",
		"user_type",
		"is_staff",
		"is_active",
	)
	fieldsets = (
		(
			None,
			{
				"fields": (
					"first_name",
					"last_name",
					"email",
					"user_type",
					"password",
					"bessie_admin",
				)
			},
		),
		(
			"Permissions",
			{"fields": ("is_staff", "is_active", "groups", "user_permissions")},
		),
	)
	add_fieldsets = (
		(
			None,
			{
				"fields": (
					"first_name",
					"last_name",
					"email",
					"user_type",
					"password1",
					"password2",
					"is_staff",
					"is_active",
					"groups",
					"user_permissions",
				)
			},
		),
	)
	search_fields = ("email",)
	ordering = ("email",)


admin.site.register(User, UserAdmin)
