from llm.base_llm import BaseLLM

CLOZE_SYSTEM_PROMPT = '''
You are an expert assistant in the domain of climate science for fill-in-the-blank question-answering.
The question will contain a sientific statement with a single word masked with the token - <MASK>.
You need to find the most appropriate word that can be filled in it's place based on the context around it.

you need to ouput a single word that best fits the blank
'''

class ClozeAgent:
    def __init__(self, llm: BaseLLM):
        self.llm = llm
        self.name = llm.name

    def get_answer(self, question):
        return self.llm.get_result(CLOZE_SYSTEM_PROMPT, f'{question}\nAnswer: ').strip()