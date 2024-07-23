import pandas as pd
from langchain.schema import Document
from langchain_community.vectorstores import Chroma

def make_database(api_key, database):
    data = pd.read_csv('./qna_data/생활잡화응답_변환.csv', encoding='utf-8')
    documents = [Document(page_content=text) for text in data['qna'].tolist()]
    database.add_documents(documents)