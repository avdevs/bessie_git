from django.urls import path
from .views import calculate_scores

urlpatterns = [
    path('quiz/', calculate_scores, name='calculate_scores')
]