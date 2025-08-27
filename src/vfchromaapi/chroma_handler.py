import chromadb

class ChromaHandler:
    def __init__(self):
        self.chroma_client = chromadb.PersistentClient(path="src\chroma")
        if not self.chroma_client.heartbeat():
            self.collection = None
            return
        self.collection_name = "blocker_title"
        try:
            self.collection = self.chroma_client.get_collection(self.collection_name)
            print(f"Successfully accessed collection: {self.collection_name}")
        except Exception as e:
            print(f"Error accessing collection '{self.collection_name}': {e}")
            self.collection = None
    
    def query(self, query_text, n_results=5):
        if not self.collection:
            return {"error": "ChromaDB collection is not initialized."}
        
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            return results
        except Exception as e:
            return {"error": f"Error querying ChromaDB: {e}"}