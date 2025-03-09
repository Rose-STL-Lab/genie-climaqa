from llm.base_llm import BaseLLM
from mcq.mcq import MCQ

MCQ_SYSTEM_PROMPT = '''
You are an expert assistant in the domain of climate science for multiple choice question-answering tasks. The question will be of the following format:
--------------
Question_text

a) Option a
b) Option b
c) Option c
d) Option d

-----------

you need to ouput a single letter that represents the correct option. Make sure to output a single letter.
'''

class MCQAgent:
    def __init__(self, llm: BaseLLM):
        self.llm = llm
        self.name = llm.name

    def get_answer(self, mcq: MCQ):
        top_token = self.llm.get_top_token(MCQ_SYSTEM_PROMPT, f'{mcq.get_text()} Correct Option: ')
        if top_token not in mcq.options:
            return 'Bad Answer'
        else:
            return top_token