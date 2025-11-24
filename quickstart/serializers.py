from django.contrib.auth.models import User, Group
from rest_framework import serializers
from django.core.exceptions import ValidationError


class UserSerializer(serializers.HyperlinkedModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    email = serializers.EmailField()

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email Already Exist.")
        return value
    
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'password', 'groups']

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']