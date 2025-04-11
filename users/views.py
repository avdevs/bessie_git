from django.shortcuts import redirect
from django.urls import reverse
from .forms import BulkUserInviteForm
from django.contrib import messages
from formtools.wizard.views import SessionWizardView
from django.contrib.auth import login
from bessie.models import Company, Employee, CompanyAdmin
from .models import User
from django.http import HttpResponse
from django.contrib import messages
from django.utils.text import slugify
from django.template.loader import render_to_string
from django.utils.html import strip_tags

import csv

import io
from django.core.mail import EmailMultiAlternatives, get_connection
from django.db import IntegrityError

import os
from pathlib import Path
from os.path import join, dirname
from dotenv import load_dotenv


def inviteUsers(request, id):
    # THIS IS FOR ADMIN USER TO UPLOAD EMPLOYEE CSV
    # comp_admin = CompanyAdmin.objects.get(user=request.user)
    # company = comp_admin.company

    # THIS IS SO SUPER ADMIN CAN UPLOAD EMPLOYEE CSV
    company = Company.objects.get(id=id)

    if request.method == "POST":
        form = BulkUserInviteForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES["csv_file"]
            decoded_file = csv_file.read().decode("utf-8")
            csv_data = csv.reader(io.StringIO(decoded_file))
            csv_list = list(csv_data)

            row_count = len(csv_list) - 1
            if company.slots < row_count:
                messages.error(
                    request,
                    f"You don't have enough slots to invite {row_count} employees.",
                )
                return redirect("dashboard")

            headers = csv_list[0]
            data_rows = csv_list[1:]
            print(data_rows)
            existing_emails = set(User.objects.values_list("email", flat=True))
            MIN_COLUMNS = 3  # Adjust based on your CSV structure
            data_rows = [
                data
                for data in data_rows
                if len(data) >= MIN_COLUMNS and data[2] not in existing_emails
            ]

            users_to_create = []
            employees_to_create = []
            emails = []
            company_teams = set(company.teams)

            login_url = request.build_absolute_uri(reverse("login"))

            for data in data_rows:
                try:
                    password = User.objects.make_random_password()
                    user = User(
                        first_name=data[0],
                        last_name=data[1],
                        email=data[2],
                        user_type=User.UserTypes.EMPLOYEE,
                    )
                    user.set_password(password)
                    users_to_create.append(user)

                    team = ""
                    if len(data) == 4:
                        team = slugify(data[3].strip())

                    if team:
                        if team not in company_teams:
                            company_teams.add(
                                team
                            )  # only one of these I think - will crash
                            # company.teams.append(team)  # only one of these I think - will crash
                        employees_to_create.append(
                            Employee(company=company, user=user, team=team)
                        )
                    else:
                        employees_to_create.append(Employee(company=company, user=user))

                    subject = "Your Account Details"
                    html_message = render_to_string(
                        "emails/employee_invitation_email.html",
                        {
                            "user": user,
                            "password": password,
                            "login_url": login_url,
                            "company": company,
                        },
                    )
                    plain_message = strip_tags(html_message)
                    email = EmailMultiAlternatives(
                        subject=subject,
                        body=plain_message,
                        from_email=None,
                        to=[data[2]],
                    )
                    email.attach_alternative(html_message, "text/html")
                    emails.append(email)
                except IntegrityError:
                    continue

            User.objects.bulk_create(users_to_create)
            Employee.objects.bulk_create(employees_to_create)
            company.slots -= len(users_to_create)
            company.save()

            # Send all emails in one connection
            connection = get_connection()
            connection.send_messages(emails)

            messages.success(
                request, f"File uploaded successfully. {len(data_rows)} rows found."
            )
            return redirect("dashboard")


def csvSample(request):

    response = HttpResponse(
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="data.csv"'},
    )

    # Create CSV writer
    writer = csv.writer(response)

    # Write header row
    writer.writerow(["FirstName", "LastName", "Email", "Team"])

    return response


class RegistrationWizard(SessionWizardView):
    template_name = "registration/signup_wizard.html"

    def done(self, form_list, **kwargs):

        if self.request.user.is_authenticated:
            messages.warning(self.request, "Your can't register while logged in.")
            return redirect("homepage")

        # Get the forms
        user_form = form_list[0]
        company_form = form_list[1]

        # Save the user first
        user = user_form.save()

        # Create company with user as owner
        company = company_form.save(commit=False)
        company.owner = user
        company.save()

        # Log the user in
        login(self.request, user)

        # Redirect to success page
        return redirect("upload_csv")
