import os
from qa.metrics.base_metric import BaseMetric
from qa import qa_utils
from openai import OpenAI
import numpy as np
import tiktoken

LABELS = ['SUPPORTS', 'REFUTES']

LOGIT_SYS_PROMPT = f'''
You are a climate expert that annotates if a given claim either SUPPORTS or REFUTES the presented evidence.
You will be provided the following as the input:

Evidence: <evidence>
Claim: <claim>

Respond with just one word - {LABELS[0]} if the claim supports the evidence and {LABELS[1]} otherwise.
'''

USER_PROMPT = '''
Evidence: {}
Claim: {}
'''

class FAScore(BaseMetric):
    
    def __init__(self, openai_model='gpt-4') -> None:
        super().__init__()
        self.client = OpenAI()
        self.model_name = openai_model
        encoding_model =  openai_model.split(':')[1] if openai_model[:2] == 'ft' else openai_model
        self.encoder = tiktoken.encoding_for_model(encoding_model)
    
    def get_sentence_score(self, reference_answer, generated_answer):
        response = self.client.chat.completions.create(
            model=self.model_name,
            logprobs=True,
            top_logprobs=20,
            messages=[
                {
                    "role": "system", 
                    "content": LOGIT_SYS_PROMPT
                },
                {
                    "role": "user",
                    "content": USER_PROMPT.format(reference_answer, generated_answer)
                }
            ],
        )
        result = response.choices[0].logprobs.content[0].top_logprobs

        label_tokens = [self.encoder.decode(self.encoder.encode(label)[:1]) for label in LABELS]
        label_logprobs = [-100, -100]
        for i in range(len(label_logprobs)):
            for res in result:
                if res.token == label_tokens[i]:
                    label_logprobs[i] = res.logprob

        ratio = np.exp(label_logprobs[0] - label_logprobs[1])
        score = ratio/(ratio+1)

        return qa_utils.smooth_probability(score)
    
    def get_corpus_score(self, reference_answer_corpus, generated_answer_corpus):
        if len(reference_answer_corpus) == 0:
            return 0
        scores = []
        binary_scores = []
        for reference_answer, generated_answer in zip(reference_answer_corpus, generated_answer_corpus):
            score = self.get_sentence_score(reference_answer, generated_answer)
            scores.append(score)
            binary_scores.append(1 if score>0.5 else 0)
        return np.mean(scores), np.mean(binary_scores)
