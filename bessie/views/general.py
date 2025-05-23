from django.core.paginator import Paginator
from django.shortcuts import render
from django.db.models import Exists, OuterRef
from bessie.forms import AdminInviteForm
from bessie.models import BessieResponse, BessieResult, Company, CompanyAdmin, Employee
from users.forms import BulkUserInviteForm


def index(request):
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
            return render(
                request,
                "bessie/index.html",
                {"response": response, "employee": employee},
            )

        case "COMPANY_ADMIN":
            comp_admin = CompanyAdmin.objects.get(user=request.user)
            company_admins = CompanyAdmin.objects.filter(company=comp_admin.company)
            employees = Employee.objects.filter(company=comp_admin.company).annotate(
                has_response=Exists(
                    BessieResponse.objects.filter(employee=OuterRef("pk"))
                )
            )[:5]
            quiz_count = BessieResult.objects.filter(company=comp_admin.company).count()

            employees_with_responses_count = (
                Employee.objects.filter(company=comp_admin.company, owner__isnull=False)
                .distinct()
                .count()
            )

            results_ready = (
                employees.count() > 0
                and employees.count() == employees_with_responses_count
            )

            form = BulkUserInviteForm()
            form1 = AdminInviteForm(initial={"company_id": comp_admin.company.pk})

            return render(
                request,
                "bessie/comp_admin_home.html",
                {
                    "company": comp_admin.company,
                    "quizzes": quiz_count,
                    "company_admins": company_admins,
                    "employees": employees,
                    "available_slots": comp_admin.company.slots
                    - comp_admin.company.used_slots,
                    "form": form,
                    "form1": form1,
                    "results_ready": results_ready,
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
