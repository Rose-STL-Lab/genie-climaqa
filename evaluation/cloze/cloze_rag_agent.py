from llm.base_llm import BaseLLM
from vector_store_handler import VectorStoreHandler

CLOZE_SYSTEM_PROMPT = '''
You are an expert assistant in the domain of climate science for fill-in-the-blank question-answering.
The question will contain a sientific statement with a single word masked with the token - <MASK>.
You need to find the most appropriate word that can be filled in it's place based on the context around it.

you need to ouput a single word that best fits the blank

The input will be of the following format:
--------------
Question: <question_text>

--------------

Retrieved Contexts:
<retrieved_contexts>

The retrieved contexts will be seperated by "--------------"
Make sure to ouput a single word that best fits the blank
'''

USER_PROMPT = '''
{}
--------------

Retrieved Contexts:
{}

Answer: '''

class ClozeRagAgent:
    def __init__(self, llm: BaseLLM):
        self.llm = llm
        self.name = f'{llm.name}-rag'
        self.vector_store_handler = VectorStoreHandler(threshold=0.5)

    def get_answer(self, question):
        retrieved_contexts = self.vector_store_handler.retrieve_contexts(question)
        return self.llm.get_result(CLOZE_SYSTEM_PROMPT, USER_PROMPT.format(question,'\n\n--------------\n\n'.join(retrieved_contexts[:4]))).strip()