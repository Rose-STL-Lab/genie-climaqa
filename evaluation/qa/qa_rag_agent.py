from llm.base_llm import BaseLLM
from vector_store_handler import VectorStoreHandler

QA_SYSTEM_PROMPT = '''
You are an expert assistant in the domain of climate science for question-answering tasks.
You need to answer the question based on the retrieved contexts given along with it.
Use two sentences maximum and keep the answer concise.

The input will be of the following format:
--------------
Question: <question_text>

--------------

Retrieved Contexts:
<retrieved_contexts>

The retrieved contexts will be seperated by "--------------" 
'''

USER_PROMPT = '''
Question: {}

--------------

Retrieved Contexts:
{}

Answer: '''

class QARagAgent:

    def __init__(self, llm: BaseLLM):
        self.llm = llm
        self.name = f'{self.llm.name}-rag'
        self.vector_store_handler = VectorStoreHandler(threshold=0.5)
    
    def get_answer(self, question):
        retrieved_contexts = self.vector_store_handler.retrieve_contexts(question)
        return self.llm.get_result(QA_SYSTEM_PROMPT, USER_PROMPT.format(question,'\n\n--------------\n\n'.join(retrieved_contexts[:4]))).strip()