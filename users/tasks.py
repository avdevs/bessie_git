from background_task import background
from django.core.mail import EmailMultiAlternatives, send_mail, get_connection
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.text import slugify
from django.utils.html import strip_tags
from bessie.models import Employee, EmployeeProcessTask
import csv
import os

from users.models import User


@background(schedule=5)
def process_csv_chunk(chunk_path, job_id):
  job = EmployeeProcessTask.objects.get(id=job_id)
  company = job.company

  existing_emails = set(User.objects.values_list("email", flat=True))
  users_to_create = []
  employees_to_create = []
  emails = []
  company_teams = set(company.teams)
  failed = []

  with open(chunk_path, 'r') as file:
    reader = csv.reader(file)
    next(reader)

    for row in reader:
      if row[2] in existing_emails:
        failed.append(row)
        continue

      # We need to keep django's user model in mind as admins and superusers will login normally,
      # Employees will login with a magic link, but to be able to use existing logics without major changes,
      # we need to create the user and set the password to a random value.
      try:
        password = User.objects.make_random_password()
        email = row[2].lower()

        user = User(
            first_name=row[0],
            last_name=row[1],
            email=email,
            user_type=User.UserTypes.EMPLOYEE,
        )
        user.set_password(password)
        users_to_create.append(user)

        team = slugify(row[3].strip()) if len(
          row) == 4 and row[3].strip() else ""

        if team:
          company_teams.add(team)

        employees_to_create.append(
          Employee(company=company, user=user, team=team or None)
        )

        subject = "Your Account Details"
        html_message = render_to_string(
            "emails/employee_invitation_email.html",
            {
                "user": user,
                "password": password,
                "login_url": "login_url",
                "company": company,
            },
        )
        plain_message = strip_tags(html_message)
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=None,
            to=email,
        )
        email.attach_alternative(html_message, "text/html")
        emails.append(email)
      except Exception as e:
        print(f"Error creating password: {e}")
        failed.append(row)
        continue

    os.remove(chunk_path)

    existing_teams = set(company.teams if company.teams else [])
    updated_teams = existing_teams.union(company_teams)
    company.teams = list(updated_teams)

  job.chunks_completed += 1
  job.save()

  User.objects.bulk_create(users_to_create)
  Employee.objects.bulk_create(employees_to_create)

  company.slots -= len(users_to_create)
  company.save()

  connection = get_connection()
  connection.send_messages(emails)

  if job.chunks_completed >= job.chunks_number:
    folder_name = company.name.replace(" ", "_").lower()
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'csv_chunks', folder_name)
    os.rmdir(upload_dir)

    send_completion_email(job.notification_email, company.name)


@background(schedule=5)
def send_completion_email(email, company_name):
  send_mail(
    'CSV Processing Complete',
    f'Your CSV file for company: {company_name} has been processed successfully.',
    'no_reply@bessiestressriskassessment.com',
    [email],
    fail_silently=False,
  )
