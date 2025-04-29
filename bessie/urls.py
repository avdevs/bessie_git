from django.urls import path

from .views import (
    BessieQuestionaireWizard,
    user_list,
    view_company_results,
    export_data,
    CompanyFormView,
    company_detail,
    toggle_company_results_visible,
)


from .forms import *


urlpatterns = [
    # path('dashboard/', dashboard, name='dashboard'),
    path(
        "take-quiz/",
        BessieQuestionaireWizard.as_view(
            [
                Form1,
                Form2,
                Form3,
                Form4,
                Form5,
                Form6,
                Form7,
                Form8,
                Form9,
                Form10,
                Form11,
                Form12,
                Form13,
                Form14,
                Form15,
                Form16,
                Form17,
                Form18,
                Form19,
                Form20,
                Form21,
                Form22,
                Form23,
                Form24,
                Form25,
                Form26,
                Form27,
            ]
        ),
        name="take_quiz",
    ),
    path("export-data/<int:id>", export_data, name="export_data"),  # Export CSV data
    # path("my-result/", user_results, name="user_results"),
    path("company/<int:id>/users/", user_list, name="user_list"),
    path("company-result/<int:id>", view_company_results, name="company_results"),
    path(
        "company-result-toggle/<int:id>",
        toggle_company_results_visible,
        name="toggle-company-results-visible",
    ),
    path("create-company/", CompanyFormView.as_view(), name="create_company"),
    path("company/<int:id>", company_detail, name="company"),
]
