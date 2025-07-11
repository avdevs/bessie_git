# Generated manually to fix duplicate CompanyAdmin records

from django.db import migrations


def cleanup_duplicate_company_admins(apps, schema_editor):
	"""
	Remove duplicate CompanyAdmin records keeping only the first occurrence
	for each user_id to prepare for unique constraint creation.
	"""
	CompanyAdmin = apps.get_model("bessie", "CompanyAdmin")

	# Find all user_ids that have duplicates
	from django.db import connection

	with connection.cursor() as cursor:
		cursor.execute("""
            SELECT user_id, COUNT(*) 
            FROM bessie_companyadmin 
            GROUP BY user_id 
            HAVING COUNT(*) > 1
        """)
		duplicate_user_ids = [row[0] for row in cursor.fetchall()]

	# For each duplicate user_id, keep only the first record and delete the rest
	for user_id in duplicate_user_ids:
		duplicate_records = CompanyAdmin.objects.filter(user_id=user_id).order_by("id")
		# Keep the first record, delete the rest
		records_to_delete = duplicate_records[1:]
		for record in records_to_delete:
			record.delete()


def reverse_cleanup(apps, schema_editor):
	# This is irreversible - we can't restore deleted duplicate records
	pass


class Migration(migrations.Migration):
	dependencies = [
		("bessie", "0015_AUTH_DANGER__lowercase_all_emails"),
	]

	operations = [
		migrations.RunPython(
			cleanup_duplicate_company_admins, reverse_code=reverse_cleanup
		),
	]
