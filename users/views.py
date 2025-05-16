import csv
import os
import pandas as pd
from django.shortcuts import redirect
from .forms import BulkUserInviteForm
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from formtools.wizard.views import SessionWizardView
from django.contrib.auth import login
from bessie.models import Company
from .tasks import process_csv_chunk
from bessie.models import EmployeeProcessTask
from django.http import HttpResponse
from django.contrib import messages


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
      file = pd.read_csv(csv_file)
      row_count = len(file) - 1

      if company.slots < row_count:
        messages.error(
            request,
            f"You don't have enough slots to invite {row_count} employees.",
        )
        return redirect("dashboard")

      folder_name = company.name.replace(" ", "_").lower()
      upload_dir = os.path.join(settings.MEDIA_ROOT, 'csv_chunks', folder_name)
      os.makedirs(upload_dir, exist_ok=True)

      file_path = os.path.join(upload_dir, csv_file.name)

      with open(file_path, "wb+") as destination:
        for chunk in csv_file.chunks():
          destination.write(chunk)

      chunk_paths = []
      for i, chunk in enumerate(pd.read_csv(file_path, chunksize=10)):
        chunk_path = os.path.join(upload_dir, f'chunk_{i}.csv')
        chunk.to_csv(chunk_path, index=False)
        chunk_paths.append(chunk_path)

      os.remove(file_path)

      job = EmployeeProcessTask.objects.create(
        job_id=timezone.now().timestamp(),
        company=company,
        chunks_number=len(chunk_paths),
        chunks_completed=0,
        notification_email=request.user.email,
        completed=False
      )

      for chunk_path in chunk_paths:
        process_csv_chunk(chunk_path, job.pk)

  messages.success(
    request, f"File uploaded successfully for processing. You will receive an email when it's done."
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
