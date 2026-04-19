from rest_framework import serializers
from .models import User, AccessRoleRule

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'patronymic', 'email', 'role']
        read_only_fields = ['id', 'role']

class AccessRoleRuleSerializer(serializers.ModelSerializer):
    role = serializers.StringRelatedField()
    element = serializers.StringRelatedField()
    class Meta:
        model = AccessRoleRule
        fields = '__all__'