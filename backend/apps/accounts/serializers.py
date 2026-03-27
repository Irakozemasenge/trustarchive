from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'phone', 'role', 'partner_type',
                  'organization_name', 'organization_logo', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class RegisterPublicSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['email', 'full_name', 'phone', 'password']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data, role='public')


class CreateAdminSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    partner_type = serializers.CharField(required=False, allow_blank=True, default='autre')
    organization_name = serializers.CharField(required=False, allow_blank=True, default='')
    phone = serializers.CharField(required=False, allow_blank=True, default='')

    class Meta:
        model = User
        fields = ['email', 'full_name', 'phone', 'password', 'partner_type', 'organization_name', 'organization_logo']

    def create(self, validated_data):
        validated_data.pop('organization_logo', None)
        return User.objects.create_user(**validated_data, role='admin')


class CustomTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['full_name'] = user.full_name
        token['email'] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data
