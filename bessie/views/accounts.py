import uuid
from datetime import timedelta

from django.contrib.auth import login
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Exists, OuterRef
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

from bessie.forms import EmployeeForgotIDForm, EmployeeLoginForm
from bessie.models import BessieResponse, Company, CompanyAdmin, Employee
from users.models import User


def user_list(request, id):
	# Initialize employees to empty queryset to satisfy the type checker
	employees = Employee.objects.none()
	company = None

	if request.user.user_type == User.UserTypes.COMPANY_ADMIN:
		comp_admin = CompanyAdmin.objects.get(user=request.user)
		company = comp_admin.company
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


def employee_login(request):
	form = EmployeeLoginForm(request.POST or None)

	if request.method == "POST" and form.is_valid():
		employee = Employee.objects.filter(
			unique_id=form.cleaned_data["unique_user_id"],
		).first()

		if not employee:
			form.add_error("unique_user_id", "Employee with this ID does not exist.")
			return render(request, "bessie/employee_login.html", {"form": form})

		token = str(uuid.uuid4())

		employee.magic_link_token = token
		employee.magic_link_expiry = timezone.now() + timedelta(minutes=15)
		employee.save()

		link = request.build_absolute_uri(f"/bessie/employee/login/{token}")

		html_message = render_to_string(
			"emails/employee_login.html",
			{
				"url": link,
			},
		)

		plain_message = strip_tags(html_message)

		send_mail(
			subject="Bessie Employee Login",
			message=plain_message,
			from_email=None,
			recipient_list=[employee.user.email],
			html_message=html_message,
		)

		return render(
			request,
			"bessie/employee_login.html",
			{
				"form": form,
				"success": "A magic link has been sent to your email. Please check your inbox.",
			},
		)

	return render(
		request,
		"bessie/employee_login.html",
		{"form": form},
	)


def employee_login_process(request, token):
	employee = Employee.objects.filter(magic_link_token=token).first()

	if not employee:
		return render(request, "bessie/employee_login_invalid.html")

	employee.magic_link_token = None
	employee.magic_link_expiry = None
	employee.save()

	request.session["employee_id"] = employee.pk

	login(request, employee.user)

	return redirect("dashboard")


def employee_forgot_id(request):
	form = EmployeeForgotIDForm()

	if request.method == "POST":
		email = request.POST.get("email")
		employee = Employee.objects.filter(user__email=email).first()

		if employee:
			html_message = render_to_string(
				"emails/employee_login_forgot_id.html",
				{
					"employee_id": employee.unique_id,
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
				"bessie/employee_login_forgot_id.html",
				{"success": "Your Employee ID has been sent to your email.", "form": form},
			)

		return render(
			request,
			"bessie/employee_login_forgot_id.html",
			{"error": "No employee found with that email.", "form": form},
		)

	return render(
		request,
		"bessie/employee_login_forgot_id.html",
		{
			"form": form,
			"error": None,
			"success": None,
		},
	)
