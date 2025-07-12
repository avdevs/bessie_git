from django.urls import path

from .forms import *
from .views import (
	BessieQuestionaireWizard,
	CompanyFormView,
	all_system_users,
	clear_company_selection,
	company_detail,
	company_selection,
	demote_user_from_admin,
	export_data,
	forgot_unique_id,
	get_companies_for_promotion,
	get_user_companies_for_demotion,
	promote_user_to_bessie_admin,
	select_company,
	toggle_company_results_visible,
	user_list,
	user_login,
	user_login_process,
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
	path("login", user_login, name="user_login"),
	path("login/<str:token>", user_login_process, name="user_login_process"),
	path("forgot-id", forgot_unique_id, name="forgot_unique_id"),
	path("users", all_system_users, name="all_system_users"),
	path("company-selection/", company_selection, name="company_selection"),
	path("select-company/<int:company_id>/", select_company, name="select_company"),
	path(
		"clear-company-selection/", clear_company_selection, name="clear_company_selection"
	),
	path(
		"get-companies-for-promotion/",
		get_companies_for_promotion,
		name="get_companies_for_promotion",
	),
	path(
		"get-user-companies-for-demotion/",
		get_user_companies_for_demotion,
		name="get_user_companies_for_demotion",
	),
	path(
		"promote-user-to-admin/", promote_user_to_bessie_admin, name="promote_user_to_admin"
	),
	path(
		"demote-user-from-admin/", demote_user_from_admin, name="demote_user_from_admin"
	),
]
