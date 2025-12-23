from django.urls import path

from . import views
from .api import DepartmentDataAPIView

urlpatterns = [
    path('', views.index, name='index'),
    path(
        'api/department-data/<int:pk>/',
        DepartmentDataAPIView.as_view(),
        name='api-department-data',
    ),
]
