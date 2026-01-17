from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.embeddings.base import Embeddings
from dotenv import load_dotenv
import os
import shutil
import requests

class AliyunEmbeddings(Embeddings):
    """自定义阿里云百炼Embeddings类"""
    def __init__(self, api_key, model="text-embedding-v4"):
        self.api_key = api_key
        self.model = model
        self.url = "https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings"
    
    def embed_documents(self, texts):
        """获取多个文档的embedding"""
        # 确保texts是字符串列表
        if not isinstance(texts, list):
            texts = [texts]
        
        # 过滤空字符串
        texts = [text for text in texts if text and isinstance(text, str)]
        
        if not texts:
            return []
        
        # 阿里云百炼API配置
        api_key = self.api_key
        model = self.model
        url = self.url
        
        # 确保URL格式正确
        if not url.endswith('/'):
            url = url + '/'  # 确保URL以/结尾
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json"
        }
        
        # 确保输入文本数量不超过API限制（阿里云限制一次不超过10条）
        batch_size = 10
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            
            data = {
                "model": model,
                "input": batch_texts,
                "encoding_format": "float"
            }
            
            try:
                print(f"[DEBUG] Sending batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1} to Aliyun API")
                print(f"[DEBUG] URL: {url}")
                print(f"[DEBUG] Headers: {headers}")
                print(f"[DEBUG] Request data size: {len(batch_texts)} texts")
                
                # 直接使用POST请求，不依赖requests的默认行为
                import http.client
                import json
                
                # 解析URL
                from urllib.parse import urlparse
                parsed_url = urlparse(url)
                host = parsed_url.netloc
                path = parsed_url.path
                
                # 创建HTTPS连接
                conn = http.client.HTTPSConnection(host, timeout=30)
                
                # 准备请求
                conn.request(
                    "POST",
                    path,
                    body=json.dumps(data),
                    headers=headers
                )
                
                # 获取响应
                response = conn.getresponse()
                response_data = response.read().decode()
                conn.close()
                
                print(f"[DEBUG] Response status: {response.status}")
                print(f"[DEBUG] Response reason: {response.reason}")
                print(f"[DEBUG] Response data: {response_data}")
                
                # 检查响应状态
                if response.status != 200:
                    raise Exception(f"API Error: {response.status} {response.reason} - {response_data}")
                
                # 解析响应
                result = json.loads(response_data)
                embeddings = [item["embedding"] for item in result["data"]]
                all_embeddings.extend(embeddings)
                
            except Exception as e:
                print(f"[ERROR] Batch {i//batch_size + 1} failed: {type(e).__name__}: {str(e)}")
                import traceback
                traceback.print_exc()
                raise
        
        return all_embeddings
    
    def embed_query(self, text):
        """获取查询文本的embedding"""
        if not isinstance(text, str):
            text = str(text)
        
        # 确保文本不为空
        if not text.strip():
            # 返回一个默认的零向量作为备选
            return [0.0] * 1024  # 使用默认维度1024
        
        try:
            embeddings = self.embed_documents([text])
            if embeddings and len(embeddings) > 0:
                return embeddings[0]
            else:
                # 如果没有获取到有效嵌入，返回默认零向量
                print(f"[WARNING] Failed to get embedding for query: {text}")
                return [0.0] * 1024  # 使用默认维度1024
        except Exception as e:
            print(f"[ERROR] Error in embed_query: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            # 返回默认零向量作为备选
            return [0.0] * 1024  # 使用默认维度1024

class KnowledgeBaseLoader:
    def __init__(self, kb_dir, persist_dir="./chroma_db", api_key=None):
        load_dotenv()
        self.kb_dir = kb_dir
        self.persist_dir = persist_dir
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY is required. Please set it in .env file or provide it directly.")
        
        # 检查阿里云API密钥
        self.dashscope_api_key = os.getenv("DASHSCOPE_API_KEY")
        if not self.dashscope_api_key:
            raise ValueError("DASHSCOPE_API_KEY is required. Please set it in .env file.")
        
        # Initialize embeddings - 使用自定义阿里云百炼接口
        self.embeddings = AliyunEmbeddings(
            api_key=self.dashscope_api_key,
            model="text-embedding-v4"
        )
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", "", "\r\n\r\n", "\r\n"]
        )
    
    def load_documents(self):
        """Load all markdown documents from the knowledge base directory"""
        loader = DirectoryLoader(
            self.kb_dir,
            glob="*.md",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"}
        )
        return loader.load()
    
    def process_documents(self, documents):
        """Split documents into chunks"""
        return self.text_splitter.split_documents(documents)
    
    def create_vector_store(self, documents):
        """Create vector store from processed documents"""
        # Clear existing vector store if it exists
        if os.path.exists(self.persist_dir):
            shutil.rmtree(self.persist_dir)
        
        # Create new vector store
        vector_store = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_dir
        )
        
        return vector_store
    
    def load_vector_store(self):
        """Load existing vector store"""
        if not os.path.exists(self.persist_dir):
            raise ValueError(f"Vector store not found at {self.persist_dir}. Please build the knowledge base first.")
        
        return Chroma(
            persist_directory=self.persist_dir,
            embedding_function=self.embeddings
        )
    
    def build_knowledge_base(self):
        """Complete pipeline to build knowledge base"""
        print("Loading documents...")
        documents = self.load_documents()
        print(f"Loaded {len(documents)} documents")
        
        print("Processing documents...")
        chunks = self.process_documents(documents)
        print(f"Created {len(chunks)} document chunks")
        
        print("Creating vector store...")
        vector_store = self.create_vector_store(chunks)
        print(f"Knowledge base built successfully! Vector store persisted at {self.persist_dir}")
        
        return vector_store
