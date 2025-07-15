from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import IntegrityError, transaction
from django.db.models import Exists, OuterRef
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.html import strip_tags
from django.views.generic.edit import FormView

from bessie.forms import CompanyForm
from bessie.models import BessieResponse, BessieResult, Company, CompanyAdmin, Employee
from users.forms import BulkUserInviteForm
from users.models import User


class CompanyFormView(FormView):
    template_name = "bessie/create_company.html"
    form_class = CompanyForm
    success_url = reverse_lazy("dashboard")

    def form_valid(self, form):
        try:
            with transaction.atomic():
                company = Company.objects.create(
                    name=form.cleaned_data["name"],
                    slots=form.cleaned_data["slots"],
                    survey_start_date=form.cleaned_data["survey_start_date"],
                    survey_completion_date=form.cleaned_data["survey_completion_date"],
                    strategy_meeting_date=form.cleaned_data["strategy_meeting_date"],
                )
        except IntegrityError as e:
            error_msg = str(e)
            if "bessie_company.name" in error_msg:
                messages.error(
                    self.request,
                    f"Company with name: {form.cleaned_data['name']} already exists in the system",
                )
            return redirect("create_company")
        except ValidationError as e:
            messages.error(
                self.request, f'{e.messages[0]} : {form.cleaned_data["name"]}'
            )
            return redirect("create_company")

        return super().form_valid(form)


def company_detail(request, id):
    company = get_object_or_404(Company, pk=id)

    company_admins = CompanyAdmin.objects.filter(company=company).select_related("user")

    employees = (
        Employee.objects.filter(company=company)
        .select_related("owner")
        .annotate(
            has_response=Exists(BessieResponse.objects.filter(employee=OuterRef("pk")))
        )[:5]
    )

    quiz_count = BessieResult.objects.filter(company=company).count()
    employees_with_responses_count = (
        Employee.objects.filter(company=company, owner__isnull=False).distinct().count()
    )

    results_ready = (
        employees.count() > 0 and employees.count() == employees_with_responses_count
    )

    form = BulkUserInviteForm()

    context = {
        "company": company,
        "quizzes": quiz_count,
        "company_admins": company_admins,
        "employees": employees,
        "available_slots": company.slots - company.used_slots,
        "results_ready": results_ready,
        "form": form,
    }

    return render(request, "bessie/company.html", context)


def toggle_company_results_visible(request, id):
    company = get_object_or_404(Company, pk=id)

    if request.method == "POST":
        company.results_visible = not company.results_visible
        company.save()

        messages.success(request, "Results enabled successfully.")

    return redirect("company", id=company.pk)
