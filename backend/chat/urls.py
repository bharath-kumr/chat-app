from django.contrib import admin
from django.urls import path
from chat.views import RegisterView, LoginView, SendMessageView, MessageListView, send_voice_message

urlpatterns = [
    path('admin/', admin.site.urls),
    path('send-voice/', send_voice_message),
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('send/', SendMessageView.as_view()),
    path('messages/<str:room>/', MessageListView.as_view()),
]



