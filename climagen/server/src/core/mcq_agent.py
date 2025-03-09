from src.entities.multiple_choice_question import MultipleChoiceQuestion
from src.service.openai_client import OpenAIClient
from src.entities.context import Context
from src.utils import prompts
import json

class MCQAgent:
    def __init__(self):
        self.llm = OpenAIClient()

    def is_answer_valid(self, json_string):
        try:
            json_obj = json.loads(json_string)
            if 'answer' in json_obj:
                return True
            else:
                return False
        except Exception as e:
            return False

    async def get_answer(self, mcq: MultipleChoiceQuestion, context: Context, retrieved_contexts: list[Context], max_retries=2):
        user_prompt = mcq.get_text()
        user_prompt += '\nContext:\n' + context.content
        user_prompt += '\n\nRetrieved Contexts:\n'
        for doc in retrieved_contexts:
            user_prompt += doc.content + '\n\n-------------------\n\n'
        json_string = await self.llm.get_result(prompts.MCQ_AGENT_SYSTEM_PROMPT, user_prompt)
        if self.is_answer_valid(json_string):
            json_obj = json.loads(json_string)
            return json_obj['answer']
        else:
            json_string = await self.llm.get_result(prompts.JSON_FIX_SYSTEM_PROMPT, json_string)
            if self.is_answer_valid(json_string):
                json_obj = json.loads(json_string)
                return json_obj['answer']
            elif max_retries > 0:
                print('The answer was in wrong format:')
                print(json_string)
                print('Retrying...')
                return await self.get_answer(mcq, context, retrieved_contexts, max_retries-1)
            else:
                return 'Bad Answer'