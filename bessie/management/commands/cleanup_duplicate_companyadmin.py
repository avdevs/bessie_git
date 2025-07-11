from django.core.management.base import BaseCommand
from django.db import connection

from bessie.models import CompanyAdmin


class Command(BaseCommand):
	help = "Clean up duplicate CompanyAdmin records keeping only the first occurrence for each user_id"

	def handle(self, *args, **options):
		self.stdout.write("Starting cleanup of duplicate CompanyAdmin records...")

		# Find all user_ids that have duplicates
		with connection.cursor() as cursor:
			cursor.execute("""
                SELECT user_id, COUNT(*) as count
                FROM bessie_companyadmin 
                GROUP BY user_id 
                HAVING COUNT(*) > 1
            """)
			duplicates = cursor.fetchall()

		if not duplicates:
			self.stdout.write(self.style.SUCCESS("No duplicate records found."))
			return

		self.stdout.write(f"Found {len(duplicates)} users with duplicate records:")

		total_deleted = 0
		for user_id, count in duplicates:
			self.stdout.write(f"  User ID {user_id}: {count} records")

			# Get all records for this user_id, ordered by id
			duplicate_records = CompanyAdmin.objects.filter(user_id=user_id).order_by("id")

			# Keep the first record, delete the rest
			records_to_delete = duplicate_records[1:]
			deleted_count = len(records_to_delete)

			for record in records_to_delete:
				self.stdout.write(
					f"    Deleting record (User: {record.user}, Company: {record.company})"
				)
				record.delete()

			total_deleted += deleted_count

		self.stdout.write(
			self.style.SUCCESS(f"Successfully deleted {total_deleted} duplicate records.")
		)

		# Verify no duplicates remain
		with connection.cursor() as cursor:
			cursor.execute("""
                SELECT user_id, COUNT(*) 
                FROM bessie_companyadmin 
                GROUP BY user_id 
                HAVING COUNT(*) > 1
            """)
			remaining_duplicates = cursor.fetchall()

		if remaining_duplicates:
			self.stdout.write(
				self.style.ERROR(
					f"Warning: {len(remaining_duplicates)} duplicate users still remain!"
				)
			)
		else:
			self.stdout.write(
				self.style.SUCCESS("Cleanup complete - no duplicates remaining.")
			)
