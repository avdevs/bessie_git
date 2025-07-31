import json

from django.shortcuts import render
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from formtools.wizard.views import SessionWizardView

from bessie.forms import get_choice_score

from .models import CaseStudy, OrgQuizTakers


class HomePageView(TemplateView):
  template_name = "pages/home.html"


class BessiePageView(TemplateView):
  template_name = "pages/bessie.html"


class MiniBessiePageView(TemplateView):
  template_name = "pages/mini_bessie.html"


# class ContactUsPageView(TemplateView):
#     template_name = "pages/contact_us.html"


class AboutPageView(TemplateView):
  template_name = "pages/about.html"


class OurServicesPageView(TemplateView):
  template_name = "pages/our_services.html"


class TermsAndConditionsPageView(TemplateView):
  template_name = "pages/terms_and_conditions.html"


class CaseStudiesPageView(ListView):
  model = CaseStudy
  paginate_by = 6
  template_name = "pages/case_studies.html"


class WellbeingCalenderPageView(TemplateView):
  template_name = "pages/wellbeing_calender.html"


class CaseStudyPageView(DetailView):
  model = CaseStudy
  template_name = "pages/case_study.html"

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context["now"] = timezone.now()
    return context


class QuizPageView(SessionWizardView):
  template_name = "pages/quiz.html"

  def _get_question_score(self, form_data, key, default=0):
    """Get score for a single question key, handling choice identifiers."""
    value = form_data.get(key, default)
    if isinstance(value, str):
      score = get_choice_score(value)
      if score != value and score is not None:  # If mapping found
        return int(score)
      else:
        # Try to convert string to int, fallback to default
        try:
          return int(value)
        except (ValueError, TypeError):
          return int(default)
    return int(value) if value is not None else int(default)

  def done(self, form_list, **kwargs):
    # Extract cleaned data from all forms
    form_data = {}
    for form in form_list:
      form_data = {**form_data, **form.cleaned_data}

    quiz_taker = OrgQuizTakers(
      first_name=form_data.get("first_name"),
      last_name=form_data.get("last_name"),
      email=form_data.get("email"),
      consent=form_data.get("consent", False),
    )
    quiz_taker.save()

    workplace_env = (
      self._get_question_score(form_data, "q1")
      + self._get_question_score(form_data, "q2")
      + self._get_question_score(form_data, "q3")
    )
    org_polices = self._get_question_score(form_data, "q4") + self._get_question_score(
      form_data, "q5"
    )
    leadership_app = (
      self._get_question_score(form_data, "q6")
      + self._get_question_score(form_data, "q7")
      + self._get_question_score(form_data, "q8")
      + self._get_question_score(form_data, "q9")
    )
    training_and_dev = self._get_question_score(form_data, "q10")
    performance_management = self._get_question_score(
      form_data, "q11"
    ) + self._get_question_score(form_data, "q12")
    workplace_culture = self._get_question_score(
      form_data, "q13"
    ) + self._get_question_score(form_data, "q14")
    impact_assessment = self._get_question_score(
      form_data, "q15"
    ) + self._get_question_score(form_data, "q16")
    future_planning = (
      self._get_question_score(form_data, "q17")
      + self._get_question_score(form_data, "q18")
      + self._get_question_score(form_data, "q19")
    )

    results = list()
    results.append(workplace_env)
    results.append(org_polices)
    results.append(leadership_app)
    results.append(training_and_dev)
    results.append(performance_management)
    results.append(workplace_culture)
    results.append(impact_assessment)
    results.append(future_planning)

    return render(
      self.request,
      "pages/done.html",
      {
        "results": json.dumps(results),
      },
    )

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
