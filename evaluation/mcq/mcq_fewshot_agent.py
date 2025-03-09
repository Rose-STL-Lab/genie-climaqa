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

you need to ouput a single letter that represents the correct option. Here are a few examples:
--------------  
Which type of clouds have a greenhouse effect that dominates over their albedo effect?


a) Cirrus clouds
b) Nimbostratus clouds
c) Stratus clouds
d) Stratocumulus clouds

Output: a
--------------
What is a characteristic difference between the block-kriged surface and the distribution of log10 K?


a) The block-kriged surface is more variable than the log10 K distribution.
b) The block-kriged surface is more jagged than the log10 K distribution.
c) The block-kriged surface is smoother than the log10 K distribution.
d) The block-kriged surface is less smooth than the log10 K distribution.

Output: c
--------------
Which of the following gases is mainly produced by the oxidation of methane or nonmethane hydrocarbons and has a dominant sink through oxidation by OH?


a) Nitrous oxide
b) Hydrogen peroxide
c) Carbon monoxide
d) Carbon dioxide

Output: c
--------------
What type of spatial correlation dominates for Cd, Pb, and Cu compared to Co and Ni in the soil at La Chaux-de-Fonds?


a) Moderate range
b) Short range
c) No correlation
d) Long range

Output: b
--------------
Question: What is the level beyond which an air parcel rises freely due to its positive buoyancy?


a) Level of Forced Convection (LFC)
b) Level of Stable Air (LSA)
c) Level of Neutral Buoyancy (LNB)
d) Level of Free Convection (LFC)

Output: d
-----------

Make sure to output a single letter that represents the correct option.
'''

class MCQFewShotAgent:
    def __init__(self, llm: BaseLLM):
        self.llm = llm
        self.name = f'{llm.name}-fs'

    def get_answer(self, mcq: MCQ):
        top_token = self.llm.get_top_token(MCQ_SYSTEM_PROMPT, mcq.get_text() + 'Output: ')
        if top_token not in mcq.options:
            return 'Bad Answer'
        else:
            return top_token