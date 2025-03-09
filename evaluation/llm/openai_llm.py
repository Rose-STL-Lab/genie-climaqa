from llm.base_llm import BaseLLM
import os
from openai import OpenAI


class OpenAIILLM(BaseLLM):

    def __init__(self, name):
        super().__init__(name)
        self.client = OpenAI()
    
    def get_result(self, system_prompt, user_prompt):
        response = self.client.chat.completions.create(
            model=self.name,
            messages=[
                {
                    "role": "system", 
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
        )
        return response.choices[0].message.content
    
    def get_logit_result(self, system_prompt, user_prompt, tokens):
        response = self.client.chat.completions.create(
            model=self.name,
            logprobs=True,
            top_logprobs=20,
            messages=[
                {
                    "role": "system", 
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
        )
        tokens = [token.strip() for token in tokens]
        top_logits = response.choices[0].logprobs.content[0].top_logprobs
        return sorted([{"token": logit.token, "logprob": logit.logprob}
                       for logit in top_logits if logit.token.strip() in tokens],
                       key=lambda x: x['logprob'], reverse=True)
    
    def get_top_token(self, system_prompt, user_prompt):
        response = self.client.chat.completions.create(
            model=self.name,
            logprobs=True,
            top_logprobs=1,
            messages=[
                {
                    "role": "system", 
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
        )
        return response.choices[0].logprobs.content[0].top_logprobs[0].token.strip()