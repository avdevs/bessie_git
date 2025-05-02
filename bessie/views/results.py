import json
from functools import lru_cache
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
    company = Company.objects.get(pk=id)
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

        if form_type == "stress_and_wellbeing_form":
            form = StressAndWellbeingRiskForm(request.POST)
            if form.is_valid():
                risk_summary.stress_and_wellbeing_risk_level = form.cleaned_data[
                    "stress_and_wellbeing_risk_level"
                ]
                risk_summary.stress_and_wellbeing_in_place = form.cleaned_data[
                    "stress_and_wellbeing_risk_in_place"
                ]
                risk_summary.stress_and_wellbeing_recommendations = form.cleaned_data[
                    "stress_and_wellbeing_risk_recommendations"
                ]
                risk_summary.stress_and_wellbeing_risk_date = form.cleaned_data[
                    "stress_and_wellbeing_risk_date"
                ]
                risk_summary.save()

                messages.success(
                    request, "Stress and wellbeing summary updated successfully."
                )
                return redirect("company_results", id=id)
            else:
                print("FORM INVALID", form.errors)
                stress_and_wellbeing_form = form
        elif form_type == "workplace_stress_form":
            form = WorkplaceStressRiskForm(request.POST)
            if form.is_valid():
                risk_summary.workplace_stress_risk_level = form.cleaned_data[
                    "workplace_stress_risk_level"
                ]
                risk_summary.workplace_stress_in_place = form.cleaned_data[
                    "workplace_stress_in_place"
                ]
                risk_summary.workplace_stress_recommendations = form.cleaned_data[
                    "workplace_stress_recommendations"
                ]
                risk_summary.workplace_stress_risk_date = form.cleaned_data[
                    "workplace_stress_risk_date"
                ]
                risk_summary.save()

                messages.success(
                    request, "Workplace stress summary updated successfully."
                )
                return redirect("company_results", id=id)
            else:
                workplace_stress_form = form
        elif form_type == "presenteeism_form":
            form = PresenteeismRiskForm(request.POST)
            if form.is_valid():
                risk_summary.presenteeism_risk_level = form.cleaned_data[
                    "presenteeism_risk_level"
                ]
                risk_summary.presenteeism_in_place = form.cleaned_data[
                    "presenteeism_in_place"
                ]
                risk_summary.presenteeism_recommendations = form.cleaned_data[
                    "presenteeism_recommendations"
                ]
                risk_summary.presenteeism_risk_date = form.cleaned_data[
                    "presenteeism_risk_date"
                ]
                risk_summary.save()

                messages.success(request, "Presenteeism summary updated successfully.")
                return redirect("company_results", id=id)
            else:
                presenteeism_form = form
        elif form_type == "wider_risks_form":
            form = WiderRisksForm(request.POST)
            if form.is_valid():
                risk_summary.wider_risks_risk_level = form.cleaned_data[
                    "wider_risks_risk_level"
                ]
                risk_summary.wider_risks_in_place = form.cleaned_data[
                    "wider_risks_in_place"
                ]
                risk_summary.wider_risks_recommendations = form.cleaned_data[
                    "wider_risks_recommendations"
                ]
                risk_summary.wider_risks_risk_date = form.cleaned_data[
                    "wider_risks_risk_date"
                ]
                risk_summary.save()

                messages.success(request, "Wider risks summary updated successfully.")
                return redirect("company_results", id=id)
            else:
                wider_risks_form = form

    query = Q(company_id=id)
    if team:
        query &= Q(response__employee__team=team)

    result = BessieResult.objects.filter(query).aggregate(
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
        sick_leave_and_employer_support=Avg(
            "sick_leave_and_employer_support", default=0
        ),
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
        pregnancy_and_management_support=Avg(
            "pregnancy_and_management_support", default=0
        ),
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
        identity_and_management_support=Avg(
            "identity_and_management_support", default=0
        ),
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

    texts = {}

    for key, value in result.items():
        cat = get_category(value)
        pres = report_text.get(key)
        if pres:
            texts[key] = {"content": report_text[key][cat]["team"], "category": cat}
            texts[f"{key}_overview"] = report_text[key]["overview"]

    stats = _get_field_statistics(id, team)

    res = process_results(result)
    stats = process_results(stats)

    environment_stressload = calculate_stress_load(stats.get("environment", []))
    health_stressload = calculate_stress_load(stats.get("health", []))
    family_stressload = calculate_stress_load(stats.get("family", []))
    personal_stressload = calculate_stress_load(stats.get("personal", []))

    return render(
        request,
        "bessie/company_results.html",
        {
            "stress_and_wellbeing": json.dumps(res["stress_and_wellbeing"]),
            "stress_risks_affecting_work": json.dumps(
                res["stress_risks_affecting_work"]
            ),
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
        employee = Employee.objects.get(user=request.user)
    else:
        User = get_user_model()
        user = User.objects.get(email=employee_id)
        employee = Employee.objects.get(user=user)

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

    res = process_results(results)

    can_see_result = (
        employee.company.results_visible if not request.user.is_staff else True
    )

    return render(
        request,
        "bessie/result.html",
        {
            "stress_and_wellbeing": json.dumps(res["stress_and_wellbeing"]),
            "stress_risks_affecting_work": json.dumps(
                res["stress_risks_affecting_work"]
            ),
            "workplace_stress_factors": json.dumps(res["workplace_stress_factors"]),
            "presenteeism_factors": json.dumps(res["presenteeism"]),
            "environment_factors": json.dumps(res["environment"]),
            "family_factors": json.dumps(res["family"]),
            "health_factors": json.dumps(res["health"]),
            "personal_factors": json.dumps(res["personal"]),
            "wider_risks_factors": json.dumps(res["wider_risks"]),
            "report_text": json.dumps(texts),
            "potential_cost": round(results["potential_cost"]) if results else 0,
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
        sick_leave_and_employer_support=Avg(
            "sick_leave_and_employer_support", default=0
        ),
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
        pregnancy_and_management_support=Avg(
            "pregnancy_and_management_support", default=0
        ),
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
        identity_and_management_support=Avg(
            "identity_and_management_support", default=0
        ),
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


@lru_cache(maxsize=32)
def get_field_statistics_cached(company_id, team=None):
    """
    Cached wrapper for getting field statistics.
    Uses lru_cache to prevent recalculating stats for the same company/team.
    """
    return _get_field_statistics(company_id, team)


def _get_field_statistics(companyId, team=None):
    """
    Get statistics for all fields using more efficient queries.

    This implementation reduces the number of database queries by using Django's
    conditional expressions and aggregation functions more effectively.
    """
    # Create the base query
    query = Q(company_id=companyId)
    if team:
        query &= Q(response__employee__team=team)

    # Define the thresholds for categories
    THRESHOLDS = {"low": 25.0, "medium": 50.0, "high": 75.0}

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

    result = {}

    # Process fields in batches to avoid too many annotations in a single query
    BATCH_SIZE = 10
    field_batches = [
        fields[i : i + BATCH_SIZE] for i in range(0, len(fields), BATCH_SIZE)
    ]

    for batch in field_batches:
        # Create a single query with annotations for this batch of fields
        query_obj = BessieResult.objects.filter(query)

        # Add annotations for each field - create low/medium/high/very_high counts
        annotate_dict = {}
        for field in batch:
            annotate_dict[f"{field}_low"] = Count(
                Case(
                    When(**{f"{field}__lte": THRESHOLDS["low"]}, then=1),
                    output_field=IntegerField(),
                )
            )
            annotate_dict[f"{field}_medium"] = Count(
                Case(
                    When(
                        **{
                            f"{field}__gt": THRESHOLDS["low"],
                            f"{field}__lte": THRESHOLDS["medium"],
                        },
                        then=1,
                    ),
                    output_field=IntegerField(),
                )
            )
            annotate_dict[f"{field}_high"] = Count(
                Case(
                    When(
                        **{
                            f"{field}__gt": THRESHOLDS["medium"],
                            f"{field}__lte": THRESHOLDS["high"],
                        },
                        then=1,
                    ),
                    output_field=IntegerField(),
                )
            )
            annotate_dict[f"{field}_very_high"] = Count(
                Case(
                    When(**{f"{field}__gt": THRESHOLDS["high"]}, then=1),
                    output_field=IntegerField(),
                )
            )

        # Execute the query with all annotations for this batch
        stats = (
            query_obj.annotate(**annotate_dict).values(*annotate_dict.keys()).first()
        )

        # Extract the results for each field
        for field in batch:
            if stats:
                result[field] = {
                    "low_count": stats.get(f"{field}_low", 0),
                    "medium_count": stats.get(f"{field}_medium", 0),
                    "high_count": stats.get(f"{field}_high", 0),
                    "very_high": stats.get(f"{field}_very_high", 0),
                }
            else:
                # Default values if no stats are available
                result[field] = {
                    "low_count": 0,
                    "medium_count": 0,
                    "high_count": 0,
                    "very_high": 0,
                }

    return result


def process_results(result_data):
    """
    Process result data into categorized format more efficiently.

    Args:
        result_data: Dictionary of field results

    Returns:
        Dictionary with categories as keys and lists of field data as values
    """
    # Define all category dictionaries
    categories = {
        "stress_and_wellbeing": {},
        "workplace_stress_factors": {},
        "stress_risks_affecting_work": {},
        "presenteeism": {},
        "environment": {},
        "family": {},
        "health": {},
        "personal": {},
        "wider_risks": {},
    }

    # Process stress and wellbeing fields
    stress_and_wellbeing_fields = [
        "emotional_distress",
        "emotional_health",
        "mental_health",
        "physical_health",
        "self_care",
    ]
    for field in stress_and_wellbeing_fields:
        if field in result_data:
            categories["stress_and_wellbeing"][field] = result_data[field]

    # Process workplace stress factors
    workplace_stress_fields = [
        "absence",
        "carer",
        "childcare",
        "complexity",
        "covid",
        "culture",
        "discrimination",
        "health_and_safety",
        "hours_and_flexibility",
        "management_support",
        "pay",
        "personal_finances",
        "training",
        "workload",
    ]
    for field in workplace_stress_fields:
        if field in result_data:
            categories["workplace_stress_factors"][field] = result_data[field]

    # Process stress risks affecting work (all multiplier fields)
    for field in result_data:
        if "_multiplier" in field:
            categories["stress_risks_affecting_work"][field] = result_data[field]

    # Process presenteeism fields
    presenteeism_fields = [
        "manageable_workload",
        "work_breaks",
        "work_commitments_as_a_barrier_for_holidays",
        "mental_health",
        "physical_health",
        "overtime",
        "sick_leave_and_employer_support",
        "control_and_autonomy_over_working_hours",
        "financial_position_as_a_barrier_for_holidays",
        "physical_health_factors_impacting_work",
        "fertility_and_pregnancy_impacting_work",
        "mental_health_factors_impacting_work",
        "management_support",
    ]
    for field in presenteeism_fields:
        if field in result_data:
            categories["presenteeism"][field] = result_data[field]

    # Process environment fields
    environment_fields = [
        "absence",
        "absence_and_support",
        "absence_multiplier",
        "colleague_trust",
        "complexity",
        "complexity_training_hours_and_flexibility",
        "complexity_plus_training",
        "consultation",
        "control_and_autonomy_over_working_hours",
        "covid",
        "covid_multiplier",
        "culture_multiplier",
        "culture",
        "environment",
        "environment_multiplier",
        "health_and_safety",
        "health_and_safety_multiplier",
        "hours_and_flexibility",
        "lone_working",
        "lone_working_and_wider_team_support_multiplier",
        "management_support",
        "management_support_multiplier",
        "managerial_trust",
        "overtime",
        "pay",
        "pay_and_childcare_multiplier",
        "pay_multiplier",
        "privacy",
        "privacy_multiplier",
        "residence",
        "sick_leave_and_employer_support",
        "team_and_colleague_support",
        "team_and_colleague_support_multiplier",
        "team_morale",
        "training",
        "training_multiplier",
        "travel_to_work",
        "wider_team_support",
        "willingness_to_progress",
        "work_breaks",
        "work_related_stress_impacting_family_and_relationships",
        "work_related_stress_impacting_personal_life",
        "work_related_stress_impacting_social_life",
        "workload",
        "manageable_workload",
    ]
    for field in environment_fields:
        if field in result_data:
            categories["environment"][field] = result_data[field]

    # Process family fields
    family_fields = [
        "childcare",
        "childcare_multiplier",
        "family",
        "family_factors",
        "family_multiplier",
        "family_support_companion",
        "responsibility_for_children_multiplier",
        "responsibility_for_family",
        "responsibility_of_children",
        "support_network",
        "support_network_multiplier",
    ]
    for field in family_fields:
        if field in result_data:
            categories["family"][field] = result_data[field]

    # Process health fields
    health_fields = [
        "abuse_and_trauma",
        "abuse_and_trauma_and_management_support_and_culture",
        "abuse_and_trauma_and_management_support_multiplier",
        "abuse_and_trauma_impact",
        "fertility_and_pregnancy",
        "fertility_and_pregnancy_impacting_work",
        "health",
        "mental_and_physical_health",
        "mental_and_physical_health_and_absence_from_work",
        "mental_and_physical_health_multiplier",
        "mental_health",
        "mental_health_and_absence_multiplier",
        "mental_health_and_culture_multiplier",
        "mental_health_factors_impacting_work",
        "mental_health_multiplier",
        "mental_health_physical_health_and_culture_multiplier",
        "physical_health",
        "physical_health_and_absence_multiplier",
        "physical_health_and_culture",
        "physical_health_and_management_support_multiplier",
        "physical_health_condition_affecting_work",
        "physical_health_factors_impacting_work",
        "physical_health_multiplier",
        "pregnancy_and_management_support",
        "pregnancy_and_physical_health",
        "pregnancy_and_mental_health",
        "pregnancy_impact",
        "self_care",
        "self_care_and_mental_health",
        "self_care_and_physical_health",
    ]
    for field in health_fields:
        if field in result_data:
            categories["health"][field] = result_data[field]

    # Process personal fields
    personal_fields = [
        "age_discrimination",
        "carer",
        "disability_discrimination",
        "discrimination",
        "discrimination_work_impact",
        "emotional_distress",
        "emotional_distress_multiplier",
        "emotional_health",
        "emotional_health_and_culture_at_work",
        "emotional_health_multiplier",
        "emotional_wellbeing",
        "emotional_wellbeing_and_management_support",
        "emotional_wellbeing_multiplier",
        "financial_position_as_a_barrier_for_holidays",
        "gender_discrimination",
        "hobbies",
        "holidays",
        "holidays_and_pay",
        "identity",
        "identity_and_management_support",
        "other_discrimination",
        "personal",
        "personal_barriers",
        "personal_finances",
        "personal_finances_and_pay_and_childcare_multiplier",
        "personal_finances_and_pay_multiplier",
        "personal_finances_and_responsibility_for_children",
        "personal_multiplier",
        "personal_relationships",
        "personal_relationships_and_working_relationships_impact",
        "personal_satisfaction",
        "personal_satisfaction_improvement",
        "problem_solving",
        "race_discrimination",
        "sexual_discrimination",
        "work_commitments_as_a_barrier_for_holidays",
    ]
    for field in personal_fields:
        if field in result_data:
            categories["personal"][field] = result_data[field]

    # Process wider risks fields
    wider_risk_fields = [
        "emotional_distress",
        "emotional_health",
        "responsibility_of_children",
        "family",
        "personal",
        "emotional_wellbeing",
        "support_network",
        "mental_health_and_culture_multiplier",
        "absence",
        "abuse_and_trauma_and_management_support_multiplier",
        "childcare",
        "covid",
        "culture",
        "environment",
        "health_and_safety",
        "lone_working_and_wider_team_support_multiplier",
        "management_support",
        "mental_and_physical_health",
        "mental_health_and_absence_multiplier",
        "mental_health",
        "mental_health_physical_health_and_culture_multiplier",
        "pay_and_childcare_multiplier",
        "pay",
        "personal_finances_and_pay_and_childcare_multiplier",
        "personal_finances_and_pay_multiplier",
        "physical_health_and_absence_multiplier",
        "physical_health_and_management_support_multiplier",
        "physical_health",
        "privacy",
        "team_and_colleague_support",
        "training",
    ]
    for field in wider_risk_fields:
        if field in result_data:
            categories["wider_risks"][field] = result_data[field]

    # Convert dictionaries to lists of objects for JSON serialization
    return {
        category: [{"attr": key, "val": value} for key, value in fields.items()]
        for category, fields in categories.items()
    }
