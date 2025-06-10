import csv
from io import StringIO

from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from bessie.models import BessieResponse, BessieResult, Employee


@login_required
def export_data(request, id):
  """
  Export employee data (their scores and calculations) to a csv file
  """
  employee = get_object_or_404(Employee, pk=id)

  if not request.user.is_staff and request.user != employee.user:
    raise PermissionDenied("You do not have permission to access this data")

  try:
    bessie_response = get_object_or_404(BessieResponse, employee=employee)
    sorted_questions = bessie_response.get_sorted_questions()

    bessie_result = get_object_or_404(BessieResult, response=bessie_response)
    result = model_to_dict(bessie_result)

    # Remove internal fields that shouldn't be exported
    result.pop("id", None)
    result.pop("response", None)

    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(["Question", "Score"])
    for question, answer in sorted_questions.items():
      writer.writerow([question, answer])

    writer.writerow([""])
    writer.writerow(["--------------------------------"])
    writer.writerow([""])

    writer.writerow(["Category", "Score"])
    for key, value in result.items():
      if value is not None:
        formatted_key = key.replace("_", " ").capitalize()
        writer.writerow([formatted_key, value])

    response = HttpResponse(output.getvalue(), content_type="text/csv")
    response["Content-Disposition"] = (
        f'attachment; filename="employee_{id}_data.csv"'
    )

    return response

  except Exception as e:
    import logging

    logger = logging.getLogger(__name__)
    logger.error(f"Error exporting data for employee {id}: {str(e)}")

    raise Http404("Employee data could not be exported")
