import jwt
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import User, Role, AccessRoleRule, BusinessElement
from .serializers import UserSerializer, AccessRoleRuleSerializer
from .permissions import has_permission, get_rule
from .decorators import jwt_auth_required

# ---------- JWT ----------
def generate_jwt(user):
    payload = {
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(days=1),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

# ---------- AUTH ----------
@api_view(['POST'])
def register(request):
    data = request.data
    if User.objects.filter(email=data['email']).exists():
        return Response({'error': 'Email уже существует'}, status=400)
    if data['password'] != data['password_confirm']:
        return Response({'error': 'Пароли не совпадают'}, status=400)

    role = Role.objects.get(name='user')
    user = User(
        first_name=data['first_name'],
        last_name=data['last_name'],
        patronymic=data.get('patronymic', ''),
        email=data['email'],
        role=role
    )
    user.set_password(data['password'])
    user.save()
    return Response({'message': 'Регистрация успешна'}, status=201)

@api_view(['POST'])
def login(request):
    try:
        user = User.objects.get(email=request.data['email'], is_active=True)
        if user.check_password(request.data['password']):
            token = generate_jwt(user)
            return Response({'token': token})
        return Response({'error': 'Неверный пароль'}, 401)
    except User.DoesNotExist:
        return Response({'error': 'Пользователь не найден'}, 401)

@api_view(['POST'])
def logout(request):
    return Response({'message': 'Вы вышли из системы'})

@api_view(['GET', 'PUT', 'DELETE'])
def profile(request):
    print("=== PROFILE DEBUG START ===")
    print("Headers:", dict(request.headers))

    auth_header = request.headers.get('Authorization')
    print("Auth header:", auth_header)

    if not auth_header or not auth_header.startswith('Bearer '):
        print("No Bearer token")
        return Response({'error': 'Требуется авторизация'}, status=401)

    try:
        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        print("Token payload:", payload)

        user = User.objects.get(id=payload.get('user_id'), is_active=True)
        request.user = user
        print(f"SUCCESS: User set -> {user.email} (id={user.id})")

    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        return Response({'error': 'Требуется авторизация'}, status=401)


    if request.method == 'GET':
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    if request.method == 'PUT':
        data = request.data
        for field in ['first_name', 'last_name', 'patronymic', 'email']:
            if field in data:
                setattr(request.user, field, data[field])
        request.user.save()
        return Response(UserSerializer(request.user).data)

    if request.method == 'DELETE':
        request.user.is_active = False
        request.user.save()
        return Response({'message': 'Аккаунт мягко удалён'}, status=204)

MOCK_PRODUCTS = [
    {'id': 1, 'name': 'Ноутбук', 'price': 150000, 'owner_id': 1},
    {'id': 2, 'name': 'Смартфон', 'price': 80000, 'owner_id': 2},
]

MOCK_ORDERS = [
    {'id': 1, 'product': 'Ноутбук', 'status': 'new', 'owner_id': 1},
]

MOCK_STORES = [
    {'id': 1, 'name': 'Магазин электроники', 'owner_id': 1},
]

def get_mock_data(element_name):
    if element_name == 'products': return MOCK_PRODUCTS
    if element_name == 'orders': return MOCK_ORDERS
    if element_name == 'stores': return MOCK_STORES
    return []

@api_view(['GET', 'POST'])
@jwt_auth_required
def mock_list(request, element_name):
    print("=== DEBUG START ===")
    print("USER:", request.user)
    print("ROLE:", getattr(request.user, "role", None))
    print("ELEMENT NAME:", element_name)
    print("=== DEBUG END ===")
    if not request.user:
        return Response({'error': 'Требуется авторизация'}, status=401)

    rule = get_rule(request.user, element_name)
    if not rule or not (rule.read_permission or rule.read_all_permission):
        return Response({'error': 'Доступ запрещён'}, status=403)

    data = get_mock_data(element_name)

    if request.method == 'POST':
        if not rule.create_permission:
            return Response({'error': 'Создание запрещено'}, status=403)

        new_obj = request.data
        new_obj['id'] = len(data) + 1
        new_obj['owner_id'] = request.user.id
        data.append(new_obj)
        return Response(new_obj, status=201)

    if rule.read_all_permission:
        return Response(data)

    own_data = [item for item in data if item.get('owner_id') == request.user.id]
    return Response(own_data)

@api_view(['GET', 'PUT', 'DELETE'])
@jwt_auth_required
def mock_detail(request, element_name, obj_id):
    if not request.user:
        return Response({'error': 'Требуется авторизация'}, status=401)

    data = get_mock_data(element_name)
    obj = next((x for x in data if x['id'] == int(obj_id)), None)
    if not obj:
        return Response({'error': 'Объект не найден'}, status=404)

    rule = get_rule(request.user, element_name)
    if not rule:
        return Response({'error': 'Доступ запрещён'}, status=403)

    if request.method in ['GET', 'PUT', 'DELETE']:
        owner_id = obj.get('owner_id')
        allowed = False
        if request.method == 'GET':
            allowed = rule.read_all_permission or (rule.read_permission and owner_id == request.user.id)
        elif request.method == 'PUT':
            allowed = rule.update_all_permission or (rule.update_permission and owner_id == request.user.id)
        elif request.method == 'DELETE':
            allowed = rule.delete_all_permission or (rule.delete_permission and owner_id == request.user.id)

        if not allowed:
            return Response({'error': 'Доступ запрещён'}, status=403)

        if request.method == 'GET':
            return Response(obj)
        if request.method == 'PUT':
            obj.update(request.data)
            return Response(obj)
        if request.method == 'DELETE':
            data.remove(obj)
            return Response(status=204)

    return Response(status=405)

@api_view(['GET'])
@jwt_auth_required
def access_rules_list(request):
    print("🔥 ACCESS RULES ENDPOINT HIT")
    print("COUNT:", AccessRoleRule.objects.count())
    print("USER:", request.user)
    print("ROLE:", request.user.role)
    if not request.user or not has_permission(request.user, 'access_rules', 'read'):
        return Response({'error': 'Доступ запрещён'}, status=403)
    rules = AccessRoleRule.objects.all()
    serializer = AccessRoleRuleSerializer(rules, many=True)
    return Response(serializer.data)

@api_view(['PUT'])
@jwt_auth_required
def access_rule_update(request, rule_id):
    if not request.user or not has_permission(request.user, 'access_rules', 'update'):
        return Response({'error': 'Доступ запрещён'}, status=403)
    try:
        rule = AccessRoleRule.objects.get(id=rule_id)
        for perm in ['read', 'read_all', 'create', 'update', 'update_all', 'delete', 'delete_all']:
            if perm + '_permission' in request.data:
                setattr(rule, perm + '_permission', request.data[perm + '_permission'])
        rule.save()
        return Response(AccessRoleRuleSerializer(rule).data)
    except AccessRoleRule.DoesNotExist:
        return Response({'error': 'Правило не найдено'}, status=404)