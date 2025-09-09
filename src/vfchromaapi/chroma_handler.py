import chromadb

class ChromaHandler:
    def __init__(self):
        self.chroma_client = chromadb.PersistentClient(path="src/chroma")
        
        self.collection_name = "blocker_title"
        
        # init self.collection
        if not self.chroma_client.heartbeat():
            self.collection = None
            return
        try:
            self.collection = self.chroma_client.get_collection(self.collection_name)
            print(f"Successfully accessed collection: {self.collection_name}")
        except Exception as e:
            print(f"Error accessing collection '{self.collection_name}': {e}")
            self.collection = None
        
        # init self.collection_data
        self.collection_data = None
        if self.collection is not None:
            try:
                self.collection_data = self.collection.get()
            except:
                print(f"Error getting collection data in collection {self.collection_name}")
                self.collection_data = None
        
    
    def query(self, query_texts, ids=[], n_results=5):
        if not self.collection:
            return {"error": "ChromaDB collection is not initialized."}
        
        try:
            if ids == []:
                results = self.collection.query(
                    query_texts=[query_texts],
                    n_results=n_results,
                )
            else:
                results = self.collection.query(
                    query_texts=[query_texts],
                    n_results=n_results,
                    ids=ids
                )
            return results
        except Exception as e:
            return {"error": f"Error querying ChromaDB: {e}"}
    
    def get_collection_data(self):
        return self.collection_data