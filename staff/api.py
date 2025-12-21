from django.shortcuts import get_object_or_404

from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from staff.models import Department
from staff.serializers import DepartmentSerializer, EmployeeSerializer


class DepartmentDataAPIView(APIView):
    """API для получения данных о подразделении"""

    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        dept_id = request.query_params.get('id')

        if not dept_id:
            return Response({'error': 'ID parameter is required'}, status=400)

        department = get_object_or_404(Department, id=dept_id)
        children = department.get_children()
        employees = department.employees.all()

        children_data = DepartmentSerializer(children, many=True).data
        employees_data = EmployeeSerializer(employees, many=True).data

        return Response({'children': children_data, 'employees': employees_data})
