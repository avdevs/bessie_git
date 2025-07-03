from django import forms


class EmployeeLoginForm(forms.Form):
	unique_user_id = forms.IntegerField(
		widget=forms.NumberInput(attrs={"placeholder": "Unique User ID"})
	)


class EmployeeForgotIDForm(forms.Form):
	email = forms.EmailField(
		widget=forms.EmailInput(attrs={"placeholder": "Email Address"})
	)
