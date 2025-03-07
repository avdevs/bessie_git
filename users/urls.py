from django.urls import path
from . import views
from .forms import CompanyForm, CustomSignUpForm
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('upload-csv/', views.inviteUsers, name='upload_csv'),
    path("signup/", views.RegistrationWizard.as_view([CustomSignUpForm, CompanyForm]), name="signup"),
    path("csv-smaple/", views.csvSample, name='csv_sample'),
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.html',
        html_email_template_name='registration/password_reset_email.html'
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]