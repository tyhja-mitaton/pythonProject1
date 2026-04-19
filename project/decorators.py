import jwt
from django.conf import settings
from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from .models import User


def jwt_auth_required(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'error': 'Требуется авторизация'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            token = auth_header.split(' ')[1]
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload.get('user_id'), is_active=True)

            request.user = user
            print(f"[JWT DECORATOR SUCCESS] {user.email} (id={user.id})")

        except Exception as e:
            print(f"[JWT DECORATOR FAILED] {type(e).__name__}: {e}")
            return Response({'error': 'Требуется авторизация'}, status=status.HTTP_401_UNAUTHORIZED)

        return view_func(request, *args, **kwargs)

    return wrapped_view