import os
import random
from os.path import dirname, join
from time import sleep

from django.core.mail import send_mail
from django.db import migrations
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags
from dotenv import load_dotenv

# Load all environment variables
dotenv_path = join(dirname(__file__), "../../.env")
load_dotenv(dotenv_path)


def generate_unique_ids(apps, schema_editor):
	"""Generate unique IDs for all system users"""
	User = apps.get_model("users", "User")
	users = User.objects.filter(unique_id__isnull=True)

	DOMAIN = os.getenv("SITE_DOMAIN")
	link = f"{DOMAIN}/login"

	for user in users:
		sleep(0.2)

		unique_id = str(str(int(timezone.now().timestamp())) + str(random.randint(1, 100)))

		user.unique_id = unique_id
		user.save()

		print(f"\nSENDING EMAIL WITH MAGIC LINK TO {user.email}")

		html_message = render_to_string(
			"emails/login_change.html",
			{"url": link, "unique_id": unique_id},
		)

		plain_message = strip_tags(html_message)

		send_mail(
			subject="Bessie Login Change",
			message=plain_message,
			from_email=None,
			recipient_list=[user.email],
			html_message=html_message,
		)


def reverse_unique_ids(apps, schema_editor):
	"""Revert unique IDs to null."""
	User = apps.get_model("users", "User")
	User.objects.update(unique_id=None)


class Migration(migrations.Migration):
	dependencies = [
		("users", "0004_user_magic_link_expiry_user_magic_link_token_and_more"),
	]

	operations = [
		migrations.RunPython(generate_unique_ids, reverse_unique_ids),
	]
