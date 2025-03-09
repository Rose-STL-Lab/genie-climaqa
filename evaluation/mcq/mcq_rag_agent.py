from llm.base_llm import BaseLLM
from mcq.mcq import MCQ
from vector_store_handler import VectorStoreHandler

MCQ_SYSTEM_PROMPT = '''
You are an expert assistant in the domain of climate science for multiple choice question-answering tasks. 
You need to answer the multiple choice question based on the retrieved contexts given along with it. 
The input will be of the following format:
--------------
Question_text

a) Option a
b) Option b
c) Option c
d) Option d

--------------

Retrieved Contexts:
<retrieved_contexts>

The retrieved contexts will be seperated by "--------------" 
you need to ouput a single letter that represents the correct option. Make sure to output a single letter.
'''

USER_PROMPT = '''
{}
--------------

Retrieved Contexts:
{}

Output: '''

class MCQRagAgent:
    def __init__(self, llm: BaseLLM):
        self.llm = llm
        self.name = f'{llm.name}-rag'
        self.vector_store_handler = VectorStoreHandler(threshold=0.5)

    def get_answer(self, mcq: MCQ):
        retrieved_contexts = self.vector_store_handler.retrieve_contexts(mcq.get_text())
        top_token = self.llm.get_top_token(MCQ_SYSTEM_PROMPT, USER_PROMPT.format(mcq.get_text(),'\n\n--------------\n\n'.join(retrieved_contexts[:4])))
        if top_token not in mcq.options:
            return 'Bad Answer'
        else:
            return top_token