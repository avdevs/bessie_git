from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import User


# Register your models here.
class UserAdmin(BaseUserAdmin):
	add_form = CustomUserCreationForm
	form = CustomUserChangeForm
	model = User
	list_display = (
		"email",
		"first_name",
		"last_name",
		"user_type",
		"unique_id",
		"bessie_admin",
		"is_staff",
		"is_active",
	)
	list_filter = (
		"email",
		"first_name",
		"last_name",
		"user_type",
		"unique_id",
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
					"unique_id",
					"password",
					"bessie_admin",
				)
			},
		),
		(
			"Magic Link Authentication",
			{
				"fields": ("magic_link_token", "magic_link_expiry"),
				"classes": ("collapse",),
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
					"unique_id",
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
	search_fields = ("email", "unique_id")
	ordering = ("email",)


admin.site.register(User, UserAdmin)
