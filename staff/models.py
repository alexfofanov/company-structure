from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from mptt.models import MPTTModel, TreeForeignKey


class Department(MPTTModel):
    """Модель подразделения"""

    name = models.CharField(
        verbose_name=_('Название'),
        max_length=100,
        help_text=_('Название подразделения'),
    )
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_('Родительское подразделение'),
        help_text=_('Родительское подразделение в иерархии'),
    )

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = _('Подразделение')
        verbose_name_plural = _('Подразделения')
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'parent'], name='unique_department_name_per_parent'
            )
        ]

    def __str__(self) -> str:
        return self.name


class Employee(models.Model):
    """Модель сотрудника"""

    full_name = models.CharField(
        verbose_name=_('ФИО'),
        max_length=100,
        db_index=True,
        help_text=_('Полное имя сотрудника, например'),
    )
    position = models.CharField(
        verbose_name=_('Должность'), max_length=100, help_text=_('Должность сотрудника')
    )
    hire_date = models.DateField(
        verbose_name=_('Дата приёма'), help_text=_('Дата приёма на работу')
    )
    salary = models.DecimalField(
        verbose_name=_('Зарплата'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text=_('Ежемесячная зарплата сотрудника. Должна быть неотрицательной'),
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='employees',
        verbose_name='Подразделение',
        help_text=_('Подразделение, в котором работает сотрудник'),
    )

    class Meta:
        verbose_name = _('Сотрудник')
        verbose_name_plural = _('Сотрудники')

        constraints = [
            models.UniqueConstraint(
                fields=['full_name', 'department'],
                name='unique_employee_per_department',
            )
        ]

    def __str__(self) -> str:
        return f'{self.full_name} ({self.position})'
