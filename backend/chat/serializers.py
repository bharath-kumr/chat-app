from rest_framework import serializers
from .models import Message
from django.contrib.auth.models import User

class MessageSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username')
    voice = serializers.FileField(required=False)

    class Meta:
        model = Message
        fields = ['id', 'user', 'room', 'content', 'voice', 'timestamp']

