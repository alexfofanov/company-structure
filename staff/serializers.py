from rest_framework import serializers

from .models import Department, Employee


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'full_name', 'position', 'salary', 'hire_date']


class DepartmentSerializer(serializers.ModelSerializer):
    # Добавляем поле, чтобы фронтенд знал, рисовать ли "плюс"
    has_children = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ['id', 'name', 'has_children']

    def get_has_children(self, obj: Department) -> bool:
        return not obj.is_leaf_node()
