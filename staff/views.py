from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .models import Department


def index(request: HttpRequest) -> HttpResponse:
    """Главная страница"""

    roots = Department.objects.root_nodes()
    return render(request, 'staff/index.html', {'roots': roots})
