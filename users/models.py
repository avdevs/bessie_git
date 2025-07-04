import os
import secrets
import string
from os.path import dirname, join
from pathlib import Path

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import Group, Permission, PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv


class UserManager(BaseUserManager):
	"""
	Defines how the User(or the model to which attached)
	will create users and superusers.
	"""

	def create_user(self, email, password, **extra_fields):
		"""
		Create and save a user with the given email, password,
		and date_of_birth.
		"""
		if not email:
			raise ValueError(_("The Email must be set"))
		email = self.normalize_email(email)  # lowercase the domain
		user = self.model(email=email, **extra_fields)
		user.set_password(password)  # hash raw password and set
		user.save()
		return user

	def create_superuser(self, email, password, **extra_fields):
		"""
		Create and save a superuser with the given email,
		password, and date_of_birth. Extra fields are added
		to indicate that the user is staff, active, and indeed
		a superuser.
		"""
		extra_fields.setdefault("is_staff", True)
		extra_fields.setdefault("is_superuser", True)
		extra_fields.setdefault("is_active", True)
		extra_fields.setdefault("user_type", "STAFF")
		if extra_fields.get("is_staff") is not True:
			raise ValueError(_("Superuser must have is_staff=True."))
		if extra_fields.get("is_superuser") is not True:
			raise ValueError(_("Superuser must have is_superuser=True."))
		return self.create_user(email, password, **extra_fields)

	def make_random_password(
		self,
		length=12,
		use_upper=True,
		use_lower=True,
		use_digits=True,
		use_special=True,
	):
		"""
		Generate a cryptographically secure random password.

		Args:
		    length (int): Total length of the password. Defaults to 12.
		    use_upper (bool): Include uppercase letters. Defaults to True.
		    use_lower (bool): Include lowercase letters. Defaults to True.
		    use_digits (bool): Include digits. Defaults to True.
		    use_special (bool): Include special characters. Defaults to True.

		Returns:
		    str: A randomly generated password
		"""
		# Define character sets
		char_sets = []

		if use_upper:
			char_sets.append(string.ascii_uppercase)
		if use_lower:
			char_sets.append(string.ascii_lowercase)
		if use_digits:
			char_sets.append(string.digits)
		if use_special:
			char_sets.append(string.punctuation)

		# Ensure at least one character set is selected
		if not char_sets:
			raise ValueError("At least one character set must be selected")

		# Combine all selected character sets
		all_chars = "".join(char_sets)

		# Ensure each selected character set is represented
		password = []
		for char_set in char_sets:
			password.append(secrets.choice(char_set))

		# Fill the rest of the password length with random characters
		while len(password) < length:
			password.append(secrets.choice(all_chars))

		# Shuffle the password characters
		secrets.SystemRandom().shuffle(password)

		# Convert to string
		return "".join(password)


class User(AbstractBaseUser, PermissionsMixin):
	class Meta:
		app_label = "authentication"

	class UserTypes(models.TextChoices):
		STAFF = "STAFF", "Staff"
		COMPANY_ADMIN = "COMPANY_ADMIN", "Company Admin"
		EMPLOYEE = "EMPLOYEE", "Employee"

	user_type = models.CharField(
		max_length=20, choices=UserTypes.choices, default=UserTypes.STAFF
	)
	"""
    Custom user model with unique email as the user
    identifier. This model is used for both superusers and
    regular users as well.
    """
	# The inherited field 'username' is nullified, so it will
	# neither become a DB column nor will it be required.
	email = models.EmailField(_("email address"), unique=True)
	first_name = models.CharField(max_length=255)
	last_name = models.CharField(max_length=255)
	is_staff = models.BooleanField(default=False)
	is_active = models.BooleanField(default=True)
	bessie_admin = models.BooleanField(default=False)
	date_joined = models.DateTimeField(default=timezone.now)
	groups = models.ManyToManyField(Group, related_name="custom_users", blank=True)

	user_permissions = models.ManyToManyField(
		Permission,
		verbose_name="user permissions",
		blank=True,
		related_name="custom_users_permissions",
		help_text="Specific permissions for this user.",
		related_query_name="custom_user",
	)
	# Set up the email field as the unique identifier for users.
	# This has nothing to do with the username that we nullified.

	USERNAME_FIELD = "email"

	# The USERNAME_FIELD aka 'email' cannot be included here
	REQUIRED_FIELDS = ["first_name", "last_name"]

	objects = UserManager()

	def __str__(self):
		return self.email

	class Meta:
		verbose_name = _("user")
		verbose_name_plural = _("users")
		abstract = False

	def clean(self):
		super().clean()
		self.email = self.__class__.objects.normalize_email(self.email)

	def email_user(self, subject, message, from_email=None, **kwargs):
		"""Email this user."""
		send_mail(subject, message, from_email, [self.email], **kwargs)
