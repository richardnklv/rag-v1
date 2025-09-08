import os
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.openrouter import OpenRouter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Load environment variables from .env file
load_dotenv()

# Configure LLM
llm = OpenRouter(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    max_tokens=256,
    context_window=4096,
    model="deepseek/deepseek-chat-v3.1:free",
)

# Configure embedding model (using local HuggingFace model to avoid OpenAI costs)
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

# Set global settings
Settings.llm = llm
Settings.embed_model = embed_model

documents = SimpleDirectoryReader("data").load_data()
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()


response = query_engine.query("What is my name?")
print(response)