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


class DepartmentDetailsSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    employees = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ['children', 'employees']

    def get_children(self, obj: Department):
        children = obj.get_children()
        return DepartmentSerializer(children, many=True).data

    def get_employees(self, obj: Department):
        return EmployeeSerializer(obj.employees.all(), many=True).data
