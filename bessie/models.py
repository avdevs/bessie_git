from django.core.exceptions import ValidationError
from django.db import models

from users.models import User

RISK_LEVELS = [
	("low", "Low"),
	("medium", "Medium"),
	("high", "High"),
	("veryhigh", "Very High"),
]


class Company(models.Model):
	name = models.CharField(max_length=255, unique=True)
	teams = models.JSONField(default=list, blank=True)
	slots = models.IntegerField(default=0)
	used_slots = models.IntegerField(default=0)
	survey_start_date = models.DateField()
	survey_completion_date = models.DateField()
	strategy_meeting_date = models.DateField()
	results_visible = models.BooleanField(default=False)
	induction_video = models.FileField(upload_to="videos/", null=True, blank=True)
	results_video = models.FileField(upload_to="videos/", null=True, blank=True)

	class Meta:
		verbose_name_plural = "Companies"
		ordering = ["-name"]

	def clean(self):
		super().clean()

		# Only perform validation if all date fields have values
		if (
			self.survey_start_date
			and self.survey_completion_date
			and self.strategy_meeting_date
		):
			# Validate that survey_start_date is not after survey_completion_date
			if self.survey_start_date > self.survey_completion_date:
				raise ValidationError(
					{
						"survey_start_date": "Survey start date cannot be after survey completion date.",
						"survey_completion_date": "Survey completion date cannot be before survey start date.",
					}
				)

			# Validate that strategy_meeting_date is not before survey_completion_date
			if self.strategy_meeting_date < self.survey_completion_date:
				raise ValidationError(
					{
						"strategy_meeting_date": "Strategy meeting date must be after survey completion date."
					}
				)

			# Validate that strategy_meeting_date is not before survey_start_date
			if self.strategy_meeting_date < self.survey_start_date:
				raise ValidationError(
					{
						"strategy_meeting_date": "Strategy meeting date must be after survey start date."
					}
				)

	def save(self, *args, **kwargs):
		# Run validation before saving
		self.full_clean()
		super().save(*args, **kwargs)

	def __str__(self):
		return self.name


class CompanyRiskSummary(models.Model):
	company = models.OneToOneField(Company, on_delete=models.CASCADE)
	stress_and_wellbeing_risk_level = models.CharField(
		max_length=10,
		choices=RISK_LEVELS,
		blank=True,
		null=True,
	)
	stress_and_wellbeing_in_place = models.TextField()
	stress_and_wellbeing_recommendations = models.TextField(
		blank=True,
		null=True,
	)
	stress_and_wellbeing_risk_date = models.DateField(null=True, blank=True)

	workplace_stress_risk_level = models.CharField(
		max_length=10,
		choices=RISK_LEVELS,
		default="low",
		blank=True,
		null=True,
	)
	workplace_stress_in_place = models.TextField()
	workplace_stress_recommendations = models.TextField(
		blank=True,
		null=True,
	)
	workplace_stress_risk_date = models.DateField(null=True, blank=True)

	presenteeism_risk_level = models.CharField(
		max_length=10,
		choices=RISK_LEVELS,
		default="low",
		blank=True,
		null=True,
	)
	presenteeism_in_place = models.TextField()
	presenteeism_recommendations = models.TextField(
		blank=True,
		null=True,
	)
	presenteeism_risk_date = models.DateField(null=True, blank=True)

	wider_risks_risk_level = models.CharField(
		max_length=10,
		choices=RISK_LEVELS,
		default="low",
		blank=True,
		null=True,
	)
	wider_risks_in_place = models.TextField()
	wider_risks_recommendations = models.TextField(
		blank=True,
		null=True,
	)
	wider_risks_risk_date = models.DateField(null=True, blank=True)

	def __str__(self):
		return f"Risk Summary for {self.company.name}"


class CompanyAdmin(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	company = models.ForeignKey(Company, on_delete=models.CASCADE)
	admin_level = models.IntegerField(default=1)

	class Meta:
		unique_together = ("user", "company")  # Prevent duplicate user-company combinations

	def save(self, *args, **kwargs):
		if self.user.user_type != User.UserTypes.COMPANY_ADMIN:
			raise ValidationError("User must be a company admin")
		super().save(*args, **kwargs)

	def __str__(self):
		return f"{self.user.first_name} - {self.company}"


class Employee(models.Model):
	company = models.ForeignKey(Company, on_delete=models.CASCADE)
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	team = models.CharField(max_length=256, null=True, blank=True)

	def __str__(self):
		return f"{self.user.email} ({self.company.name})"


class WizardState(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	data = models.JSONField(default=dict)
	step = models.CharField(max_length=50)


class BessieResponse(models.Model):
	employee = models.OneToOneField(
		Employee, on_delete=models.CASCADE, related_name="owner"
	)
	timestamp = models.DateTimeField(auto_now_add=True)
	multichoice = models.JSONField()
	q1 = models.TextField()
	q14 = models.CharField(max_length=255)
	q45 = models.TextField()
	q66 = models.TextField()
	q74 = models.TextField()
	q100 = models.TextField()
	q154 = models.TextField()
	q159 = models.TextField()
	q167 = models.TextField()
	q168 = models.TextField()
	q176 = models.TextField()
	q228 = models.TextField()

	def get_sorted_questions(self):
		# Extract questions from the JSON field
		questions = self.multichoice.copy()

		# Add individual question fields to the dictionary
		for field in self._meta.get_fields():
			if field.name.startswith("q") and field.name[1:].isdigit():
				questions[field.name] = getattr(self, field.name)

		# Filter and sort the questions by their keys
		sorted_questions = dict(
			sorted(
				(
					item
					for item in questions.items()
					if item[0].startswith("q") and item[0][1:].isdigit()
				),
				key=lambda item: int(item[0][1:]),
			)
		)

		return sorted_questions

	def __str__(self):
		return f"Response from {self.employee.user.first_name} on {self.timestamp}"


class BessieResult(models.Model):
	response = models.OneToOneField(
		BessieResponse, on_delete=models.CASCADE, related_name="response"
	)
	company = models.ForeignKey(Company, on_delete=models.CASCADE)
	environment = models.FloatField()
	residence = models.FloatField()
	privacy = models.FloatField()
	privacy_multiplier = models.FloatField()
	travel_to_work = models.FloatField()
	pay = models.FloatField()
	pay_and_childcare_multiplier = models.FloatField()
	pay_multiplier = models.FloatField()
	complexity = models.FloatField()
	hours_and_flexibility = models.FloatField()
	control_and_autonomy_over_working_hours = models.FloatField()
	workload = models.FloatField()
	manageable_workload = models.FloatField()
	complexity_plus_training = models.FloatField()
	complexity_training_hours_and_flexibility = models.FloatField()
	work_breaks = models.FloatField()
	overtime = models.FloatField()
	team_and_colleague_support = models.FloatField()
	management_support = models.FloatField()
	management_support_multiplier = models.FloatField()
	team_and_colleague_support_multiplier = models.FloatField()
	training = models.FloatField()
	training_multiplier = models.FloatField()
	culture = models.FloatField()
	managerial_trust = models.FloatField()
	colleague_trust = models.FloatField()
	consultation = models.FloatField()
	team_morale = models.FloatField()
	willingness_to_progress = models.FloatField()
	culture_multiplier = models.FloatField()
	lone_working = models.FloatField()
	wider_team_support = models.FloatField()
	lone_working_and_wider_team_support_multiplier = models.FloatField()
	health_and_safety = models.FloatField()
	health_and_safety_multiplier = models.FloatField()
	absence = models.FloatField()
	sick_leave_and_employer_support = models.FloatField()
	absence_and_support = models.FloatField()
	absence_multiplier = models.FloatField()
	covid = models.FloatField()
	covid_multiplier = models.FloatField()
	work_related_stress_impacting_family_and_relationships = models.FloatField()
	environment_multiplier = models.FloatField()
	work_related_stress_impacting_social_life = models.FloatField()
	work_related_stress_impacting_personal_life = models.FloatField()
	family = models.FloatField()
	family_multiplier = models.FloatField()
	family_support_companion = models.FloatField()
	responsibility_of_children = models.FloatField()
	responsibility_for_children_multiplier = models.FloatField()
	support_network = models.FloatField()
	support_network_multiplier = models.FloatField()
	childcare = models.FloatField()
	childcare_multiplier = models.FloatField()
	responsibility_for_family = models.FloatField()
	family_factors = models.FloatField()
	health = models.FloatField()
	physical_health_condition_affecting_work = models.FloatField()
	physical_health_factors_impacting_work = models.FloatField()
	mental_health_factors_impacting_work = models.FloatField()
	physical_health = models.FloatField()
	physical_health_multiplier = models.FloatField()
	physical_health_and_absence_multiplier = models.FloatField()
	physical_health_and_management_support_multiplier = models.FloatField()
	physical_health_and_culture = models.FloatField()
	mental_health = models.FloatField()
	mental_and_physical_health = models.FloatField()
	mental_and_physical_health_multiplier = models.FloatField()
	mental_and_physical_health_and_absence_from_work = models.FloatField()
	mental_health_and_absence_multiplier = models.FloatField()
	mental_health_and_culture_multiplier = models.FloatField()
	mental_health_physical_health_and_culture_multiplier = models.FloatField()
	mental_health_multiplier = models.FloatField()
	fertility_and_pregnancy = models.FloatField()
	fertility_and_pregnancy_impacting_work = models.FloatField()
	pregnancy_impact = models.FloatField()
	pregnancy_and_management_support = models.FloatField()
	abuse_and_trauma = models.FloatField()
	abuse_and_trauma_impact = models.FloatField()
	abuse_and_trauma_and_management_support_multiplier = models.FloatField()
	abuse_and_trauma_and_management_support_and_culture = models.FloatField()
	pregnancy_and_mental_health = models.FloatField()
	pregnancy_and_physical_health = models.FloatField()
	self_care = models.FloatField()
	self_care_and_physical_health = models.FloatField()
	self_care_and_mental_health = models.FloatField()
	personal = models.FloatField()
	identity = models.FloatField()
	identity_and_management_support = models.FloatField()
	discrimination = models.FloatField()
	discrimination_work_impact = models.FloatField()
	age_discrimination = models.FloatField()
	race_discrimination = models.FloatField()
	disability_discrimination = models.FloatField()
	gender_discrimination = models.FloatField()
	sexual_discrimination = models.FloatField()
	other_discrimination = models.FloatField()
	carer = models.FloatField()
	personal_relationships = models.FloatField()
	personal_relationships_and_working_relationships_impact = models.FloatField()
	problem_solving = models.FloatField()
	personal_finances = models.FloatField()
	personal_finances_and_responsibility_for_children = models.FloatField()
	personal_finances_and_pay_multiplier = models.FloatField()
	personal_finances_and_pay_and_childcare_multiplier = models.FloatField()
	hobbies = models.FloatField()
	personal_barriers = models.FloatField()
	financial_position_as_a_barrier_for_holidays = models.FloatField()
	work_commitments_as_a_barrier_for_holidays = models.FloatField()
	holidays = models.FloatField()
	holidays_and_pay = models.FloatField()
	personal_satisfaction = models.FloatField()
	personal_satisfaction_improvement = models.FloatField()
	emotional_health = models.FloatField()
	emotional_health_multiplier = models.FloatField()
	emotional_distress = models.FloatField()
	emotional_distress_multiplier = models.FloatField()
	emotional_wellbeing = models.FloatField()
	emotional_wellbeing_and_management_support = models.FloatField()
	emotional_health_and_culture_at_work = models.FloatField()
	personal_multiplier = models.FloatField()
	emotional_wellbeing_multiplier = models.FloatField()
	staff_comment = models.TextField()
	potential_cost = models.FloatField()

	def __str__(self):
		return f"Result for {self.response.employee.user.first_name} - {self.response.employee.company.name}"


class EmployeeProcessTask(models.Model):
	job_id = models.IntegerField()
	company = models.ForeignKey(Company, on_delete=models.CASCADE)
	chunks_number = models.IntegerField()
	chunks_completed = models.IntegerField(default=0)
	notification_email = models.EmailField()
	completed = models.BooleanField(default=False)

	def __str__(self):
		return f"{self.company.name}"
