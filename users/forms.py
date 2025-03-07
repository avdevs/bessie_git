from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms import ModelForm
from django import forms
from .models import User
from bessie.models import Company

class CustomSignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "first_name", 
            "last_name", 
            "email",
        ]

class CustomUserCreationForm(UserCreationForm):
    """
    Specify the user model created while adding a user
    on the admin page.
    """
    class Meta:
        model = User
        fields = [
            "first_name", 
            "last_name", 
            "email",
            "user_type",
            "password", 
            "is_staff",
            "is_active",
            "groups",
            "user_permissions"
        ]
class CustomUserChangeForm(UserChangeForm):
    """
    Specify the user model edited while editing a user on the
    admin page.
    """
    class Meta:
        model = User
        fields = [
            "first_name", 
            "last_name", 
            "email", 
            "user_type",
            "password",
            "is_staff",
            "is_active", 
            "groups",
            "user_permissions"
         ]
        

class BulkUserInviteForm(forms.Form):
    csv_file = forms.FileField(
        label='Select a CSV file',
        help_text='Maximum file size: 5 MB',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv'
        })
    )

    def clean_csv_file(self):
        csv_file = self.cleaned_data.get('csv_file')
        
        # Check file extension
        if not csv_file.name.endswith('.csv'):
            raise forms.ValidationError('Only CSV files are allowed.')
        
        # Optional: Check file size (5MB limit)
        if csv_file.size > 5 * 1024 * 1024:
            raise forms.ValidationError('File too large. Max size is 5 MB.')
        
        return csv_file
    
class CompanyForm(ModelForm):
    class Meta:
        model = Company
        fields = ["name"]