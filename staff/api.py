from rest_framework.authentication import SessionAuthentication
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from staff.models import Department
from staff.serializers import DepartmentDetailsSerializer


class DepartmentDataAPIView(RetrieveAPIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = DepartmentDetailsSerializer

    def get_queryset(self):
        return Department.objects.prefetch_related('employees')
