from langchain_community.chat_models import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

def chatbot(question, api_key, database):
    # Initialize the chat model
    
    chat = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=api_key, temperature=0.1)

    # Set up the retriever
    k = 3
    retriever = database.as_retriever(search_kwargs={"k": k})
    
    # Create conversation memory
    memory = ConversationBufferMemory(memory_key="chat_history", input_key="question", output_key="answer", return_messages=True)
    
    # Create the ConversationalRetrievalQA chain
    qa = ConversationalRetrievalChain.from_llm(llm=chat, retriever=retriever, memory=memory, return_source_documents=True, output_key="answer")
    # print(qa)
    response=qa({"question": question})
    
    question = response["question"]
    answer = response["answer"]
    
    # print(f"Question: {question}")
    # print(f"Answer: {answer}")

    return answer