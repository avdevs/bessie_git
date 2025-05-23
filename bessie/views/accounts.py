from django.db.models import Exists, OuterRef
from django.core.paginator import Paginator
from django.shortcuts import render
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
