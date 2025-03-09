from llm.base_llm import BaseLLM

CLOZE_SYSTEM_PROMPT = '''
You are an expert assistant in the domain of climate science for fill-in-the-blank question-answering.
The question will contain a sientific statement with a single word masked with the token - <MASK>.
You need to find the most appropriate word that can be filled in it's place based on the context around it.

you need to ouput a single word that best fits the blank

Here are a few examples:
-------------

The exchange of heat between the atmosphere and the ocean mixed layer plays a crucial role in damping and <MASK> the response of local sea-surface temperature to various atmospheric variability.
Answer: delaying
-------------

Aerosol optical depth is the column-integrated aerosol extinction of radiation at a given <MASK>, and it can be measured using ground-based or space-borne remote-sensing instruments, being widely used in the volcanic aerosol community.
Answer: wavelength
-------------

The radar reflectivity factor Z increases sharply with increasing size of hydrometeors, which can lead to an <MASK> of precipitation if not accounted for.
Answer: underestimation
-------------

<MASK> imagery allows for the distinction between high and low clouds based on their temperatures, with high clouds typically exhibiting lower temperatures than low clouds.
Answer: Infrared
-------------

The thermal wind in the atmosphere varies with altitude due to the non-uniform temperature distribution, leading to changes in the <MASK> wind shear.
Answer: geostrophic
-------------
'''

class ClozeFewShotAgent:
    def __init__(self, llm: BaseLLM):
        self.llm = llm
        self.name = f'{llm.name}-fs'

    def get_answer(self, question):
        return self.llm.get_result(CLOZE_SYSTEM_PROMPT, f'{question}\nAnswer: ').strip()