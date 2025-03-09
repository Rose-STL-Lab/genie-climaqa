import os
import json
import random
import logging
import asyncio
import numpy as np

from src.entities.base_question import QuestionType, BaseQuestion
from src.service.firebase_client import FirebaseClient
from src.service.openai_client import OpenAIClient
from src.entities.context import Context
from src.utils import utils, prompts

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Annotator:
    def __init__(self, mcq_trigger_count=15, ffq_trigger_count=10):
        self.ft_model_name = {
            QuestionType.MCQ: None,
            QuestionType.FREE_FORM: None,
            QuestionType.CLOZE: None
        }
        self.mcq_trigger_count = mcq_trigger_count
        self.ffq_trigger_count = ffq_trigger_count
        self.interval = 5
        
        self.firebase_client = FirebaseClient()
        self.openai_client = OpenAIClient()
    
    async def get_annotation(self, question: BaseQuestion):
        model_name = self.ft_model_name[question.question_type]
        if model_name is None:
            return None, None
        
        if question.question_type == QuestionType.CLOZE:
            result = await self.openai_client.get_result(prompts.ANNOTATE_CLOZE_SYS_PROMPT,
                        prompts.ANNOTATE_CLOZE_USER_PROMPT.format(question.statement), model_name)
            return result
            
        elif question.question_type == QuestionType.MCQ:
            sys_prompt = prompts.ANNOTATE_MCQ_SYS_PROMPT
            answer = question.correct_option
        else:
            sys_prompt = prompts.ANNOTATE_FFQ_SYS_PROMPT
            answer = question.answer
        
        result = await self.openai_client.get_logit_result(sys_prompt, 
                    prompts.ANNOTATE_USER_PROMPT.format(question.get_text(), answer, question.full_context),
                   model_name)
        
        annotation = result.token
        ratio = np.exp(result.top_logprobs[0].logprob - result.top_logprobs[1].logprob)
        confidence = ratio/(ratio+1)
        confidence = utils.smooth_probability(confidence)
        logger.info(f"Used model {model_name} for annotation: {annotation}, {confidence}")
        return annotation, confidence

    async def trigger(self):
        mcq_invalid_count, ffq_invalid_count = self.firebase_client.get_invalid_question_count()

        if mcq_invalid_count >= self.mcq_trigger_count:
            most_recent_count = (mcq_invalid_count//self.interval)*self.interval
            suffix = f'mcq-{most_recent_count}'
            await self.schedule_finetuning_if_req(suffix, QuestionType.MCQ)
        if ffq_invalid_count >= self.ffq_trigger_count:
            most_recent_count = (ffq_invalid_count//self.interval)*self.interval
            suffix = f'freeform-{most_recent_count}'
            await self.schedule_finetuning_if_req(suffix, QuestionType.FREE_FORM)
    
    async def schedule_finetuning_if_req(self, suffix, question_type: QuestionType):
        job = await self.openai_client.get_job_with_suffix(suffix)
        if job is None:
            logger.info(f"Found no job with suffix {suffix}. Scheduling a fine-tuning job")
            training_file = await self.prepare_train_file(suffix, question_type)
            job = await self.openai_client.create_ft_job(training_file, suffix)
            logger.info(f"Created openai fine-tuning job: {job.id}, {suffix}")
            
            job = await self.openai_client.wait_for_job_completion(job.id)
            if job.status == "failed" or job.status == "cancelled":
                logger.warning(f"There was a problem in the fine-tuning job: {job.id}, {job.status}")
            elif job.status == "succeeded":
                logger.info(f"Finetuning job was successful. Updating {question_type.value} annotator to: {job.fine_tuned_model}")
                self.ft_model_name[question_type] = job.fine_tuned_model
        elif job.status == "failed" or job.status == "cancelled":
            logger.warning(f"Found job {job.id} with status: {job.status}")
        elif job.status != "succeeded":
            logger.info(f"Found running job {job.id} with status: {job.status}, Waiting...")
            job = await self.openai_client.wait_for_job_completion(job.id)
            if job.status == "failed" or job.status == "cancelled":
                logger.warning(f"There was a problem in the fine-tuning job: {job.id}, {job.status}")
            elif job.status == "succeeded":
                logger.info(f"Finetuning job was successful. Updating {question_type.value} annotator to: {job.fine_tuned_model}")
                self.ft_model_name[question_type] = job.fine_tuned_model
        elif self.ft_model_name[question_type] != job.fine_tuned_model:
            logger.info(f"Found successful job {job.id} with status: {job.status}")
            logger.info(f"Setting {question_type.value} annotator to: {job.fine_tuned_model}")
            self.ft_model_name[question_type] = job.fine_tuned_model

    async def prepare_train_file(self, suffix, question_type: QuestionType):
        root_dir = 'annotation_data/'
        os.makedirs(root_dir, exist_ok=True)
        file_name = os.path.join(root_dir, f'{suffix}-train.jsonl')
        
        questions = list(self.firebase_client.get_questions_by_user(os.getenv('ADMIN_UID'), question_type).values())
        qn_list = []
        for question in questions:
            qn = utils.question_from_dict(question, question_type)
            qn.full_context = await self.get_full_context(qn)
            qn_list.append(qn)
        train_qn_list = self.select_training_Set(qn_list)
        finetune_dataset = [self.create_finetune_data(qn, question_type) for qn in train_qn_list]
        logger.info(f"Prepared training data with {len(finetune_dataset)} examples")

        with open(file_name, 'w') as f:
            for entry in finetune_dataset:
                json.dump(entry, f)
                f.write('\n')
        return file_name
    
    def select_training_Set(self, question_list):
        valid_question_list = []
        invalid_question_list = []
        for qn in question_list:
            if qn.is_valid:
                valid_question_list.append(qn)
            else:
                invalid_question_list.append(qn)
        
        random.shuffle(valid_question_list)
        final_question_list = invalid_question_list + valid_question_list[:len(invalid_question_list)]
        random.shuffle(final_question_list)
        return final_question_list

    async def get_full_context(self, question):
        context_dicts = list((await asyncio.to_thread(self.firebase_client.get_contexts, [question.context_id] + question.retrieved_context_ids)).values())
        contexts = []
        for context_dict in context_dicts:
            del context_dict['hash']
            contexts.append(Context(**context_dict))
        return utils.build_retrieved_context_string(contexts)
    
    def create_finetune_data(self, question, question_type):
        if question_type == QuestionType.MCQ:
            sys_prompt = prompts.ANNOTATE_MCQ_SYS_PROMPT
            answer = question.correct_option
        else:
            sys_prompt = prompts.ANNOTATE_FFQ_SYS_PROMPT
            answer = question.answer
        
        return {'messages':[
            {
                "role": "system",
                "content": sys_prompt
            },
            {
                "role": "user",
                "content": prompts.ANNOTATE_USER_PROMPT.format(question.get_text(), answer, question.full_context)
            },
            {
                "role": "assistant",
                "content": "VALID" if question.is_valid else "INVALID"
            }
        ]}
