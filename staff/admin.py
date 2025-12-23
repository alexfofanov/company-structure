from django.contrib import admin
from django.db.models import QuerySet
from django.db.models.expressions import RawSQL
from django.http import HttpRequest
from django.urls import reverse
from django.utils.html import format_html

from mptt.admin import DraggableMPTTAdmin, TreeRelatedFieldListFilter

from .models import Department, Employee


@admin.register(Department)
class DepartmentAdmin(DraggableMPTTAdmin):
    mptt_indent_field = 'name'
    list_display = (
        'tree_actions',
        'indented_title',
        'employee_count_display',
        'id',
    )
    list_display_links = ('indented_title',)
    search_fields = ('name',)

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        qs = super().get_queryset(request)
        qs = qs.annotate(
            employees_cumulative_count=RawSQL(
                """
                SELECT COUNT(e.id)
                FROM staff_employee e
                         JOIN staff_department d ON e.department_id = d.id
                WHERE d.tree_id = staff_department.tree_id
                  AND d.lft >= staff_department.lft
                  AND d.rght <= staff_department.rght
                """,
                [],
            )
        )
        return qs

    @admin.display(description='Сотр. (всего)', ordering='employees_cumulative_count')
    def employee_count_display(self, obj: Department) -> str:
        """Отображение количества сотрудников"""

        count = obj.employees_cumulative_count or 0
        return count if count > 0 else '—'


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """Админка для сотрудников"""

    list_display = (
        'full_name',
        'position',
        'department_link',
        'salary_fmt',
        'hire_date',
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
        ('Основная информация', {'fields': ('full_name', 'position', 'department')}),
        (
            'Финансы и даты',
            {
                'fields': ('salary', 'hire_date'),
            },
        ),
    )

    @admin.display(description='Подразделение', ordering='department')
    def department_link(self, obj: Employee) -> str:
        """Получение ссылки на редактирование отдела"""

        if obj.department:
            url = reverse('admin:staff_department_change', args=[obj.department.id])
            return format_html('<a href="{}">{}</a>', url, obj.department.name)
        return '-'

    @admin.display(description='Зарплата', ordering='salary')
    def salary_fmt(self, obj: Employee) -> str:
        """Форматирование зарплаты"""

        if obj.salary:
            return f'{obj.salary:,.2f} ₽'.replace(',', ' ')
        return '-'
