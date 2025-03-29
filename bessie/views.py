import json
import sys
from django.shortcuts import render, redirect, get_object_or_404
from formtools.wizard.views import SessionWizardView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required
from .models import BessieResponse, BessieResult, Employee, CompanyAdmin, Company
from django.core.paginator import Paginator
from users.forms import BulkUserInviteForm
from .forms import AdminInviteForm, CompanyForm
from django.views.generic.edit import FormView
from django.db import IntegrityError, transaction
from django.core.exceptions import ValidationError
from django.contrib import messages
import csv
from django.http import HttpResponse


def index(request):
    match request.user.user_type:
        case "STAFF":
            companies = Company.objects.all().order_by("name")
            paginator = Paginator(companies, 15)  # Show 25 contacts per page.

            page_number = request.GET.get("page", 1)
            page_obj = paginator.get_page(page_number)
            # TODO: View companies, create company, edit company, Invite company admins
            # assign slot, view company results, view individual results, comment on results
            # upload induction videos
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
            # TODO: Invite employees/quiz-takers, invite company admins, view results / team results
            comp_admin = CompanyAdmin.objects.get(user=request.user)
            company_admins = CompanyAdmin.objects.filter(company=comp_admin.company)
            employees = Employee.objects.filter(company=comp_admin.company).annotate(
                has_response=Exists(
                    BessieResponse.objects.filter(employee=OuterRef("pk"))
                )
            )[:5]
            quizzes = BessieResult.objects.filter(company=comp_admin.company).count()
            # decoder = json.decoder.JSONDecoder().decode('')
            print(comp_admin.company.teams)

            results_ready = employees.count() == len(
                list(filter(lambda x: x.has_response == True, employees))
            )
            form = BulkUserInviteForm()
            form1 = AdminInviteForm(initial={"company_id": comp_admin.company.id})
            return render(
                request,
                "bessie/comp_admin_home.html",
                {
                    "company": comp_admin.company,
                    "quizzes": quizzes,
                    "company_admins": company_admins,
                    "employees": employees,
                    "available_slots": comp_admin.company.slots
                    - comp_admin.company.used_slots,
                    "form": form,
                    "form1": form1,
                    "results_ready": results_ready,
                },
            )


from django.urls import reverse_lazy
from users.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse


class CompanyFormView(FormView):
    template_name = "bessie/create_company.html"
    form_class = CompanyForm
    success_url = reverse_lazy("dashboard")

    def form_valid(self, form):
        try:
            with transaction.atomic():
                company = Company(
                    name=form.cleaned_data["name"],
                    slots=form.cleaned_data["slots"],
                    survey_start_date=form.cleaned_data["survey_start_date"],
                    survey_completion_date=form.cleaned_data["survey_completion_date"],
                    strategy_meeting_date=form.cleaned_data["strategy_meeting_date"],
                )
                company.save()
                password = User.objects.make_random_password()
                user = User(
                    first_name=form.cleaned_data["first_name"],
                    last_name=form.cleaned_data["last_name"],
                    email=form.cleaned_data["email"],
                    user_type=User.UserTypes.COMPANY_ADMIN,
                )
                user.set_password(password)  # Hash the password
                user.save()
                cmpAdmin = CompanyAdmin(company=company, user=user)
                cmpAdmin.save()
        except IntegrityError as e:
            if str(e) == "UNIQUE constraint failed: users_user.email":
                messages.error(
                    self.request,
                    f"user with email: {form.cleaned_data['email']} already exists in the system",
                )
            elif str(e) == "UNIQUE constraint failed: bessie_company.name":
                messages.error(
                    self.request,
                    f"company with name: {form.cleaned_data['name']} already exists in the system",
                )
            return redirect("create_company")
        except ValidationError as e:
            messages.error(
                self.request, f'{e.messages[0]} : {form.cleaned_data["name"]}'
            )
            return redirect("create_company")

        login_url = self.request.build_absolute_uri(reverse("login"))

        # Prepare email details
        subject = "Welcome to Bessie - Let's Get Started!"
        html_message = render_to_string(
            "emails/admin_invitation_email.html",
            {
                "user": user,
                "password": password,
                "login_url": login_url,
                "company": company,
            },
        )
        plain_message = strip_tags(html_message)
        send_mail(
            subject=subject,
            message=plain_message,
            from_email="no-reply@bessietech.com",
            recipient_list=[form.cleaned_data["email"]],
            html_message=html_message,
        )

        return super().form_valid(form)


def inviteAdmin(request):
    if request.method == "POST":
        form = AdminInviteForm(request.POST)
        print(form.errors)
        if form.is_valid():
            company_id = form.cleaned_data["company_id"]
            company = Company.objects.get(pk=int(company_id))

            password = (
                User.objects.make_random_password()
            )  # Generate a secure random password
            try:
                with transaction.atomic():
                    user = User(
                        first_name=form.cleaned_data["first_name"],
                        last_name=form.cleaned_data["last_name"],
                        email=form.cleaned_data["email"],
                        user_type=User.UserTypes.COMPANY_ADMIN,
                    )
                    user.set_password(password)  # Hash the password
                    user.save()
                    cmpAdmin = CompanyAdmin(company=company, user=user)
                    cmpAdmin.save()
            except IntegrityError:
                messages.error(
                    request,
                    f"user with email: {form.cleaned_data['email']} already exists in the system",
                )
                return redirect("dashboard")

            # Prepare email details
            login_url = request.build_absolute_uri(reverse("login"))

            # Prepare email details
            subject = "Welcome to Bessie - Let's Get Started!"
            html_message = render_to_string(
                "emails/admin_invitation_email.html",
                {
                    "user": user,
                    "password": password,
                    "login_url": login_url,
                    "company": company,
                },
            )
            plain_message = strip_tags(html_message)
            send_mail(
                subject=subject,
                message=plain_message,
                from_email="no-reply@bessietech.com",
                recipient_list=[form.cleaned_data["email"]],
                html_message=html_message,
            )

        else:
            print("form is invalid")
    return redirect("dashboard")


from django.db.models import Exists, OuterRef, BooleanField


def companyDetail(request, id):
    company = get_object_or_404(Company, pk=id)
    company_admins = CompanyAdmin.objects.filter(company=company)
    employees = Employee.objects.filter(company=company).annotate(
        has_response=Exists(BessieResponse.objects.filter(employee=OuterRef("pk")))
    )[:5]
    quizzes = BessieResult.objects.filter(company=company).count()
    results_ready = employees.count() == len(
        list(filter(lambda x: x.has_response == True, employees))
    )

    return render(
        request,
        "bessie/company.html",
        {
            "company": company,
            "quizzes": quizzes,
            "company_admins": company_admins,
            "employees": employees,
            "available_slots": company.slots - company.used_slots,
            "results_ready": results_ready,
        },
    )


from .models import WizardState
from .utils import calc_potential_cost


class BessieQuizWizard(LoginRequiredMixin, SessionWizardView):

    template_name = "bessie/form.html"

    def get_user_state(self):
        """Retrieve or create the wizard state for the current user."""
        if self.request.user.is_authenticated:
            state, created = WizardState.objects.get_or_create(user=self.request.user)
            return state
        return None

    def process_step(self, form):
        current_data = form.cleaned_data
        if self.request.user.is_authenticated:
            state = self.get_user_state()
            if state:
                state.data[self.steps.current] = current_data
                state.step = self.steps.current
                state.save()
        return self.get_form_step_data(form)

    def get_form_initial(self, step):
        """Load initial data from the database."""
        if self.request.user.is_authenticated:
            state = self.get_user_state()
            if state and state.data:
                return state.data.get(step, {})
        return super().get_form_initial(step)

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)

        # Add custom HTML for the current form
        output = []
        elrsCount = 0
        for field in form:
            widget_type = field.field.widget.__class__.__name__
            help_text = (
                f'<p class="help-text">{field.help_text}</p>' if field.help_text else ""
            )
            label = str(field.label_tag())
            field_html = str(field)
            errors = "".join(f'<p class="error">{e}</p>' for e in field.errors)

            output.append(help_text)

            if widget_type == "ExternalLabelRadioSelect":
                # if elrsCount == 0:
                # elrsCount += 1
                # output.append('<div class="frm_likert__heading form-field"><div class="frm_primary_label"></div>\
                #     <div class="opt-group"><div class="frm_likert__column">Strongly Agree</div><div class="frm_likert__column">Agree</div><div class="frm_likert__column">Somewhat Agree</div><div class="frm_likert__column">\
                # 	Neither Agree Nor Disagree</div><div class="frm_likert__column">Somewhat Disagree</div><div class="frm_likert__column">\
                # 	Disagree</div><div class="frm_likert__column">Strongly Disagree</div></div></div>')
                output.append(
                    f'<div class="form-group" id="{field.name}"><div class="label-opt-cont">{label}{field_html}</div>{errors}</div>'
                )
            else:
                elrsCount = 0
                output.append(
                    f'<div class="form-group" id="{field.name}">{label}{field_html}{errors}</div>'
                )

        context["custom_form"] = mark_safe("\n".join(output))
        return context

    def done(self, form_list, **kwargs):
        # Extract cleaned data from all forms

        if self.request.user.is_authenticated:
            state = self.get_user_state()
            if state:
                state.delete()

        form_data = {}
        for form in form_list:
            form_data = {**form_data, **form.cleaned_data}

        form_data = {k: (0 if v == "" else v) for k, v in form_data.items()}

        employee = Employee.objects.get(user=self.request.user)

        BessieResponse.objects.filter(employee=employee).delete()

        response = BessieResponse(
            employee=employee,
            multichoice=form_data,
            q1=form_data.get("q1", ""),
            q14=form_data.get("q14", ""),
            q45=form_data.get("q45", ""),
            q66=form_data.get("q66", ""),
            q74=form_data.get("q74", ""),
            q100=form_data.get("q100", ""),
            q154=form_data.get("q154", ""),
            q159=form_data.get("q159", ""),
            q167=form_data.get("q167", ""),
            q168=form_data.get("q168", ""),
            q176=form_data.get("q176", ""),
            q228=form_data.get("q228", ""),
        )

        response.save()

        results = BessieResult(response=response, company=employee.company)

        # Example: Environment calculation
        # Question 1 and 66 are skipped as they are not scored
        environment_questions = [f"q{i}" for i in range(2, 66)]

        max_environment_score = 311
        total_environment_score = 0

        for question_key in environment_questions:
            value = form_data.get(question_key)
            if value is not None:
                if isinstance(value, int):
                    total_environment_score += value
                elif isinstance(value, str):
                    if value.isdigit():
                        total_environment_score += int(value)

        # Calculate Environment Percentage
        environment_percentage = (total_environment_score / max_environment_score) * 100
        results.environment = round(environment_percentage, 2)

        # Environment Multiplier Calculation
        # Fetch the response for Q63, which acts as the multiplier
        q63_response = int(form_data.get("q63", 0))

        # Calculate the Environment Multiplier
        max_environment_multiplier_score = 1244  # Defined maximum score
        environment_multiplier_score = total_environment_score * q63_response

        # Normalize the Environment Multiplier score as a percentage
        environment_multiplier_percentage = (
            (environment_multiplier_score / max_environment_multiplier_score) * 100
            if max_environment_multiplier_score
            else 0
        )

        # Add to the scores dictionary
        results.environment_multiplier = round(environment_multiplier_percentage, 2)

        # Example: Privacy calculation
        privacy_questions = ["q6", "q7", "q8"]
        max_privacy_score = 18
        total_privacy_score = 0

        for question_key in privacy_questions:
            total_privacy_score += int(form_data.get(question_key, 0))

        privacy_percentage = (total_privacy_score / max_privacy_score) * 100
        results.privacy = round(privacy_percentage, 2)

        privacy_multiplier_score = total_privacy_score * q63_response
        max_privacy_multiplier_score = 72
        privacy_multiplier_percentage = (
            (privacy_multiplier_score / max_privacy_multiplier_score) * 100
            if max_privacy_multiplier_score
            else 0
        )
        results.privacy_multiplier = round(privacy_multiplier_percentage, 2)

        #  Travel to work
        travel_questions = ["q10", "q11", "q12"]
        max_travel_score = 13
        total_travel_score = sum(
            int(form_data.get(question_key, 0)) for question_key in travel_questions
        )
        travel_percentage = (total_travel_score / max_travel_score) * 100
        results.travel_to_work = round(travel_percentage, 2)

        # Residence calculation
        residence_questions = ["q2", "q3", "q4", "q5"]
        max_residence_score = 24
        total_residence_score = sum(
            int(form_data.get(question_key, 0)) for question_key in residence_questions
        )
        residence_percentage = (total_residence_score / max_residence_score) * 100
        results.residence = round(residence_percentage, 2)

        # Potential Cost to Organisation for user
        results.potential_cost = calc_potential_cost(int(form_data.get("q17")))

        # Pay calculation
        pay_questions = ["q15", "q16", "q17", "q18", "q19", "q20"]
        max_pay_score = 18
        total_pay_score = sum(
            int(form_data.get(question_key, 0)) for question_key in pay_questions
        )
        pay_percentage = (total_pay_score / max_pay_score) * 100
        results.pay = round(pay_percentage, 2)

        # Pay Multiplier calculation
        pay_multiplier_score = total_pay_score * q63_response
        max_pay_multiplier_score = 72
        pay_multiplier_percentage = (
            (pay_multiplier_score / max_pay_multiplier_score) * 100
            if max_pay_multiplier_score
            else 0
        )
        results.pay_multiplier = round(pay_multiplier_percentage, 2)

        # Childcare calculation
        childcare_questions = ["q80", "q88", "q89"]
        max_childcare_score = 14
        total_childcare_score = sum(
            int(form_data.get(question_key, 0)) for question_key in childcare_questions
        )
        childcare_percentage = (
            (total_childcare_score / max_childcare_score) * 100
            if max_childcare_score
            else 0
        )
        results.childcare = round(childcare_percentage, 2)

        q97_response = int(form_data.get("q97", 0))

        # Pay and Childcare Multiplier calculation
        if total_pay_score == 0 or total_childcare_score == 0:
            pay_childcare_multiplier_score = 0
        else:
            pay_childcare_multiplier_score = (
                total_pay_score + total_childcare_score
            ) * q97_response
        max_pay_childcare_multiplier_score = 128
        pay_childcare_multiplier_percentage = (
            (pay_childcare_multiplier_score / max_pay_childcare_multiplier_score) * 100
            if max_pay_childcare_multiplier_score
            else 0
        )
        results.pay_and_childcare_multiplier = round(
            pay_childcare_multiplier_percentage, 2
        )

        # Complexity calculation
        complexity_questions = ["q31", "q32", "q33", "q34", "q35", "q36", "q37"]
        max_complexity_score = 42
        total_complexity_score = sum(
            int(form_data.get(question_key, 0)) for question_key in complexity_questions
        )
        complexity_percentage = (total_complexity_score / max_complexity_score) * 100
        results.complexity = round(complexity_percentage, 2)

        # Hours and Flexibility calculation
        hours_flexibility_questions = ["q24", "q25", "q26", "q27", "q28", "q29", "q30"]
        max_hours_flexibility_score = 42
        total_hours_flexibility_score = sum(
            int(form_data.get(question_key, 0))
            for question_key in hours_flexibility_questions
        )
        hours_flexibility_percentage = (
            total_hours_flexibility_score / max_hours_flexibility_score
        ) * 100
        results.hours_and_flexibility = round(hours_flexibility_percentage, 2)

        # Control and Autonomy over Working Hours calculation
        control_autonomy_score = int(form_data.get("q25", 0))
        max_control_autonomy_score = 6
        control_autonomy_percentage = (
            (control_autonomy_score / max_control_autonomy_score) * 100
            if max_control_autonomy_score
            else 0
        )
        results.control_and_autonomy_over_working_hours = round(
            control_autonomy_percentage, 2
        )

        # Workload calculation
        workload_score = int(form_data.get("q29", 0))
        max_workload_score = 6
        workload_percentage = (workload_score / max_workload_score) * 100
        results.workload = round(workload_percentage, 2)

        # Manageable Workload calculation
        manageable_workload_questions = ["q28", "q29"]
        max_manageable_workload_score = 12
        total_manageable_workload_score = sum(
            int(form_data.get(question_key, 0))
            for question_key in manageable_workload_questions
        )
        manageable_workload_percentage = (
            total_manageable_workload_score / max_manageable_workload_score
        ) * 100
        results.manageable_workload = round(manageable_workload_percentage, 2)

        # Training calculation
        training_questions = ["q46", "q47", "q48"]
        max_training_score = 18
        total_training_score = sum(
            int(form_data.get(question_key, 0)) for question_key in training_questions
        )
        training_percentage = (
            (total_training_score / max_training_score) * 100
            if max_training_score
            else 0
        )
        results.training = round(training_percentage, 2)

        # Complexity plus Training calculation
        if total_complexity_score == 0:
            complexity_plus_training_score = 0
        else:
            complexity_plus_training_score = (
                total_complexity_score + total_training_score
            )
        max_complexity_plus_training_score = 60
        complexity_plus_training_percentage = (
            (complexity_plus_training_score / max_complexity_plus_training_score) * 100
            if max_complexity_plus_training_score
            else 0
        )
        results.complexity_plus_training = round(complexity_plus_training_percentage, 2)

        # Complexity + Training + Hours and Flexibility calculation
        if total_complexity_score == 0:
            complexity_training_hours_flexibility_score = 0
        else:
            complexity_training_hours_flexibility_score = (
                total_complexity_score
                + total_training_score
                + total_hours_flexibility_score
            )
        max_complexity_training_hours_flexibility_score = 102
        complexity_training_hours_flexibility_percentage = (
            (
                complexity_training_hours_flexibility_score
                / max_complexity_training_hours_flexibility_score
            )
            * 100
            if max_complexity_training_hours_flexibility_score
            else 0
        )
        results.complexity_training_hours_and_flexibility = round(
            complexity_training_hours_flexibility_percentage, 2
        )

        # Work Breaks calculation
        work_breaks_score = int(form_data.get("q28", 0))
        max_work_breaks_score = 6
        work_breaks_percentage = (
            (work_breaks_score / max_work_breaks_score) * 100
            if max_work_breaks_score
            else 0
        )
        results.work_breaks = round(work_breaks_percentage, 2)

        # Overtime calculation
        overtime_score = int(form_data.get("q30", 0))
        max_overtime_score = 6
        overtime_percentage = (
            (overtime_score / max_overtime_score) * 100 if max_overtime_score else 0
        )
        results.overtime = round(overtime_percentage, 2)

        # Team and Colleague Support calculation
        team_support_questions = ["q41", "q42", "q43", "q51", "q52"]
        max_team_support_score = 30
        total_team_support_score = sum(
            int(form_data.get(question_key, 0))
            for question_key in team_support_questions
        )
        team_support_percentage = (
            total_team_support_score / max_team_support_score
        ) * 100
        results.team_and_colleague_support = round(team_support_percentage, 2)

        # Management Support calculation
        management_support_questions = ["q39", "q40", "q43", "q44", "q50", "q56"]
        max_management_support_score = 36
        total_management_support_score = sum(
            int(form_data.get(question_key, 0))
            for question_key in management_support_questions
        )
        management_support_percentage = (
            total_management_support_score / max_management_support_score
        ) * 100
        results.management_support = round(management_support_percentage, 2)

        # Management Support Multiplier calculation
        management_support_multiplier_score = (
            total_management_support_score * q63_response
        )
        max_management_support_multiplier_score = 144
        management_support_multiplier_percentage = (
            (
                management_support_multiplier_score
                / max_management_support_multiplier_score
            )
            * 100
            if max_management_support_multiplier_score
            else 0
        )
        results.management_support_multiplier = round(
            management_support_multiplier_percentage, 2
        )

        # Culture calculation
        culture_questions = ["q50", "q51", "q52", "q53"]
        max_culture_score = 24
        total_culture_score = sum(
            int(form_data.get(question_key, 0)) for question_key in culture_questions
        )
        culture_percentage = (total_culture_score / max_culture_score) * 100
        results.culture = round(culture_percentage, 2)

        # Culture Multiplier calculation
        culture_multiplier_score = total_culture_score * q63_response
        max_culture_multiplier_score = 96
        culture_multiplier_percentage = (
            (culture_multiplier_score / max_culture_multiplier_score) * 100
            if max_culture_multiplier_score
            else 0
        )
        results.culture_multiplier = round(culture_multiplier_percentage, 2)

        # Problem Solving calculation
        problem_solving_questions = ["q182", "q183"]
        total_problem_solving_score = sum(
            int(form_data.get(question_key, 0))
            for question_key in problem_solving_questions
        )
        max_problem_solving_score = 12
        problem_solving_percentage = (
            total_problem_solving_score / max_problem_solving_score
        ) * 100
        results.problem_solving = round(problem_solving_percentage, 2)

        # Managerial Trust calculation
        managerial_trust_score = int(form_data.get("q50", 0))
        max_managerial_trust_score = 6
        managerial_trust_percentage = (
            (managerial_trust_score / max_managerial_trust_score) * 100
            if max_managerial_trust_score
            else 0
        )
        results.managerial_trust = round(managerial_trust_percentage, 2)

        # Colleague Trust calculation
        colleague_trust_score = int(form_data.get("q51", 0))
        max_colleague_trust_score = 6
        colleague_trust_percentage = (
            (colleague_trust_score / max_colleague_trust_score) * 100
            if max_colleague_trust_score
            else 0
        )
        results.colleague_trust = round(colleague_trust_percentage, 2)

        # Consultation calculation
        consultation_score = int(form_data.get("q44", 0))
        max_consultation_score = 6
        consultation_percentage = (
            (consultation_score / max_consultation_score) * 100
            if max_consultation_score
            else 0
        )
        results.consultation = round(consultation_percentage, 2)

        # Team Morale calculation
        team_morale_score = int(form_data.get("q52", 0))
        max_team_morale_score = 6
        team_morale_percentage = (
            (team_morale_score / max_team_morale_score) * 100
            if max_team_morale_score
            else 0
        )
        results.team_morale = round(team_morale_percentage, 2)

        # Willingness to Progress calculation
        willingness_to_progress_score = int(form_data.get("q48", 0))
        max_willingness_to_progress_score = 6
        willingness_to_progress_percentage = (
            (willingness_to_progress_score / max_willingness_to_progress_score) * 100
            if max_willingness_to_progress_score
            else 0
        )
        results.willingness_to_progress = round(willingness_to_progress_percentage, 2)

        # Lone Working calculation
        lone_working_score = int(form_data.get("q49", 0))
        max_lone_working_score = 6
        lone_working_percentage = (
            (lone_working_score / max_lone_working_score) * 100
            if max_lone_working_score
            else 0
        )
        results.lone_working = round(lone_working_percentage, 2)

        # Wider Team Support calculation
        wider_team_support_score = int(form_data.get("q53", 0))
        max_wider_team_support_score = 6
        wider_team_support_percentage = (
            (wider_team_support_score / max_wider_team_support_score) * 100
            if max_wider_team_support_score
            else 0
        )
        results.wider_team_support = round(wider_team_support_percentage, 2)

        # Lone Working and Wider Team Support Multiplier calculation
        if lone_working_score == 0:
            lone_wider_support_multiplier_score = 0
        else:
            lone_wider_support_multiplier_score = (
                lone_working_score + wider_team_support_score
            ) * q63_response
        max_lone_wider_support_multiplier_score = 48
        lone_wider_support_multiplier_percentage = (
            (
                lone_wider_support_multiplier_score
                / max_lone_wider_support_multiplier_score
            )
            * 100
            if max_lone_wider_support_multiplier_score
            else 0
        )
        results.lone_working_and_wider_team_support_multiplier = round(
            lone_wider_support_multiplier_percentage, 2
        )

        # Team and Colleague Support Multiplier calculation
        team_colleague_support_multiplier_score = (
            total_team_support_score * q63_response
        )
        max_team_colleague_support_multiplier_score = 120
        team_colleague_support_multiplier_percentage = (
            (
                team_colleague_support_multiplier_score
                / max_team_colleague_support_multiplier_score
            )
            * 100
            if max_team_colleague_support_multiplier_score
            else 0
        )
        results.team_and_colleague_support_multiplier = round(
            team_colleague_support_multiplier_percentage, 2
        )

        # Health and Safety calculation
        health_safety_questions = ["q54", "q55", "q56"]
        max_health_safety_score = 18
        total_health_safety_score = sum(
            int(form_data.get(question_key, 0))
            for question_key in health_safety_questions
        )
        health_safety_percentage = (
            total_health_safety_score / max_health_safety_score
        ) * 100
        results.health_and_safety = round(health_safety_percentage, 2)

        # Health and Safety Multiplier calculation
        health_safety_multiplier_score = total_health_safety_score * q63_response
        max_health_safety_multiplier_score = 72
        health_safety_multiplier_percentage = (
            (health_safety_multiplier_score / max_health_safety_multiplier_score) * 100
            if max_health_safety_multiplier_score
            else 0
        )
        results.health_and_safety_multiplier = round(
            health_safety_multiplier_percentage, 2
        )

        # Absence calculation
        absence_questions = ["q57", "q58"]
        max_absence_score = 12
        total_absence_score = sum(
            int(form_data.get(question_key, 0)) for question_key in absence_questions
        )
        absence_percentage = (total_absence_score / max_absence_score) * 100
        results.absence = round(absence_percentage, 2)

        # Absence and Support calculation
        q59_response = int(form_data.get("q59", 0))
        absence_and_support_score = (
            total_absence_score + q59_response if total_absence_score > 0 else 0
        )
        max_absence_and_support_score = 18
        absence_and_support_percentage = (
            (absence_and_support_score / max_absence_and_support_score) * 100
            if max_absence_and_support_score
            else 0
        )
        results.absence_and_support = round(absence_and_support_percentage, 2)

        # Absence Multiplier calculation
        absence_multiplier_score = (
            (total_absence_score + q59_response) * q63_response
            if total_absence_score > 0
            else 0
        )
        max_absence_multiplier_score = 72
        absence_multiplier_percentage = (
            (absence_multiplier_score / max_absence_multiplier_score) * 100
            if max_absence_multiplier_score
            else 0
        )
        results.absence_multiplier = round(absence_multiplier_percentage, 2)

        # Sick Leave and Employer Support calculation
        sick_leave_support_score = int(form_data.get("q59", 0))
        max_sick_leave_support_score = 6
        sick_leave_support_percentage = (
            (sick_leave_support_score / max_sick_leave_support_score) * 100
            if max_sick_leave_support_score
            else 0
        )
        results.sick_leave_and_employer_support = round(
            sick_leave_support_percentage, 2
        )

        # Covid calculation
        covid_score = int(form_data.get("q60", 0)) + int(form_data.get("q61", 0))
        max_covid_score = 8
        covid_percentage = covid_score / max_covid_score * 100
        results.covid = round(covid_percentage, 2)

        # Covid Multiplier calculation
        covid_multiplier_score = covid_score * q63_response
        max_covid_multiplier_score = 32
        covid_multiplier_percentage = (
            covid_multiplier_score / max_covid_multiplier_score * 100
        )
        results.covid_multiplier = covid_multiplier_percentage

        # Work-Related Stress Impacting personal life calculation
        work_stress_personal_life_score = total_environment_score * q63_response
        max_work_stress_personal_life_score = 1244
        work_stress_personal_life_percentage = (
            (work_stress_personal_life_score / max_work_stress_personal_life_score)
            * 100
            if max_work_stress_personal_life_score
            else 0
        )
        results.work_related_stress_impacting_personal_life = round(
            work_stress_personal_life_percentage, 2
        )

        q62_response = int(form_data.get("q62", 0))

        # Work-Related Stress Impacting Family and Relationships calculation
        work_stress_family_score = total_environment_score * q62_response
        max_work_stress_family_score = 1244
        work_stress_family_percentage = (
            work_stress_family_score / max_work_stress_family_score
        ) * 100
        results.work_related_stress_impacting_family_and_relationships = round(
            work_stress_family_percentage, 2
        )

        # Get Q64 response
        q64_response = int(form_data.get("q64", 0))

        # Work-Related Stress Impacting Social Life calculation
        work_stress_social_life_score = total_environment_score * q64_response
        max_work_stress_social_life_score = 1244
        work_stress_social_life_percentage = (
            (work_stress_social_life_score / max_work_stress_social_life_score) * 100
            if max_work_stress_social_life_score
            else 0
        )
        results.work_related_stress_impacting_social_life = round(
            work_stress_social_life_percentage, 2
        )

        # Mental Health calculation
        mental_health_questions = [
            "q114",
            "q115",
            "q116",
            "q117",
            "q118",
            "q119",
            "q120",
            "q121",
            "q122",
        ]
        max_mental_health_score = 30
        total_mental_health_score = sum(
            int(form_data.get(question_key, 0))
            for question_key in mental_health_questions
        )
        mental_health_percentage = (
            total_mental_health_score / max_mental_health_score
        ) * 100
        results.mental_health = round(mental_health_percentage, 2)

        q121_response = int(form_data.get("q121", 0))

        # Mental Health Multiplier calculation
        mental_health_multiplier_score = total_mental_health_score * q121_response
        max_mental_health_multiplier_score = 120
        mental_health_multiplier_percentage = (
            (mental_health_multiplier_score / max_mental_health_multiplier_score) * 100
            if max_mental_health_multiplier_score
            else 0
        )
        results.mental_health_multiplier = round(mental_health_multiplier_percentage, 2)

        # Carer calculation
        carer_score = int(form_data.get("q83", 0)) + int(form_data.get("q198", 0))
        max_carer_score = 6
        carer_percentage = (carer_score / max_carer_score) * 100
        results.carer = round(carer_percentage, 2)

        # Physical Health calculation
        physical_health_questions = [
            "q104",
            "q105",
            "q106",
            "q107",
            "q108",
            "q109",
            "q110",
            "q111",
            "q112",
            "q113",
        ]
        max_physical_health_score = 28
        total_physical_health_score = sum(
            int(form_data.get(question_key, 0))
            for question_key in physical_health_questions
        )
        physical_health_percentage = (
            total_physical_health_score / max_physical_health_score
        ) * 100
        results.physical_health = round(physical_health_percentage, 2)

        q112_response = int(form_data.get("q112", 0))

        # Physical Health Multiplier calculation
        physical_health_multiplier_score = total_physical_health_score * q112_response
        max_physical_health_multiplier_score = 112
        physical_health_multiplier_percentage = (
            (physical_health_multiplier_score / max_physical_health_multiplier_score)
            * 100
            if max_physical_health_multiplier_score
            else 0
        )
        results.physical_health_multiplier = round(
            physical_health_multiplier_percentage, 2
        )

        # Physical Health and Absence Multiplier calculation
        if total_absence_score > 0:
            physical_absence_multiplier_score = (
                total_physical_health_score + total_absence_score
            ) * q112_response
        else:
            physical_absence_multiplier_score = 0
        max_physical_absence_multiplier_score = 160
        physical_absence_multiplier_percentage = (
            (physical_absence_multiplier_score / max_physical_absence_multiplier_score)
            * 100
            if max_physical_absence_multiplier_score
            else 0
        )
        results.physical_health_and_absence_multiplier = round(
            physical_absence_multiplier_percentage, 2
        )

        # Mental and Physical Health calculation
        mental_physical_health_score = (
            total_mental_health_score + total_physical_health_score
        )
        max_mental_physical_health_score = 58
        mental_physical_health_percentage = (
            (mental_physical_health_score / max_mental_physical_health_score) * 100
            if max_mental_physical_health_score
            else 0
        )
        results.mental_and_physical_health = round(mental_physical_health_percentage, 2)

        q156_response = int(form_data.get("q156", 0))

        # Mental and Physical Health Multiplier calculation
        mental_physical_health_multiplier_score = (
            mental_physical_health_score * q156_response
        )
        max_mental_physical_health_multiplier_score = 232
        mental_physical_health_multiplier_percentage = (
            (
                mental_physical_health_multiplier_score
                / max_mental_physical_health_multiplier_score
            )
            * 100
            if max_mental_physical_health_multiplier_score
            else 0
        )
        results.mental_and_physical_health_multiplier = round(
            mental_physical_health_multiplier_percentage, 2
        )

        # Family Support Companion calculation
        family_support_questions = ["q75", "q76"]
        max_family_support_score = 4
        total_family_support_score = sum(
            int(form_data.get(question_key, 0))
            for question_key in family_support_questions
        )
        family_support_percentage = (
            total_family_support_score / max_family_support_score
        ) * 100
        results.family_support_companion = round(family_support_percentage, 2)

        # Responsibility of Children calculation
        responsibility_children_questions = ["q77", "q78", "q79", "q80", "q81", "q82"]
        max_responsibility_children_score = 17
        total_responsibility_children_score = sum(
            int(form_data.get(question_key, 0))
            for question_key in responsibility_children_questions
        )
        responsibility_children_percentage = (
            total_responsibility_children_score / max_responsibility_children_score
        ) * 100
        results.responsibility_of_children = round(
            responsibility_children_percentage, 2
        )

        # Responsibility for Children Multiplier calculation
        responsibility_children_multiplier_score = (
            total_responsibility_children_score * q97_response
        )
        max_responsibility_children_multiplier_score = 68
        responsibility_children_multiplier_percentage = (
            (
                responsibility_children_multiplier_score
                / max_responsibility_children_multiplier_score
            )
            * 100
            if max_responsibility_children_multiplier_score
            else 0
        )
        results.responsibility_for_children_multiplier = round(
            responsibility_children_multiplier_percentage, 2
        )

        # Childcare calculation
        childcare_questions = ["q80", "q88", "q89"]
        max_childcare_score = 14
        total_childcare_score = sum(
            int(form_data.get(question_key, 0)) for question_key in childcare_questions
        )
        childcare_percentage = (total_childcare_score / max_childcare_score) * 100
        results.childcare = round(childcare_percentage, 2)

        # Childcare Multiplier calculation
        childcare_multiplier_score = total_childcare_score * q97_response
        max_childcare_multiplier_score = 56
        childcare_multiplier_percentage = (
            (childcare_multiplier_score / max_childcare_multiplier_score) * 100
            if max_childcare_multiplier_score
            else 0
        )
        results.childcare_multiplier = round(childcare_multiplier_percentage, 2)

        # Emotional Health calculation
        emotional_health_questions = ["q204", "q205", "q206", "q207", "q208"]
        max_emotional_health_score = 10
        total_emotional_health_score = sum(
            int(form_data.get(question_key, 0))
            for question_key in emotional_health_questions
        )
        emotional_health_percentage = (
            total_emotional_health_score / max_emotional_health_score
        ) * 100
        results.emotional_health = round(emotional_health_percentage, 2)

        # Personal Satisfaction calculation
        personal_satisfaction_score = int(form_data.get("q202", 0))
        max_personal_satisfaction_score = 6
        personal_satisfaction_percentage = (
            (personal_satisfaction_score / max_personal_satisfaction_score) * 100
            if max_personal_satisfaction_score
            else 0
        )
        results.personal_satisfaction = round(personal_satisfaction_percentage, 2)

        # Personal Satisfaction Improvement calculation
        personal_satisfaction_improvement_score = personal_satisfaction_score + int(
            form_data.get("q203", 0)
        )
        max_personal_satisfaction_improvement_score = 12
        personal_satisfaction_improvement_percentage = (
            (
                personal_satisfaction_improvement_score
                / max_personal_satisfaction_improvement_score
            )
            * 100
            if max_personal_satisfaction_improvement_score
            else 0
        )
        results.personal_satisfaction_improvement = round(
            personal_satisfaction_improvement_percentage, 2
        )

        # Personal Finances calculation
        personal_finances_questions = ["q184", "q185", "q186", "q187"]
        max_personal_finances_score = 12
        total_personal_finances_score = sum(
            int(form_data.get(question_key, 0))
            for question_key in personal_finances_questions
        )
        personal_finances_percentage = (
            (total_personal_finances_score / max_personal_finances_score) * 100
            if max_personal_finances_score
            else 0
        )
        results.personal_finances = round(personal_finances_percentage, 2)

        # Personal Finances and Responsibility for Children calculation
        if total_personal_finances_score > 0:
            finances_children_score = (
                total_personal_finances_score + total_responsibility_children_score
            )
        else:
            finances_children_score = 0
        max_finances_children_score = 29
        finances_children_percentage = (
            (finances_children_score / max_finances_children_score) * 100
            if max_finances_children_score
            else 0
        )
        results.personal_finances_and_responsibility_for_children = round(
            finances_children_percentage, 2
        )

        # Personal Finances and Pay Multiplier calculation
        if total_personal_finances_score > 0:
            finances_pay_multiplier_score = (
                total_personal_finances_score * pay_multiplier_score
            )
        else:
            finances_pay_multiplier_score = 0
        max_finances_pay_multiplier_score = 864
        finances_pay_multiplier_percentage = (
            (finances_pay_multiplier_score / max_finances_pay_multiplier_score) * 100
            if max_finances_pay_multiplier_score
            else 0
        )
        results.personal_finances_and_pay_multiplier = round(
            finances_pay_multiplier_percentage, 2
        )

        # Barriers calculation
        barriers_questions = [
            "q189",
            "q190",
            "q191",
            "q192",
            "q193",
            "q194",
            "q195",
            "q196",
        ]
        max_barriers_score = 48
        total_barriers_score = sum(
            int(form_data.get(question_key, 0)) for question_key in barriers_questions
        )
        barriers_percentage = (
            (total_barriers_score / max_barriers_score) * 100
            if max_barriers_score
            else 0
        )
        results.personal_barriers = round(barriers_percentage, 2)

        # Emotional Wellbeing calculation
        emotional_wellbeing_questions = [
            "q215",
            "q216",
            "q217",
            "q218",
            "q219",
            "q220",
            "q221",
            "q222",
            "q223",
        ]
        max_emotional_wellbeing_score = 31
        total_emotional_wellbeing_score = sum(
            int(form_data.get(question_key, 0))
            for question_key in emotional_wellbeing_questions
        )
        emotional_wellbeing_percentage = (
            (total_emotional_wellbeing_score / max_emotional_wellbeing_score) * 100
            if max_emotional_wellbeing_score
            else 0
        )
        results.emotional_wellbeing = round(emotional_wellbeing_percentage, 2)

        q225_response = int(form_data.get("q225", 0))

        # Emotional Wellbeing Multiplier calculation
        emotional_wellbeing_multiplier_score = (
            total_emotional_wellbeing_score * q225_response
        )
        max_emotional_wellbeing_multiplier_score = 124
        emotional_wellbeing_multiplier_percentage = (
            (
                emotional_wellbeing_multiplier_score
                / max_emotional_wellbeing_multiplier_score
            )
            * 100
            if max_emotional_wellbeing_multiplier_score
            else 0
        )
        results.emotional_wellbeing_multiplier = round(
            emotional_wellbeing_multiplier_percentage, 2
        )

        # Holidays calculation
        holiday_questions = ["q198", "q199", "q200", "q201"]
        max_holiday_score = 20
        total_holiday_score = sum(
            int(form_data.get(question_key, 0)) for question_key in holiday_questions
        )
        holiday_percentage = (total_holiday_score / max_holiday_score) * 100
        results.holidays = round(holiday_percentage, 2)

        # Financial Position as a Barrier for Holidays calculation
        financial_position_barrier_score = int(form_data.get("q199", 0))
        max_financial_position_barrier_score = 6
        financial_position_barrier_percentage = (
            (financial_position_barrier_score / max_financial_position_barrier_score)
            * 100
            if max_financial_position_barrier_score
            else 0
        )
        results.financial_position_as_a_barrier_for_holidays = round(
            financial_position_barrier_percentage, 2
        )

        # Identity calculation
        identity_questions = [
            "q162",
            "q163",
            "q164",
            "q165",
            "q166",
            "q169",
            "q170",
            "q171",
            "q172",
            "q173",
            "q174",
            "q175",
        ]
        max_identity_score = 39
        total_identity_score = sum(
            int(form_data.get(question_key, 0)) for question_key in identity_questions
        )
        identity_percentage = (
            (total_identity_score / max_identity_score) * 100
            if max_identity_score
            else 0
        )
        results.identity = round(identity_percentage, 2)

        # Identity and Management Support calculation
        if total_identity_score > 0:
            identity_management_support_score = (
                total_identity_score + total_management_support_score
            )
        else:
            identity_management_support_score = 0
        max_identity_management_support_score = 75
        identity_management_support_percentage = (
            (identity_management_support_score / max_identity_management_support_score)
            * 100
            if max_identity_management_support_score
            else 0
        )
        results.identity_and_management_support = round(
            identity_management_support_percentage, 2
        )

        # Discrimination calculation
        discrimination_questions = [
            "q169",
            "q170",
            "q171",
            "q172",
            "q173",
            "q174",
            "q175",
        ]
        max_discrimination_score = 15
        total_discrimination_score = sum(
            int(form_data.get(question_key, 0))
            for question_key in discrimination_questions
        )
        discrimination_percentage = (
            (total_discrimination_score / max_discrimination_score) * 100
            if max_discrimination_score
            else 0
        )
        results.discrimination = round(discrimination_percentage, 2)

        # Discrimination Work Impact calculation
        if total_discrimination_score > 0:
            discrimination_work_impact_score = (
                total_discrimination_score * q225_response
            )
        else:
            discrimination_work_impact_score = 0
        max_discrimination_work_impact_score = 60
        discrimination_work_impact_percentage = (
            (discrimination_work_impact_score / max_discrimination_work_impact_score)
            * 100
            if max_discrimination_work_impact_score
            else 0
        )
        results.discrimination_work_impact = round(
            discrimination_work_impact_percentage, 2
        )

        # Personal Relationships calculation
        personal_relationships_questions = ["q177", "q178", "q179", "q180", "q181"]
        max_personal_relationships_score = 22
        total_personal_relationships_score = sum(
            int(form_data.get(question_key, 0))
            for question_key in personal_relationships_questions
        )
        personal_relationships_percentage = (
            (total_personal_relationships_score / max_personal_relationships_score)
            * 100
            if max_personal_relationships_score
            else 0
        )
        results.personal_relationships = round(personal_relationships_percentage, 2)

        # Personal Relationships and Working Relationships Impact calculation
        if total_personal_relationships_score > 0:
            personal_work_relationships_impact_score = (
                total_personal_relationships_score + int(form_data.get("q179", 0))
            )
        else:
            personal_work_relationships_impact_score = 0
        max_personal_work_relationships_impact_score = 132
        personal_work_relationships_impact_percentage = (
            (
                personal_work_relationships_impact_score
                / max_personal_work_relationships_impact_score
            )
            * 100
            if max_personal_work_relationships_impact_score
            else 0
        )
        results.personal_relationships_and_working_relationships_impact = round(
            personal_work_relationships_impact_percentage, 2
        )

        # Emotional Distress calculation
        emotional_distress_questions = ["q209", "q210", "q211", "q212", "q213", "q214"]
        max_emotional_distress_score = 12
        total_emotional_distress_score = sum(
            int(form_data.get(question_key, 0))
            for question_key in emotional_distress_questions
        )
        emotional_distress_percentage = (
            (total_emotional_distress_score / max_emotional_distress_score) * 100
            if max_emotional_distress_score
            else 0
        )
        results.emotional_distress = round(emotional_distress_percentage, 2)

        # Emotional Distress Multiplier calculation
        emotional_distress_multiplier_score = (
            total_emotional_distress_score * q225_response
        )
        max_emotional_distress_multiplier_score = 48
        emotional_distress_multiplier_percentage = (
            (
                emotional_distress_multiplier_score
                / max_emotional_distress_multiplier_score
            )
            * 100
            if max_emotional_distress_multiplier_score
            else 0
        )
        results.emotional_distress_multiplier = round(
            emotional_distress_multiplier_percentage, 2
        )

        # Holidays and Pay calculation
        if total_holiday_score > 0:
            holidays_and_pay_score = total_holiday_score + total_pay_score
        else:
            holidays_and_pay_score = 0
        max_holidays_and_pay_score = 38
        holidays_and_pay_percentage = (
            (holidays_and_pay_score / max_holidays_and_pay_score) * 100
            if max_holidays_and_pay_score
            else 0
        )
        results.holidays_and_pay = round(holidays_and_pay_percentage, 2)

        # Emotional Wellbeing and Management Support calculation
        if total_emotional_wellbeing_score > 0:
            wellbeing_management_support_score = (
                total_emotional_wellbeing_score + total_management_support_score
            )
        else:
            wellbeing_management_support_score = 0
        max_wellbeing_management_support_score = 67
        wellbeing_management_support_percentage = (
            (
                wellbeing_management_support_score
                / max_wellbeing_management_support_score
            )
            * 100
            if max_wellbeing_management_support_score
            else 0
        )
        results.emotional_wellbeing_and_management_support = round(
            wellbeing_management_support_percentage, 2
        )

        # Personal Multiplier calculation
        personal_multiplier_score = total_personal_relationships_score * q225_response
        max_personal_multiplier_score = 952
        personal_multiplier_percentage = (
            (personal_multiplier_score / max_personal_multiplier_score) * 100
            if max_personal_multiplier_score
            else 0
        )
        results.personal_multiplier = round(personal_multiplier_percentage, 2)

        # Mental and Physical Health and Absence calculation
        if mental_physical_health_score > 0:
            mental_physical_absence_score = (
                mental_physical_health_score + absence_and_support_score
            )
        else:
            mental_physical_absence_score = 0
        max_mental_physical_absence_score = 76
        mental_physical_absence_percentage = (
            (mental_physical_absence_score / max_mental_physical_absence_score) * 100
            if max_mental_physical_absence_score
            else 0
        )
        results.mental_and_physical_health_and_absence_from_work = round(
            mental_physical_absence_percentage, 2
        )

        # Mental Health and Culture Multiplier calculation
        mental_health_culture_score = total_mental_health_score + total_culture_score
        max_mental_health_culture_score = 54
        mental_health_culture_percentage = (
            (mental_health_culture_score / max_mental_health_culture_score) * 100
            if max_mental_health_culture_score
            else 0
        )
        results.mental_health_and_culture_multiplier = round(
            mental_health_culture_percentage, 2
        )

        # Health and Safety Multiplier calculation
        health_and_safety_multiplier_score = total_health_safety_score * q63_response
        max_health_and_safety_multiplier_score = 72
        health_and_safety_multiplier_percentage = (
            (
                health_and_safety_multiplier_score
                / max_health_and_safety_multiplier_score
            )
            * 100
            if max_health_and_safety_multiplier_score
            else 0
        )
        results.health_and_safety_multiplier = round(
            health_and_safety_multiplier_percentage, 2
        )

        # Fertility and Pregnancy calculation
        fertility_questions = [
            "q123",
            "q124",
            "q125",
            "q126",
            "q127",
            "q128",
            "q129",
            "q130",
            "q131",
            "q132",
        ]
        max_fertility_score = 30
        total_fertility_score = sum(
            int(form_data.get(question_key, 0)) for question_key in fertility_questions
        )
        fertility_percentage = (
            (total_fertility_score / max_fertility_score) * 100
            if max_fertility_score
            else 0
        )
        results.fertility_and_pregnancy = round(fertility_percentage, 2)

        q132_response = int(form_data.get("q132", 0))

        # Pregnancy Impact calculation
        if total_fertility_score > 0:
            pregnancy_impact_score = total_fertility_score * q132_response
        else:
            pregnancy_impact_score = 0
        max_pregnancy_impact_score = 180
        pregnancy_impact_percentage = (
            (pregnancy_impact_score / max_pregnancy_impact_score) * 100
            if max_pregnancy_impact_score
            else 0
        )
        results.pregnancy_impact = round(pregnancy_impact_percentage, 2)

        # Abuse and Trauma calculation
        abuse_trauma_questions = [
            "q134",
            "q135",
            "q136",
            "q137",
            "q138",
            "q139",
            "q140",
            "q141",
            "q142",
        ]
        max_abuse_trauma_score = 38
        total_abuse_trauma_score = sum(
            int(form_data.get(question_key, 0))
            for question_key in abuse_trauma_questions
        )
        abuse_trauma_percentage = (
            (total_abuse_trauma_score / max_abuse_trauma_score) * 100
            if max_abuse_trauma_score
            else 0
        )
        results.abuse_and_trauma = round(abuse_trauma_percentage, 2)

        q140_response = int(form_data.get("q140", 0))

        # Abuse and Trauma Impact calculation
        if total_abuse_trauma_score > 0:
            abuse_trauma_impact_score = total_abuse_trauma_score * q140_response
        else:
            abuse_trauma_impact_score = 0
        max_abuse_trauma_impact_score = 228
        abuse_trauma_impact_percentage = (
            (abuse_trauma_impact_score / max_abuse_trauma_impact_score) * 100
            if max_abuse_trauma_impact_score
            else 0
        )
        results.abuse_and_trauma_impact = round(abuse_trauma_impact_percentage, 2)

        # Abuse and Trauma and Management Support and Culture calculation
        if total_abuse_trauma_score > 0:
            abuse_trauma_management_culture_score = (
                total_abuse_trauma_score + total_culture_score
            )
        else:
            abuse_trauma_management_culture_score = 0
        max_abuse_trauma_management_culture_score = 62
        abuse_trauma_management_culture_percentage = (
            (
                abuse_trauma_management_culture_score
                / max_abuse_trauma_management_culture_score
            )
            * 100
            if max_abuse_trauma_management_culture_score
            else 0
        )
        results.abuse_and_trauma_and_management_support_and_culture = round(
            abuse_trauma_management_culture_percentage, 2
        )

        # Self-Care calculation
        self_care_questions = ["q143", "q144", "q145"]
        max_self_care_score = 18
        total_self_care_score = sum(
            int(form_data.get(question_key, 0)) for question_key in self_care_questions
        )
        self_care_percentage = (
            (total_self_care_score / max_self_care_score) * 100
            if max_self_care_score
            else 0
        )
        results.self_care = round(self_care_percentage, 2)

        # Self-Care and Physical Health calculation
        if total_self_care_score > 0:
            self_care_physical_health_score = (
                total_self_care_score + total_physical_health_score
            )
        else:
            self_care_physical_health_score = 0
        max_self_care_physical_health_score = 46
        self_care_physical_health_percentage = (
            (self_care_physical_health_score / max_self_care_physical_health_score)
            * 100
            if max_self_care_physical_health_score
            else 0
        )
        results.self_care_and_physical_health = round(
            self_care_physical_health_percentage, 2
        )

        # Self-Care and Mental Health calculation
        if total_self_care_score > 0:
            self_care_mental_health_score = (
                total_self_care_score + total_mental_health_score
            )
        else:
            self_care_mental_health_score = 0
        max_self_care_mental_health_score = 48
        self_care_mental_health_percentage = (
            (self_care_mental_health_score / max_self_care_mental_health_score) * 100
            if max_self_care_mental_health_score
            else 0
        )
        results.self_care_and_mental_health = round(
            self_care_mental_health_percentage, 2
        )

        # Emotional Health and Culture at Work calculation
        if total_emotional_wellbeing_score > 0:
            emotional_health_culture_score = (
                total_emotional_wellbeing_score + total_culture_score
            )
        else:
            emotional_health_culture_score = 0
        max_emotional_health_culture_score = 55
        emotional_health_culture_percentage = (
            (emotional_health_culture_score / max_emotional_health_culture_score) * 100
            if max_emotional_health_culture_score
            else 0
        )
        results.emotional_health_and_culture_at_work = round(
            emotional_health_culture_percentage, 2
        )

        # Discrimination Work Impact calculation
        if total_discrimination_score > 0:
            discrimination_work_impact_score = (
                total_discrimination_score * q225_response
            )
        else:
            discrimination_work_impact_score = 0
        max_discrimination_work_impact_score = 60
        discrimination_work_impact_percentage = (
            (discrimination_work_impact_score / max_discrimination_work_impact_score)
            * 100
            if max_discrimination_work_impact_score
            else 0
        )
        results.discrimination_work_impact = round(
            discrimination_work_impact_percentage, 2
        )

        # Age Discrimination calculation
        age_discrimination_score = int(form_data.get("q170", 0)) * q225_response
        max_age_discrimination_score = 8
        age_discrimination_percentage = (
            (age_discrimination_score / max_age_discrimination_score) * 100
            if max_age_discrimination_score
            else 0
        )
        results.age_discrimination = round(age_discrimination_percentage, 2)

        # Race Discrimination calculation
        race_discrimination_score = int(form_data.get("q171", 0)) * q225_response
        max_race_discrimination_score = 8
        race_discrimination_percentage = (
            (race_discrimination_score / max_race_discrimination_score) * 100
            if max_race_discrimination_score
            else 0
        )
        results.race_discrimination = round(race_discrimination_percentage, 2)

        # Disability Discrimination calculation
        disability_discrimination_score = int(form_data.get("q172", 0)) * q225_response
        max_disability_discrimination_score = 8
        disability_discrimination_percentage = (
            (disability_discrimination_score / max_disability_discrimination_score)
            * 100
            if max_disability_discrimination_score
            else 0
        )
        results.disability_discrimination = round(
            disability_discrimination_percentage, 2
        )

        # Gender Discrimination calculation
        gender_discrimination_score = int(form_data.get("q173", 0)) * q225_response
        max_gender_discrimination_score = 8
        gender_discrimination_percentage = (
            (gender_discrimination_score / max_gender_discrimination_score) * 100
            if max_gender_discrimination_score
            else 0
        )
        results.gender_discrimination = round(gender_discrimination_percentage, 2)

        # Sexual Discrimination calculation
        sexual_discrimination_score = int(form_data.get("q174", 0)) * q225_response
        max_sexual_discrimination_score = 8
        sexual_discrimination_percentage = (
            (sexual_discrimination_score / max_sexual_discrimination_score) * 100
            if max_sexual_discrimination_score
            else 0
        )
        results.sexual_discrimination = round(sexual_discrimination_percentage, 2)

        # Other Discrimination calculation
        other_discrimination_score = int(form_data.get("q175", 0)) * q225_response
        max_other_discrimination_score = 8
        other_discrimination_percentage = (
            (other_discrimination_score / max_other_discrimination_score) * 100
            if max_other_discrimination_score
            else 0
        )
        results.other_discrimination = round(other_discrimination_percentage, 2)

        # abuse_and_trauma_and_management_support_multiplier
        if total_abuse_trauma_score > 0:
            abuse_trauma_management_support_multiplier_score = (
                total_abuse_trauma_score + total_management_support_score
            )
        else:
            abuse_trauma_management_support_multiplier_score = 0
        max_abuse_trauma_management_support_multiplier_score = 74
        abuse_trauma_management_support_multiplier_score_percentage = (
            (
                abuse_trauma_management_support_multiplier_score
                / max_abuse_trauma_management_support_multiplier_score
            )
            * 100
            if max_abuse_trauma_management_support_multiplier_score
            else 0
        )
        results.abuse_and_trauma_and_management_support_multiplier = round(
            abuse_trauma_management_support_multiplier_score_percentage, 2
        )

        # Emotional health multiplier
        emotional_health_multiplier_score = (
            int(form_data.get("q225", 0)) * total_emotional_health_score
        )
        max_emotional_health_multiplier_score = 40
        emotional_health_multiplier_percentage = (
            (emotional_health_multiplier_score / max_emotional_health_multiplier_score)
            * 100
            if max_emotional_health_multiplier_score
            else 0
        )
        results.emotional_health_multiplier = round(
            emotional_health_multiplier_percentage, 2
        )

        # Family
        family_questions = [f"q{i}" for i in range(67, 100)]  # Questions 1 to 66
        max_family_score = 112
        total_family_score = 0

        for question_key in family_questions:
            value = form_data.get(question_key)
            if value is not None:
                if isinstance(value, int):
                    total_family_score += value
                elif isinstance(value, str) and value.isdigit():
                    total_family_score += int(value)

        # Calculate family Percentage
        family_percentage = (total_family_score / max_family_score) * 100
        results.family = round(family_percentage, 2)

        # Responsibility for family
        responsibility_family = ["q92", "q93", "q94", "q95"]
        max_responsibility_family_score = 16
        total_responsibility_family_score = sum(
            int(form_data.get(question_key, 0))
            for question_key in responsibility_family
        )
        responsibility_family_percentage = (
            total_responsibility_family_score / max_responsibility_family_score
        ) * 100
        results.responsibility_for_family = round(responsibility_family_percentage, 2)

        # Family factors
        if total_responsibility_children_score + total_responsibility_family_score > 0:
            family_factors_score = (
                total_responsibility_children_score
                + childcare_multiplier_score
                + total_responsibility_family_score
            )
        else:
            family_factors_score = 0
        max_family_factors_score = 89
        family_factors_score_percentage = (
            (family_factors_score / max_family_factors_score) * 100
            if max_family_factors_score
            else 0
        )
        results.family_factors = round(family_factors_score_percentage, 2)

        # Family multiplier
        family_multiplier_score = q97_response * total_family_score
        max_family_multiplier_score = 448
        family_multiplier_percentage = (
            (family_multiplier_score / max_family_multiplier_score) * 100
            if max_family_multiplier_score
            else 0
        )
        results.family_multiplier = round(family_multiplier_percentage, 2)

        # fertility and pregnancy impacting work
        fertility_pregnancy_work_score = int(form_data.get("q132", 0))
        max_fertility_pregnancy_work_score = 6
        fertility_pregnancy_work_percentage = (
            (fertility_pregnancy_work_score / max_fertility_pregnancy_work_score) * 100
            if max_fertility_pregnancy_work_score
            else 0
        )
        results.fertility_and_pregnancy_impacting_work = round(
            fertility_pregnancy_work_percentage, 2
        )

        # Work commitments as a barrier for holidays
        work_commitment_barrier_for_holidays_score = int(form_data.get("q200", 0))
        max_work_commitment_barrier_for_holidays_score = 6
        work_commitment_barrier_for_holidays_percentage = (
            (
                work_commitment_barrier_for_holidays_score
                / max_work_commitment_barrier_for_holidays_score
            )
            * 100
            if max_work_commitment_barrier_for_holidays_score
            else 0
        )
        results.work_commitments_as_a_barrier_for_holidays = round(
            work_commitment_barrier_for_holidays_percentage, 2
        )

        # physical_health_factors_impacting_work
        physical_health_factors_impacting_work_score = int(form_data.get("q156", 0))
        max_physical_health_factors_impacting_work_score = 4
        physical_health_factors_impacting_work_percentage = (
            (
                physical_health_factors_impacting_work_score
                / max_physical_health_factors_impacting_work_score
            )
            * 100
            if max_physical_health_factors_impacting_work_score
            else 0
        )
        results.physical_health_factors_impacting_work = round(
            physical_health_factors_impacting_work_percentage, 2
        )

        # physical_health_condition_affecting_work
        physical_health_condition_affecting_work_score = int(form_data.get("q112", 0))
        max_physical_health_condition_affecting_work_score = 4
        physical_health_condition_affecting_work_percentage = (
            physical_health_condition_affecting_work_score
            / max_physical_health_condition_affecting_work_score
            * 100
        )
        results.physical_health_condition_affecting_work = round(
            physical_health_condition_affecting_work_percentage, 2
        )

        # mental_health_factors_impacting_work
        mental_health_factors_impacting_work_score = int(form_data.get("q121", 0))
        max_mental_health_factors_impacting_work_score = 6
        mental_health_factors_impacting_work_percentage = (
            (
                mental_health_factors_impacting_work_score
                / max_mental_health_factors_impacting_work_score
            )
            * 100
            if max_mental_health_factors_impacting_work_score
            else 0
        )
        results.mental_health_factors_impacting_work = round(
            mental_health_factors_impacting_work_percentage, 2
        )

        # Health
        health_questions = [f"q{i}" for i in range(101, 160)]  # Questions 1 to 66
        max_health_score = 198
        total_health_score = 0

        for question_key in health_questions:
            value = form_data.get(question_key)
            if value is not None:
                if isinstance(value, int):
                    total_health_score += value
                elif isinstance(value, str) and value.isdigit():
                    total_health_score += int(value)

        # Calculate personal Percentage
        health_percentage = (total_health_score / max_health_score) * 100
        results.health = round(health_percentage, 2)

        # Personal
        personal_questions = [f"q{i}" for i in range(160, 228)]  # Questions 1 to 66
        max_personal_score = 238
        total_personal_score = 0

        for question_key in personal_questions:
            value = form_data.get(question_key)
            if value is not None:
                if isinstance(value, int):
                    total_personal_score += value
                elif isinstance(value, str) and value.isdigit():
                    total_personal_score += int(value)

        # Calculate personal Percentage
        personal_percentage = (total_personal_score / max_personal_score) * 100
        results.personal = round(personal_percentage, 2)

        # Hobbies
        hobbies_score = int(form_data.get("q188", 0))
        max_hobbies_score = 2
        hobbies_percentage = (
            (hobbies_score / max_hobbies_score) * 100 if max_hobbies_score else 0
        )
        results.hobbies = round(hobbies_percentage, 2)

        # Mental and physical health and absence from work
        if total_mental_health_score + total_physical_health_score > 0:
            mental_physical_absence_from_work_score = (
                total_mental_health_score
                + total_physical_health_score
                + absence_and_support_score
            )
        else:
            mental_physical_absence_from_work_score = 0
        max_mental_physical_absence_from_work_score = 76
        mental_physical_absence_from_work_percentage = (
            (
                mental_physical_absence_from_work_score
                / max_mental_physical_absence_from_work_score
                * 100
            )
            if max_mental_physical_absence_from_work_score > 0
            else 0
        )

        results.mental_and_physical_health_and_absence_from_work = round(
            mental_physical_absence_from_work_percentage, 2
        )

        # Mental health and absence multiplier
        mental_health_absence_multiplier_score = (
            total_mental_health_score + total_absence_score
        ) * q121_response
        max_mental_health_absence_multiplier_score = 168
        mental_health_absence_multiplier_percentage = (
            (
                mental_health_absence_multiplier_score
                / max_mental_health_absence_multiplier_score
            )
            * 100
            if max_mental_health_absence_multiplier_score
            else 0
        )
        results.mental_health_and_absence_multiplier = round(
            mental_health_absence_multiplier_percentage, 2
        )

        # Mental health, physical health and culture multiplier
        if total_mental_health_score + total_physical_health_score > 0:
            mental_physical_culture_multiplier_score = (
                total_mental_health_score
                + total_physical_health_score
                + total_culture_score
            ) * q63_response
        else:
            mental_physical_culture_multiplier_score = 0
        max_mental_physical_culture_multiplier_score = 328

        mental_physical_culture_multiplier_percentage = (
            (
                mental_physical_culture_multiplier_score
                / max_mental_physical_culture_multiplier_score
            )
            * 100
            if max_mental_physical_culture_multiplier_score
            else 0
        )
        results.mental_health_physical_health_and_culture_multiplier = round(
            mental_physical_culture_multiplier_percentage, 2
        )

        # Personal finances and pay, and childcare multiplier
        personal_finances_pay_childcare_multiplier_score = (
            total_personal_finances_score * pay_childcare_multiplier_score
        )
        max_personal_finances_pay_childcare_multiplier_score = 1536
        personal_finances_pay_childcare_multiplier_percentage = (
            (
                personal_finances_pay_childcare_multiplier_score
                / max_personal_finances_pay_childcare_multiplier_score
            )
            * 100
            if max_personal_finances_pay_childcare_multiplier_score
            else 0
        )
        results.personal_finances_and_pay_and_childcare_multiplier = round(
            personal_finances_pay_childcare_multiplier_percentage, 2
        )

        # Personal relationships and working relationship impact
        if total_personal_relationships_score > 0:
            personal_working_relationship_impact_score = (
                total_personal_relationships_score + int(form_data.get("q179", 0))
            )
        else:
            personal_working_relationship_impact_score = 0
        max_personal_working_relationship_impact_score = 328
        personal_working_relationship_impact_percentage = (
            (
                personal_working_relationship_impact_score
                / max_personal_working_relationship_impact_score
            )
            * 100
            if max_personal_working_relationship_impact_score
            else 0
        )
        results.personal_relationships_and_working_relationships_impact = round(
            personal_working_relationship_impact_percentage, 2
        )

        # Physical health and culture at work
        physical_health_and_culture_work_score = (
            total_physical_health_score + total_culture_score
        ) * q63_response
        max_physical_health_and_culture_work_score = 208
        physical_health_and_culture_work_percentage = (
            (
                physical_health_and_culture_work_score
                / max_physical_health_and_culture_work_score
            )
            * 100
            if max_physical_health_and_culture_work_score
            else 0
        )
        results.physical_health_and_culture = round(
            physical_health_and_culture_work_percentage, 2
        )

        # Physical health and management support multiplier
        physical_health_and_management_support_multiplier_score = (
            total_physical_health_score + total_management_support_score
        ) * q63_response
        max_physical_health_and_management_support_multiplier_score = 256
        physical_health_and_management_support_multiplier_percentage = (
            (
                physical_health_and_management_support_multiplier_score
                / max_physical_health_and_management_support_multiplier_score
            )
            * 100
            if max_physical_health_and_management_support_multiplier_score
            else 0
        )
        results.physical_health_and_management_support_multiplier = round(
            physical_health_and_management_support_multiplier_percentage, 2
        )

        # Pregnancy and management support
        if total_fertility_score > 0:
            pregnancy_management_support_score = (
                total_fertility_score + total_management_support_score
            )
        else:
            pregnancy_management_support_score = 0
        max_pregnancy_management_support_score = 66
        pregnancy_management_support_percentage = (
            (
                pregnancy_management_support_score
                / max_pregnancy_management_support_score
            )
            * 100
            if max_pregnancy_management_support_score
            else 0
        )
        results.pregnancy_and_management_support = round(
            pregnancy_management_support_percentage, 2
        )

        # Pregnancy and physical health
        if pregnancy_impact_score > 0:
            pregnancy_physical_health_score = (
                pregnancy_impact_score + total_physical_health_score
            )
        else:
            pregnancy_physical_health_score = 0
        max_pregnancy_physical_health_score = 58
        pregnancy_physical_health_percentage = (
            (pregnancy_physical_health_score / max_pregnancy_physical_health_score)
            * 100
            if max_pregnancy_physical_health_score
            else 0
        )
        results.pregnancy_and_physical_health = round(
            pregnancy_physical_health_percentage, 2
        )

        # Pregnancy and mental health
        if total_fertility_score > 0:
            pregnancy_mental_health_score = (
                total_fertility_score + total_mental_health_score
            )
        else:
            pregnancy_mental_health_score = 0
        max_pregnancy_mental_health_score = 60
        pregnancy_mental_health_percentage = (
            (pregnancy_mental_health_score / max_pregnancy_mental_health_score) * 100
            if max_pregnancy_mental_health_score
            else 0
        )
        results.pregnancy_and_mental_health = round(
            pregnancy_mental_health_percentage, 2
        )

        # Support network
        support_network = ["q84", "q85", "q86", "q87"]
        max_support_network_score = 19
        total_support_network_score = sum(
            int(form_data.get(question_key, 0)) for question_key in support_network
        )
        support_network_percentage = (
            total_support_network_score / max_support_network_score
        ) * 100
        results.support_network = round(support_network_percentage, 2)

        # Support Network Multiplier calculation
        support_network_multiplier_score = total_support_network_score * q97_response
        max_support_network_multiplier_score = 76
        support_network_multiplier_percentage = (
            support_network_multiplier_score / max_support_network_multiplier_score
        ) * 100
        results.support_network_multiplier = round(
            support_network_multiplier_percentage, 2
        )

        # Training multiplier
        training_multiplier_score = total_training_score * q63_response
        max_training_multiplier_score = 70
        training_multiplier_percentage = (
            (training_multiplier_score / max_training_multiplier_score) * 100
            if max_training_multiplier_score
            else 0
        )
        results.training_multiplier = round(training_multiplier_percentage, 2)

        results.save()

        return redirect("user_results")


@login_required
def dashboard(request):
    """
    Perform calculations on the quiz responses and display results.
    """
    # Mockup calculation logic
    results = {
        "physical_health": 75,
        "mental_health": 85,
    }
    return render(request, "bessie/result.html", {"results": results})


@login_required
def user_results(request):
    """
    View previously calculated results (mocked here).
    """
    employee = Employee.objects.get(user=request.user)
    response = BessieResponse.objects.get(employee=employee)
    results = BessieResult.objects.filter(response=response).values().first()

    staff_comment = results["staff_comment"]

    texts = {}

    for key, value in results.items():
        if isinstance(value, str):
            continue
        cat = get_category(value)
        pres = report_text.get(key)
        if pres:
            texts[key] = {
                "content": report_text[key][cat]["individual"],
                "category": cat,
            }
            texts[f"{key}_overview"] = report_text[key]["overview"]

    res = read_result(results)

    # TODO: MAKE CAN SEE RESULT FUNCTIONALITY

    return render(
        request,
        "bessie/result.html",
        {
            "stress_and_wellbeing": json.dumps(res["stress_and_wellbeing"]),
            "stress_risks_affecting_work": json.dumps(
                res["stress_risks_affecting_work"]
            ),
            "workplace_stress_factors": json.dumps(res["workplace_stress_factors"]),
            "presenteeism_factors": json.dumps(res["presenteeism"]),
            "environment_factors": json.dumps(res["environment"]),
            "family_factors": json.dumps(res["family"]),
            "health_factors": json.dumps(res["health"]),
            "personal_factors": json.dumps(res["personal"]),
            "report_text": json.dumps(texts),
            "potential_cost": round(results["potential_cost"]),
            "staff_comment": staff_comment,
            "can_see_result": False,
        },
    )


from django.core.exceptions import ObjectDoesNotExist


def view_results(request, id):
    """
    View previously calculated results (mocked here).
    """
    employee = Employee.objects.get(pk=id)

    if request.method == "POST":
        try:
            response = BessieResponse.objects.get(employee=employee)
            results = BessieResult.objects.get(response=response)
            results.staff_comment = request.POST.get("comment")
            results.save()

        except ObjectDoesNotExist:
            return render(
                request,
                "bessie/error.html",
                {"message": "this user has not taken the quiz yet"},
            )

        return redirect("view_results", id)

    if request.method == "GET":
        try:
            response = BessieResponse.objects.get(employee=employee)
        except ObjectDoesNotExist:
            return render(
                request,
                "bessie/error.html",
                {"message": "this user has not taken the quiz yet"},
            )

        results = BessieResult.objects.filter(response=response).values().first()

        staff_comment = results["staff_comment"]

        texts = {}

        for key, value in results.items():
            if isinstance(value, str):
                continue
            cat = get_category(value)
            pres = report_text.get(key)
            if pres:
                texts[key] = {
                    "content": report_text[key][cat]["individual"],
                    "category": cat,
                }
                texts[f"{key}_overview"] = report_text[key]["overview"]

        res = read_result(results)

        return render(
            request,
            "bessie/result.html",
            {
                "stress_and_wellbeing": json.dumps(res["stress_and_wellbeing"]),
                "stress_risks_affecting_work": json.dumps(
                    res["stress_risks_affecting_work"]
                ),
                "workplace_stress_factors": json.dumps(res["workplace_stress_factors"]),
                "presenteeism_factors": json.dumps(res["presenteeism"]),
                "environment_factors": json.dumps(res["environment"]),
                "family_factors": json.dumps(res["family"]),
                "health_factors": json.dumps(res["health"]),
                "personal_factors": json.dumps(res["personal"]),
                "report_text": json.dumps(texts),
                "responses": response,
                "potential_cost": round(results["potential_cost"]),
                "staff_comment": staff_comment,
            },
        )


from django.db.models import Avg, Sum
from .report_text import report_text
from django.db.models import Q


def calculate_stress_load(factors):
    """
    Calculate stress load percentage based on given factors.

    Args:
        factors (list): A list of dictionaries, each containing a 'val' key with counts.

    Returns:
        float: Stress load percentage.
    """
    if not factors or not isinstance(factors, list):  # Ensure valid data
        return 0

    medium = high = very_high = total = 0

    for factor in factors:
        if isinstance(factor, dict) and "val" in factor:
            val = factor["val"]  # Extract 'val' dictionary

            # Convert values to integers safely
            medium += int(val.get("medium_count", 0) or 0)
            high += int(val.get("high_count", 0) or 0)
            very_high += int(val.get("very_high", 0) or 0)

            total += sum(
                int(value)
                for value in val.values()
                if isinstance(value, int) or str(value).isdigit()
            )

    if total == 0:  # Avoid division by zero
        return 0

    stress_load = ((medium + high + very_high) / total) * 100
    return round(stress_load, 2)  # Return rounded percentage


def view_company_results(request, id):

    team = request.GET.get("team")

    query = Q(company_id=id)
    if team:
        query &= Q(response__employee__team=team)

    result = BessieResult.objects.filter(query).aggregate(
        environment=Avg("environment", default=0),
        residence=Avg("residence", default=0),
        privacy=Avg("privacy", default=0),
        privacy_multiplier=Avg("privacy_multiplier", default=0),
        travel_to_work=Avg("travel_to_work", default=0),
        pay=Avg("pay", default=0),
        pay_and_childcare_multiplier=Avg("pay_and_childcare_multiplier", default=0),
        pay_multiplier=Avg("pay_multiplier", default=0),
        complexity=Avg("complexity", default=0),
        hours_and_flexibility=Avg("hours_and_flexibility", default=0),
        control_and_autonomy_over_working_hours=Avg(
            "control_and_autonomy_over_working_hours", default=0
        ),
        workload=Avg("workload", default=0),
        manageable_workload=Avg("manageable_workload", default=0),
        complexity_plus_training=Avg("complexity_plus_training", default=0),
        complexity_training_hours_and_flexibility=Avg(
            "complexity_training_hours_and_flexibility", default=0
        ),
        work_breaks=Avg("work_breaks", default=0),
        overtime=Avg("overtime", default=0),
        team_and_colleague_support=Avg("team_and_colleague_support", default=0),
        management_support=Avg("management_support", default=0),
        management_support_multiplier=Avg("management_support_multiplier", default=0),
        team_and_colleague_support_multiplier=Avg(
            "team_and_colleague_support_multiplier", default=0
        ),
        training=Avg("training", default=0),
        training_multiplier=Avg("training_multiplier", default=0),
        culture=Avg("culture", default=0),
        managerial_trust=Avg("managerial_trust", default=0),
        colleague_trust=Avg("colleague_trust", default=0),
        consultation=Avg("consultation", default=0),
        team_morale=Avg("team_morale", default=0),
        willingness_to_progress=Avg("willingness_to_progress", default=0),
        culture_multiplier=Avg("culture_multiplier", default=0),
        lone_working=Avg("lone_working", default=0),
        wider_team_support=Avg("wider_team_support", default=0),
        lone_working_and_wider_team_support_multiplier=Avg(
            "lone_working_and_wider_team_support_multiplier", default=0
        ),
        health_and_safety=Avg("health_and_safety", default=0),
        health_and_safety_multiplier=Avg("health_and_safety_multiplier", default=0),
        absence=Avg("absence", default=0),
        sick_leave_and_employer_support=Avg(
            "sick_leave_and_employer_support", default=0
        ),
        absence_and_support=Avg("absence_and_support", default=0),
        absence_multiplier=Avg("absence_multiplier", default=0),
        covid=Avg("covid", default=0),
        covid_multiplier=Avg("covid_multiplier", default=0),
        work_related_stress_impacting_family_and_relationships=Avg(
            "work_related_stress_impacting_family_and_relationships", default=0
        ),
        environment_multiplier=Avg("environment_multiplier", default=0),
        work_related_stress_impacting_social_life=Avg(
            "work_related_stress_impacting_social_life", default=0
        ),
        work_related_stress_impacting_personal_life=Avg(
            "work_related_stress_impacting_personal_life", default=0
        ),
        family=Avg("family", default=0),
        family_multiplier=Avg("family_multiplier", default=0),
        family_support_companion=Avg("family_support_companion", default=0),
        responsibility_of_children=Avg("responsibility_of_children", default=0),
        responsibility_for_children_multiplier=Avg(
            "responsibility_for_children_multiplier", default=0
        ),
        support_network=Avg("support_network", default=0),
        support_network_multiplier=Avg("support_network_multiplier", default=0),
        childcare=Avg("childcare", default=0),
        childcare_multiplier=Avg("childcare_multiplier", default=0),
        responsibility_for_family=Avg("responsibility_for_family", default=0),
        family_factors=Avg("family_factors", default=0),
        health=Avg("health", default=0),
        physical_health_condition_affecting_work=Avg(
            "physical_health_condition_affecting_work", default=0
        ),
        physical_health_factors_impacting_work=Avg(
            "physical_health_factors_impacting_work", default=0
        ),
        mental_health_factors_impacting_work=Avg(
            "mental_health_factors_impacting_work", default=0
        ),
        physical_health=Avg("physical_health", default=0),
        physical_health_multiplier=Avg("physical_health_multiplier", default=0),
        physical_health_and_absence_multiplier=Avg(
            "physical_health_and_absence_multiplier", default=0
        ),
        physical_health_and_management_support_multiplier=Avg(
            "physical_health_and_management_support_multiplier", default=0
        ),
        physical_health_and_culture=Avg("physical_health_and_culture", default=0),
        mental_health=Avg("mental_health", default=0),
        mental_and_physical_health=Avg("mental_and_physical_health", default=0),
        mental_and_physical_health_multiplier=Avg(
            "mental_and_physical_health_multiplier", default=0
        ),
        mental_and_physical_health_and_absence_from_work=Avg(
            "mental_and_physical_health_and_absence_from_work", default=0
        ),
        mental_health_and_absence_multiplier=Avg(
            "mental_health_and_absence_multiplier", default=0
        ),
        mental_health_and_culture_multiplier=Avg(
            "mental_health_and_culture_multiplier", default=0
        ),
        mental_health_physical_health_and_culture_multiplier=Avg(
            "mental_health_physical_health_and_culture_multiplier", default=0
        ),
        mental_health_multiplier=Avg("mental_health_multiplier", default=0),
        fertility_and_pregnancy=Avg("fertility_and_pregnancy", default=0),
        fertility_and_pregnancy_impacting_work=Avg(
            "fertility_and_pregnancy_impacting_work", default=0
        ),
        pregnancy_impact=Avg("pregnancy_impact", default=0),
        pregnancy_and_management_support=Avg(
            "pregnancy_and_management_support", default=0
        ),
        abuse_and_trauma=Avg("abuse_and_trauma", default=0),
        abuse_and_trauma_impact=Avg("abuse_and_trauma_impact", default=0),
        abuse_and_trauma_and_management_support_multiplier=Avg(
            "abuse_and_trauma_and_management_support_multiplier", default=0
        ),
        abuse_and_trauma_and_management_support_and_culture=Avg(
            "abuse_and_trauma_and_management_support_and_culture", default=0
        ),
        pregnancy_and_mental_health=Avg("pregnancy_and_mental_health", default=0),
        pregnancy_and_physical_health=Avg("pregnancy_and_physical_health", default=0),
        self_care=Avg("self_care", default=0),
        self_care_and_physical_health=Avg("self_care_and_physical_health", default=0),
        self_care_and_mental_health=Avg("self_care_and_mental_health", default=0),
        personal=Avg("personal", default=0),
        identity=Avg("identity", default=0),
        identity_and_management_support=Avg(
            "identity_and_management_support", default=0
        ),
        discrimination=Avg("discrimination", default=0),
        discrimination_work_impact=Avg("discrimination_work_impact", default=0),
        age_discrimination=Avg("age_discrimination", default=0),
        race_discrimination=Avg("race_discrimination", default=0),
        disability_discrimination=Avg("disability_discrimination", default=0),
        gender_discrimination=Avg("gender_discrimination", default=0),
        sexual_discrimination=Avg("sexual_discrimination", default=0),
        other_discrimination=Avg("other_discrimination", default=0),
        carer=Avg("carer", default=0),
        personal_relationships=Avg("personal_relationships", default=0),
        personal_relationships_and_working_relationships_impact=Avg(
            "personal_relationships_and_working_relationships_impact", default=0
        ),
        problem_solving=Avg("problem_solving", default=0),
        personal_finances=Avg("personal_finances", default=0),
        personal_finances_and_responsibility_for_children=Avg(
            "personal_finances_and_responsibility_for_children", default=0
        ),
        personal_finances_and_pay_multiplier=Avg(
            "personal_finances_and_pay_multiplier", default=0
        ),
        personal_finances_and_pay_and_childcare_multiplier=Avg(
            "personal_finances_and_pay_and_childcare_multiplier", default=0
        ),
        hobbies=Avg("hobbies", default=0),
        personal_barriers=Avg("personal_barriers", default=0),
        financial_position_as_a_barrier_for_holidays=Avg(
            "financial_position_as_a_barrier_for_holidays", default=0
        ),
        work_commitments_as_a_barrier_for_holidays=Avg(
            "work_commitments_as_a_barrier_for_holidays", default=0
        ),
        holidays=Avg("holidays", default=0),
        holidays_and_pay=Avg("holidays_and_pay", default=0),
        personal_satisfaction=Avg("personal_satisfaction", default=0),
        personal_satisfaction_improvement=Avg(
            "personal_satisfaction_improvement", default=0
        ),
        emotional_health=Avg("emotional_health", default=0),
        emotional_health_multiplier=Avg("emotional_health_multiplier", default=0),
        emotional_distress=Avg("emotional_distress", default=0),
        emotional_distress_multiplier=Avg("emotional_distress_multiplier", default=0),
        emotional_wellbeing=Avg("emotional_wellbeing", default=0),
        emotional_wellbeing_and_management_support=Avg(
            "emotional_wellbeing_and_management_support", default=0
        ),
        emotional_health_and_culture_at_work=Avg(
            "emotional_health_and_culture_at_work", default=0
        ),
        personal_multiplier=Avg("personal_multiplier", default=0),
        emotional_wellbeing_multiplier=Avg("emotional_wellbeing_multiplier", default=0),
        potential_cost=Sum("potential_cost", default=0),
    )

    texts = {}

    for key, value in result.items():
        cat = get_category(value)
        pres = report_text.get(key)
        if pres:
            texts[key] = {"content": report_text[key][cat]["team"], "category": cat}
            texts[f"{key}_overview"] = report_text[key]["overview"]

    stats = get_field_statistics(id, team)

    res = read_result(result)
    stats = read_result(stats)

    environment_stressload = calculate_stress_load(stats.get("environment", []))
    health_stressload = calculate_stress_load(stats.get("health", []))
    family_stressload = calculate_stress_load(stats.get("family", []))
    personal_stressload = calculate_stress_load(stats.get("personal", []))

    return render(
        request,
        "bessie/company_results.html",
        {
            "stress_and_wellbeing": json.dumps(res["stress_and_wellbeing"]),
            "stress_risks_affecting_work": json.dumps(
                res["stress_risks_affecting_work"]
            ),
            "workplace_stress_factors": json.dumps(res["workplace_stress_factors"]),
            "presenteeism_factors": json.dumps(res["presenteeism"]),
            "environment_factors": json.dumps(res["environment"]),
            "family_factors": json.dumps(res["family"]),
            "health_factors": json.dumps(res["health"]),
            "personal_factors": json.dumps(res["personal"]),
            "environment_factors_stats": json.dumps(stats["environment"]),
            "health_factors_stats": json.dumps(stats["health"]),
            "family_factors_stats": json.dumps(stats["family"]),
            "personal_factors_stats": json.dumps(stats["personal"]),
            "report_text": json.dumps(texts),
            "environment_stressload": environment_stressload,
            "health_stressload": health_stressload,
            "family_stressload": family_stressload,
            "personal_stressload": personal_stressload,
            "potential_cost": round(result["potential_cost"]),
        },
    )


def user_list(request, id):
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


def read_result(res: BessieResult):

    stress_and_wellbeing = {}
    workplace_stress_factors = {}
    stress_risks_affecting_work = {}
    presenteeism = {}
    environment = {}
    family = {}
    health = {}
    personal = {}

    stress_and_wellbeing["emotional_distress"] = res["emotional_distress"]
    stress_and_wellbeing["emotional_health"] = res["emotional_health"]
    stress_and_wellbeing["mental_health"] = res["mental_health"]
    stress_and_wellbeing["physical_health"] = res["physical_health"]
    stress_and_wellbeing["self_care"] = res["self_care"]

    workplace_stress_factors["absence"] = res["absence"]
    workplace_stress_factors["carer"] = res["carer"]
    workplace_stress_factors["childcare"] = res["childcare"]
    workplace_stress_factors["complexity"] = res["complexity"]
    workplace_stress_factors["covid"] = res["covid"]
    workplace_stress_factors["culture"] = res["culture"]
    workplace_stress_factors["discrimination"] = res["discrimination"]
    workplace_stress_factors["health_and_safety"] = res["health_and_safety"]
    workplace_stress_factors["hours_and_flexibility"] = res["hours_and_flexibility"]
    workplace_stress_factors["management_support"] = res["management_support"]
    workplace_stress_factors["pay"] = res["pay"]
    workplace_stress_factors["personal_finances"] = res["personal_finances"]
    workplace_stress_factors["training"] = res["training"]
    workplace_stress_factors["workload"] = res["workload"]

    stress_risks_affecting_work["absence_multiplier"] = res["absence_multiplier"]
    stress_risks_affecting_work[
        "abuse_and_trauma_and_management_support_multiplier"
    ] = res["abuse_and_trauma_and_management_support_multiplier"]
    stress_risks_affecting_work["childcare_multiplier"] = res["childcare_multiplier"]
    stress_risks_affecting_work["covid_multiplier"] = res["covid_multiplier"]
    stress_risks_affecting_work["culture_multiplier"] = res["culture_multiplier"]
    stress_risks_affecting_work["emotional_distress_multiplier"] = res[
        "emotional_distress_multiplier"
    ]
    stress_risks_affecting_work["emotional_health_multiplier"] = res[
        "emotional_health_multiplier"
    ]
    stress_risks_affecting_work["emotional_wellbeing_multiplier"] = res[
        "emotional_wellbeing_multiplier"
    ]
    stress_risks_affecting_work["environment_multiplier"] = res[
        "environment_multiplier"
    ]
    stress_risks_affecting_work["family_multiplier"] = res["family_multiplier"]
    stress_risks_affecting_work["health_and_safety_multiplier"] = res[
        "health_and_safety_multiplier"
    ]
    stress_risks_affecting_work["lone_working_and_wider_team_support_multiplier"] = res[
        "lone_working_and_wider_team_support_multiplier"
    ]
    stress_risks_affecting_work["management_support_multiplier"] = res[
        "management_support_multiplier"
    ]
    stress_risks_affecting_work["mental_and_physical_health_multiplier"] = res[
        "mental_and_physical_health_multiplier"
    ]
    stress_risks_affecting_work["mental_health_and_absence_multiplier"] = res[
        "mental_health_and_absence_multiplier"
    ]
    stress_risks_affecting_work["mental_health_and_culture_multiplier"] = res[
        "mental_health_and_culture_multiplier"
    ]
    stress_risks_affecting_work["mental_health_multiplier"] = res[
        "mental_health_multiplier"
    ]
    stress_risks_affecting_work[
        "mental_health_physical_health_and_culture_multiplier"
    ] = res["mental_health_physical_health_and_culture_multiplier"]
    stress_risks_affecting_work["pay_and_childcare_multiplier"] = res[
        "pay_and_childcare_multiplier"
    ]
    stress_risks_affecting_work["pay_multiplier"] = res["pay_multiplier"]
    stress_risks_affecting_work[
        "personal_finances_and_pay_and_childcare_multiplier"
    ] = res["personal_finances_and_pay_and_childcare_multiplier"]
    stress_risks_affecting_work["personal_finances_and_pay_multiplier"] = res[
        "personal_finances_and_pay_multiplier"
    ]
    stress_risks_affecting_work["personal_multiplier"] = res["personal_multiplier"]
    stress_risks_affecting_work["physical_health_and_absence_multiplier"] = res[
        "physical_health_and_absence_multiplier"
    ]
    stress_risks_affecting_work["physical_health_and_management_support_multiplier"] = (
        res["physical_health_and_management_support_multiplier"]
    )
    stress_risks_affecting_work["physical_health_multiplier"] = res[
        "physical_health_multiplier"
    ]
    stress_risks_affecting_work["privacy_multiplier"] = res["privacy_multiplier"]
    stress_risks_affecting_work["responsibility_for_children_multiplier"] = res[
        "responsibility_for_children_multiplier"
    ]
    stress_risks_affecting_work["support_network_multiplier"] = res[
        "support_network_multiplier"
    ]
    stress_risks_affecting_work["team_and_colleague_support"] = res[
        "team_and_colleague_support"
    ]
    stress_risks_affecting_work["training_multiplier"] = res["training_multiplier"]

    environment["absence"] = res["absence"]
    environment["absence_and_support"] = res["absence_and_support"]
    environment["absence_multiplier"] = res["absence_multiplier"]
    environment["colleague_trust"] = res["colleague_trust"]
    environment["complexity"] = res["complexity"]
    environment["complexity_training_hours_and_flexibility"] = res[
        "complexity_training_hours_and_flexibility"
    ]
    environment["complexity_plus_training"] = res["complexity_plus_training"]
    environment["consultation"] = res["consultation"]
    environment["control_and_autonomy_over_working_hours"] = res[
        "control_and_autonomy_over_working_hours"
    ]
    environment["covid"] = res["covid"]
    environment["covid_multiplier"] = res["covid_multiplier"]
    environment["culture_multiplier"] = res["culture_multiplier"]
    environment["culture"] = res["culture"]
    environment["environment"] = res["environment"]
    environment["environment_multiplier"] = res["environment_multiplier"]
    environment["health_and_safety"] = res["health_and_safety"]
    environment["health_and_safety_multiplier"] = res["health_and_safety_multiplier"]
    environment["hours_and_flexibility"] = res["hours_and_flexibility"]
    environment["lone_working"] = res["lone_working"]
    environment["lone_working_and_wider_team_support_multiplier"] = res[
        "lone_working_and_wider_team_support_multiplier"
    ]
    environment["management_support"] = res["management_support"]
    environment["management_support_multiplier"] = res["management_support_multiplier"]
    environment["managerial_trust"] = res["managerial_trust"]
    environment["overtime"] = res["overtime"]
    environment["pay"] = res["pay"]
    environment["pay_and_childcare_multiplier"] = res["pay_and_childcare_multiplier"]
    environment["pay_multiplier"] = res["pay_multiplier"]
    environment["privacy"] = res["privacy"]
    environment["privacy_multiplier"] = res["privacy_multiplier"]
    environment["residence"] = res["residence"]
    environment["sick_leave_and_employer_support"] = res[
        "sick_leave_and_employer_support"
    ]
    environment["team_and_colleague_support"] = res["team_and_colleague_support"]
    environment["team_and_colleague_support_multiplier"] = res[
        "team_and_colleague_support_multiplier"
    ]
    environment["team_morale"] = res["team_morale"]
    environment["training"] = res["training"]
    environment["training_multiplier"] = res["training_multiplier"]
    environment["travel_to_work"] = res["travel_to_work"]
    environment["wider_team_support"] = res["wider_team_support"]
    environment["willingness_to_progress"] = res["willingness_to_progress"]
    environment["work_breaks"] = res["work_breaks"]
    environment["work_related_stress_impacting_family_and_relationships"] = res[
        "work_related_stress_impacting_family_and_relationships"
    ]
    environment["work_related_stress_impacting_personal_life"] = res[
        "work_related_stress_impacting_personal_life"
    ]
    environment["work_related_stress_impacting_social_life"] = res[
        "work_related_stress_impacting_social_life"
    ]
    environment["workload"] = res["workload"]
    environment["manageable_workload"] = res["manageable_workload"]

    presenteeism["control_and_autonomy_over_working_hours"] = res[
        "control_and_autonomy_over_working_hours"
    ]
    presenteeism["fertility_and_pregnancy_impacting_work"] = res[
        "fertility_and_pregnancy_impacting_work"
    ]
    presenteeism["financial_position_as_a_barrier_for_holidays"] = res[
        "financial_position_as_a_barrier_for_holidays"
    ]
    presenteeism["manageable_workload"] = res["manageable_workload"]
    presenteeism["management_support"] = res["management_support"]
    presenteeism["mental_health"] = res["mental_health"]
    presenteeism["mental_health_factors_impacting_work"] = res[
        "mental_health_factors_impacting_work"
    ]
    presenteeism["overtime"] = res["overtime"]
    presenteeism["physical_health"] = res["physical_health"]
    presenteeism["physical_health_factors_impacting_work"] = res[
        "physical_health_factors_impacting_work"
    ]
    presenteeism["sick_leave_and_employer_support"] = res[
        "sick_leave_and_employer_support"
    ]
    presenteeism["work_breaks"] = res["work_breaks"]
    presenteeism["work_commitments_as_a_barrier_for_holidays"] = res[
        "work_commitments_as_a_barrier_for_holidays"
    ]

    family["childcare"] = res["childcare"]
    family["childcare_multiplier"] = res["childcare_multiplier"]
    family["family"] = res["family"]
    family["family_factors"] = res["family_factors"]
    family["family_multiplier"] = res["family_multiplier"]
    family["family_support_companion"] = res["family_support_companion"]
    family["responsibility_for_children_multiplier"] = res[
        "responsibility_for_children_multiplier"
    ]
    family["responsibility_for_family"] = res["responsibility_for_family"]
    family["responsibility_of_children"] = res["responsibility_of_children"]
    family["support_network"] = res["support_network"]
    family["support_network_multiplier"] = res["support_network_multiplier"]

    health["abuse_and_trauma"] = res["abuse_and_trauma"]
    health["abuse_and_trauma_and_management_support_and_culture"] = res[
        "abuse_and_trauma_and_management_support_and_culture"
    ]
    health["abuse_and_trauma_and_management_support_multiplier"] = res[
        "abuse_and_trauma_and_management_support_multiplier"
    ]
    health["abuse_and_trauma_impact"] = res["abuse_and_trauma_impact"]
    health["fertility_and_pregnancy"] = res["fertility_and_pregnancy"]
    health["fertility_and_pregnancy_impacting_work"] = res[
        "fertility_and_pregnancy_impacting_work"
    ]
    health["health"] = res["health"]
    health["mental_and_physical_health"] = res["mental_and_physical_health"]
    health["mental_and_physical_health_and_absence_from_work"] = res[
        "mental_and_physical_health_and_absence_from_work"
    ]
    health["mental_and_physical_health_multiplier"] = res[
        "mental_and_physical_health_multiplier"
    ]
    health["mental_health"] = res["mental_health"]
    health["mental_health_and_absence_multiplier"] = res[
        "mental_health_and_absence_multiplier"
    ]
    health["mental_health_and_culture_multiplier"] = res[
        "mental_health_and_culture_multiplier"
    ]
    health["mental_health_factors_impacting_work"] = res[
        "mental_health_factors_impacting_work"
    ]
    health["mental_health_multiplier"] = res["mental_health_multiplier"]
    health["mental_health_physical_health_and_culture_multiplier"] = res[
        "mental_health_physical_health_and_culture_multiplier"
    ]
    health["physical_health"] = res["physical_health"]
    health["physical_health_and_absence_multiplier"] = res[
        "physical_health_and_absence_multiplier"
    ]
    health["physical_health_and_culture"] = res["physical_health_and_culture"]
    health["physical_health_and_management_support_multiplier"] = res[
        "physical_health_and_management_support_multiplier"
    ]
    health["physical_health_condition_affecting_work"] = res[
        "physical_health_condition_affecting_work"
    ]
    health["physical_health_multiplier"] = res["physical_health_multiplier"]
    health["pregnancy_and_management_support"] = res["pregnancy_and_management_support"]
    health["pregnancy_and_physical_health"] = res["pregnancy_and_physical_health"]
    health["pregnancy_and_mental_health"] = res["pregnancy_and_mental_health"]
    health["pregnancy_impact"] = res["pregnancy_impact"]
    health["self_care"] = res["self_care"]
    health["self_care_and_mental_health"] = res["self_care_and_mental_health"]
    health["self_care_and_physical_health"] = res["self_care_and_physical_health"]

    personal["age_discrimination"] = res["age_discrimination"]
    personal["carer"] = res["carer"]
    personal["disability_discrimination"] = res["disability_discrimination"]
    personal["discrimination"] = res["discrimination"]
    personal["discrimination_work_impact"] = res["discrimination_work_impact"]
    personal["emotional_distress"] = res["emotional_distress"]
    personal["emotional_distress_multiplier"] = res["emotional_distress_multiplier"]
    personal["emotional_health"] = res["emotional_health"]
    personal["emotional_health_and_culture_at_work"] = res[
        "emotional_health_and_culture_at_work"
    ]
    personal["emotional_health_multiplier"] = res["emotional_health_multiplier"]
    personal["emotional_wellbeing"] = res["emotional_wellbeing"]
    personal["emotional_wellbeing_and_management_support"] = res[
        "emotional_wellbeing_and_management_support"
    ]
    personal["emotional_wellbeing_multiplier"] = res["emotional_wellbeing_multiplier"]
    personal["financial_position_as_a_barrier_for_holidays"] = res[
        "financial_position_as_a_barrier_for_holidays"
    ]
    personal["gender_discrimination"] = res["gender_discrimination"]
    personal["hobbies"] = res["hobbies"]
    personal["holidays"] = res["holidays"]
    personal["holidays_and_pay"] = res["holidays_and_pay"]
    personal["identity"] = res["identity"]
    personal["identity_and_management_support"] = res["identity_and_management_support"]
    personal["other_discrimination"] = res["other_discrimination"]
    personal["personal"] = res["personal"]
    personal["personal_barriers"] = res["personal_barriers"]
    personal["personal_finances"] = res["personal_finances"]
    personal["personal_finances_and_pay_and_childcare_multiplier"] = res[
        "personal_finances_and_pay_and_childcare_multiplier"
    ]
    personal["personal_finances_and_pay_multiplier"] = res[
        "personal_finances_and_pay_multiplier"
    ]
    personal["personal_finances_and_responsibility_for_children"] = res[
        "personal_finances_and_responsibility_for_children"
    ]
    personal["personal_multiplier"] = res["personal_multiplier"]
    personal["personal_relationships"] = res["personal_relationships"]
    personal["personal_relationships_and_working_relationships_impact"] = res[
        "personal_relationships_and_working_relationships_impact"
    ]
    personal["personal_satisfaction"] = res["personal_satisfaction"]
    personal["personal_satisfaction_improvement"] = res[
        "personal_satisfaction_improvement"
    ]
    personal["problem_solving"] = res["problem_solving"]
    personal["race_discrimination"] = res["race_discrimination"]
    personal["sexual_discrimination"] = res["sexual_discrimination"]
    personal["work_commitments_as_a_barrier_for_holidays"] = res[
        "work_commitments_as_a_barrier_for_holidays"
    ]

    return {
        "stress_and_wellbeing": [
            {"attr": key, "val": value} for key, value in stress_and_wellbeing.items()
        ],
        "workplace_stress_factors": [
            {"attr": key, "val": value}
            for key, value in workplace_stress_factors.items()
        ],
        "stress_risks_affecting_work": [
            {"attr": key, "val": value}
            for key, value in stress_risks_affecting_work.items()
        ],
        "presenteeism": [
            {"attr": key, "val": value} for key, value in presenteeism.items()
        ],
        "environment": [
            {"attr": key, "val": value} for key, value in environment.items()
        ],
        "family": [{"attr": key, "val": value} for key, value in family.items()],
        "health": [{"attr": key, "val": value} for key, value in health.items()],
        "personal": [{"attr": key, "val": value} for key, value in personal.items()],
    }


from django.db.models import Case, When, Value, IntegerField, Count, CharField
from django.db.models.functions import Concat
from django.forms.models import model_to_dict


def get_field_statistics(companyId, team=None):
    # List of all fields we want to analyze
    query = Q(company_id=companyId)
    if team:
        query &= Q(response__employee__team=team)
    fields = [
        "environment",
        "residence",
        "privacy",
        "privacy_multiplier",
        "travel_to_work",
        "pay",
        "pay_and_childcare_multiplier",
        "pay_multiplier",
        "complexity",
        "hours_and_flexibility",
        "control_and_autonomy_over_working_hours",
        "workload",
        "manageable_workload",
        "complexity_plus_training",
        "complexity_training_hours_and_flexibility",
        "work_breaks",
        "overtime",
        "team_and_colleague_support",
        "management_support",
        "management_support_multiplier",
        "team_and_colleague_support_multiplier",
        "training",
        "training_multiplier",
        "culture",
        "managerial_trust",
        "colleague_trust",
        "consultation",
        "team_morale",
        "willingness_to_progress",
        "culture_multiplier",
        "lone_working",
        "wider_team_support",
        "lone_working_and_wider_team_support_multiplier",
        "health_and_safety",
        "health_and_safety_multiplier",
        "absence",
        "sick_leave_and_employer_support",
        "absence_and_support",
        "absence_multiplier",
        "covid",
        "covid_multiplier",
        "work_related_stress_impacting_family_and_relationships",
        "environment_multiplier",
        "work_related_stress_impacting_social_life",
        "work_related_stress_impacting_personal_life",
        "family",
        "family_multiplier",
        "family_support_companion",
        "responsibility_of_children",
        "responsibility_for_children_multiplier",
        "support_network",
        "support_network_multiplier",
        "childcare",
        "childcare_multiplier",
        "responsibility_for_family",
        "family_factors",
        "health",
        "physical_health_condition_affecting_work",
        "physical_health_factors_impacting_work",
        "mental_health_factors_impacting_work",
        "physical_health",
        "physical_health_multiplier",
        "physical_health_and_absence_multiplier",
        "physical_health_and_management_support_multiplier",
        "physical_health_and_culture",
        "mental_health",
        "mental_and_physical_health",
        "mental_and_physical_health_multiplier",
        "mental_and_physical_health_and_absence_from_work",
        "mental_health_and_absence_multiplier",
        "mental_health_and_culture_multiplier",
        "mental_health_physical_health_and_culture_multiplier",
        "mental_health_multiplier",
        "fertility_and_pregnancy",
        "fertility_and_pregnancy_impacting_work",
        "pregnancy_impact",
        "pregnancy_and_management_support",
        "abuse_and_trauma",
        "abuse_and_trauma_impact",
        "abuse_and_trauma_and_management_support_multiplier",
        "abuse_and_trauma_and_management_support_and_culture",
        "pregnancy_and_mental_health",
        "pregnancy_and_physical_health",
        "self_care",
        "self_care_and_physical_health",
        "self_care_and_mental_health",
        "personal",
        "identity",
        "identity_and_management_support",
        "discrimination",
        "discrimination_work_impact",
        "age_discrimination",
        "race_discrimination",
        "disability_discrimination",
        "gender_discrimination",
        "sexual_discrimination",
        "other_discrimination",
        "carer",
        "personal_relationships",
        "personal_relationships_and_working_relationships_impact",
        "problem_solving",
        "personal_finances",
        "personal_finances_and_responsibility_for_children",
        "personal_finances_and_pay_multiplier",
        "personal_finances_and_pay_and_childcare_multiplier",
        "hobbies",
        "personal_barriers",
        "financial_position_as_a_barrier_for_holidays",
        "work_commitments_as_a_barrier_for_holidays",
        "holidays",
        "holidays_and_pay",
        "personal_satisfaction",
        "personal_satisfaction_improvement",
        "emotional_health",
        "emotional_health_multiplier",
        "emotional_distress",
        "emotional_distress_multiplier",
        "emotional_wellbeing",
        "emotional_wellbeing_and_management_support",
        "emotional_health_and_culture_at_work",
        "personal_multiplier",
        "emotional_wellbeing_multiplier",
    ]

    # Build the statistics for each field
    result = {}

    for field in fields:
        stats = (
            BessieResult.objects.filter(query)
            .annotate(field_name=Value(field, output_field=CharField()))
            .values("field_name")
            .annotate(
                low_count=Count(
                    Case(
                        When(**{f"{field}__lte": 25.0}, then=1),
                        output_field=IntegerField(),
                    )
                ),
                medium_count=Count(
                    Case(
                        When(**{f"{field}__gt": 25.0, f"{field}__lte": 50.0}, then=1),
                        output_field=IntegerField(),
                    )
                ),
                high_count=Count(
                    Case(
                        When(**{f"{field}__gt": 50.0, f"{field}__lte": 75.0}, then=1),
                        output_field=IntegerField(),
                    )
                ),
                very_high_count=Count(
                    Case(
                        When(**{f"{field}__gt": 75.0}, then=1),
                        output_field=IntegerField(),
                    )
                ),
            )
        )
        result[field] = {
            "low_count": stats[0]["low_count"],
            "medium_count": stats[0]["medium_count"],
            "high_count": stats[0]["high_count"],
            "very_high": stats[0]["very_high_count"],
        }

    return result


def get_category(value):
    if value <= 25.0:
        return "low"
    elif value <= 50.0:
        return "medium"
    elif value <= 75.0:
        return "high"
    else:
        return "very_high"


def export_data(request, id):
    """
    Export employee data (their scores and calculations) to a csv file
    """
    employee = Employee.objects.get(pk=id)
    bessie_response = BessieResponse.objects.get(employee=employee)
    sorted_questions = bessie_response.get_sorted_questions()

    bessie_result = BessieResult.objects.get(response=bessie_response)
    result = model_to_dict(bessie_result)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="employee_{id}_data.csv"'

    writer = csv.writer(response)
    writer.writerow(["Question", "Score"])
    for question, answer in sorted_questions.items():
        writer.writerow([question, answer])

    writer.writerow([""])
    writer.writerow(["--------------------------------"])
    writer.writerow([""])

    writer.writerow(["Category", "Score"])
    for key, value in result.items():
        formatted_key = key.replace("_", " ").capitalize()
        writer.writerow([formatted_key, value])

    return response
