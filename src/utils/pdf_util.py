import os
import tempfile

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

def set_pdf(id, name, file):
    
    docs = []
    temp_dir = tempfile.TemporaryDirectory()    
    temp_filepath = os.path.join(temp_dir.name, name)

    with open(temp_filepath, "wb") as f:
        f.write(file)
        
    loader = PyPDFLoader(temp_filepath)
    documents = loader.load()
    
    for doc in documents:
        doc.metadata['id'] = str(id)
    docs.extend(documents)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")
    
    vectorstore = FAISS.from_documents(splits, embeddings)
    vectorstore.save_local(folder_path="src", index_name="chatPDF")