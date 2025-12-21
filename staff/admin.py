from django.contrib import admin
from django.db.models import Count, IntegerField, OuterRef, QuerySet, Subquery
from django.http import HttpRequest
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
        employees_count_subquery = Subquery(
            Employee.objects.filter(
                department__tree_id=OuterRef('tree_id'),
                department__lft__gte=OuterRef('lft'),
                department__rght__lte=OuterRef('rght'),
            )
            .values('department__tree_id')
            .annotate(cnt=Count('id'))
            .values('cnt')[:1],
            output_field=IntegerField(),
        )
        return qs.annotate(employees_cumulative_count=employees_count_subquery)

    @admin.display(description='Сотр. (всего)', ordering='employees_cumulative_count')
    def employee_count_display(self, obj: Department) -> str:
        """Отображение количества сотрудников"""

        count = obj.employees_cumulative_count or 0

        if count > 0:
            url = f'/admin/staff/employee/?department__id__exact={obj.id}'
            return format_html(
                '<a href="{url}" title="Показать сотрудников" style="font-weight: bold;">{count}</a>',
                url=url,
                count=count,
            )
        return '—'


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
            url = f'/admin/staff/department/{obj.department.id}/change/'
            return format_html('<a href="{}">{}</a>', url, obj.department.name)
        return '-'

    @admin.display(description='Зарплата', ordering='salary')
    def salary_fmt(self, obj: Employee) -> str:
        """Форматирование зарплаты"""

        if obj.salary:
            return f'{obj.salary:,.2f} ₽'.replace(',', ' ')
        return '-'
