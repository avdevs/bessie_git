from django.urls import path

from .forms import *
from .views import (
	BessieQuestionaireWizard,
	CompanyFormView,
	company_detail,
	employee_forgot_id,
	employee_login,
	employee_login_process,
	export_data,
	toggle_company_results_visible,
	user_list,
	user_results,
	view_company_results,
)

urlpatterns = [
	# path('dashboard/', dashboard, name='dashboard'),
	path(
		"take-quiz/",
		BessieQuestionaireWizard.as_view(
			[
				Form1,
				Form2,
				Form3,
				Form4,
				Form5,
				Form6,
				Form7,
				Form8,
				Form9,
				Form10,
				Form11,
				Form12,
				Form13,
				Form14,
				Form15,
				Form16,
				Form17,
				Form18,
				Form19,
				Form20,
				Form21,
				Form22,
				Form23,
				Form24,
				Form25,
				Form26,
				Form27,
			]
		),
		name="take_quiz",
	),
	path("export-data/<int:id>", export_data, name="export_data"),  # Export CSV data
	path("user-result/", user_results, name="user_results"),
	path("user-result/<str:employee_id>", user_results, name="user_results"),
	path("company/<int:id>/users/", user_list, name="user_list"),
	path("company-result/<int:id>", view_company_results, name="company_results"),
	path(
		"company-result-toggle/<int:id>",
		toggle_company_results_visible,
		name="toggle-company-results-visible",
	),
	path("create-company/", CompanyFormView.as_view(), name="create_company"),
	path("company/<int:id>", company_detail, name="company"),
	path("employee/login", employee_login, name="employee_login"),
	path(
		"employee/login/<str:token>", employee_login_process, name="employee_login_process"
	),
	path("employee/forgot-id", employee_forgot_id, name="employee_forgot_id"),
]
