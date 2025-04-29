from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from formtools.wizard.views import SessionWizardView
from django.utils.safestring import mark_safe

from ..utils import calc_potential_cost

from bessie.models import BessieResponse, BessieResult, Employee, WizardState


class BessieQuestionaireWizard(LoginRequiredMixin, SessionWizardView):
    template_name = "bessie/form.html"

    def get_user_state(self):
        """Retrieve or create the wizard state for the current user."""
        if self.request.user.is_authenticated:
            state, created = WizardState.objects.get_or_create(user=self.request.user)
            return state
        return None

    def process_step(self, form):
        current_data = form.cleaned_data
        if self.request.user.is_authenticated:
            state = self.get_user_state()
            if state:
                state.data[self.steps.current] = current_data
                state.step = self.steps.current
                state.save()
        return self.get_form_step_data(form)

    def get_form_initial(self, step):
        """Load initial data from the database."""
        if self.request.user.is_authenticated:
            state = self.get_user_state()
            if state and state.data:
                return state.data.get(step, {})
        return super().get_form_initial(step)

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)

        # Add custom HTML for the current form
        output = []
        elrsCount = 0
        for field in form:
            widget_type = field.field.widget.__class__.__name__
            help_text = (
                f'<p class="help-text">{field.help_text}</p>' if field.help_text else ""
            )
            label = str(field.label_tag())
            field_html = str(field)
            errors = "".join(f'<p class="error">{e}</p>' for e in field.errors)

            output.append(help_text)

            if widget_type == "ExternalLabelRadioSelect":
                # if elrsCount == 0:
                # elrsCount += 1
                # output.append('<div class="frm_likert__heading form-field"><div class="frm_primary_label"></div>\
                #     <div class="opt-group"><div class="frm_likert__column">Strongly Agree</div><div class="frm_likert__column">Agree</div><div class="frm_likert__column">Somewhat Agree</div><div class="frm_likert__column">\
                # 	Neither Agree Nor Disagree</div><div class="frm_likert__column">Somewhat Disagree</div><div class="frm_likert__column">\
                # 	Disagree</div><div class="frm_likert__column">Strongly Disagree</div></div></div>')
                output.append(
                    f'<div class="form-group" id="{field.name}"><div class="label-opt-cont">{label}{field_html}</div>{errors}</div>'
                )
            else:
                elrsCount = 0
                output.append(
                    f'<div class="form-group" id="{field.name}">{label}{field_html}{errors}</div>'
                )

        context["custom_form"] = mark_safe("\n".join(output))
        return context

    def _calculate_percentage(self, score, max_score):
        """Calculate a percentage score, handling division by zero."""
        if max_score == 0:
            return 0
        return round((score / max_score) * 100, 2)

    def _sum_question_scores(self, form_data, question_keys):
        """Sum scores for a list of question keys."""
        return sum(int(form_data.get(key, 0)) for key in question_keys)

    def _calculate_multiplier(self, score, multiplier_val, max_score):
        """Calculate a multiplier score and percentage."""
        if score == 0:
            return 0, 0

        multiplier_score = score * multiplier_val
        return multiplier_score, self._calculate_percentage(multiplier_score, max_score)

    def done(self, form_list, **kwargs):
        # Clean up wizard state
        if self.request.user.is_authenticated:
            state = self.get_user_state()
            if state:
                state.delete()

        # Extract cleaned data from all forms
        form_data = {}
        for form in form_list:
            form_data = {**form_data, **form.cleaned_data}

        form_data = {k: (0 if v == "" else v) for k, v in form_data.items()}
        employee = Employee.objects.get(user=self.request.user)

        # Delete previous responses
        BessieResponse.objects.filter(employee=employee).delete()

        # Create new response
        response = BessieResponse(
            employee=employee,
            multichoice=form_data,
            q1=form_data.get("q1", ""),
            q14=form_data.get("q14", ""),
            q45=form_data.get("q45", ""),
            q66=form_data.get("q66", ""),
            q74=form_data.get("q74", ""),
            q100=form_data.get("q100", ""),
            q154=form_data.get("q154", ""),
            q159=form_data.get("q159", ""),
            q167=form_data.get("q167", ""),
            q168=form_data.get("q168", ""),
            q176=form_data.get("q176", ""),
            q228=form_data.get("q228", ""),
        )
        response.save()

        # Create results record
        results = BessieResult(response=response, company=employee.company)

        # Get important multiplier values that are used in multiple calculations
        q63_response = int(form_data.get("q63", 0))
        q97_response = int(form_data.get("q97", 0))
        q112_response = int(form_data.get("q112", 0))
        q121_response = int(form_data.get("q121", 0))
        q132_response = int(form_data.get("q132", 0))
        q140_response = int(form_data.get("q140", 0))
        q156_response = int(form_data.get("q156", 0))
        q225_response = int(form_data.get("q225", 0))

        # ===== ENVIRONMENT CALCULATIONS =====
        environment_questions = [f"q{i}" for i in range(2, 66)]
        max_environment_score = 311
        total_environment_score = 0

        for question_key in environment_questions:
            value = form_data.get(question_key)
            if value is not None:
                if isinstance(value, int):
                    total_environment_score += value
                elif isinstance(value, str) and value.isdigit():
                    total_environment_score += int(value)

        results.environment = self._calculate_percentage(
            total_environment_score, max_environment_score
        )

        # Environment Multiplier
        max_environment_multiplier_score = 1244
        environment_multiplier_score = total_environment_score * q63_response
        results.environment_multiplier = self._calculate_percentage(
            environment_multiplier_score, max_environment_multiplier_score
        )

        # ===== PRIVACY CALCULATIONS =====
        privacy_questions = ["q6", "q7", "q8"]
        max_privacy_score = 18
        total_privacy_score = self._sum_question_scores(form_data, privacy_questions)

        results.privacy = self._calculate_percentage(
            total_privacy_score, max_privacy_score
        )

        # Privacy Multiplier
        max_privacy_multiplier_score = 72
        privacy_multiplier_score = total_privacy_score * q63_response
        results.privacy_multiplier = self._calculate_percentage(
            privacy_multiplier_score, max_privacy_multiplier_score
        )

        # ===== TRAVEL CALCULATIONS =====
        travel_questions = ["q10", "q11", "q12"]
        max_travel_score = 13
        total_travel_score = self._sum_question_scores(form_data, travel_questions)
        results.travel_to_work = self._calculate_percentage(
            total_travel_score, max_travel_score
        )

        # ===== RESIDENCE CALCULATIONS =====
        residence_questions = ["q2", "q3", "q4", "q5"]
        max_residence_score = 24
        total_residence_score = self._sum_question_scores(
            form_data, residence_questions
        )
        results.residence = self._calculate_percentage(
            total_residence_score, max_residence_score
        )

        # ===== PAY CALCULATIONS =====
        potential_cost = calc_potential_cost(int(form_data.get("q17", 0)))
        results.potential_cost = (
            0.0 if potential_cost is None else float(potential_cost)
        )

        pay_questions = ["q15", "q16", "q17", "q18", "q19", "q20"]
        max_pay_score = 18
        total_pay_score = self._sum_question_scores(form_data, pay_questions)
        results.pay = self._calculate_percentage(total_pay_score, max_pay_score)

        # Pay Multiplier
        max_pay_multiplier_score = 72
        pay_multiplier_score = total_pay_score * q63_response
        results.pay_multiplier = self._calculate_percentage(
            pay_multiplier_score, max_pay_multiplier_score
        )

        # ===== CHILDCARE CALCULATIONS =====
        childcare_questions = ["q80", "q88", "q89"]
        max_childcare_score = 14
        total_childcare_score = self._sum_question_scores(
            form_data, childcare_questions
        )
        results.childcare = self._calculate_percentage(
            total_childcare_score, max_childcare_score
        )

        # Pay and Childcare Multiplier
        pay_childcare_multiplier_score = 0
        if total_pay_score > 0 and total_childcare_score > 0:
            pay_childcare_multiplier_score = (
                total_pay_score + total_childcare_score
            ) * q97_response

        max_pay_childcare_multiplier_score = 128
        results.pay_and_childcare_multiplier = self._calculate_percentage(
            pay_childcare_multiplier_score, max_pay_childcare_multiplier_score
        )

        # ===== COMPLEXITY CALCULATIONS =====
        complexity_questions = ["q31", "q32", "q33", "q34", "q35", "q36", "q37"]
        max_complexity_score = 42
        total_complexity_score = self._sum_question_scores(
            form_data, complexity_questions
        )
        results.complexity = self._calculate_percentage(
            total_complexity_score, max_complexity_score
        )

        # ===== HOURS AND FLEXIBILITY CALCULATIONS =====
        hours_flexibility_questions = ["q24", "q25", "q26", "q27", "q28", "q29", "q30"]
        max_hours_flexibility_score = 42
        total_hours_flexibility_score = self._sum_question_scores(
            form_data, hours_flexibility_questions
        )
        results.hours_and_flexibility = self._calculate_percentage(
            total_hours_flexibility_score, max_hours_flexibility_score
        )

        # Control and Autonomy over Working Hours
        control_autonomy_score = int(form_data.get("q25", 0))
        max_control_autonomy_score = 6
        results.control_and_autonomy_over_working_hours = self._calculate_percentage(
            control_autonomy_score, max_control_autonomy_score
        )

        # Workload
        workload_score = int(form_data.get("q29", 0))
        max_workload_score = 6
        results.workload = self._calculate_percentage(
            workload_score, max_workload_score
        )

        # Manageable Workload
        manageable_workload_questions = ["q28", "q29"]
        max_manageable_workload_score = 12
        total_manageable_workload_score = self._sum_question_scores(
            form_data, manageable_workload_questions
        )
        results.manageable_workload = self._calculate_percentage(
            total_manageable_workload_score, max_manageable_workload_score
        )

        # ===== TRAINING CALCULATIONS =====
        training_questions = ["q46", "q47", "q48"]
        max_training_score = 18
        total_training_score = self._sum_question_scores(form_data, training_questions)
        results.training = self._calculate_percentage(
            total_training_score, max_training_score
        )

        # Complexity plus Training
        complexity_plus_training_score = 0
        if total_complexity_score > 0:
            complexity_plus_training_score = (
                total_complexity_score + total_training_score
            )

        max_complexity_plus_training_score = 60
        results.complexity_plus_training = self._calculate_percentage(
            complexity_plus_training_score, max_complexity_plus_training_score
        )

        # Complexity + Training + Hours and Flexibility
        complexity_training_hours_flexibility_score = 0
        if total_complexity_score > 0:
            complexity_training_hours_flexibility_score = (
                total_complexity_score
                + total_training_score
                + total_hours_flexibility_score
            )

        max_complexity_training_hours_flexibility_score = 102
        results.complexity_training_hours_and_flexibility = self._calculate_percentage(
            complexity_training_hours_flexibility_score,
            max_complexity_training_hours_flexibility_score,
        )

        # ===== WORK PATTERNS CALCULATIONS =====
        # Work Breaks
        work_breaks_score = int(form_data.get("q28", 0))
        max_work_breaks_score = 6
        results.work_breaks = self._calculate_percentage(
            work_breaks_score, max_work_breaks_score
        )

        # Overtime
        overtime_score = int(form_data.get("q30", 0))
        max_overtime_score = 6
        results.overtime = self._calculate_percentage(
            overtime_score, max_overtime_score
        )

        # ===== TEAM AND MANAGEMENT SUPPORT CALCULATIONS =====
        # Team and Colleague Support
        team_support_questions = ["q41", "q42", "q43", "q51", "q52"]
        max_team_support_score = 30
        total_team_support_score = self._sum_question_scores(
            form_data, team_support_questions
        )
        results.team_and_colleague_support = self._calculate_percentage(
            total_team_support_score, max_team_support_score
        )

        # Management Support
        management_support_questions = ["q39", "q40", "q43", "q44", "q50", "q56"]
        max_management_support_score = 36
        total_management_support_score = self._sum_question_scores(
            form_data, management_support_questions
        )
        results.management_support = self._calculate_percentage(
            total_management_support_score, max_management_support_score
        )

        # Management Support Multiplier
        management_support_multiplier_score = (
            total_management_support_score * q63_response
        )
        max_management_support_multiplier_score = 144
        results.management_support_multiplier = self._calculate_percentage(
            management_support_multiplier_score, max_management_support_multiplier_score
        )

        # ===== CULTURE CALCULATIONS =====
        culture_questions = ["q50", "q51", "q52", "q53"]
        max_culture_score = 24
        total_culture_score = self._sum_question_scores(form_data, culture_questions)
        results.culture = self._calculate_percentage(
            total_culture_score, max_culture_score
        )

        # Culture Multiplier
        culture_multiplier_score = total_culture_score * q63_response
        max_culture_multiplier_score = 96
        results.culture_multiplier = self._calculate_percentage(
            culture_multiplier_score, max_culture_multiplier_score
        )

        # ===== PROBLEM SOLVING CALCULATIONS =====
        problem_solving_questions = ["q182", "q183"]
        total_problem_solving_score = self._sum_question_scores(
            form_data, problem_solving_questions
        )
        max_problem_solving_score = 12
        results.problem_solving = self._calculate_percentage(
            total_problem_solving_score, max_problem_solving_score
        )

        # ===== TRUST AND MORALE CALCULATIONS =====
        # Managerial Trust
        managerial_trust_score = int(form_data.get("q50", 0))
        max_managerial_trust_score = 6
        results.managerial_trust = self._calculate_percentage(
            managerial_trust_score, max_managerial_trust_score
        )

        # Colleague Trust
        colleague_trust_score = int(form_data.get("q51", 0))
        max_colleague_trust_score = 6
        results.colleague_trust = self._calculate_percentage(
            colleague_trust_score, max_colleague_trust_score
        )

        # Consultation
        consultation_score = int(form_data.get("q44", 0))
        max_consultation_score = 6
        results.consultation = self._calculate_percentage(
            consultation_score, max_consultation_score
        )

        # Team Morale
        team_morale_score = int(form_data.get("q52", 0))
        max_team_morale_score = 6
        results.team_morale = self._calculate_percentage(
            team_morale_score, max_team_morale_score
        )

        # Willingness to Progress
        willingness_to_progress_score = int(form_data.get("q48", 0))
        max_willingness_to_progress_score = 6
        results.willingness_to_progress = self._calculate_percentage(
            willingness_to_progress_score, max_willingness_to_progress_score
        )

        # ===== LONE WORKING AND TEAM SUPPORT CALCULATIONS =====
        # Lone Working
        lone_working_score = int(form_data.get("q49", 0))
        max_lone_working_score = 6
        results.lone_working = self._calculate_percentage(
            lone_working_score, max_lone_working_score
        )

        # Wider Team Support
        wider_team_support_score = int(form_data.get("q53", 0))
        max_wider_team_support_score = 6
        results.wider_team_support = self._calculate_percentage(
            wider_team_support_score, max_wider_team_support_score
        )

        # Lone Working and Wider Team Support Multiplier
        lone_wider_support_multiplier_score = 0
        if lone_working_score > 0:
            lone_wider_support_multiplier_score = (
                lone_working_score + wider_team_support_score
            ) * q63_response

        max_lone_wider_support_multiplier_score = 48
        results.lone_working_and_wider_team_support_multiplier = (
            self._calculate_percentage(
                lone_wider_support_multiplier_score,
                max_lone_wider_support_multiplier_score,
            )
        )

        # Team and Colleague Support Multiplier
        team_colleague_support_multiplier_score = (
            total_team_support_score * q63_response
        )
        max_team_colleague_support_multiplier_score = 120
        results.team_and_colleague_support_multiplier = self._calculate_percentage(
            team_colleague_support_multiplier_score,
            max_team_colleague_support_multiplier_score,
        )

        # ===== HEALTH AND SAFETY CALCULATIONS =====
        health_safety_questions = ["q54", "q55", "q56"]
        max_health_safety_score = 18
        total_health_safety_score = self._sum_question_scores(
            form_data, health_safety_questions
        )
        results.health_and_safety = self._calculate_percentage(
            total_health_safety_score, max_health_safety_score
        )

        # Health and Safety Multiplier
        health_safety_multiplier_score = total_health_safety_score * q63_response
        max_health_safety_multiplier_score = 72
        results.health_and_safety_multiplier = self._calculate_percentage(
            health_safety_multiplier_score, max_health_safety_multiplier_score
        )

        # ===== ABSENCE CALCULATIONS =====
        absence_questions = ["q57", "q58"]
        max_absence_score = 12
        total_absence_score = self._sum_question_scores(form_data, absence_questions)
        results.absence = self._calculate_percentage(
            total_absence_score, max_absence_score
        )

        # Absence and Support
        q59_response = int(form_data.get("q59", 0))
        absence_and_support_score = (
            total_absence_score + q59_response if total_absence_score > 0 else 0
        )
        max_absence_and_support_score = 18
        results.absence_and_support = self._calculate_percentage(
            absence_and_support_score, max_absence_and_support_score
        )

        # Absence Multiplier
        absence_multiplier_score = (
            (total_absence_score + q59_response) * q63_response
            if total_absence_score > 0
            else 0
        )
        max_absence_multiplier_score = 72
        results.absence_multiplier = self._calculate_percentage(
            absence_multiplier_score, max_absence_multiplier_score
        )

        # Sick Leave and Employer Support
        sick_leave_support_score = int(form_data.get("q59", 0))
        max_sick_leave_support_score = 6
        results.sick_leave_and_employer_support = self._calculate_percentage(
            sick_leave_support_score, max_sick_leave_support_score
        )

        # ===== COVID CALCULATIONS =====
        covid_score = int(form_data.get("q60", 0)) + int(form_data.get("q61", 0))
        max_covid_score = 8
        results.covid = self._calculate_percentage(covid_score, max_covid_score)

        # Covid Multiplier
        covid_multiplier_score = covid_score * q63_response
        max_covid_multiplier_score = 32
        results.covid_multiplier = self._calculate_percentage(
            covid_multiplier_score, max_covid_multiplier_score
        )

        # ===== WORK-RELATED STRESS IMPACT CALCULATIONS =====
        # Work-Related Stress Impacting personal life
        work_stress_personal_life_score = total_environment_score * q63_response
        max_work_stress_personal_life_score = 1244
        results.work_related_stress_impacting_personal_life = (
            self._calculate_percentage(
                work_stress_personal_life_score, max_work_stress_personal_life_score
            )
        )

        # Get Q62, Q64 responses
        q62_response = int(form_data.get("q62", 0))
        q64_response = int(form_data.get("q64", 0))

        # Work-Related Stress Impacting Family and Relationships
        work_stress_family_score = total_environment_score * q62_response
        max_work_stress_family_score = 1244
        results.work_related_stress_impacting_family_and_relationships = (
            self._calculate_percentage(
                work_stress_family_score, max_work_stress_family_score
            )
        )

        # Work-Related Stress Impacting Social Life
        work_stress_social_life_score = total_environment_score * q64_response
        max_work_stress_social_life_score = 1244
        results.work_related_stress_impacting_social_life = self._calculate_percentage(
            work_stress_social_life_score, max_work_stress_social_life_score
        )

        # ===== MENTAL HEALTH CALCULATIONS =====
        mental_health_questions = [
            "q114",
            "q115",
            "q116",
            "q117",
            "q118",
            "q119",
            "q120",
            "q121",
            "q122",
        ]
        max_mental_health_score = 30
        total_mental_health_score = self._sum_question_scores(
            form_data, mental_health_questions
        )
        results.mental_health = self._calculate_percentage(
            total_mental_health_score, max_mental_health_score
        )

        # Mental Health Multiplier
        mental_health_multiplier_score = total_mental_health_score * q121_response
        max_mental_health_multiplier_score = 120
        results.mental_health_multiplier = self._calculate_percentage(
            mental_health_multiplier_score, max_mental_health_multiplier_score
        )

        # ===== CARER CALCULATION =====
        carer_score = int(form_data.get("q83", 0)) + int(form_data.get("q198", 0))
        max_carer_score = 6
        results.carer = self._calculate_percentage(carer_score, max_carer_score)

        # ===== PHYSICAL HEALTH CALCULATIONS =====
        physical_health_questions = [
            "q104",
            "q105",
            "q106",
            "q107",
            "q108",
            "q109",
            "q110",
            "q111",
            "q112",
            "q113",
        ]
        max_physical_health_score = 28
        total_physical_health_score = self._sum_question_scores(
            form_data, physical_health_questions
        )
        results.physical_health = self._calculate_percentage(
            total_physical_health_score, max_physical_health_score
        )

        # Physical Health Multiplier
        physical_health_multiplier_score = total_physical_health_score * q112_response
        max_physical_health_multiplier_score = 112
        results.physical_health_multiplier = self._calculate_percentage(
            physical_health_multiplier_score, max_physical_health_multiplier_score
        )

        # Physical Health and Absence Multiplier
        physical_absence_multiplier_score = (
            (total_physical_health_score + total_absence_score) * q112_response
            if total_absence_score > 0
            else 0
        )
        max_physical_absence_multiplier_score = 160
        results.physical_health_and_absence_multiplier = self._calculate_percentage(
            physical_absence_multiplier_score, max_physical_absence_multiplier_score
        )

        # ===== MENTAL AND PHYSICAL HEALTH COMBINED CALCULATIONS =====
        # Mental and Physical Health
        mental_physical_health_score = (
            total_mental_health_score + total_physical_health_score
        )
        max_mental_physical_health_score = 58
        results.mental_and_physical_health = self._calculate_percentage(
            mental_physical_health_score, max_mental_physical_health_score
        )

        # Mental and Physical Health Multiplier
        mental_physical_health_multiplier_score = (
            mental_physical_health_score * q156_response
        )
        max_mental_physical_health_multiplier_score = 232
        results.mental_and_physical_health_multiplier = self._calculate_percentage(
            mental_physical_health_multiplier_score,
            max_mental_physical_health_multiplier_score,
        )

        # ===== FAMILY SUPPORT CALCULATIONS =====
        # Family Support Companion
        family_support_questions = ["q75", "q76"]
        max_family_support_score = 4
        total_family_support_score = self._sum_question_scores(
            form_data, family_support_questions
        )
        results.family_support_companion = self._calculate_percentage(
            total_family_support_score, max_family_support_score
        )

        # Responsibility of Children
        responsibility_children_questions = ["q77", "q78", "q79", "q80", "q81", "q82"]
        max_responsibility_children_score = 17
        total_responsibility_children_score = self._sum_question_scores(
            form_data, responsibility_children_questions
        )
        results.responsibility_of_children = self._calculate_percentage(
            total_responsibility_children_score, max_responsibility_children_score
        )

        # Responsibility for Children Multiplier
        responsibility_children_multiplier_score = (
            total_responsibility_children_score * q97_response
        )
        max_responsibility_children_multiplier_score = 68
        results.responsibility_for_children_multiplier = self._calculate_percentage(
            responsibility_children_multiplier_score,
            max_responsibility_children_multiplier_score,
        )

        # Childcare Multiplier (note: childcare score was calculated above)
        childcare_multiplier_score = total_childcare_score * q97_response
        max_childcare_multiplier_score = 56
        results.childcare_multiplier = self._calculate_percentage(
            childcare_multiplier_score, max_childcare_multiplier_score
        )

        # ===== EMOTIONAL HEALTH CALCULATIONS =====
        emotional_health_questions = ["q204", "q205", "q206", "q207", "q208"]
        max_emotional_health_score = 10
        total_emotional_health_score = self._sum_question_scores(
            form_data, emotional_health_questions
        )
        results.emotional_health = self._calculate_percentage(
            total_emotional_health_score, max_emotional_health_score
        )

        # Emotional Health Multiplier
        emotional_health_multiplier_score = total_emotional_health_score * q225_response
        max_emotional_health_multiplier_score = 40
        results.emotional_health_multiplier = self._calculate_percentage(
            emotional_health_multiplier_score, max_emotional_health_multiplier_score
        )

        # ===== PERSONAL SATISFACTION CALCULATIONS =====
        personal_satisfaction_score = int(form_data.get("q202", 0))
        max_personal_satisfaction_score = 6
        results.personal_satisfaction = self._calculate_percentage(
            personal_satisfaction_score, max_personal_satisfaction_score
        )

        # Personal Satisfaction Improvement
        personal_satisfaction_improvement_score = personal_satisfaction_score + int(
            form_data.get("q203", 0)
        )
        max_personal_satisfaction_improvement_score = 12
        results.personal_satisfaction_improvement = self._calculate_percentage(
            personal_satisfaction_improvement_score,
            max_personal_satisfaction_improvement_score,
        )

        # ===== PERSONAL FINANCES CALCULATIONS =====
        personal_finances_questions = ["q184", "q185", "q186", "q187"]
        max_personal_finances_score = 12
        total_personal_finances_score = self._sum_question_scores(
            form_data, personal_finances_questions
        )
        results.personal_finances = self._calculate_percentage(
            total_personal_finances_score, max_personal_finances_score
        )

        # Personal Finances and Responsibility for Children
        finances_children_score = (
            total_personal_finances_score + total_responsibility_children_score
            if total_personal_finances_score > 0
            else 0
        )
        max_finances_children_score = 29
        results.personal_finances_and_responsibility_for_children = (
            self._calculate_percentage(
                finances_children_score, max_finances_children_score
            )
        )

        # Personal Finances and Pay Multiplier
        finances_pay_multiplier_score = (
            total_personal_finances_score * pay_multiplier_score
            if total_personal_finances_score > 0
            else 0
        )
        max_finances_pay_multiplier_score = 864
        results.personal_finances_and_pay_multiplier = self._calculate_percentage(
            finances_pay_multiplier_score, max_finances_pay_multiplier_score
        )

        # ===== BARRIERS CALCULATIONS =====
        barriers_questions = [
            "q189",
            "q190",
            "q191",
            "q192",
            "q193",
            "q194",
            "q195",
            "q196",
        ]
        max_barriers_score = 48
        total_barriers_score = self._sum_question_scores(form_data, barriers_questions)
        results.personal_barriers = self._calculate_percentage(
            total_barriers_score, max_barriers_score
        )

        # ===== EMOTIONAL WELLBEING CALCULATIONS =====
        emotional_wellbeing_questions = [
            "q215",
            "q216",
            "q217",
            "q218",
            "q219",
            "q220",
            "q221",
            "q222",
            "q223",
        ]
        max_emotional_wellbeing_score = 31
        total_emotional_wellbeing_score = self._sum_question_scores(
            form_data, emotional_wellbeing_questions
        )
        results.emotional_wellbeing = self._calculate_percentage(
            total_emotional_wellbeing_score, max_emotional_wellbeing_score
        )

        # Emotional Wellbeing Multiplier
        emotional_wellbeing_multiplier_score = (
            total_emotional_wellbeing_score * q225_response
        )
        max_emotional_wellbeing_multiplier_score = 124
        results.emotional_wellbeing_multiplier = self._calculate_percentage(
            emotional_wellbeing_multiplier_score,
            max_emotional_wellbeing_multiplier_score,
        )

        # ===== HOLIDAYS CALCULATIONS =====
        holiday_questions = ["q198", "q199", "q200", "q201"]
        max_holiday_score = 20
        total_holiday_score = self._sum_question_scores(form_data, holiday_questions)
        results.holidays = self._calculate_percentage(
            total_holiday_score, max_holiday_score
        )

        # Financial Position as a Barrier for Holidays
        financial_position_barrier_score = int(form_data.get("q199", 0))
        max_financial_position_barrier_score = 6
        results.financial_position_as_a_barrier_for_holidays = (
            self._calculate_percentage(
                financial_position_barrier_score, max_financial_position_barrier_score
            )
        )

        # Work Commitments as a Barrier for Holidays
        work_commitment_barrier_for_holidays_score = int(form_data.get("q200", 0))
        max_work_commitment_barrier_for_holidays_score = 6
        results.work_commitments_as_a_barrier_for_holidays = self._calculate_percentage(
            work_commitment_barrier_for_holidays_score,
            max_work_commitment_barrier_for_holidays_score,
        )

        # ===== IDENTITY CALCULATIONS =====
        identity_questions = [
            "q162",
            "q163",
            "q164",
            "q165",
            "q166",
            "q169",
            "q170",
            "q171",
            "q172",
            "q173",
            "q174",
            "q175",
        ]
        max_identity_score = 39
        total_identity_score = self._sum_question_scores(form_data, identity_questions)
        results.identity = self._calculate_percentage(
            total_identity_score, max_identity_score
        )

        # Identity and Management Support
        identity_management_support_score = (
            total_identity_score + total_management_support_score
            if total_identity_score > 0
            else 0
        )
        max_identity_management_support_score = 75
        results.identity_and_management_support = self._calculate_percentage(
            identity_management_support_score, max_identity_management_support_score
        )

        # ===== DISCRIMINATION CALCULATIONS =====
        discrimination_questions = [
            "q169",
            "q170",
            "q171",
            "q172",
            "q173",
            "q174",
            "q175",
        ]
        max_discrimination_score = 15
        total_discrimination_score = self._sum_question_scores(
            form_data, discrimination_questions
        )
        results.discrimination = self._calculate_percentage(
            total_discrimination_score, max_discrimination_score
        )

        # Discrimination Work Impact
        discrimination_work_impact_score = (
            total_discrimination_score * q225_response
            if total_discrimination_score > 0
            else 0
        )
        max_discrimination_work_impact_score = 60
        results.discrimination_work_impact = self._calculate_percentage(
            discrimination_work_impact_score, max_discrimination_work_impact_score
        )

        # Specific discrimination types
        discrimination_types = {
            "age": ("q170", 8),
            "race": ("q171", 8),
            "disability": ("q172", 8),
            "gender": ("q173", 8),
            "sexual": ("q174", 8),
            "other": ("q175", 8),
        }

        for disc_type, (q_key, max_score) in discrimination_types.items():
            disc_score = int(form_data.get(q_key, 0)) * q225_response
            setattr(
                results,
                f"{disc_type}_discrimination",
                self._calculate_percentage(disc_score, max_score),
            )

        # ===== PERSONAL RELATIONSHIPS CALCULATIONS =====
        personal_relationships_questions = ["q177", "q178", "q179", "q180", "q181"]
        max_personal_relationships_score = 22
        total_personal_relationships_score = self._sum_question_scores(
            form_data, personal_relationships_questions
        )
        results.personal_relationships = self._calculate_percentage(
            total_personal_relationships_score, max_personal_relationships_score
        )

        # Personal Relationships and Working Relationships Impact
        personal_work_relationships_impact_score = 0
        if total_personal_relationships_score > 0:
            personal_work_relationships_impact_score = (
                total_personal_relationships_score + int(form_data.get("q179", 0))
            )
        max_personal_work_relationships_impact_score = 132
        results.personal_relationships_and_working_relationships_impact = (
            self._calculate_percentage(
                personal_work_relationships_impact_score,
                max_personal_work_relationships_impact_score,
            )
        )

        # ===== EMOTIONAL DISTRESS CALCULATIONS =====
        emotional_distress_questions = ["q209", "q210", "q211", "q212", "q213", "q214"]
        max_emotional_distress_score = 12
        total_emotional_distress_score = self._sum_question_scores(
            form_data, emotional_distress_questions
        )
        results.emotional_distress = self._calculate_percentage(
            total_emotional_distress_score, max_emotional_distress_score
        )

        # Emotional Distress Multiplier
        emotional_distress_multiplier_score = (
            total_emotional_distress_score * q225_response
        )
        max_emotional_distress_multiplier_score = 48
        results.emotional_distress_multiplier = self._calculate_percentage(
            emotional_distress_multiplier_score, max_emotional_distress_multiplier_score
        )

        # ===== COMBINED CALCULATIONS =====
        # Holidays and Pay
        holidays_and_pay_score = (
            total_holiday_score + total_pay_score if total_holiday_score > 0 else 0
        )
        max_holidays_and_pay_score = 38
        results.holidays_and_pay = self._calculate_percentage(
            holidays_and_pay_score, max_holidays_and_pay_score
        )

        # Emotional Wellbeing and Management Support
        wellbeing_management_support_score = 0
        if total_emotional_wellbeing_score > 0:
            wellbeing_management_support_score = (
                total_emotional_wellbeing_score + total_management_support_score
            )

        max_wellbeing_management_support_score = 67
        results.emotional_wellbeing_and_management_support = self._calculate_percentage(
            wellbeing_management_support_score, max_wellbeing_management_support_score
        )

        # Mental and Physical Health and Absence
        mental_physical_absence_score = 0
        if mental_physical_health_score > 0:
            mental_physical_absence_score = (
                mental_physical_health_score + absence_and_support_score
            )

        max_mental_physical_absence_score = 76
        results.mental_and_physical_health_and_absence_from_work = (
            self._calculate_percentage(
                mental_physical_absence_score, max_mental_physical_absence_score
            )
        )

        # Mental Health and Culture Multiplier
        mental_health_culture_score = total_mental_health_score + total_culture_score
        max_mental_health_culture_score = 54
        results.mental_health_and_culture_multiplier = self._calculate_percentage(
            mental_health_culture_score, max_mental_health_culture_score
        )

        # ===== FERTILITY AND PREGNANCY CALCULATIONS =====
        fertility_questions = [
            "q123",
            "q124",
            "q125",
            "q126",
            "q127",
            "q128",
            "q129",
            "q130",
            "q131",
            "q132",
        ]
        max_fertility_score = 30
        total_fertility_score = self._sum_question_scores(
            form_data, fertility_questions
        )
        results.fertility_and_pregnancy = self._calculate_percentage(
            total_fertility_score, max_fertility_score
        )

        # Pregnancy Impact
        pregnancy_impact_score = (
            total_fertility_score * q132_response if total_fertility_score > 0 else 0
        )
        max_pregnancy_impact_score = 180
        results.pregnancy_impact = self._calculate_percentage(
            pregnancy_impact_score, max_pregnancy_impact_score
        )

        # Fertility and Pregnancy Impacting Work
        fertility_pregnancy_work_score = int(form_data.get("q132", 0))
        max_fertility_pregnancy_work_score = 6
        results.fertility_and_pregnancy_impacting_work = self._calculate_percentage(
            fertility_pregnancy_work_score, max_fertility_pregnancy_work_score
        )

        # ===== ABUSE AND TRAUMA CALCULATIONS =====
        abuse_trauma_questions = [
            "q134",
            "q135",
            "q136",
            "q137",
            "q138",
            "q139",
            "q140",
            "q141",
            "q142",
        ]
        max_abuse_trauma_score = 38
        total_abuse_trauma_score = self._sum_question_scores(
            form_data, abuse_trauma_questions
        )
        results.abuse_and_trauma = self._calculate_percentage(
            total_abuse_trauma_score, max_abuse_trauma_score
        )

        # Abuse and Trauma Impact
        abuse_trauma_impact_score = (
            total_abuse_trauma_score * q140_response
            if total_abuse_trauma_score > 0
            else 0
        )
        max_abuse_trauma_impact_score = 228
        results.abuse_and_trauma_impact = self._calculate_percentage(
            abuse_trauma_impact_score, max_abuse_trauma_impact_score
        )

        # Abuse and Trauma and Management Support and Culture
        abuse_trauma_management_culture_score = 0
        if total_abuse_trauma_score > 0:
            abuse_trauma_management_culture_score = (
                total_abuse_trauma_score + total_culture_score
            )

        max_abuse_trauma_management_culture_score = 62
        results.abuse_and_trauma_and_management_support_and_culture = (
            self._calculate_percentage(
                abuse_trauma_management_culture_score,
                max_abuse_trauma_management_culture_score,
            )
        )

        # Abuse and Trauma and Management Support Multiplier
        abuse_trauma_management_support_multiplier_score = 0
        if total_abuse_trauma_score > 0:
            abuse_trauma_management_support_multiplier_score = (
                total_abuse_trauma_score + total_management_support_score
            )

        max_abuse_trauma_management_support_multiplier_score = 74
        results.abuse_and_trauma_and_management_support_multiplier = (
            self._calculate_percentage(
                abuse_trauma_management_support_multiplier_score,
                max_abuse_trauma_management_support_multiplier_score,
            )
        )

        # ===== SELF-CARE CALCULATIONS =====
        self_care_questions = ["q143", "q144", "q145"]
        max_self_care_score = 18
        total_self_care_score = self._sum_question_scores(
            form_data, self_care_questions
        )
        results.self_care = self._calculate_percentage(
            total_self_care_score, max_self_care_score
        )

        # Self-Care and Physical Health
        self_care_physical_health_score = 0
        if total_self_care_score > 0:
            self_care_physical_health_score = (
                total_self_care_score + total_physical_health_score
            )

        max_self_care_physical_health_score = 46
        results.self_care_and_physical_health = self._calculate_percentage(
            self_care_physical_health_score, max_self_care_physical_health_score
        )

        # Self-Care and Mental Health
        self_care_mental_health_score = 0
        if total_self_care_score > 0:
            self_care_mental_health_score = (
                total_self_care_score + total_mental_health_score
            )

        max_self_care_mental_health_score = 48
        results.self_care_and_mental_health = self._calculate_percentage(
            self_care_mental_health_score, max_self_care_mental_health_score
        )

        # ===== EMOTIONAL HEALTH AND CULTURE AT WORK =====
        emotional_health_culture_score = 0
        if total_emotional_wellbeing_score > 0:
            emotional_health_culture_score = (
                total_emotional_wellbeing_score + total_culture_score
            )

        max_emotional_health_culture_score = 55
        results.emotional_health_and_culture_at_work = self._calculate_percentage(
            emotional_health_culture_score, max_emotional_health_culture_score
        )

        # ===== PHYSICAL HEALTH AND CULTURE =====
        physical_health_and_culture_work_score = (
            total_physical_health_score + total_culture_score
        ) * q63_response
        max_physical_health_and_culture_work_score = 208
        results.physical_health_and_culture = self._calculate_percentage(
            physical_health_and_culture_work_score,
            max_physical_health_and_culture_work_score,
        )

        # ===== PHYSICAL HEALTH FACTORS IMPACTING WORK =====
        physical_health_factors_impacting_work_score = int(form_data.get("q156", 0))
        max_physical_health_factors_impacting_work_score = 4
        results.physical_health_factors_impacting_work = self._calculate_percentage(
            physical_health_factors_impacting_work_score,
            max_physical_health_factors_impacting_work_score,
        )

        # Physical Health Condition Affecting Work
        physical_health_condition_affecting_work_score = int(form_data.get("q112", 0))
        max_physical_health_condition_affecting_work_score = 4
        results.physical_health_condition_affecting_work = self._calculate_percentage(
            physical_health_condition_affecting_work_score,
            max_physical_health_condition_affecting_work_score,
        )

        # Mental Health Factors Impacting Work
        mental_health_factors_impacting_work_score = int(form_data.get("q121", 0))
        max_mental_health_factors_impacting_work_score = 6
        results.mental_health_factors_impacting_work = self._calculate_percentage(
            mental_health_factors_impacting_work_score,
            max_mental_health_factors_impacting_work_score,
        )

        # ===== HEALTH CALCULATIONS =====
        health_questions = [f"q{i}" for i in range(101, 160)]
        max_health_score = 198
        total_health_score = 0

        for question_key in health_questions:
            value = form_data.get(question_key)
            if value is not None:
                if isinstance(value, int):
                    total_health_score += value
                elif isinstance(value, str) and value.isdigit():
                    total_health_score += int(value)

        results.health = self._calculate_percentage(
            total_health_score, max_health_score
        )

        # ===== PERSONAL CALCULATIONS =====
        personal_questions = [f"q{i}" for i in range(160, 228)]
        max_personal_score = 238
        total_personal_score = 0

        for question_key in personal_questions:
            value = form_data.get(question_key)
            if value is not None:
                if isinstance(value, int):
                    total_personal_score += value
                elif isinstance(value, str) and value.isdigit():
                    total_personal_score += int(value)

        results.personal = self._calculate_percentage(
            total_personal_score, max_personal_score
        )

        # Personal Multiplier
        personal_multiplier_score = total_personal_score * q225_response
        max_personal_multiplier_score = 952
        results.personal_multiplier = self._calculate_percentage(
            personal_multiplier_score, max_personal_multiplier_score
        )

        # ===== HOBBIES CALCULATIONS =====
        hobbies_score = int(form_data.get("q188", 0))
        max_hobbies_score = 2
        results.hobbies = self._calculate_percentage(hobbies_score, max_hobbies_score)

        # ===== MENTAL HEALTH AND ABSENCE MULTIPLIER =====
        mental_health_absence_multiplier_score = (
            total_mental_health_score + total_absence_score
        ) * q121_response
        max_mental_health_absence_multiplier_score = 168
        results.mental_health_and_absence_multiplier = self._calculate_percentage(
            mental_health_absence_multiplier_score,
            max_mental_health_absence_multiplier_score,
        )

        # ===== MENTAL HEALTH, PHYSICAL HEALTH AND CULTURE MULTIPLIER =====
        mental_physical_culture_multiplier_score = 0
        if total_mental_health_score + total_physical_health_score > 0:
            mental_physical_culture_multiplier_score = (
                total_mental_health_score
                + total_physical_health_score
                + total_culture_score
            ) * q63_response

        max_mental_physical_culture_multiplier_score = 328
        results.mental_health_physical_health_and_culture_multiplier = (
            self._calculate_percentage(
                mental_physical_culture_multiplier_score,
                max_mental_physical_culture_multiplier_score,
            )
        )

        # ===== PERSONAL FINANCES AND PAY, AND CHILDCARE MULTIPLIER =====
        personal_finances_pay_childcare_multiplier_score = (
            total_personal_finances_score * pay_childcare_multiplier_score
        )
        max_personal_finances_pay_childcare_multiplier_score = 1536
        results.personal_finances_and_pay_and_childcare_multiplier = (
            self._calculate_percentage(
                personal_finances_pay_childcare_multiplier_score,
                max_personal_finances_pay_childcare_multiplier_score,
            )
        )

        # ===== FAMILY CALCULATIONS =====
        # Family
        family_questions = [f"q{i}" for i in range(67, 100)]
        max_family_score = 112
        total_family_score = 0

        for question_key in family_questions:
            value = form_data.get(question_key)
            if value is not None:
                if isinstance(value, int):
                    total_family_score += value
                elif isinstance(value, str) and value.isdigit():
                    total_family_score += int(value)

        results.family = self._calculate_percentage(
            total_family_score, max_family_score
        )

        # Responsibility for family
        responsibility_family = ["q92", "q93", "q94", "q95"]
        max_responsibility_family_score = 16
        total_responsibility_family_score = self._sum_question_scores(
            form_data, responsibility_family
        )
        results.responsibility_for_family = self._calculate_percentage(
            total_responsibility_family_score, max_responsibility_family_score
        )

        # Family factors
        family_factors_score = 0
        if total_responsibility_children_score + total_responsibility_family_score > 0:
            family_factors_score = (
                total_responsibility_children_score
                + childcare_multiplier_score
                + total_responsibility_family_score
            )

        max_family_factors_score = 89
        results.family_factors = self._calculate_percentage(
            family_factors_score, max_family_factors_score
        )

        # Family multiplier
        family_multiplier_score = q97_response * total_family_score
        max_family_multiplier_score = 448
        results.family_multiplier = self._calculate_percentage(
            family_multiplier_score, max_family_multiplier_score
        )

        # Fix for personal working relationship impact score
        personal_working_relationship_impact_score = 0
        if total_personal_relationships_score > 0:
            personal_working_relationship_impact_score = (
                total_personal_relationships_score + int(form_data.get("q179", 0))
            )

        max_personal_working_relationship_impact_score = 328
        results.personal_relationships_and_working_relationships_impact = (
            self._calculate_percentage(
                personal_working_relationship_impact_score,
                max_personal_working_relationship_impact_score,
            )
        )

        # Save all results
        results.save()

        return redirect("bessie:results")
