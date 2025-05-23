from django import forms
from django.core.exceptions import ValidationError


class CompanyForm(forms.Form):
  name = forms.CharField(
      max_length=256,
      widget=forms.TextInput(attrs={"placeholder": "Enter company name"}),
  )
  slots = forms.IntegerField(
      widget=forms.NumberInput(attrs={"placeholder": "Enter number of slots"})
  )
  survey_start_date = forms.DateField(
      widget=forms.DateInput(attrs={"type": "date"}), label="Select Date"
  )
  survey_completion_date = forms.DateField(
      widget=forms.DateInput(attrs={"type": "date"}), label="Select Date"
  )
  strategy_meeting_date = forms.DateField(
      widget=forms.DateInput(attrs={"type": "date"}), label="Select Date"
  )
  first_name = forms.CharField(
      max_length=256,
      widget=forms.TextInput(attrs={"placeholder": "Enter first name"}),
  )
  last_name = forms.CharField(
      max_length=256, widget=forms.TextInput(attrs={"placeholder": "Enter last name"})
  )
  email = forms.CharField(
      max_length=256,
      widget=forms.EmailInput(attrs={"placeholder": "Enter email address"}),
  )

  def clean(self):
    cleaned_data = super().clean()
    survey_start = cleaned_data.get("survey_start_date")
    survey_completion = cleaned_data.get("survey_completion_date")
    strategy_meeting = cleaned_data.get("strategy_meeting_date")

    # Only perform validation if all date fields have values
    if survey_start and survey_completion and strategy_meeting:
      # Validate that survey_start_date is not after survey_completion_date
      if survey_start > survey_completion:
        raise ValidationError(
            "Survey start date cannot be after survey completion date."
        )

      # Validate that strategy_meeting_date is not before survey_completion_date
      if strategy_meeting < survey_completion:
        raise ValidationError(
            "Strategy meeting date must be after survey completion date."
        )

      # Validate that strategy_meeting_date is not before survey_start_date
      if strategy_meeting < survey_start:
        raise ValidationError(
            "Strategy meeting date must be after survey start date."
        )

    return cleaned_data


class AdminInviteForm(forms.Form):
  company_id = forms.CharField(widget=forms.HiddenInput())
  first_name = forms.CharField(
      max_length=256,
      widget=forms.TextInput(attrs={"placeholder": "Enter first name"}),
  )
  last_name = forms.CharField(
      max_length=256, widget=forms.TextInput(attrs={"placeholder": "Enter last name"})
  )
  email = forms.CharField(
      max_length=256,
      widget=forms.EmailInput(attrs={"placeholder": "Enter email address"}),
  )
