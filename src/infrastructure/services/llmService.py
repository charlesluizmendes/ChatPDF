from langchain_openai import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains.retrieval_qa.base import RetrievalQA

from src.domain.interfaces.services.llmService import IllmService

class LlmService(IllmService):
    def __init__(
        self,
        model: str,
        api_key: str
    ):
        self.model = model
        self.api_key = api_key
    
    async def ask(self, message: str, retriever, prompt: str, temperature: float) -> str:
        try:
            system_message = SystemMessagePromptTemplate.from_template(prompt)
            
            human_message = HumanMessagePromptTemplate.from_template(
                "Contexto: {context}\n\nPergunta: {question}"
            )
            
            chat_prompt = ChatPromptTemplate.from_messages([system_message, human_message])
            
            llm = ChatOpenAI(
                model=self.model,
                api_key=self.api_key,
                temperature=temperature
            )

            chat_chain = RetrievalQA.from_chain_type(
                llm=llm,
                retriever=retriever,
                chain_type_kwargs={"prompt": chat_prompt},
                return_source_documents=True
            )
            
            result = chat_chain.invoke({"query": message})
            
            return result["result"]
        
        except Exception:
            raise