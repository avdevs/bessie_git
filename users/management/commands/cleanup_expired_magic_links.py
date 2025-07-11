from django.core.management.base import BaseCommand
from django.utils import timezone

from users.models import User


class Command(BaseCommand):
	help = "Clean up expired magic links for users"

	def handle(self, *args, **options):
		self.stdout.write("Running cleanup of expired magic links...")
		now = timezone.now()

		expired_users = User.objects.filter(
			magic_link_expiry__lt=now, magic_link_expiry__isnull=False
		)

		updated_count = expired_users.update(magic_link_expiry=None, magic_link_token=None)

		if updated_count > 0:
			self.stdout.write(
				self.style.SUCCESS(
					f"Successfully cleaned up {updated_count} expired magic links"
				)
			)
		else:
			self.stdout.write("No expired magic links found to clean up")
