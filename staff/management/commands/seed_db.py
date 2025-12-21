import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from faker import Faker

from staff.models import Department, Employee

LOCATIONS = [
    'Головной офис (Москва)',
    'Филиал "Северо-Запад" (Санкт-Петербург)',
    'Филиал "Поволжье" (Нижний Новгород)',
    'Филиал "Сибирь" (Новосибирск)',
    'Технологический хаб (Иннополис)',
]

STRUCTURE_MAP = {
    'Блок Информационных Технологий': {
        'Дирекция Разработки ПО': [
            'Отдел Backend разработки',
            'Отдел Frontend разработки',
            'Отдел мобильной разработки',
            'Отдел QA и автоматизации',
            'Отдел архитектуры',
        ],
        'Дирекция Инфраструктуры': [
            'Отдел DevOps',
            'Отдел системного администрирования',
            'Отдел баз данных',
            'Отдел технической поддержки',
        ],
        'Дирекция Аналитики': [
            'Отдел системного анализа',
            'Отдел Data Science',
            'Отдел BI отчетности',
        ],
    },
    'Финансовый Блок': {
        'Департамент Бухгалтерии': [
            'Отдел расчета зарплаты',
            'Отдел работы с поставщиками',
            'Отдел основных средств',
            'Отдел налогового учета',
        ],
        'Департамент Планирования': [
            'Отдел бюджетирования',
            'Отдел финансового контроля',
            'Отдел инвестиционного анализа',
        ],
    },
    'Блок Управления Персоналом (HR)': {
        'Дирекция по подбору': [
            'Отдел IT-рекрутмента',
            'Отдел массового подбора',
            'Отдел Executive Search',
        ],
        'Дирекция развития талантов': [
            'Отдел обучения',
            'Отдел корпоративной культуры',
            'Отдел кадрового резерва',
        ],
    },
    'Коммерческий Блок': {
        'Департамент B2B продаж': [
            'Отдел по работе с ключевыми клиентами',
            'Отдел тендерных продаж',
            'Отдел регионального развития',
        ],
        'Департамент Маркетинга': [
            'Отдел Digital-маркетинга',
            'Отдел PR и коммуникаций',
            'Отдел продуктового маркетинга',
        ],
    },
}

GROUP_PREFIXES = ['Группа', 'Сектор', 'Команда']
PROJECT_NAMES = ['Альфа', 'Бета', 'Гамма', 'Омега', 'Феникс', 'Прайм', 'Кор', 'Легаси']


class Command(BaseCommand):
    help = 'Генерация реалистичной корпоративной структуры (5 уровней)'

    def handle(self, *args, **kwargs):
        fake = Faker('ru_RU')

        self.stdout.write(self.style.WARNING('Удаление старых данных...'))
        with transaction.atomic():
            Employee.objects.all().delete()
            Department.objects.all().delete()

        self.stdout.write('Построение дерева организации...')

        all_departments = []

        dept_count = 0

        with transaction.atomic():
            lvl1_branches = []
            for loc_name in LOCATIONS:
                branch = Department.objects.create(name=loc_name, parent=None)
                lvl1_branches.append(branch)
                all_departments.append(branch)

            lvl2_blocks = []
            for branch in lvl1_branches:
                for block_name in STRUCTURE_MAP.keys():
                    dept = Department.objects.create(name=block_name, parent=branch)
                    lvl2_blocks.append(dept)
                    all_departments.append(dept)

            lvl3_directorates = []
            for block in lvl2_blocks:
                substructure = STRUCTURE_MAP.get(block.name, {})

                for dir_name in substructure.keys():
                    dept = Department.objects.create(name=dir_name, parent=block)
                    lvl3_directorates.append(dept)
                    all_departments.append(dept)

            # ==========================================
            # УРОВЕНЬ 4: ОТДЕЛЫ
            # ==========================================
            lvl4_divisions = []
            for directorate in lvl3_directorates:
                block_name = directorate.parent.name
                dir_name = directorate.name

                divisions_list = STRUCTURE_MAP[block_name][dir_name]

                for div_name in divisions_list:
                    dept = Department.objects.create(name=div_name, parent=directorate)
                    lvl4_divisions.append(dept)
                    all_departments.append(dept)

            lvl5_groups = []
            for division in lvl4_divisions:
                # В каждом отделе от 2 до 5 групп
                for i in range(random.randint(2, 5)):
                    prefix = random.choice(GROUP_PREFIXES)
                    if (
                        'IT' in division.parent.parent.name
                        or 'Разработки' in division.name
                    ):
                        # IT-шные названия групп
                        proj = random.choice(PROJECT_NAMES)
                        group_name = f'{prefix} проекта {proj}-{i + 1}'
                    else:
                        # Обычные названия
                        group_name = f'{prefix} №{i + 1}'

                    dept = Department.objects.create(name=group_name, parent=division)
                    lvl5_groups.append(dept)
                    all_departments.append(dept)

        dept_count = len(all_departments)
        self.stdout.write(
            self.style.SUCCESS(f'Структура построена! Подразделений: {dept_count}')
        )

        self.stdout.write('Найм 50,000 сотрудников...')

        employees_buffer = []
        batch_size = 5000
        target_employees = 50000
        total_created = 0

        POSITIONS = {  # noqa: N806
            'entry': ['Стажер', 'Младший специалист', 'Специалист', 'Ассистент'],
            'mid': ['Ведущий специалист', 'Старший специалист', 'Инженер', 'Менеджер'],
            'senior': [
                'Главный специалист',
                'Эксперт',
                'Руководитель группы',
                'Архитектор',
            ],
        }

        while total_created < target_employees:
            for _ in range(batch_size):
                rnd = random.random()

                if rnd < 0.8:
                    dept = random.choice(lvl5_groups)
                    salary = random.randint(40000, 120000)
                    position = f'{random.choice(POSITIONS["entry"])} {fake.job()}'
                elif rnd < 0.95:
                    dept = random.choice(lvl4_divisions)
                    salary = random.randint(90000, 200000)
                    position = f'{random.choice(POSITIONS["mid"])}'
                else:
                    top_depts = lvl1_branches + lvl2_blocks + lvl3_directorates
                    dept = random.choice(top_depts)
                    salary = random.randint(200000, 800000)
                    position = (
                        'Начальник подразделения'
                        if dept.level > 0
                        else 'Директор филиала'
                    )

                employees_buffer.append(
                    Employee(
                        full_name=fake.name(),
                        position=position,
                        hire_date=fake.date_between(
                            start_date='-10y', end_date='today'
                        ),
                        salary=salary,
                        department=dept,
                    )
                )

            Employee.objects.bulk_create(employees_buffer, ignore_conflicts=True)
            employees_buffer = []

            total_created = Employee.objects.count()
            self.stdout.write(f'   ...в штате {total_created} чел.')

            if total_created >= target_employees:
                break

        User = get_user_model()  # noqa N806
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin')
            self.stdout.write(
                self.style.SUCCESS('\nСуперпользователь создан (admin/admin)')
            )

        self.stdout.write(self.style.SUCCESS('\nЗАДАНИЕ ВЫПОЛНЕНО:'))
        self.stdout.write(f'1. Сотрудников: {Employee.objects.count()}')
        self.stdout.write(f'2. Подразделений: {Department.objects.count()}')
        self.stdout.write(
            '3. Уровни иерархии: 5 (Филиал -> Блок -> Дирекция -> Отдел -> Группа)'
        )
