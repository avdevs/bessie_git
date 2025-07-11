from django.contrib import admin

from .models import *

# Register your models here.


@admin.register(BessieResponse)
class BessieResponseAdmin(admin.ModelAdmin):
	list_display = [
		"id",
		"get_employee_first_name",
		"get_employee_last_name",
		"employee__company__name",
	]
	list_filter = ["employee__company__name"]

	def get_employee_first_name(self, obj):
		return obj.employee.user.first_name

	get_employee_first_name.short_description = "Employee First Name"

	def get_employee_last_name(self, obj):
		return obj.employee.user.last_name

	get_employee_last_name.short_description = "Employee Last Name"


@admin.register(BessieResult)
class BessieResultAdmin(admin.ModelAdmin):
	list_display = [
		"id",
		"get_employee_first_name",
		"get_employee_last_name",
		"company__name",
	]
	list_filter = ["company__name"]

	def get_employee_first_name(self, obj):
		return obj.response.employee.user.first_name

	get_employee_first_name.short_description = "Employee First Name"

	def get_employee_last_name(self, obj):
		return obj.response.employee.user.last_name

	get_employee_last_name.short_description = "Employee Last Name"


@admin.register(CompanyAdmin)
class CompanyAdminAdmin(admin.ModelAdmin):
	list_display = ["user__first_name", "user__last_name", "company__name"]
	list_filter = ["company__name"]


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
	list_display = [
		"name",
		"slots",
		"survey_start_date",
		"survey_completion_date",
		"strategy_meeting_date",
	]
	search_fields = ["name"]


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
	list_display = [
		"user__first_name",
		"user__last_name",
		"company__name",
		"get_unique_id",
		"team",
	]
	list_filter = ["company__name"]
	search_fields = ["user__first_name", "user__last_name"]

	def get_unique_id(self, obj):
		"""Get unique_id from the related User model"""
		if hasattr(obj.user, "unique_id"):
			return obj.user.unique_id
		return "-"

	get_unique_id.short_description = "Unique ID"  # type: ignore


# register CompanyRiskSummary model
@admin.register(CompanyRiskSummary)
class CompanyRiskSummaryAdmin(admin.ModelAdmin):
	list_filter = ["company__name"]
	search_fields = ["company__name"]


admin.site.register(EmployeeProcessTask)
