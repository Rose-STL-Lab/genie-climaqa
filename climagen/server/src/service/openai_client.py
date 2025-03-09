import asyncio
from openai import AsyncOpenAI

class OpenAIClient():

    def __init__(self):
        self.client = AsyncOpenAI()
    
    async def get_result(self, system_prompt, user_prompt, model_name='gpt-3.5-turbo'):
        response = await self.client.chat.completions.create(
            model=model_name,
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
            temperature=0
        )
        return response.choices[0].message.content
    
    async def get_job_with_suffix(self, suffix):
        obj = await self.client.fine_tuning.jobs.list()
        jobs = obj.data
        for job in jobs:
            if job.user_provided_suffix == suffix:
                return job
        return None

    async def create_ft_job(self, training_file, suffix, model_name="gpt-4o-mini-2024-07-18"):
        train_file = await self.client.files.create(
            file=open(training_file, "rb"),
            purpose="fine-tune"
        )
        job = await self.client.fine_tuning.jobs.create(
            training_file=train_file.id, 
            model=model_name,
            suffix=suffix
        )
        return job
    
    async def wait_for_job_completion(self, id):
        job = await self.client.fine_tuning.jobs.retrieve(id)
        while job.status != "succeeded" and job.status != "failed" and job.status != "cancelled":
            await asyncio.sleep(10)
            job = await self.client.fine_tuning.jobs.retrieve(id)
        return job

    async def get_logit_result(self, system_prompt, user_prompt, model_name):
        response = await self.client.chat.completions.create(
            model=model_name,
            logprobs=True,
            top_logprobs=2,
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
        return response.choices[0].logprobs.content[0]