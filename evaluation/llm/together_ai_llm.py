from llm.base_llm import BaseLLM
import os
from openai import OpenAI
import time

TOGETHER_API_KEY = os.getenv('TOGETHER_API_KEY')

MODEL_MAP = {
    'mixtral-8x22b': 'mistralai/Mixtral-8x22B-Instruct-v0.1',
    'llama3-70b': 'meta-llama/Llama-3-70b-chat-hf',
    'gemma-27b': 'google/gemma-2-27b-it'
}

class TogetherAILLM(BaseLLM):

    def __init__(self, name):
        super().__init__(name)
        self.client = OpenAI(
            api_key=TOGETHER_API_KEY,
            base_url='https://api.together.xyz/v1',
        )
        self.model_name = MODEL_MAP[name]
    
    def get_result(self, system_prompt, user_prompt):
        response = self.client.chat.completions.create(
            model=self.model_name,
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
            model=self.model_name,
            logprobs=True,
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
        generated_token = response.choices[0].logprobs.tokens[0].strip()
        logprob = response.choices[0].logprobs.token_logprobs[0]
        if generated_token in tokens:
            return [{'token': generated_token, 'logprob': logprob}]
        else:
            return []
    
    def get_top_token(self, system_prompt, user_prompt, retry=2):
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                logprobs=True,
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
            return response.choices[0].logprobs.tokens[0].strip()
        except Exception as e:
            if retry > 0:
                print(f'Got error {e}\nRetrying after 5 seconds...')
                time.sleep(5)
                return self.get_top_token(system_prompt, user_prompt, retry-1)
            else:
                raise e
