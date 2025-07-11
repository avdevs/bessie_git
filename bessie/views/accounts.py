import uuid
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import login
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Exists, OuterRef
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags
from django.views.decorators.http import require_http_methods

from bessie.forms import EmployeeForgotIDForm, EmployeeLoginForm
from bessie.models import BessieResponse, Company, CompanyAdmin, Employee
from users.models import User


def user_list(request, id):
	# Initialize employees to empty queryset to satisfy the type checker
	employees = Employee.objects.none()
	company = None

	if request.user.user_type == User.UserTypes.COMPANY_ADMIN:
		# Get the specific company for this view
		company = Company.objects.get(pk=id)
		# Check if user is admin for this company
		comp_admin = CompanyAdmin.objects.filter(user=request.user, company=company).first()
		if not comp_admin:
			return redirect("dashboard")  # User is not admin for this company
		employees = Employee.objects.filter(company=company).annotate(
			has_response=Exists(BessieResponse.objects.filter(employee=OuterRef("pk")))
		)

	if request.user.user_type == User.UserTypes.STAFF:
		company = Company.objects.get(pk=id)
		employees = Employee.objects.filter(company=company).annotate(
			has_response=Exists(BessieResponse.objects.filter(employee=OuterRef("pk")))
		)

	paginator = Paginator(employees, 15)
	page_number = request.GET.get("page", 1)
	page_obj = paginator.get_page(page_number)

	return render(
		request, "bessie/user_list.html", {"company": company, "page_obj": page_obj}
	)


def user_login(request):
	form = EmployeeLoginForm(request.POST or None)

	if request.method == "POST" and form.is_valid():
		user = User.objects.filter(unique_id=form.cleaned_data["unique_user_id"]).first()

		if not user:
			form.add_error("unique_user_id", "Employee with this ID does not exist.")
			return render(request, "bessie/user_login.html", {"form": form})

		token = str(uuid.uuid4())

		user.magic_link_token = token
		user.magic_link_expiry = timezone.now() + timedelta(minutes=15)
		user.save()

		link = request.build_absolute_uri(f"/bessie/login/{token}")

		html_message = render_to_string(
			"emails/user_login.html",
			{
				"url": link,
			},
		)

		plain_message = strip_tags(html_message)

		send_mail(
			subject="Bessie Account Login",
			message=plain_message,
			from_email=None,
			recipient_list=[user.email],
			html_message=html_message,
		)

		return render(
			request,
			"bessie/user_login.html",
			{
				"form": form,
				"success": "A magic link has been sent to your email. Please check your inbox.",
			},
		)

	return render(
		request,
		"bessie/user_login.html",
		{"form": form},
	)


def user_login_process(request, token):
	user = User.objects.filter(magic_link_token=token).first()

	if not user:
		return render(request, "bessie/user_login_invalid.html")

	user.magic_link_token = None
	user.magic_link_expiry = None
	user.save()

	request.session["user_id"] = user.pk

	login(request, user)

	return redirect("dashboard")


def employee_forgot_id(request):
	form = EmployeeForgotIDForm()

	if request.method == "POST":
		email = request.POST.get("email")
		employee = Employee.objects.filter(user__email=email).first()
		link = request.build_absolute_uri("/bessie/employee/login")

		if employee:
			# Check if User model has unique_id field before using it
			if hasattr(employee.user, "unique_id"):
				employee_id = employee.user.unique_id
			else:
				# Fallback - could use user ID or email as identifier
				employee_id = employee.user.email

			html_message = render_to_string(
				"emails/user_login_forgot_id.html",
				{
					"employee_id": employee_id,
					"url": link,
				},
			)

			plain_message = strip_tags(html_message)

			send_mail(
				subject="Bessie Employee ID Recovery",
				message=plain_message,
				from_email=None,
				recipient_list=[email],
				html_message=html_message,
			)

			return render(
				request,
				"bessie/user_login_forgot_id.html",
				{"success": "Your Employee ID has been sent to your email.", "form": form},
			)

		return render(
			request,
			"bessie/user_login_forgot_id.html",
			{"error": "No employee found with that email.", "form": form},
		)

	return render(
		request,
		"bessie/user_login_forgot_id.html",
		{
			"form": form,
			"error": None,
			"success": None,
		},
	)


def all_system_users(request):
	if not request.user.is_authenticated:
		return redirect("login")
	if request.user.user_type != User.UserTypes.STAFF:
		return redirect("dashboard")

	users = User.objects.all()

	# Handle search functionality
	search_query = request.GET.get("search", "").strip()
	if search_query:
		from django.db.models import Q

		users = users.filter(
			Q(first_name__icontains=search_query)
			| Q(last_name__icontains=search_query)
			| Q(email__icontains=search_query)
		)

	paginator = Paginator(users, 15)
	page_number = request.GET.get("page", 1)
	page_obj = paginator.get_page(page_number)

	return render(
		request,
		"bessie/all_system_users.html",
		{"page_obj": page_obj},
	)


def company_selection(request):
	"""Show company selection page for users who admin multiple companies"""
	user = request.user

	if not user.is_authenticated:
		return redirect("login")

	# Get all companies this user is admin for
	company_admins = CompanyAdmin.objects.filter(user=user).select_related("company")
	companies = [ca.company for ca in company_admins]

	if len(companies) == 0:
		# User is not admin for any company, redirect to dashboard
		return redirect("dashboard")
	# elif len(companies) == 1:
	# 	# User is admin for only one company, redirect directly to that company's dashboard
	# 	request.session["selected_company_id"] = companies[0].pk
	# 	return redirect("dashboard")

	# User is admin for multiple companies, show selection page
	return render(
		request,
		"bessie/company_selection.html",
		{"companies": companies},
	)


def select_company(request, company_id):
	"""Handle company selection and store in session"""
	if not request.user.is_authenticated:
		return redirect("login")

	# Check if user is a bessie admin (same logic as general.py)
	if not request.user.bessie_admin:
		return redirect("dashboard")

	# Verify user is admin for this company
	company_admin = CompanyAdmin.objects.filter(
		user=request.user, company_id=company_id
	).first()
	if not company_admin:
		return redirect("company_selection")

	# Store selected company in session
	request.session["selected_company_id"] = company_id
	return redirect("dashboard")


def clear_company_selection(request):
	"""Clear the selected company from session and redirect to company selection"""
	if not request.user.is_authenticated:
		return redirect("login")

	# Check if user is a bessie admin (same logic as general.py)
	if not request.user.bessie_admin:
		return redirect("dashboard")

	# Clear the selected company from session
	if "selected_company_id" in request.session:
		del request.session["selected_company_id"]

	return redirect("company_selection")


def get_companies_for_promotion(request):
	"""Get all companies for the promotion modal"""
	if not request.user.is_authenticated:
		return JsonResponse({"error": "Unauthorized"}, status=401)
	if request.user.user_type != User.UserTypes.STAFF:
		return JsonResponse({"error": "Unauthorized"}, status=403)

	companies = Company.objects.all().values("id", "name").order_by("name")
	return JsonResponse({"companies": list(companies)})


@require_http_methods(["POST"])
def promote_user_to_bessie_admin(request):
	"""Promote a user to company admin for selected companies"""
	if not request.user.is_authenticated:
		messages.error(request, "You must be logged in to perform this action.")
		return redirect("login")
	if request.user.user_type != User.UserTypes.STAFF:
		messages.error(request, "You don't have permission to perform this action.")
		return redirect("dashboard")

	try:
		user_id = request.POST.get("user_id")
		company_ids = request.POST.getlist("company_ids")

		if not user_id or not company_ids:
			messages.error(request, "Missing user ID or company selection.")
			return redirect("all_system_users")

		user = User.objects.get(pk=user_id)

		# Change user type to COMPANY_ADMIN
		user.bessie_admin = True
		user.save()

		# Create CompanyAdmin instances for each selected company
		company_names = []
		for company_id in company_ids:
			company = Company.objects.get(pk=company_id)
			CompanyAdmin.objects.get_or_create(
				user=user, company=company, defaults={"admin_level": 1}
			)
			company_names.append(company.name)

		companies_text = ", ".join(company_names)
		messages.success(
			request,
			f"Successfully promoted {user.first_name} {user.last_name} to Bessie Admin for: {companies_text}",
		)
		return redirect("all_system_users")

	except User.DoesNotExist:
		messages.error(request, "User not found.")
		return redirect("all_system_users")
	except Company.DoesNotExist:
		messages.error(request, "One or more companies not found.")
		return redirect("all_system_users")
	except Exception as e:
		messages.error(request, f"An error occurred: {str(e)}")
		return redirect("all_system_users")


@require_http_methods(["GET"])
def get_user_companies_for_demotion(request):
	"""Get companies that a user is currently admin for"""
	if not request.user.is_authenticated:
		return JsonResponse({"error": "Unauthorized"}, status=401)
	if request.user.user_type != User.UserTypes.STAFF:
		return JsonResponse({"error": "Unauthorized"}, status=403)

	user_id = request.GET.get("user_id")
	if not user_id:
		return JsonResponse({"error": "Missing user ID"}, status=400)

	try:
		user = User.objects.get(pk=user_id)
		if not user.bessie_admin:
			return JsonResponse({"companies": []})

		# Get companies this user is admin for
		company_admins = CompanyAdmin.objects.filter(user=user).select_related("company")
		companies = [
			{"id": ca.company.pk, "name": ca.company.name} for ca in company_admins
		]

		return JsonResponse({"companies": companies})

	except User.DoesNotExist:
		return JsonResponse({"error": "User not found"}, status=404)
	except Exception as e:
		return JsonResponse({"error": str(e)}, status=500)


@require_http_methods(["POST"])
def demote_user_from_admin(request):
	"""Demote a user from company admin for selected companies or completely"""
	if not request.user.is_authenticated:
		messages.error(request, "You must be logged in to perform this action.")
		return redirect("login")
	if request.user.user_type != User.UserTypes.STAFF:
		messages.error(request, "You don't have permission to perform this action.")
		return redirect("dashboard")

	try:
		user_id = request.POST.get("user_id")
		company_ids = request.POST.getlist("company_ids")

		if not user_id:
			messages.error(request, "Missing user ID.")
			return redirect("all_system_users")

		user = User.objects.get(pk=user_id)

		if not user.bessie_admin:
			messages.error(request, "User is not currently an admin.")
			return redirect("all_system_users")

		# Get company names before deletion for the message
		company_names = []
		if company_ids:
			companies_to_remove = CompanyAdmin.objects.filter(
				user=user, company_id__in=company_ids
			).select_related("company")
			company_names = [ca.company.name for ca in companies_to_remove]

			# Remove CompanyAdmin instances for selected companies
			CompanyAdmin.objects.filter(user=user, company_id__in=company_ids).delete()

		# Check if user has any remaining company admin roles
		remaining_companies = CompanyAdmin.objects.filter(user=user).count()

		# If no companies remain, demote user completely
		if remaining_companies == 0:
			user.bessie_admin = False
			user.save()
			messages.success(
				request,
				f"Successfully demoted {user.first_name} {user.last_name} from all admin roles. User is now a regular employee.",
			)
		else:
			companies_text = ", ".join(company_names)
			messages.success(
				request,
				f"Successfully removed {user.first_name} {user.last_name}'s admin access from: {companies_text}",
			)

		return redirect("all_system_users")

	except User.DoesNotExist:
		messages.error(request, "User not found.")
		return redirect("all_system_users")
	except Exception as e:
		messages.error(request, f"An error occurred: {str(e)}")
		return redirect("all_system_users")
