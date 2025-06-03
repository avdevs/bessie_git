from django.db import migrations
from django.utils import timezone
from time import sleep
import random


def generate_unique_ids(apps, schema_editor):
	"""Generate unique IDs for existing employee records."""
	Employee = apps.get_model("bessie", "Employee")
	employees = Employee.objects.filter(unique_id__isnull=True)

	for employee in employees:
		sleep(0.2)

		unique_id = str(str(int(timezone.now().timestamp())) + str(random.randint(1, 100)))

		employee.unique_id = unique_id
		employee.save()


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
