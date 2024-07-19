import os
import json
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from langchain.chains import RetrievalQA

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

@csrf_exempt
def upload_csv(request):
    if request.method == 'POST' and request.FILES['file']:
        # Clear the existing files in the upload directory
        upload_dir = os.path.join(settings.BASE_DIR, "llm_model", "uploaded_data")
        for filename in os.listdir(upload_dir):
            file_path = os.path.join(upload_dir, filename)
            os.remove(file_path)
        
        # Save the new file
        uploaded_file = request.FILES['file']
        with open(os.path.join(upload_dir, uploaded_file.name), 'wb') as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)
        
        return JsonResponse({'message': 'File uploaded successfully'})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def start_learning(request):
    if request.method == 'POST':
        # Load the uploaded CSV
        upload_dir = os.path.join(settings.BASE_DIR, "llm_model", "uploaded_data")
        csv_files = [f for f in os.listdir(upload_dir) if f.endswith('.csv')]
        if not csv_files:
            return JsonResponse({'error': 'No CSV file found'}, status=400)

        csv_path = os.path.join(upload_dir, csv_files[0])
        data = pd.read_csv(csv_path)

        # Check if the 'qna' column exists in the CSV
        if 'qna' not in data.columns:
            return JsonResponse({'error': "'qna' column not found in CSV"}, status=400)

        # Initialize and populate ChromaDB
        documents = [Document(page_content=row['qna']) for _, row in data.iterrows()]
        database.add_documents(documents)
        database.persist()

        return JsonResponse({'message': 'Learning process success'})
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