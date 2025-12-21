from django.urls import path

from . import views
from .api import DepartmentDataAPIView

urlpatterns = [
    path('', views.index, name='index'),
    path('api/node-data/', DepartmentDataAPIView.as_view(), name='api-node-data'),
]
