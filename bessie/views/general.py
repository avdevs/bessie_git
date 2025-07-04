from django.core.paginator import Paginator
from django.db.models import Exists, OuterRef
from django.shortcuts import redirect, render

from bessie.models import BessieResponse, Company, CompanyAdmin, Employee


def index(request):
	if not request.user.is_authenticated:
		return redirect("login")

	match request.user.user_type:
		case "STAFF":
			companies = Company.objects.all().order_by("name")
			paginator = Paginator(companies, 15)

			page_number = request.GET.get("page", 1)
			page_obj = paginator.get_page(page_number)

			return render(request, "bessie/companies.html", {"page_obj": page_obj})

		case "EMPLOYEE":
			employee = Employee.objects.filter(user=request.user).first()
			response = BessieResponse.objects.filter(employee=employee).first()
			company = employee.company if employee else None

			print("Employee:", employee)
			if company:
				print("Company:", company.results_visible)

			return render(
				request,
				"bessie/index.html",
				{"response": response, "employee": employee, "company": company},
			)

		case "COMPANY_ADMIN":
			# Check if user has multiple companies to admin
			company_admins = CompanyAdmin.objects.filter(user=request.user).select_related(
				"company"
			)
			companies = [ca.company for ca in company_admins]

			if len(companies) == 0:
				# User is marked as COMPANY_ADMIN but has no companies assigned
				return redirect("login")
			elif len(companies) > 1:
				# User administers multiple companies
				# Check if they have already selected a company in this session
				selected_company_id = request.session.get("selected_company_id")
				if selected_company_id:
					# Verify the selected company is one they can admin
					selected_company = None
					for company in companies:
						if company.pk == selected_company_id:
							selected_company = company
							break
					if selected_company:
						comp_admin = CompanyAdmin.objects.filter(
							user=request.user, company=selected_company
						).first()
					else:
						# Invalid company selection, redirect to selection page
						return redirect("company_selection")
				else:
					# No company selected, redirect to selection page
					return redirect("company_selection")
			else:
				# User administers only one company
				comp_admin = company_admins[0]

			if not comp_admin:
				# This shouldn't happen, but just in case
				return redirect("login")

			company_admins = CompanyAdmin.objects.filter(company=comp_admin.company)
			employees = Employee.objects.filter(company=comp_admin.company).annotate(
				has_response=Exists(BessieResponse.objects.filter(employee=OuterRef("pk")))
			)[:5]

			employees_with_responses_count = (
				Employee.objects.filter(company=comp_admin.company, owner__isnull=False)
				.distinct()
				.count()
			)

			results_ready = (
				employees.count() > 0 and employees.count() == employees_with_responses_count
			)

			# Get all companies that the user administers
			company_admins_for_user = CompanyAdmin.objects.filter(
				user=request.user
			).select_related("company")
			available_companies = [ca.company for ca in company_admins_for_user]

			return render(
				request,
				"bessie/comp_admin_home.html",
				{
					"company": comp_admin.company,
					"results_ready": results_ready,
					"available_companies": available_companies,
				},
			)


def get_category(value):
	if value <= 25.0:
		return "low"
	elif value <= 50.0:
		return "medium"
	elif value <= 75.0:
		return "high"
	else:
		return "very_high"
