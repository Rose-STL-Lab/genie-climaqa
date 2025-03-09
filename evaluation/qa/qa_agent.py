from llm.base_llm import BaseLLM

QA_SYSTEM_PROMPT = '''
You are an expert assistant in the domain of climate science for question-answering tasks.
Use two sentences maximum and keep the answer concise.
'''

class QAAgent:

    def __init__(self, llm: BaseLLM):
        self.llm = llm
        self.name = self.llm.name 
    
    def get_answer(self, question):
        return self.llm.get_result(QA_SYSTEM_PROMPT, question).strip()