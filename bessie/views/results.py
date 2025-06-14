import json
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import (
	Avg,
	Case,
	When,
	IntegerField,
	Count,
	Sum,
	Q,
)
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

from bessie.models import (
	BessieResult,
	BessieResponse,
	Employee,
	Company,
	CompanyRiskSummary,
)
from bessie.views import calculate_stress_load, get_category

from bessie.forms import (
	StressAndWellbeingRiskForm,
	WorkplaceStressRiskForm,
	PresenteeismRiskForm,
	WiderRisksForm,
)

from bessie.report_text import report_text


@require_http_methods(["GET", "POST"])
def view_company_results(request, id):
	try:
		company = Company.objects.get(pk=id)
	except Company.DoesNotExist:
		messages.error(request, "Company not found.")
		return redirect("dashboard")

	user = request.user

	if not company.results_visible and not user.is_staff:
		return redirect("dashboard")

	team = request.GET.get("team")
	risk_summary, created = CompanyRiskSummary.objects.get_or_create(company=company)

	stress_and_wellbeing_form = StressAndWellbeingRiskForm(
		initial={
			"stress_and_wellbeing_risk_level": risk_summary.stress_and_wellbeing_risk_level,
			"stress_and_wellbeing_risk_in_place": risk_summary.stress_and_wellbeing_in_place,
			"stress_and_wellbeing_risk_recommendations": risk_summary.stress_and_wellbeing_recommendations,
			"stress_and_wellbeing_risk_date": risk_summary.stress_and_wellbeing_risk_date,
		}
	)

	workplace_stress_form = WorkplaceStressRiskForm(
		initial={
			"workplace_stress_risk_level": risk_summary.workplace_stress_risk_level,
			"workplace_stress_in_place": risk_summary.workplace_stress_in_place,
			"workplace_stress_recommendations": risk_summary.workplace_stress_recommendations,
			"workplace_stress_risk_date": risk_summary.workplace_stress_risk_date,
		}
	)

	presenteeism_form = PresenteeismRiskForm(
		initial={
			"presenteeism_risk_level": risk_summary.presenteeism_risk_level,
			"presenteeism_in_place": risk_summary.presenteeism_in_place,
			"presenteeism_recommendations": risk_summary.presenteeism_recommendations,
			"presenteeism_risk_date": risk_summary.presenteeism_risk_date,
		}
	)

	wider_risks_form = WiderRisksForm(
		initial={
			"wider_risks_risk_level": risk_summary.wider_risks_risk_level,
			"wider_risks_in_place": risk_summary.wider_risks_in_place,
			"wider_risks_recommendations": risk_summary.wider_risks_recommendations,
			"wider_risks_risk_date": risk_summary.wider_risks_risk_date,
		}
	)

	if request.method == "POST":
		form_type = request.POST.get("form_type")

		# Define form configuration
		form_configs = {
			"stress_and_wellbeing_form": {
				"form_class": StressAndWellbeingRiskForm,
				"success_message": "Stress and wellbeing summary updated successfully.",
				"fields": {
					"stress_and_wellbeing_risk_level": "stress_and_wellbeing_risk_level",
					"stress_and_wellbeing_risk_in_place": "stress_and_wellbeing_in_place",
					"stress_and_wellbeing_risk_recommendations": "stress_and_wellbeing_recommendations",
					"stress_and_wellbeing_risk_date": "stress_and_wellbeing_risk_date",
				},
			},
			"workplace_stress_form": {
				"form_class": WorkplaceStressRiskForm,
				"success_message": "Workplace stress summary updated successfully.",
				"fields": {
					"workplace_stress_risk_level": "workplace_stress_risk_level",
					"workplace_stress_in_place": "workplace_stress_in_place",
					"workplace_stress_recommendations": "workplace_stress_recommendations",
					"workplace_stress_risk_date": "workplace_stress_risk_date",
				},
			},
			"presenteeism_form": {
				"form_class": PresenteeismRiskForm,
				"success_message": "Presenteeism summary updated successfully.",
				"fields": {
					"presenteeism_risk_level": "presenteeism_risk_level",
					"presenteeism_in_place": "presenteeism_in_place",
					"presenteeism_recommendations": "presenteeism_recommendations",
					"presenteeism_risk_date": "presenteeism_risk_date",
				},
			},
			"wider_risks_form": {
				"form_class": WiderRisksForm,
				"success_message": "Wider risks summary updated successfully.",
				"fields": {
					"wider_risks_risk_level": "wider_risks_risk_level",
					"wider_risks_in_place": "wider_risks_in_place",
					"wider_risks_recommendations": "wider_risks_recommendations",
					"wider_risks_risk_date": "wider_risks_risk_date",
				},
			},
		}

		if form_type in form_configs:
			config = form_configs[form_type]
			form = config["form_class"](request.POST)

			if form.is_valid():
				# Update risk_summary fields based on configuration
				for form_field, model_field in config["fields"].items():
					setattr(risk_summary, model_field, form.cleaned_data[form_field])

				risk_summary.save()
				messages.success(request, config["success_message"])
				return redirect("company_results", id=id)
			else:
				# Set the appropriate form variable for template rendering
				if form_type == "stress_and_wellbeing_form":
					stress_and_wellbeing_form = form
				elif form_type == "workplace_stress_form":
					workplace_stress_form = form
				elif form_type == "presenteeism_form":
					presenteeism_form = form
				elif form_type == "wider_risks_form":
					wider_risks_form = form

	query = Q(company_id=id)
	if team:
		query &= Q(response__employee__team=team)

	result = get_aggregated_results(query)

	texts = {}

	for key, value in result.items():
		cat = get_category(value)
		pres = report_text.get(key)
		if pres:
			texts[key] = {"content": report_text[key][cat]["team"], "category": cat}
			texts[f"{key}_overview"] = report_text[key]["overview"]

	stats = get_field_statistics(id, team)

	res = read_result(result)
	stats = read_result(stats)

	return render(
		request,
		"bessie/company_results.html",
		{
			"stress_and_wellbeing": json.dumps(res["stress_and_wellbeing"]),
			"stress_risks_affecting_work": json.dumps(res["stress_risks_affecting_work"]),
			"workplace_stress_factors": json.dumps(res["workplace_stress_factors"]),
			"presenteeism_factors": json.dumps(res["presenteeism"]),
			"environment_factors": json.dumps(res["environment"]),
			"family_factors": json.dumps(res["family"]),
			"health_factors": json.dumps(res["health"]),
			"personal_factors": json.dumps(res["personal"]),
			"environment_factors_stats": json.dumps(stats["environment"]),
			"health_factors_stats": json.dumps(stats["health"]),
			"family_factors_stats": json.dumps(stats["family"]),
			"personal_factors_stats": json.dumps(stats["personal"]),
			"wider_risks_factors": json.dumps(res["wider_risks"]),
			"report_text": json.dumps(texts),
			"potential_cost": round(result["potential_cost"]),
			"stress_and_wellbeing_form": stress_and_wellbeing_form,
			"workplace_stress_form": workplace_stress_form,
			"presenteeism_form": presenteeism_form,
			"wider_risks_form": wider_risks_form,
			"company": company,
		},
	)


@login_required
def user_results(request, employee_id=None):
	if employee_id is None:
		employee = Employee.objects.select_related("user", "company").get(user=request.user)
	else:
		User = get_user_model()
		user = User.objects.get(email=employee_id)
		employee = Employee.objects.select_related("user", "company").get(user=user)

	response = BessieResponse.objects.get(employee=employee)
	results = BessieResult.objects.filter(response=response).values().first()
	texts = {}

	if results is not None:
		for key, value in results.items():
			if isinstance(value, str):
				continue
			cat = get_category(value)
			pres = report_text.get(key)
			if pres:
				texts[key] = {
					"content": report_text[key][cat]["individual"],
					"category": cat,
				}
				texts[f"{key}_overview"] = report_text[key]["overview"]

	stats = get_field_statistics(employee.company.pk, employee_id=employee.pk)

	res = read_result(results)
	stats = read_result(stats)

	can_see_result = (
		employee.company.results_visible if not request.user.is_staff else True
	)

	environment_stressload = calculate_stress_load(stats.get("environment", []))
	health_stressload = calculate_stress_load(stats.get("health", []))
	family_stressload = calculate_stress_load(stats.get("family", []))
	personal_stressload = calculate_stress_load(stats.get("personal", []))

	return render(
		request,
		"bessie/result.html",
		{
			"stress_and_wellbeing": json.dumps(res["stress_and_wellbeing"]),
			"stress_risks_affecting_work": json.dumps(res["stress_risks_affecting_work"]),
			"workplace_stress_factors": json.dumps(res["workplace_stress_factors"]),
			"presenteeism_factors": json.dumps(res["presenteeism"]),
			"environment_factors": json.dumps(res["environment"]),
			"family_factors": json.dumps(res["family"]),
			"health_factors": json.dumps(res["health"]),
			"personal_factors": json.dumps(res["personal"]),
			"environment_factors_stats": json.dumps(stats["environment"]),
			"health_factors_stats": json.dumps(stats["health"]),
			"family_factors_stats": json.dumps(stats["family"]),
			"personal_factors_stats": json.dumps(stats["personal"]),
			"wider_risks_factors": json.dumps(res["wider_risks"]),
			"report_text": json.dumps(texts),
			"environment_stressload": environment_stressload,
			"health_stressload": health_stressload,
			"family_stressload": family_stressload,
			"personal_stressload": personal_stressload,
			"company": employee.company,
			"can_see_result": can_see_result,
		},
	)


def get_aggregated_results(query):
	"""Get aggregated results from BessieResult for the given query."""
	return BessieResult.objects.filter(query).aggregate(
		environment=Avg("environment", default=0),
		residence=Avg("residence", default=0),
		privacy=Avg("privacy", default=0),
		privacy_multiplier=Avg("privacy_multiplier", default=0),
		travel_to_work=Avg("travel_to_work", default=0),
		pay=Avg("pay", default=0),
		pay_and_childcare_multiplier=Avg("pay_and_childcare_multiplier", default=0),
		pay_multiplier=Avg("pay_multiplier", default=0),
		complexity=Avg("complexity", default=0),
		hours_and_flexibility=Avg("hours_and_flexibility", default=0),
		control_and_autonomy_over_working_hours=Avg(
			"control_and_autonomy_over_working_hours", default=0
		),
		workload=Avg("workload", default=0),
		manageable_workload=Avg("manageable_workload", default=0),
		complexity_plus_training=Avg("complexity_plus_training", default=0),
		complexity_training_hours_and_flexibility=Avg(
			"complexity_training_hours_and_flexibility", default=0
		),
		work_breaks=Avg("work_breaks", default=0),
		overtime=Avg("overtime", default=0),
		team_and_colleague_support=Avg("team_and_colleague_support", default=0),
		management_support=Avg("management_support", default=0),
		management_support_multiplier=Avg("management_support_multiplier", default=0),
		team_and_colleague_support_multiplier=Avg(
			"team_and_colleague_support_multiplier", default=0
		),
		training=Avg("training", default=0),
		training_multiplier=Avg("training_multiplier", default=0),
		culture=Avg("culture", default=0),
		managerial_trust=Avg("managerial_trust", default=0),
		colleague_trust=Avg("colleague_trust", default=0),
		consultation=Avg("consultation", default=0),
		team_morale=Avg("team_morale", default=0),
		willingness_to_progress=Avg("willingness_to_progress", default=0),
		culture_multiplier=Avg("culture_multiplier", default=0),
		lone_working=Avg("lone_working", default=0),
		wider_team_support=Avg("wider_team_support", default=0),
		lone_working_and_wider_team_support_multiplier=Avg(
			"lone_working_and_wider_team_support_multiplier", default=0
		),
		health_and_safety=Avg("health_and_safety", default=0),
		health_and_safety_multiplier=Avg("health_and_safety_multiplier", default=0),
		absence=Avg("absence", default=0),
		sick_leave_and_employer_support=Avg("sick_leave_and_employer_support", default=0),
		absence_and_support=Avg("absence_and_support", default=0),
		absence_multiplier=Avg("absence_multiplier", default=0),
		covid=Avg("covid", default=0),
		covid_multiplier=Avg("covid_multiplier", default=0),
		work_related_stress_impacting_family_and_relationships=Avg(
			"work_related_stress_impacting_family_and_relationships", default=0
		),
		environment_multiplier=Avg("environment_multiplier", default=0),
		work_related_stress_impacting_social_life=Avg(
			"work_related_stress_impacting_social_life", default=0
		),
		work_related_stress_impacting_personal_life=Avg(
			"work_related_stress_impacting_personal_life", default=0
		),
		family=Avg("family", default=0),
		family_multiplier=Avg("family_multiplier", default=0),
		family_support_companion=Avg("family_support_companion", default=0),
		responsibility_of_children=Avg("responsibility_of_children", default=0),
		responsibility_for_children_multiplier=Avg(
			"responsibility_for_children_multiplier", default=0
		),
		support_network=Avg("support_network", default=0),
		support_network_multiplier=Avg("support_network_multiplier", default=0),
		childcare=Avg("childcare", default=0),
		childcare_multiplier=Avg("childcare_multiplier", default=0),
		responsibility_for_family=Avg("responsibility_for_family", default=0),
		family_factors=Avg("family_factors", default=0),
		health=Avg("health", default=0),
		physical_health_condition_affecting_work=Avg(
			"physical_health_condition_affecting_work", default=0
		),
		physical_health_factors_impacting_work=Avg(
			"physical_health_factors_impacting_work", default=0
		),
		mental_health_factors_impacting_work=Avg(
			"mental_health_factors_impacting_work", default=0
		),
		physical_health=Avg("physical_health", default=0),
		physical_health_multiplier=Avg("physical_health_multiplier", default=0),
		physical_health_and_absence_multiplier=Avg(
			"physical_health_and_absence_multiplier", default=0
		),
		physical_health_and_management_support_multiplier=Avg(
			"physical_health_and_management_support_multiplier", default=0
		),
		physical_health_and_culture=Avg("physical_health_and_culture", default=0),
		mental_health=Avg("mental_health", default=0),
		mental_and_physical_health=Avg("mental_and_physical_health", default=0),
		mental_and_physical_health_multiplier=Avg(
			"mental_and_physical_health_multiplier", default=0
		),
		mental_and_physical_health_and_absence_from_work=Avg(
			"mental_and_physical_health_and_absence_from_work", default=0
		),
		mental_health_and_absence_multiplier=Avg(
			"mental_health_and_absence_multiplier", default=0
		),
		mental_health_and_culture_multiplier=Avg(
			"mental_health_and_culture_multiplier", default=0
		),
		mental_health_physical_health_and_culture_multiplier=Avg(
			"mental_health_physical_health_and_culture_multiplier", default=0
		),
		mental_health_multiplier=Avg("mental_health_multiplier", default=0),
		fertility_and_pregnancy=Avg("fertility_and_pregnancy", default=0),
		fertility_and_pregnancy_impacting_work=Avg(
			"fertility_and_pregnancy_impacting_work", default=0
		),
		pregnancy_impact=Avg("pregnancy_impact", default=0),
		pregnancy_and_management_support=Avg("pregnancy_and_management_support", default=0),
		abuse_and_trauma=Avg("abuse_and_trauma", default=0),
		abuse_and_trauma_impact=Avg("abuse_and_trauma_impact", default=0),
		abuse_and_trauma_and_management_support_multiplier=Avg(
			"abuse_and_trauma_and_management_support_multiplier", default=0
		),
		abuse_and_trauma_and_management_support_and_culture=Avg(
			"abuse_and_trauma_and_management_support_and_culture", default=0
		),
		pregnancy_and_mental_health=Avg("pregnancy_and_mental_health", default=0),
		pregnancy_and_physical_health=Avg("pregnancy_and_physical_health", default=0),
		self_care=Avg("self_care", default=0),
		self_care_and_physical_health=Avg("self_care_and_physical_health", default=0),
		self_care_and_mental_health=Avg("self_care_and_mental_health", default=0),
		personal=Avg("personal", default=0),
		identity=Avg("identity", default=0),
		identity_and_management_support=Avg("identity_and_management_support", default=0),
		discrimination=Avg("discrimination", default=0),
		discrimination_work_impact=Avg("discrimination_work_impact", default=0),
		age_discrimination=Avg("age_discrimination", default=0),
		race_discrimination=Avg("race_discrimination", default=0),
		disability_discrimination=Avg("disability_discrimination", default=0),
		gender_discrimination=Avg("gender_discrimination", default=0),
		sexual_discrimination=Avg("sexual_discrimination", default=0),
		other_discrimination=Avg("other_discrimination", default=0),
		carer=Avg("carer", default=0),
		personal_relationships=Avg("personal_relationships", default=0),
		personal_relationships_and_working_relationships_impact=Avg(
			"personal_relationships_and_working_relationships_impact", default=0
		),
		problem_solving=Avg("problem_solving", default=0),
		personal_finances=Avg("personal_finances", default=0),
		personal_finances_and_responsibility_for_children=Avg(
			"personal_finances_and_responsibility_for_children", default=0
		),
		personal_finances_and_pay_multiplier=Avg(
			"personal_finances_and_pay_multiplier", default=0
		),
		personal_finances_and_pay_and_childcare_multiplier=Avg(
			"personal_finances_and_pay_and_childcare_multiplier", default=0
		),
		hobbies=Avg("hobbies", default=0),
		personal_barriers=Avg("personal_barriers", default=0),
		financial_position_as_a_barrier_for_holidays=Avg(
			"financial_position_as_a_barrier_for_holidays", default=0
		),
		work_commitments_as_a_barrier_for_holidays=Avg(
			"work_commitments_as_a_barrier_for_holidays", default=0
		),
		holidays=Avg("holidays", default=0),
		holidays_and_pay=Avg("holidays_and_pay", default=0),
		personal_satisfaction=Avg("personal_satisfaction", default=0),
		personal_satisfaction_improvement=Avg(
			"personal_satisfaction_improvement", default=0
		),
		emotional_health=Avg("emotional_health", default=0),
		emotional_health_multiplier=Avg("emotional_health_multiplier", default=0),
		emotional_distress=Avg("emotional_distress", default=0),
		emotional_distress_multiplier=Avg("emotional_distress_multiplier", default=0),
		emotional_wellbeing=Avg("emotional_wellbeing", default=0),
		emotional_wellbeing_and_management_support=Avg(
			"emotional_wellbeing_and_management_support", default=0
		),
		emotional_health_and_culture_at_work=Avg(
			"emotional_health_and_culture_at_work", default=0
		),
		personal_multiplier=Avg("personal_multiplier", default=0),
		emotional_wellbeing_multiplier=Avg("emotional_wellbeing_multiplier", default=0),
		potential_cost=Sum("potential_cost", default=0),
	)


def get_field_statistics(companyId, team=None, employee_id=None):
	"""Get field statistics for all fields in a single optimized query."""
	query = Q(company_id=companyId)
	if team:
		query &= Q(response__employee__team=team)
	if employee_id:
		query &= Q(response__employee_id=employee_id)

	fields = [
		"environment",
		"residence",
		"privacy",
		"privacy_multiplier",
		"travel_to_work",
		"pay",
		"pay_and_childcare_multiplier",
		"pay_multiplier",
		"complexity",
		"hours_and_flexibility",
		"control_and_autonomy_over_working_hours",
		"workload",
		"manageable_workload",
		"complexity_plus_training",
		"complexity_training_hours_and_flexibility",
		"work_breaks",
		"overtime",
		"team_and_colleague_support",
		"management_support",
		"management_support_multiplier",
		"team_and_colleague_support_multiplier",
		"training",
		"training_multiplier",
		"culture",
		"managerial_trust",
		"colleague_trust",
		"consultation",
		"team_morale",
		"willingness_to_progress",
		"culture_multiplier",
		"lone_working",
		"wider_team_support",
		"lone_working_and_wider_team_support_multiplier",
		"health_and_safety",
		"health_and_safety_multiplier",
		"absence",
		"sick_leave_and_employer_support",
		"absence_and_support",
		"absence_multiplier",
		"covid",
		"covid_multiplier",
		"work_related_stress_impacting_family_and_relationships",
		"environment_multiplier",
		"work_related_stress_impacting_social_life",
		"work_related_stress_impacting_personal_life",
		"family",
		"family_multiplier",
		"family_support_companion",
		"responsibility_of_children",
		"responsibility_for_children_multiplier",
		"support_network",
		"support_network_multiplier",
		"childcare",
		"childcare_multiplier",
		"responsibility_for_family",
		"family_factors",
		"health",
		"physical_health_condition_affecting_work",
		"physical_health_factors_impacting_work",
		"mental_health_factors_impacting_work",
		"physical_health",
		"physical_health_multiplier",
		"physical_health_and_absence_multiplier",
		"physical_health_and_management_support_multiplier",
		"physical_health_and_culture",
		"mental_health",
		"mental_and_physical_health",
		"mental_and_physical_health_multiplier",
		"mental_and_physical_health_and_absence_from_work",
		"mental_health_and_absence_multiplier",
		"mental_health_and_culture_multiplier",
		"mental_health_physical_health_and_culture_multiplier",
		"mental_health_multiplier",
		"fertility_and_pregnancy",
		"fertility_and_pregnancy_impacting_work",
		"pregnancy_impact",
		"pregnancy_and_management_support",
		"abuse_and_trauma",
		"abuse_and_trauma_impact",
		"abuse_and_trauma_and_management_support_multiplier",
		"abuse_and_trauma_and_management_support_and_culture",
		"pregnancy_and_mental_health",
		"pregnancy_and_physical_health",
		"self_care",
		"self_care_and_physical_health",
		"self_care_and_mental_health",
		"personal",
		"identity",
		"identity_and_management_support",
		"discrimination",
		"discrimination_work_impact",
		"age_discrimination",
		"race_discrimination",
		"disability_discrimination",
		"gender_discrimination",
		"sexual_discrimination",
		"other_discrimination",
		"carer",
		"personal_relationships",
		"personal_relationships_and_working_relationships_impact",
		"problem_solving",
		"personal_finances",
		"personal_finances_and_responsibility_for_children",
		"personal_finances_and_pay_multiplier",
		"personal_finances_and_pay_and_childcare_multiplier",
		"hobbies",
		"personal_barriers",
		"financial_position_as_a_barrier_for_holidays",
		"work_commitments_as_a_barrier_for_holidays",
		"holidays",
		"holidays_and_pay",
		"personal_satisfaction",
		"personal_satisfaction_improvement",
		"emotional_health",
		"emotional_health_multiplier",
		"emotional_distress",
		"emotional_distress_multiplier",
		"emotional_wellbeing",
		"emotional_wellbeing_and_management_support",
		"emotional_health_and_culture_at_work",
		"personal_multiplier",
		"emotional_wellbeing_multiplier",
	]

	# Build a single query with all field statistics - MAJOR OPTIMIZATION
	# This replaces 80+ individual queries with 1 optimized query
	aggregation_dict = {}

	for field in fields:
		aggregation_dict.update(
			{
				f"{field}_low_count": Count(
					Case(
						When(**{f"{field}__lte": 25.0}, then=1),
						output_field=IntegerField(),
					)
				),
				f"{field}_medium_count": Count(
					Case(
						When(**{f"{field}__gt": 25.0, f"{field}__lte": 50.0}, then=1),
						output_field=IntegerField(),
					)
				),
				f"{field}_high_count": Count(
					Case(
						When(**{f"{field}__gt": 50.0, f"{field}__lte": 75.0}, then=1),
						output_field=IntegerField(),
					)
				),
				f"{field}_very_high_count": Count(
					Case(
						When(**{f"{field}__gt": 75.0}, then=1),
						output_field=IntegerField(),
					)
				),
			}
		)

	# Execute single aggregated query
	stats = BessieResult.objects.filter(query).aggregate(**aggregation_dict)

	# Transform results into expected format
	result = {}
	for field in fields:
		result[field] = {
			"low_count": stats[f"{field}_low_count"],
			"medium_count": stats[f"{field}_medium_count"],
			"high_count": stats[f"{field}_high_count"],
			"very_high": stats[f"{field}_very_high_count"],
		}

	return result


def read_result(res):
	if not res:
		return {}

	# Initialize all category dictionaries
	stress_and_wellbeing = {}
	workplace_stress_factors = {}
	stress_risks_affecting_work = {}
	environment = {}
	presenteeism = {}
	family = {}
	health = {}
	personal = {}
	wider_risks = {}

	# Populate stress_and_wellbeing category
	stress_and_wellbeing["emotional_distress"] = res["emotional_distress"]
	stress_and_wellbeing["emotional_health"] = res["emotional_health"]
	stress_and_wellbeing["mental_health"] = res["mental_health"]
	stress_and_wellbeing["physical_health"] = res["physical_health"]
	stress_and_wellbeing["self_care"] = res["self_care"]

	# Populate workplace_stress_factors category
	workplace_stress_factors["absence"] = res["absence"]
	workplace_stress_factors["carer"] = res["carer"]
	workplace_stress_factors["childcare"] = res["childcare"]
	workplace_stress_factors["complexity"] = res["complexity"]
	workplace_stress_factors["covid"] = res["covid"]
	workplace_stress_factors["culture"] = res["culture"]
	workplace_stress_factors["discrimination"] = res["discrimination"]
	workplace_stress_factors["health_and_safety"] = res["health_and_safety"]
	workplace_stress_factors["hours_and_flexibility"] = res["hours_and_flexibility"]
	workplace_stress_factors["management_support"] = res["management_support"]
	workplace_stress_factors["pay"] = res["pay"]
	workplace_stress_factors["personal_finances"] = res["personal_finances"]
	workplace_stress_factors["training"] = res["training"]
	workplace_stress_factors["workload"] = res["workload"]

	# Populate stress_risks_affecting_work category
	stress_risks_affecting_work["absence_multiplier"] = res["absence_multiplier"]
	stress_risks_affecting_work["abuse_and_trauma_and_management_support_multiplier"] = (
		res["abuse_and_trauma_and_management_support_multiplier"]
	)
	stress_risks_affecting_work["childcare_multiplier"] = res["childcare_multiplier"]
	stress_risks_affecting_work["covid_multiplier"] = res["covid_multiplier"]
	stress_risks_affecting_work["culture_multiplier"] = res["culture_multiplier"]
	stress_risks_affecting_work["emotional_distress_multiplier"] = res[
		"emotional_distress_multiplier"
	]
	stress_risks_affecting_work["emotional_health_multiplier"] = res[
		"emotional_health_multiplier"
	]
	stress_risks_affecting_work["emotional_wellbeing_multiplier"] = res[
		"emotional_wellbeing_multiplier"
	]
	stress_risks_affecting_work["environment_multiplier"] = res["environment_multiplier"]
	stress_risks_affecting_work["family_multiplier"] = res["family_multiplier"]
	stress_risks_affecting_work["health_and_safety_multiplier"] = res[
		"health_and_safety_multiplier"
	]
	stress_risks_affecting_work["lone_working_and_wider_team_support_multiplier"] = res[
		"lone_working_and_wider_team_support_multiplier"
	]
	stress_risks_affecting_work["management_support_multiplier"] = res[
		"management_support_multiplier"
	]
	stress_risks_affecting_work["mental_and_physical_health_multiplier"] = res[
		"mental_and_physical_health_multiplier"
	]
	stress_risks_affecting_work["mental_health_and_absence_multiplier"] = res[
		"mental_health_and_absence_multiplier"
	]
	stress_risks_affecting_work["mental_health_and_culture_multiplier"] = res[
		"mental_health_and_culture_multiplier"
	]
	stress_risks_affecting_work["mental_health_multiplier"] = res[
		"mental_health_multiplier"
	]
	stress_risks_affecting_work[
		"mental_health_physical_health_and_culture_multiplier"
	] = res["mental_health_physical_health_and_culture_multiplier"]
	stress_risks_affecting_work["pay_and_childcare_multiplier"] = res[
		"pay_and_childcare_multiplier"
	]
	stress_risks_affecting_work["pay_multiplier"] = res["pay_multiplier"]
	stress_risks_affecting_work["personal_finances_and_pay_and_childcare_multiplier"] = (
		res["personal_finances_and_pay_and_childcare_multiplier"]
	)
	stress_risks_affecting_work["personal_finances_and_pay_multiplier"] = res[
		"personal_finances_and_pay_multiplier"
	]
	stress_risks_affecting_work["personal_multiplier"] = res["personal_multiplier"]
	stress_risks_affecting_work["physical_health_and_absence_multiplier"] = res[
		"physical_health_and_absence_multiplier"
	]
	stress_risks_affecting_work["physical_health_and_management_support_multiplier"] = (
		res["physical_health_and_management_support_multiplier"]
	)
	stress_risks_affecting_work["physical_health_multiplier"] = res[
		"physical_health_multiplier"
	]
	stress_risks_affecting_work["privacy_multiplier"] = res["privacy_multiplier"]
	stress_risks_affecting_work["responsibility_for_children_multiplier"] = res[
		"responsibility_for_children_multiplier"
	]
	stress_risks_affecting_work["support_network_multiplier"] = res[
		"support_network_multiplier"
	]
	stress_risks_affecting_work["team_and_colleague_support_multiplier"] = res[
		"team_and_colleague_support_multiplier"
	]
	stress_risks_affecting_work["training_multiplier"] = res["training_multiplier"]

	environment["absence"] = res["absence"]
	environment["absence_and_support"] = res["absence_and_support"]
	environment["absence_multiplier"] = res["absence_multiplier"]
	environment["colleague_trust"] = res["colleague_trust"]
	environment["complexity"] = res["complexity"]
	environment["complexity_training_hours_and_flexibility"] = res[
		"complexity_training_hours_and_flexibility"
	]
	environment["complexity_plus_training"] = res["complexity_plus_training"]
	environment["consultation"] = res["consultation"]
	environment["control_and_autonomy_over_working_hours"] = res[
		"control_and_autonomy_over_working_hours"
	]
	environment["covid"] = res["covid"]
	environment["covid_multiplier"] = res["covid_multiplier"]
	environment["culture_multiplier"] = res["culture_multiplier"]
	environment["culture"] = res["culture"]
	environment["environment"] = res["environment"]
	environment["environment_multiplier"] = res["environment_multiplier"]
	environment["health_and_safety"] = res["health_and_safety"]
	environment["health_and_safety_multiplier"] = res["health_and_safety_multiplier"]
	environment["hours_and_flexibility"] = res["hours_and_flexibility"]
	environment["lone_working"] = res["lone_working"]
	environment["lone_working_and_wider_team_support_multiplier"] = res[
		"lone_working_and_wider_team_support_multiplier"
	]
	environment["management_support"] = res["management_support"]
	environment["management_support_multiplier"] = res["management_support_multiplier"]
	environment["managerial_trust"] = res["managerial_trust"]
	environment["overtime"] = res["overtime"]
	environment["pay"] = res["pay"]
	environment["pay_and_childcare_multiplier"] = res["pay_and_childcare_multiplier"]
	environment["pay_multiplier"] = res["pay_multiplier"]
	environment["privacy"] = res["privacy"]
	environment["privacy_multiplier"] = res["privacy_multiplier"]
	environment["residence"] = res["residence"]
	environment["sick_leave_and_employer_support"] = res[
		"sick_leave_and_employer_support"
	]
	environment["team_and_colleague_support"] = res["team_and_colleague_support"]
	environment["team_and_colleague_support_multiplier"] = res[
		"team_and_colleague_support_multiplier"
	]
	environment["team_morale"] = res["team_morale"]
	environment["training"] = res["training"]
	environment["training_multiplier"] = res["training_multiplier"]
	environment["travel_to_work"] = res["travel_to_work"]
	environment["wider_team_support"] = res["wider_team_support"]
	environment["willingness_to_progress"] = res["willingness_to_progress"]
	environment["work_breaks"] = res["work_breaks"]
	environment["work_related_stress_impacting_family_and_relationships"] = res[
		"work_related_stress_impacting_family_and_relationships"
	]
	environment["work_related_stress_impacting_personal_life"] = res[
		"work_related_stress_impacting_personal_life"
	]
	environment["work_related_stress_impacting_social_life"] = res[
		"work_related_stress_impacting_social_life"
	]
	environment["workload"] = res["workload"]
	environment["manageable_workload"] = res["manageable_workload"]

	presenteeism["manageable_workload"] = res["manageable_workload"]
	presenteeism["work_breaks"] = res["work_breaks"]
	presenteeism["work_commitments_as_a_barrier_for_holidays"] = res[
		"work_commitments_as_a_barrier_for_holidays"
	]
	presenteeism["mental_health"] = res["mental_health"]
	presenteeism["physical_health"] = res["physical_health"]
	presenteeism["overtime"] = res["overtime"]
	presenteeism["sick_leave_and_employer_support"] = res[
		"sick_leave_and_employer_support"
	]
	presenteeism["control_and_autonomy_over_working_hours"] = res[
		"control_and_autonomy_over_working_hours"
	]
	presenteeism["financial_position_as_a_barrier_for_holidays"] = res[
		"financial_position_as_a_barrier_for_holidays"
	]
	presenteeism["physical_health_factors_impacting_work"] = res[
		"physical_health_factors_impacting_work"
	]
	presenteeism["fertility_and_pregnancy_impacting_work"] = res[
		"fertility_and_pregnancy_impacting_work"
	]
	presenteeism["mental_health_factors_impacting_work"] = res[
		"mental_health_factors_impacting_work"
	]
	presenteeism["management_support"] = res["management_support"]

	family["childcare"] = res["childcare"]
	family["childcare_multiplier"] = res["childcare_multiplier"]
	family["family"] = res["family"]
	family["family_factors"] = res["family_factors"]
	family["family_multiplier"] = res["family_multiplier"]
	family["family_support_companion"] = res["family_support_companion"]
	family["responsibility_for_children_multiplier"] = res[
		"responsibility_for_children_multiplier"
	]
	family["responsibility_for_family"] = res["responsibility_for_family"]
	family["responsibility_of_children"] = res["responsibility_of_children"]
	family["support_network"] = res["support_network"]
	family["support_network_multiplier"] = res["support_network_multiplier"]

	health["abuse_and_trauma"] = res["abuse_and_trauma"]
	health["abuse_and_trauma_and_management_support_and_culture"] = res[
		"abuse_and_trauma_and_management_support_and_culture"
	]
	health["abuse_and_trauma_and_management_support_multiplier"] = res[
		"abuse_and_trauma_and_management_support_multiplier"
	]
	health["abuse_and_trauma_impact"] = res["abuse_and_trauma_impact"]
	health["fertility_and_pregnancy"] = res["fertility_and_pregnancy"]
	health["fertility_and_pregnancy_impacting_work"] = res[
		"fertility_and_pregnancy_impacting_work"
	]
	health["health"] = res["health"]
	health["mental_and_physical_health"] = res["mental_and_physical_health"]
	health["mental_and_physical_health_and_absence_from_work"] = res[
		"mental_and_physical_health_and_absence_from_work"
	]
	health["mental_and_physical_health_multiplier"] = res[
		"mental_and_physical_health_multiplier"
	]
	health["mental_health"] = res["mental_health"]
	health["mental_health_and_absence_multiplier"] = res[
		"mental_health_and_absence_multiplier"
	]
	health["mental_health_and_culture_multiplier"] = res[
		"mental_health_and_culture_multiplier"
	]
	health["mental_health_factors_impacting_work"] = res[
		"mental_health_factors_impacting_work"
	]
	health["mental_health_multiplier"] = res["mental_health_multiplier"]
	health["mental_health_physical_health_and_culture_multiplier"] = res[
		"mental_health_physical_health_and_culture_multiplier"
	]
	health["physical_health"] = res["physical_health"]
	health["physical_health_and_absence_multiplier"] = res[
		"physical_health_and_absence_multiplier"
	]
	health["physical_health_and_culture"] = res["physical_health_and_culture"]
	health["physical_health_and_management_support_multiplier"] = res[
		"physical_health_and_management_support_multiplier"
	]
	health["physical_health_condition_affecting_work"] = res[
		"physical_health_condition_affecting_work"
	]
	health["physical_health_factors_impacting_work"] = res[
		"physical_health_factors_impacting_work"
	]
	health["physical_health_multiplier"] = res["physical_health_multiplier"]
	health["pregnancy_and_management_support"] = res["pregnancy_and_management_support"]
	health["pregnancy_and_physical_health"] = res["pregnancy_and_physical_health"]
	health["pregnancy_and_mental_health"] = res["pregnancy_and_mental_health"]
	health["pregnancy_impact"] = res["pregnancy_impact"]
	health["self_care"] = res["self_care"]
	health["self_care_and_mental_health"] = res["self_care_and_mental_health"]
	health["self_care_and_physical_health"] = res["self_care_and_physical_health"]

	personal["age_discrimination"] = res["age_discrimination"]
	personal["carer"] = res["carer"]
	personal["disability_discrimination"] = res["disability_discrimination"]
	personal["discrimination"] = res["discrimination"]
	personal["discrimination_work_impact"] = res["discrimination_work_impact"]
	personal["emotional_distress"] = res["emotional_distress"]
	personal["emotional_distress_multiplier"] = res["emotional_distress_multiplier"]
	personal["emotional_health"] = res["emotional_health"]
	personal["emotional_health_and_culture_at_work"] = res[
		"emotional_health_and_culture_at_work"
	]
	personal["emotional_health_multiplier"] = res["emotional_health_multiplier"]
	personal["emotional_wellbeing"] = res["emotional_wellbeing"]
	personal["emotional_wellbeing_and_management_support"] = res[
		"emotional_wellbeing_and_management_support"
	]
	personal["emotional_wellbeing_multiplier"] = res["emotional_wellbeing_multiplier"]
	personal["financial_position_as_a_barrier_for_holidays"] = res[
		"financial_position_as_a_barrier_for_holidays"
	]
	personal["gender_discrimination"] = res["gender_discrimination"]
	personal["hobbies"] = res["hobbies"]
	personal["holidays"] = res["holidays"]
	personal["holidays_and_pay"] = res["holidays_and_pay"]
	personal["identity"] = res["identity"]
	personal["identity_and_management_support"] = res["identity_and_management_support"]
	personal["other_discrimination"] = res["other_discrimination"]
	personal["personal"] = res["personal"]
	personal["personal_barriers"] = res["personal_barriers"]
	personal["personal_finances"] = res["personal_finances"]
	personal["personal_finances_and_pay_and_childcare_multiplier"] = res[
		"personal_finances_and_pay_and_childcare_multiplier"
	]
	personal["personal_finances_and_pay_multiplier"] = res[
		"personal_finances_and_pay_multiplier"
	]
	personal["personal_finances_and_responsibility_for_children"] = res[
		"personal_finances_and_responsibility_for_children"
	]
	personal["personal_multiplier"] = res["personal_multiplier"]
	personal["personal_relationships"] = res["personal_relationships"]
	personal["personal_relationships_and_working_relationships_impact"] = res[
		"personal_relationships_and_working_relationships_impact"
	]
	personal["personal_satisfaction"] = res["personal_satisfaction"]
	personal["personal_satisfaction_improvement"] = res[
		"personal_satisfaction_improvement"
	]
	personal["problem_solving"] = res["problem_solving"]
	personal["race_discrimination"] = res["race_discrimination"]
	personal["sexual_discrimination"] = res["sexual_discrimination"]
	personal["work_commitments_as_a_barrier_for_holidays"] = res[
		"work_commitments_as_a_barrier_for_holidays"
	]

	wider_risks["emotional_distress_multiplier"] = res["emotional_distress_multiplier"]
	wider_risks["emotional_health_multiplier"] = res["emotional_health_multiplier"]
	wider_risks["responsibility_for_children_multiplier"] = res[
		"responsibility_for_children_multiplier"
	]
	wider_risks["family_multiplier"] = res["family_multiplier"]
	wider_risks["personal_multiplier"] = res["personal_multiplier"]
	wider_risks["emotional_wellbeing_multiplier"] = res["emotional_wellbeing_multiplier"]
	wider_risks["support_network_multiplier"] = res["support_network_multiplier"]
	wider_risks["mental_health_and_culture_multiplier"] = res[
		"mental_health_and_culture_multiplier"
	]
	wider_risks["absence_multiplier"] = res["absence_multiplier"]
	wider_risks["abuse_and_trauma_and_management_support_multiplier"] = res[
		"abuse_and_trauma_and_management_support_multiplier"
	]
	wider_risks["childcare_multiplier"] = res["childcare_multiplier"]
	wider_risks["covid_multiplier"] = res["covid_multiplier"]
	wider_risks["culture_multiplier"] = res["culture_multiplier"]
	wider_risks["environment_multiplier"] = res["environment_multiplier"]
	wider_risks["health_and_safety_multiplier"] = res["health_and_safety_multiplier"]
	wider_risks["lone_working_and_wider_team_support_multiplier"] = res[
		"lone_working_and_wider_team_support_multiplier"
	]
	wider_risks["management_support_multiplier"] = res["management_support_multiplier"]
	wider_risks["mental_and_physical_health_multiplier"] = res[
		"mental_and_physical_health_multiplier"
	]
	wider_risks["mental_health_and_absence_multiplier"] = res[
		"mental_health_and_absence_multiplier"
	]
	wider_risks["mental_health_multiplier"] = res["mental_health_multiplier"]
	wider_risks["mental_health_physical_health_and_culture_multiplier"] = res[
		"mental_health_physical_health_and_culture_multiplier"
	]
	wider_risks["pay_and_childcare_multiplier"] = res["pay_and_childcare_multiplier"]
	wider_risks["pay_multiplier"] = res["pay_multiplier"]
	wider_risks["personal_finances_and_pay_and_childcare_multiplier"] = res[
		"personal_finances_and_pay_and_childcare_multiplier"
	]
	wider_risks["personal_finances_and_pay_multiplier"] = res[
		"personal_finances_and_pay_multiplier"
	]
	wider_risks["physical_health_and_absence_multiplier"] = res[
		"physical_health_and_absence_multiplier"
	]
	wider_risks["physical_health_and_management_support_multiplier"] = res[
		"physical_health_and_management_support_multiplier"
	]
	wider_risks["physical_health_multiplier"] = res["physical_health_multiplier"]
	wider_risks["privacy_multiplier"] = res["privacy_multiplier"]
	wider_risks["team_and_colleague_support_multiplier"] = res[
		"team_and_colleague_support_multiplier"
	]
	wider_risks["training_multiplier"] = res["training_multiplier"]

	return {
		"stress_and_wellbeing": [
			{"attr": key, "val": value} for key, value in stress_and_wellbeing.items()
		],
		"workplace_stress_factors": [
			{"attr": key, "val": value} for key, value in workplace_stress_factors.items()
		],
		"stress_risks_affecting_work": [
			{"attr": key, "val": value} for key, value in stress_risks_affecting_work.items()
		],
		"presenteeism": [
			{"attr": key, "val": value} for key, value in presenteeism.items()
		],
		"environment": [{"attr": key, "val": value} for key, value in environment.items()],
		"family": [{"attr": key, "val": value} for key, value in family.items()],
		"health": [{"attr": key, "val": value} for key, value in health.items()],
		"personal": [{"attr": key, "val": value} for key, value in personal.items()],
		"wider_risks": [{"attr": key, "val": value} for key, value in wider_risks.items()],
	}
