from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework import status, permissions
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Message, ChatRoom
from .serializers import MessageSerializer
from rest_framework_simplejwt.tokens import RefreshToken


class RegisterView(APIView):
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        if not username or not email or not password:
            return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, email=email, password=password)
        return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'username': user.username,
            })
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        room_name = request.data.get('room')
        content = request.data.get('content')

        if not room_name or not content:
            return Response({'error': 'Room and message content are required'}, status=status.HTTP_400_BAD_REQUEST)

        room, created = ChatRoom.objects.get_or_create(name=room_name)
        message = Message.objects.create(user=request.user, room=room, content=content)
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def send_voice_message(request):
    try:
        room_name = request.data.get('room')
        voice_file = request.FILES.get('voice')

        if not room_name or not voice_file:
            return Response({"error": "Missing room or voice data"}, status=status.HTTP_400_BAD_REQUEST)

        room, _ = ChatRoom.objects.get_or_create(name='room')
        message = Message.objects.create(user=request.user, room=room, voice=voice_file)
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request):
    sender = request.user
    content = request.data.get('content')
    room = request.data.get('room')
    receiver_username = request.data.get('receiver')  # front-end must send this

    try:
        receiver = User.objects.get(username=receiver_username)
    except User.DoesNotExist:
        return Response({'error': 'Receiver not found'}, status=400)

    message = Message.objects.create(
        sender=sender,
        receiver=receiver,
        content=content,
        room=room
    )

    serializer = MessageSerializer(message)
    return Response(serializer.data, status=201)



class MessageListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, room):
        try:
            room_obj = ChatRoom.objects.get(name=room)
            messages = Message.objects.filter(room=room_obj).order_by('timestamp')
            serializer = MessageSerializer(messages, many=True)
            return Response(serializer.data)
        except ChatRoom.DoesNotExist:
            return Response({'error': 'Room not found'}, status=status.HTTP_404_NOT_FOUND)

