import pandas as pd
import numpy as np
import os
import sqlite3
from datetime import datetime
# from django.conf import settings
from django.conf import settings

import argparse

import openai

from models.database import make_database
from models.chatbot import chatbot

from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import shutil
import os


def clear_folder(folder_path):
    # 폴더가 존재하는지 확인합니다.
    if os.path.exists(folder_path):
        # 폴더 안의 모든 파일과 디렉토리를 나열합니다.
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                # 파일인지 디렉토리인지 확인 후 각각에 맞는 삭제 명령을 실행합니다.
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)  # 파일이나 링크 삭제
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # 디렉토리 삭제
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

def parse_arguments():
    parser = argparse.ArgumentParser(description="Chatbot Model Training and Evaluation Script")
    parser.add_argument("--runtype", type=str, required=True, default='chatbot', choices=['chatbot', 'database'])
    parser.add_argument("--script", type=str, required=True)
    parser.add_argument("--key", type=str, required=True)
    return parser.parse_args()

def main(runtype, script, key):
    
    question=script #추후 입력방식 수정
    api_key = key
    # api_key = settings.CHATGPT_API_KEY
    # print(api_key)

    if runtype=='database':
        clear_folder('pixycustom/database')

    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002", openai_api_key=api_key)
    database = Chroma(persist_directory="pixycustom/database", embedding_function = embeddings )
    
    if runtype=='chatbot':
        print(chatbot(question, api_key, database))
        
    elif runtype=='database':
        make_database(api_key, database)

        #필요에따라 출력 바꾸면 됨




if __name__ == "__main__":
    args = parse_arguments()
    main(args.runtype, args.script, args.key)