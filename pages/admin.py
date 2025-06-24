from django.contrib import admin
from .models import CaseStudy, OrgQuizTakers

# Register your models here.
@admin.register(CaseStudy)
class CaseStudyAdmin(admin.ModelAdmin):
    list_display = ["title", "highlight"]

@admin.register(OrgQuizTakers)
class OrgQuizTakersAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "org", "position", "email", "consent", "proceed"]