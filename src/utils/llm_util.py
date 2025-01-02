import os
import tempfile
import torch

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFacePipeline
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, pipeline

from src.utils.mongo_util import MongoDBConnectionManager, MongoDBDocumentHandler

from dotenv import load_dotenv

load_dotenv()
huggingFace_model_id = os.getenv("HUGGINGFACEHUB_MODEL_ID")
huggingFace_model_name = os.getenv("HUGGINGFACEHUB_MODEL_NAME")
huggingFace_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")

def get_answer(id, content):

    quantization_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_use_double_quant=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16)
    model = AutoModelForCausalLM.from_pretrained(huggingFace_model_id, token=huggingFace_token, quantization_config=quantization_config)
    tokenizer = AutoTokenizer.from_pretrained(huggingFace_model_id, token=huggingFace_token)
    pipe = pipeline(model=model, tokenizer=tokenizer, task="text-generation", temperature=0.01, max_new_tokens=512, do_sample=True, repetition_penalty=1.2, return_full_text=False)
    llm = HuggingFacePipeline(pipeline=pipe)

    embeddings = HuggingFaceEmbeddings(model_name=huggingFace_model_name)  
    
    connection_manager = MongoDBConnectionManager()
    handler = MongoDBDocumentHandler(embeddings, connection_manager)
    retriever = handler.get_retriever(
        search_type="mmr",
        search_kwargs={
            'k': 3,
            'fetch_k': 4,
            'pre_filter': {'id': str(id)}
        }
    )

    token_start, token_end = "<|begin_of_text|><|start_header_id|>system<|end_header_id|>", "<|eot_id|><|start_header_id|>assistant<|end_header_id|>"    
    template = """Você é um assistente virtual prestativo e está respondendo perguntas.
        Use somente os seguintes pedaços de contexto recuperado para responder à pergunta.
        Se a resposta não estiver no contexto, apenas responda "Não possuo informações". 
        Mantenha a resposta concisa e detalhada. \n
        Contexto: {context} \n\n
        Pergunta: {input}"""
    prompt = ChatPromptTemplate.from_template(token_start + template + token_end)

    documents_chain = create_stuff_documents_chain(llm, prompt)
    retriver_chain = create_retrieval_chain(retriever, documents_chain)    
    response = retriver_chain.invoke({"input": content})
    
    connection_manager.close()

    return response['answer']

def upload_pdf(id, name, content):
    
    temp_dir = tempfile.TemporaryDirectory()    
    temp_filepath = os.path.join(temp_dir.name, name)

    with open(temp_filepath, "wb") as f:
        f.write(content)
        
    loader = PyPDFLoader(temp_filepath)
    documents = loader.load()
    
    data = []   
    for doc in documents:
        doc.metadata['id'] = str(id)
    data.extend(documents)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.split_documents(data)   

    embeddings = HuggingFaceEmbeddings(model_name=huggingFace_model_name)
    
    connection_manager = MongoDBConnectionManager()
    handler = MongoDBDocumentHandler(embeddings, connection_manager)
    handler.add_documents(docs)

    temp_dir.cleanup()
    connection_manager.close()

def delete_pdf(id):

    embeddings = HuggingFaceEmbeddings(model_name=huggingFace_model_name)

    connection_manager = MongoDBConnectionManager()
    handler = MongoDBDocumentHandler(embeddings, connection_manager)
    results = handler.similarity_search(
        pre_filter= {'id': str(id)}
    )

    if results:
        ids = [doc.metadata["_id"] for doc in results]
        result = handler.delete_documents(
            ids=ids
        )

    connection_manager.close()

    return result