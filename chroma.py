import chromadb
from chromadb.config import Settings
import openai
import os
import uuid

class ChromaMemory:
    def __init__(self, db_path="chroma/db", collection_name="memory_collection"):
        self.client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory=db_path))
        self.collection = self.get_or_create_collection(collection_name)
        openai.api_key = os.environ.get('OPENAI_API_KEY')

    def get_or_create_collection(self, name):
        collections = self.client.list_collections()
        if name not in [c.name for c in collections]:
            self.client.create_collection(name)
        return self.client.get_collection(name)

    def store_memory(self, memory_text):
        # print("[STORE]", memory_text)
        
        embeddings = self.get_embeddings_from_text(memory_text)
        self.collection.add(embeddings=[embeddings], ids=[str(uuid.uuid4())], metadatas={"text": memory_text})

    def retrieve_memory(self, memory_text):
        # print("[RETRIEVE]", memory_text)
        query_embeddings = self.get_embeddings_from_text(memory_text)
        result = self.collection.query(query_embeddings=[query_embeddings], n_results=1)
        if result.get("ids") and len(result['ids'][0]) > 0:
            return result['metadatas'][0][0]['text'], result['distances'][0][0]

    def get_embeddings_from_text(self, text):
        return openai.Embedding.create(
            model="text-embedding-ada-002",
            input=text
        )['data'][0]['embedding']


if __name__ == "__main__":
    memory = ChromaMemory()
    memory.store_memory("This is a memory.")
    print(memory.retrieve_memory("memory"))