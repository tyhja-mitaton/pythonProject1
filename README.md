# Custom Authentication & Authorization System

Собственная система аутентификации и авторизации на DRF + PostgreSQL (без использования встроенных механизмов Django).

## Тестовые пользователи

| Email                | Пароль       | Роль   |
|----------------------|--------------|--------|
| `admin@ex.com`       | `admin123`   | Admin  |
| `ivan@example.com`   | `password123`| User   |

## Инструкция по тестированию API

### 1. Авторизация

**Логин как обычный пользователь:**

```bash
curl -X POST http://localhost:8000/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "ivan@example.com",
    "password": "password123"
  }'
```

**Логин как обычный администратор:**
```bash
curl -X POST http://localhost:8000/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@ex.com",
    "password": "admin123"
  }'
```

```bash
curl -H "Authorization: Bearer ТОКЕН" http://localhost:8000/profile/

curl -H "Authorization: Bearer ТОКЕН" http://localhost:8000/products/

curl -H "Authorization: Bearer ТОКЕН" http://localhost:8000/access-rules/
```

**Структура проекта**
```text
pythonProject1/
├── manage.py
├── project/
│   ├── settings.py
│   ├── urls.py
│   ├── views.py
│   ├── models.py
│   ├── serializers.py
│   ├── middleware.py (или decorators.py)
│   └── ...
├── docker-compose.yml
├── Dockerfile
└── README.md
```

Таблица    Описание
Role   "Роли пользователей (admin, user)"
BusinessElement    "Бизнес-объекты системы (users, products, stores, orders, access_rules)"
AccessRoleRule Главное правило доступа — связывает роль и элемент
User   Кастомная модель пользователя

**Структура таблицы AccessRoleRule**

role_id — ссылка на роль
element_id — ссылка на бизнес-элемент
read_permission / read_all_permission
create_permission
update_permission / update_all_permission
delete_permission / delete_all_permission

**Логика прав:**

_permission (без all) — доступ только к своим объектам (где owner_id = user.id)
_all_permission — доступ ко всем объектам системы
create_permission — разрешение на создание новых объектов

**Текущие правила (после загрузки тестовых данных)**

Администратор (admin): имеет полный доступ (_all_permission = True) ко всем элементам.
Пользователь (user): имеет полный доступ к products и orders (чтение всех + создание + редактирование + удаление своих).