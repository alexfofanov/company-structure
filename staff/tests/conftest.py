from datetime import date

import pytest
from rest_framework.test import APIClient

from staff.models import Department, Employee


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(username='testuser', password='password')


@pytest.fixture
def structure():
    root = Department.objects.create(name="Root")
    child = Department.objects.create(name="Child", parent=root)
    emp = Employee.objects.create(
        full_name="Worker",
        position="Dev",
        salary=100,
        hire_date=date.today(),
        department=root
    )
    return {'root': root, 'child': child, 'emp': emp}
