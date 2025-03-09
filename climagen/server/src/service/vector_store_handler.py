import os
import logging
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

from src.entities.context import Context

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorStoreHandler:
    def __init__(self, threshold=0.85):
        self.persist_dir = os.getenv('CHROMA_PERSIST_DIR')
        self.vectorstore = Chroma(persist_directory=self.persist_dir, embedding_function=OpenAIEmbeddings())
        self.retriever = self.vectorstore.as_retriever(search_type="similarity_score_threshold", 
                                                       search_kwargs={'score_threshold': threshold})
    
    def load_context_list(self) -> list[Context]:
        docs = self.vectorstore.get()
        num_elements = len(docs['documents'])
        logger.info(f"Loaded {num_elements} context documents")
        context_list = []
        for i in range(num_elements):
            context_list.append(Context(docs['metadatas'][i]['source'], docs['metadatas'][i]['page'], 
                                        docs['metadatas'][i]['link'], docs['documents'][i]))
        return context_list
    
    async def retrieve_contexts(self, query) -> list[Context]:
        retrieved_docs = self.retriever.invoke(query)[1:]
        retrieved_contexts = []
        for doc in retrieved_docs:
            retrieved_contexts.append(Context(doc.metadata['source'], doc.metadata['page'], 
                                              doc.metadata['link'], doc.page_content))
        return retrieved_contexts