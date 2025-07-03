from django.db import migrations
from django.utils import timezone
from time import sleep
import os
from os.path import join, dirname
from dotenv import load_dotenv
import random
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail

# Load all environment variables
dotenv_path = join(dirname(__file__), "../.env")
load_dotenv(dotenv_path)


def generate_unique_ids(apps, schema_editor):
	"""Generate unique IDs for existing employee records."""
	Employee = apps.get_model("bessie", "Employee")
	employees = Employee.objects.filter(unique_id__isnull=True)

	DOMAIN = os.getenv("SITE_DOMAIN")
	link = f"{DOMAIN}/employee/login"

	for employee in employees:
		sleep(0.2)

		unique_id = str(str(int(timezone.now().timestamp())) + str(random.randint(1, 100)))

		employee.unique_id = unique_id
		employee.save()

		print("SENDING EMAIL TO EXISTING EMPLOYEE THAT WE CHANGED LOGIN SYSTEM")

		html_message = render_to_string(
			"emails/login_change.html",
			{"url": link, "unique_id": unique_id},
		)

		plain_message = strip_tags(html_message)

		send_mail(
			subject="Bessie Employee Login Change",
			message=plain_message,
			from_email=None,
			recipient_list=[employee.user.email],
			html_message=html_message,
		)


def reverse_unique_ids(apps, schema_editor):
	"""Revert unique IDs to null."""
	Employee = apps.get_model("bessie", "Employee")
	Employee.objects.update(unique_id=None)


class Migration(migrations.Migration):
	dependencies = [
		("bessie", "0017_employee_magic_link_expiry_employee_magic_link_token_and_more"),
	]

	operations = [
		migrations.RunPython(generate_unique_ids, reverse_unique_ids),
	]
