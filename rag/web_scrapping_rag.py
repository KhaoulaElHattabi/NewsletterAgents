import os 
from dotenv import load_dotenv

from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings


load_dotenv()

import os




urls = ["https://www.apple.com/"]

loader = WebBaseLoader(urls)
documents = loader.load()

text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

print(f"Number of documents: {len(docs)}")
print(f"chunk:\n{docs[0].page_content}\n")

persistent_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db', 'chroma_db_agent')
embeddings = OpenAIEmbeddings(model = os.getenv('EMBEDDING_DEPLOYMENT_NAME'), api_key = os.getenv('OPENAI_API_KEY'))

if not os.path(persistent_directory): 
    db = Chroma(docs, embeddings, persistent_directory=persistent_directory)
else:
    db =  Chroma(persistent_directory=persistent_directory,embedding_function=embeddings)