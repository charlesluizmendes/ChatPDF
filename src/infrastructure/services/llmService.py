from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.messages import HumanMessage, AIMessage

from src.domain.interfaces.services.llmService import IllmService


class LlmService(IllmService):
    def __init__(
        self,
        model: str,
        api_key: str
    ):
        self.model = model
        self.api_key = api_key
    
    def _convert_messages_to_langchain(self, messages: list) -> list:
        langchain_messages = []

        for msg in messages:
            if msg["role"] == "user":
                langchain_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                langchain_messages.append(AIMessage(content=msg["content"]))
                
        return langchain_messages

    async def ask(self, messages: list, retriever, prompt: str, temperature: float) -> str:
        try:
            current_question = messages[-1]["content"]
            
            chat_history = self._convert_messages_to_langchain(messages[:-1]) if len(messages) > 1 else []
            
            contextualize_q_prompt = ChatPromptTemplate.from_messages([
                ("system", "Dado um histórico de conversa e a última pergunta do usuário, "
                    "formule uma pergunta independente que possa ser compreendida "
                    "sem o histórico da conversa. NÃO responda a pergunta, "
                    "apenas reformule se necessário, caso contrário retorne como está."),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ])
            
            llm = ChatOpenAI(
                model=self.model,
                api_key=self.api_key,
                temperature=temperature
            )

            history_aware_retriever = create_history_aware_retriever(
                llm, 
                retriever, 
                contextualize_q_prompt
            )
            
            qa_prompt = ChatPromptTemplate.from_messages([
                ("system", prompt + "\n\nContexto: {context}"),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ])
            
            question_answer_chain = create_stuff_documents_chain(
                llm, 
                qa_prompt
            )
            
            rag_chain = create_retrieval_chain(
                history_aware_retriever, 
                question_answer_chain
            )
            
            result = await rag_chain.ainvoke({
                "input": current_question,
                "chat_history": chat_history
            })
            
            return result["answer"]
        
        except Exception:
            raise