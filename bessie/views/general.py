from django.core.paginator import Paginator
from django.db.models import Exists, OuterRef
from django.shortcuts import redirect, render

from bessie.models import BessieResponse, Company, CompanyAdmin, Employee


def index(request):
	"""
	Dashboard entry point for different user types.
	User could have multiple functions:
	- STAFF: View all companies
	- EMPLOYEE: View their own responses
	- BESSIE_ADMIN: Administer a single/multiple companies.
	  Bessie Admin does not necessarily have to be an employee, so we need to check if they have an employee record.
		This user will have to be presented with a choice to view their own results (if employee account found) or administer a company.
		Give company selection if multiple companies detected.
	"""
	user = request.user

	if user.is_staff:
		companies = Company.objects.all().order_by("name")
		paginator = Paginator(companies, 15)

		page_number = request.GET.get("page", 1)
		page_obj = paginator.get_page(page_number)

		return render(request, "bessie/super_user_view.html", {"page_obj": page_obj})

	elif user.bessie_admin:
		print("User is Bessie admin, showing company selection")

	elif user.user_type == "EMPLOYEE":
		employee = Employee.objects.filter(user=user).first()
		response = BessieResponse.objects.filter(employee=employee).first()
		company = employee.company if employee else None

		return render(
			request,
			"bessie/employee_view.html",
			{"response": response, "employee": employee, "company": company},
		)
	else:
		return redirect("login")

	# if not request.user.is_authenticated:
	# 	return redirect("login")

	# match request.user.user_type:
	# 	case "STAFF":
	# 		companies = Company.objects.all().order_by("name")
	# 		paginator = Paginator(companies, 15)

	# 		page_number = request.GET.get("page", 1)
	# 		page_obj = paginator.get_page(page_number)

	# 		return render(request, "bessie/companies.html", {"page_obj": page_obj})

	# 	case "EMPLOYEE":
	# 		employee = Employee.objects.filter(user=request.user).first()
	# 		response = BessieResponse.objects.filter(employee=employee).first()
	# 		company = employee.company if employee else None

	# 		return render(
	# 			request,
	# 			"bessie/index.html",
	# 			{"response": response, "employee": employee, "company": company},
	# 		)

	# 	case "COMPANY_ADMIN":
	# 		# Check if user has multiple companies to admin
	# 		company_admins = CompanyAdmin.objects.filter(user=request.user).select_related(
	# 			"company"
	# 		)
	# 		companies = [ca.company for ca in company_admins]

	# 		if len(companies) == 0:
	# 			# User is marked as COMPANY_ADMIN but has no companies assigned
	# 			return redirect("login")
	# 		elif len(companies) > 1:
	# 			# User administers multiple companies
	# 			# Check if they have already selected a company in this session
	# 			selected_company_id = request.session.get("selected_company_id")
	# 			if selected_company_id:
	# 				# Verify the selected company is one they can admin
	# 				selected_company = None
	# 				for company in companies:
	# 					if company.pk == selected_company_id:
	# 						selected_company = company
	# 						break
	# 				if selected_company:
	# 					comp_admin = CompanyAdmin.objects.filter(
	# 						user=request.user, company=selected_company
	# 					).first()
	# 				else:
	# 					# Invalid company selection, redirect to selection page
	# 					return redirect("company_selection")
	# 			else:
	# 				# No company selected, redirect to selection page
	# 				return redirect("company_selection")
	# 		else:
	# 			# User administers only one company
	# 			comp_admin = company_admins[0]

	# 		if not comp_admin:
	# 			# This shouldn't happen, but just in case
	# 			return redirect("login")

	# 		company_admins = CompanyAdmin.objects.filter(company=comp_admin.company)
	# 		employees = Employee.objects.filter(company=comp_admin.company).annotate(
	# 			has_response=Exists(BessieResponse.objects.filter(employee=OuterRef("pk")))
	# 		)[:5]

	# 		# Get all companies that the user administers
	# 		company_admins_for_user = CompanyAdmin.objects.filter(
	# 			user=request.user
	# 		).select_related("company")
	# 		available_companies = [ca.company for ca in company_admins_for_user]

	# 		return render(
	# 			request,
	# 			"bessie/comp_admin_home.html",
	# 			{
	# 				"company": comp_admin.company,
	# 				"employees": employees,
	# 				"available_companies": available_companies,
	# 			},
	# 		)


def get_category(value):
	if value <= 25.0:
		return "low"
	elif value <= 50.0:
		return "medium"
	elif value <= 75.0:
		return "high"
	else:
		return "very_high"
