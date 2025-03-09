import os
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

class VectorStoreHandler:
    def __init__(self, threshold=0.85):
        self.persist_dir = './chroma'
        self.vectorstore = Chroma(persist_directory=self.persist_dir, embedding_function=OpenAIEmbeddings())
        self.retriever = self.vectorstore.as_retriever(search_type="similarity_score_threshold", 
                                                       search_kwargs={'score_threshold': threshold})
    
    def retrieve_contexts(self, query) -> list[str]:
        retrieved_docs = self.retriever.invoke(query)
        retrieved_contexts = []
        for doc in retrieved_docs:
            retrieved_contexts.append(doc.page_content)
        return retrieved_contexts