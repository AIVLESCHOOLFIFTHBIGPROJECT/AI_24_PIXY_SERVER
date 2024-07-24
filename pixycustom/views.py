from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .serializers import QuestionSerializer
from drf_yasg.utils import swagger_auto_schema
import subprocess
from django.conf import settings

@swagger_auto_schema(
    method='post',
    tags=['pixycustom'],
    request_body=QuestionSerializer,
    responses={200: 'Answer', 400: 'Bad Request'}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def ask_question(request):
    serializer = QuestionSerializer(data=request.data)
    if serializer.is_valid():
        question = serializer.validated_data['question']
        api_key=settings.CHATGPT_API_KEY
        try:
            result = subprocess.run(
                ['python', 'pixycustom/main.py', '--runtype', 'chatbot', '--script', question, '--key', api_key],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print('Subprocess output:', result.stdout)  # 디버깅용 출력
                return Response({'answer': result.stdout.strip()}, status=status.HTTP_200_OK)
            else:
                print('Subprocess error:', result.stderr)  # 디버깅용 출력
                return Response({'error': result.stderr.strip()}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            print('Exception during subprocess run:', str(e))  # 디버깅용 출력
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
