from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .serializers import QuestionSerializer
from drf_yasg.utils import swagger_auto_schema
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
import subprocess
from django.conf import settings
import os, shutil
from models.database import make_database
from models.chatbot import chatbot

def clear_folder(folder_path):
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

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
        api_key = settings.CHATGPT_API_KEY

        try:
            embeddings = OpenAIEmbeddings(model="text-embedding-ada-002", openai_api_key=api_key)
            database = Chroma(persist_directory="custom/database", embedding_function=embeddings)

            if 'runtype' in request.data and request.data['runtype'] == 'database':
                clear_folder('custom/database')
                make_database(api_key, database)
                return Response({'status': 'Database created'}, status=status.HTTP_200_OK)
            else:
                answer = chatbot(question, api_key, database)
                return Response({'answer': answer}, status=status.HTTP_200_OK)

        except Exception as e:
            print('Exception during processing:', str(e))
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)