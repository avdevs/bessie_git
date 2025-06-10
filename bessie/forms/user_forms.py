from django import forms


class EmployeeLoginForm(forms.Form):
  unique_user_id = forms.IntegerField(widget=forms.NumberInput(
      attrs={"placeholder": "Unique User ID"}))
