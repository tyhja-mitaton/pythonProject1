from django.core.management.base import BaseCommand
from project.models import Role, BusinessElement, AccessRoleRule, User

class Command(BaseCommand):
    help = 'Загружает тестовые данные'

    def handle(self, *args, **options):
        # Роли
        admin_role, _ = Role.objects.get_or_create(name='admin')
        user_role, _ = Role.objects.get_or_create(name='user')

        # Элементы
        elements = ['users', 'products', 'stores', 'orders', 'access_rules']
        for name in elements:
            BusinessElement.objects.get_or_create(name=name)

        # Правила для admin
        for elem_name in elements:
            elem = BusinessElement.objects.get(name=elem_name)
            rule, _ = AccessRoleRule.objects.get_or_create(role=admin_role, element=elem)
            for field in rule._meta.fields:
                if field.name.endswith('_permission'):
                    setattr(rule, field.name, True)
            rule.save()

        # Правила для user
        for elem_name in ['products', 'orders']:
            elem = BusinessElement.objects.get(name=elem_name)
            rule, _ = AccessRoleRule.objects.get_or_create(role=user_role, element=elem)
            rule.read_all_permission = True
            rule.create_permission = True
            rule.update_permission = True
            rule.delete_permission = True
            rule.save()

        # Пользователи
        if not User.objects.filter(email='admin@ex.com').exists():
            admin = User(first_name='Admin', last_name='Admin', email='admin@ex.com', role=admin_role)
            admin.set_password('admin123')
            admin.save()

        if not User.objects.filter(email='user@ex.com').exists():
            user = User(first_name='Test', last_name='User', email='user@ex.com', role=user_role)
            user.set_password('user123')
            user.save()

        self.stdout.write(self.style.SUCCESS('Тестовые данные загружены'))