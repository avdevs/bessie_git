from django.urls import path

from .views import *
from .forms import *

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("bessie/", BessiePageView.as_view(), name="bessie"),
    path("about/", AboutPageView.as_view(), name="about"),
    path("quiz", QuizPageView.as_view([Form1, Form2, Form3, Form4, Form5, Form6, Form7, Form8, Form9]), name="quiz"),
    path("case-studies/", CaseStudiesPageView.as_view(), name="case_studies"),
    path("case-studies/<slug:slug>/", CaseStudyPageView.as_view(), name="case_study"),
    path("our-services", OurServicesPageView.as_view(), name="our_services"),
    path("wellbeing-calender/", WellbeingCalenderPageView.as_view(), name="wellbeing_calender"),
    # path("contact-us", ContactUsPageView.as_view(), name="contact_us"),
    path("mini-bessie", MiniBessiePageView.as_view(), name="mini_bessie"),
    path("terms-and-conditions", TermsAndConditionsPageView.as_view(), name="tAndC"),
    path("faqs", FAQsPageView.as_view(), name="faqs"),
]