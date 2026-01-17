from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

class KnowledgeBaseQA:
    def __init__(self, vector_store, api_key=None):
        load_dotenv()
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY is required. Please set it in .env file or provide it directly.")
        
        self.vector_store = vector_store
        
        # Initialize Deepseek chat model using OpenAI compatible client
        self.llm = ChatOpenAI(
            model="deepseek-chat",
            api_key=self.api_key,
            base_url="https://api.deepseek.com/v1",
            temperature=0.3,
            max_tokens=1024
        )
    
    def ask_question(self, question, answer_only=False):
        """Ask a question and get answer from the knowledge base"""
        # Retrieve relevant documents
        docs = self.vector_store.similarity_search(question, k=3)
        
        # Format context from retrieved documents
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # Create prompt with context and question
        prompt = f"""You are a helpful assistant that answers questions based on the provided context.\n\nContext:\n{context}\n\nQuestion:\n{question}\n\nInstructions:\n- Answer strictly based on the context provided\n- If the answer is not found in the context, say "I don't have enough information to answer that question."\n- Be clear and concise in your response\n- Use bullet points if multiple items need to be listed\n\nAnswer:\n"""
        
        # Get response from LLM
        response = self.llm.invoke(prompt)
        
        if answer_only:
            return response.content
        else:
            return {
                "answer": response.content,
                "sources": [doc.metadata["source"] for doc in docs]
            }
