from django.contrib import admin
from django.db.models import Count, QuerySet
from django.http import HttpRequest
from django.utils.html import format_html

from mptt.admin import DraggableMPTTAdmin, TreeRelatedFieldListFilter

from .models import Department, Employee


@admin.register(Department)
class DepartmentAdmin(DraggableMPTTAdmin):
    """Админка для подразделений"""

    mptt_indent_field = 'name'
    list_display = (
        'tree_actions',
        'indented_title',
        'employee_count_display',
    )
    list_display_links = ('indented_title',)
    search_fields = ('name',)

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        qs = super().get_queryset(request)
        return qs.annotate(employees_count=Count('employees'))

    @admin.display(description='Сотрудников', ordering='employees_count')
    def employee_count_display(self, obj: Department) -> str:
        """Показывает количество сотрудников и ссылку на них"""

        count = obj.employees_count
        if count > 0:
            url = f'/admin/staff/employee/?department__id__exact={obj.id}'
            return format_html('<a href="{}" title="Показать сотрудников">{} чел.</a>', url, count)
        return '—'


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """Админка для сотрудников"""

    list_display = (
        'full_name',
        'position',
        'department_link',
        'salary_fmt',
        'hire_date'
    )

    list_filter = (
        ('department', TreeRelatedFieldListFilter),
        'hire_date',
    )

    search_fields = ('full_name', 'position')
    list_select_related = ('department',)
    autocomplete_fields = ('department',)
    list_per_page = 25

    fieldsets = (
        ('Основная информация', {
            'fields': ('full_name', 'position', 'department')
        }),
        ('Финансы и даты', {
            'fields': ('salary', 'hire_date'),
        }),
    )

    @admin.display(description='Подразделение', ordering='department')
    def department_link(self, obj: Employee) -> str:
        """Получение ссылки на редактирование отдела"""

        if obj.department:
            url = f'/admin/staff/department/{obj.department.id}/change/'
            return format_html('<a href="{}">{}</a>', url, obj.department.name)
        return '-'

    @admin.display(description='Зарплата', ordering='salary')
    def salary_fmt(self, obj: Employee) -> str:
        """Форматирование зарплаты"""

        if obj.salary:
            return f'{obj.salary:,.2f} ₽'.replace(',', ' ')
        return '-'
