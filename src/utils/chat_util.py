import os
import torch

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFacePipeline
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, pipeline

from dotenv import load_dotenv

load_dotenv()
token = os.getenv("HUGGINGFACEHUB_API_TOKEN")

def get_answer(id, question):

    model_id = "meta-llama/Llama-3.2-3B-Instruct"
    
    quantization_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_use_double_quant=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16)
    model = AutoModelForCausalLM.from_pretrained(model_id, token=token, quantization_config=quantization_config)
    tokenizer = AutoTokenizer.from_pretrained(model_id, token=token)
    pipe = pipeline(model=model, tokenizer=tokenizer, task="text-generation", temperature=0.1, max_new_tokens=512, do_sample=True, repetition_penalty=1.2, return_full_text=False)
    llm = HuggingFacePipeline(pipeline=pipe)

    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")    
    vectorstore = FAISS.load_local(folder_path="src", embeddings=embeddings, index_name="chatPDF", allow_dangerous_deserialization=True)
    retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={'k': 3, 'fetch_k': 4, 'filter': {'id': str(id)}})

    token_start, token_end = "<|begin_of_text|><|start_header_id|>system<|end_header_id|>", "<|eot_id|><|start_header_id|>assistant<|end_header_id|>"    
    template = """Você é um assistente virtual prestativo e está respondendo perguntas gerais.
        Use os seguintes pedaços de contexto recuperado para responder à pergunta.
        Se você não sabe a resposta, apenas responda "Não Sei" e nada mais além disso. 
        Mantenha a resposta concisa e detalhada. \n
        Contexto: {context} \n\n
        Pergunta: {input}"""
    prompt = ChatPromptTemplate.from_template(token_start + template + token_end)

    documents_chain = create_stuff_documents_chain(llm, prompt)
    retriver_chain = create_retrieval_chain(retriever, documents_chain)    

    response = retriver_chain.invoke({"input": question})

    return response['answer']
