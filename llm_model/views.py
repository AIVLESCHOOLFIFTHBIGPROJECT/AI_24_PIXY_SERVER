import os
import json
import boto3
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from langchain.chains import RetrievalQA
from botocore.exceptions import NoCredentialsError

# Load the API key from environment variables
openai_api_key = os.getenv('OPENAI_API_KEY')

# Check if the API key is loaded correctly
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set.")

# Initialize embeddings
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002", openai_api_key=openai_api_key)
database_dir = os.path.join(settings.BASE_DIR, "llm_model", "database")

# Ensure the directory exists
os.makedirs(database_dir, exist_ok=True)

# Initialize database globally
database = Chroma(persist_directory=database_dir, embedding_function=embeddings)

# Initialize S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION
)

@csrf_exempt
def upload_csv(request):
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']
        file_name = file.name
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME

        # Delete existing files in the S3 bucket directory
        try:
            s3_client.put_object(Bucket=bucket_name, Key=f"uploaded_data/{file_name}", Body=file)
            return JsonResponse({'message': 'File uploaded successfully'})
        except NoCredentialsError:
            return JsonResponse({'error': 'Credentials not available'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def start_learning(request):
    if request.method == 'POST':
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        # Get the list of objects in the S3 bucket directory
        try:
            response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix='uploaded_data/')
            if 'Contents' in response:
                latest_file = max(response['Contents'], key=lambda x: x['LastModified'])
                file_key = latest_file['Key']
                s3_client.download_file(bucket_name, file_key, '/tmp/temp.csv')
                data = pd.read_csv('/tmp/temp.csv')
            else:
                return JsonResponse({'error': 'No CSV file found'}, status=400)
        except NoCredentialsError:
            return JsonResponse({'error': 'Credentials not available'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

        # Check if the 'qna' column exists in the CSV
        if 'qna' not in data.columns:
            return JsonResponse({'error': "'qna' column not found in CSV"}, status=400)

        # Initialize and populate ChromaDB
        documents = [Document(page_content=row['qna']) for _, row in data.iterrows()]
        database.add_documents(documents)
        database.persist()

        return JsonResponse({'message': 'Learning process started successfully'})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def process_text(request):
    if request.method == 'POST':
        # Parse the incoming JSON request
        try:
            data = json.loads(request.body)
            text = data['text']
        except (json.JSONDecodeError, KeyError):
            return JsonResponse({'error': 'Invalid input'}, status=400)

        # Initialize ChatOpenAI and RetrievalQA
        chat = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=openai_api_key)
        retriever = database.as_retriever(search_kwargs={"k": 3})
        qa = RetrievalQA.from_llm(llm=chat, retriever=retriever, return_source_documents=True)

        # Set the initial prompt to ensure responses in Korean
        initial_prompt = "모든 대답은 한국어로 해주세요."
        full_query = f"{initial_prompt}\n{text}"

        # Get the response
        result = qa(full_query)

        # Return the response
        return JsonResponse({'response': result["result"]})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

