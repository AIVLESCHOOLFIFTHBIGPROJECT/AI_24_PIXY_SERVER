from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Notification
from .serializers import NotificationSerializer, NotificationCreateSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

User = get_user_model()

@swagger_auto_schema(method='get', responses={200: NotificationSerializer(many=True)})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_list(request):
    notifications = request.user.notifications.all().order_by('-created_at')
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@swagger_auto_schema(method='post', responses={200: '알림이 읽음 상태로 변경되었습니다.'})
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_as_read(request, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.read = True
        notification.save()
        return Response({'message': '알림이 읽음 상태로 변경되었습니다.'}, status=status.HTTP_200_OK)
    except Notification.DoesNotExist:
        return Response({'error': '해당 알림을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

@swagger_auto_schema(method='post', request_body=NotificationCreateSerializer, responses={201: NotificationSerializer})
@api_view(['POST'])
@permission_classes([IsAdminUser])
def send_notification(request):
    serializer = NotificationCreateSerializer(data=request.data)
    if serializer.is_valid():
        notification = serializer.save(sender=request.user, sender_type='admin')
        return Response(NotificationSerializer(notification).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(method='post', request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Notification message'),
    },
    required=['message']
))
@api_view(['POST'])
@permission_classes([IsAdminUser])
def send_notification_to_all(request):
    message = request.data.get('message')
    if not message:
        return Response({'error': '메시지를 입력해주세요.'}, status=status.HTTP_400_BAD_REQUEST)

    users = User.objects.all()
    notifications = []
    for user in users:
        notifications.append(Notification(user=user, message=message, sender=request.user, sender_type='admin', to_all=True))
    
    Notification.objects.bulk_create(notifications)
    return Response({'message': '전체 사용자에게 알림이 전송되었습니다.'}, status=status.HTTP_201_CREATED)
