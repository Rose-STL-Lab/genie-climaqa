from llm.base_llm import BaseLLM

QA_SYSTEM_PROMPT = '''
You are an expert assistant in the domain of climate science for question-answering tasks.
Use two sentences maximum and keep the answer concise.

Here are a few examples:
-------------

Question: What is the main requirement for a cloud to be considered adiabatic?
Answer: The main requirement for a cloud to be considered adiabatic is that it forms with no exchange of energy or mass with its environment.
-------------

Question: How do changes in the net cloud radiative effect at the top of the atmosphere impact the Earth's radiative forcing due to aerosol-cloud interactions?
Answer: Changes in the net cloud radiative effect at the top of the atmosphere can cause a radiative forcing due to aerosol-cloud interactions.
-------------

Question: How does the planetary albedo impact the Earth's energy budget and what role does it play in the absorption and reflection of solar radiation?
Answer: The planetary albedo, which is the ratio of reflected solar radiation to received solar radiation, plays a crucial role in Earth's energy budget. It impacts the amount of solar radiation absorbed by the Earth's surface and atmosphere. A higher planetary albedo means more solar radiation is reflected back to space, leading to cooler temperatures on Earth. Conversely, a lower planetary albedo results in more solar radiation being absorbed, contributing to warming temperatures.
-------------

Question: What is a necessary condition for a functional J[y] to have a minimum?
Answer: A necessary condition for the functional J[y] to have a minimum for y = y is that the second variation 82J[h] be nonnegative for y ≠ y and all admissible h.
-------------

Question: How do fast climate feedbacks differ from slow climate response in terms of timescale and surface temperature response?
Answer: Fast climate feedbacks occur on a shorter timescale than the slow climate response and can occur without any surface temperature response.
-------------
'''

class QAFewshotAgent:

    def __init__(self, llm: BaseLLM):
        self.llm = llm
        self.name = f'{self.llm.name}-fs'
    
    def get_answer(self, question):
        return self.llm.get_result(QA_SYSTEM_PROMPT, f'Question: {question}\nAnswer: ').strip()