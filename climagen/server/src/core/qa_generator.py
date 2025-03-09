import json
import random
import asyncio
from datetime import datetime
import logging

from src.utils import prompts, utils
from src.service.openai_client import OpenAIClient
from src.service.vector_store_handler import VectorStoreHandler
from src.service.firebase_client import FirebaseClient
from src.entities.base_question import QuestionType, QuestionComplexity, BaseQuestion
from src.entities.free_form_question import FreeFormQuestion
from src.entities.multiple_choice_question import MultipleChoiceQuestion
from src.core.mcq_agent import MCQAgent
from src.core.annotator import Annotator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QAGenerator():
    def __init__(self, queue_max_size=10, offline_mode=True):
        self.mcq_queue = asyncio.Queue(maxsize=queue_max_size)
        self.ffq_queue = asyncio.Queue(maxsize=queue_max_size)
        self.openai_client = OpenAIClient()
        self.vectorstore_handler = VectorStoreHandler()
        self.context_list = self.vectorstore_handler.load_context_list()
        self.mcq_agent = MCQAgent()
        self.firebase_client = FirebaseClient()
        self.annotator = Annotator()
        self.offline_mode = offline_mode
    
    async def populate_queues(self):
        while True:
            are_both_full = True
            if not self.mcq_queue.full():
                question_list, context, retrieved_contexts = await self.generate_question_list(QuestionType.MCQ)
                if question_list is not None:
                    scientific_annotation = await self.generate_cloze(context, retrieved_contexts)
                    data = utils.build_queue_object(question_list, scientific_annotation, context, retrieved_contexts)
                    await self.mcq_queue.put(data)
                    logger.info("Added data to MCQ queue")
                are_both_full = False
            if not self.ffq_queue.full():
                question_list, context, retrieved_contexts = await self.generate_question_list(QuestionType.FREE_FORM)
                if question_list is not None:
                    scientific_annotation = await self.generate_cloze(context, retrieved_contexts)
                    data = utils.build_queue_object(question_list, scientific_annotation, context, retrieved_contexts)
                    await self.ffq_queue.put(data)
                    logger.info("Added data to FREE_FORM queue")
                are_both_full = False
            if are_both_full:
                # to avoid blocking other operations
                await asyncio.sleep(1)
    
    async def pop_queue(self, question_type: QuestionType):
        try:
            if question_type == QuestionType.MCQ:
                obj = await self.mcq_queue.get()
                return obj
            elif question_type == QuestionType.FREE_FORM:
                return await self.ffq_queue.get()
        except asyncio.QueueEmpty as e:
            logger.warning("Queue is empty. Retrying after 1 second...")
            await asyncio.sleep(1)
            return await self.pop_queue()

    async def generate_cloze(self, context, retrieved_contexts, retry_count=3):
        try:
            user_prompt = prompts.BASE_USER_PROMPT.format(context.content, utils.build_retrieved_context_string(retrieved_contexts))
            res = await self.openai_client.get_result(prompts.CLOZE_SYSTEM_PROMPT, user_prompt)
            # print(f"Got following json from openai:\n{res}")
            res = json.loads(res)
            assert "statement" in res
            return res
        except Exception as e:
            logger.error(f"Got error while generating cloze {e}")
            logger.info(f"Result from openai:\n{res}")
            if retry_count > 0:
                logger.info("Retrying...")
                return await self.generate_cloze(context, retrieved_contexts, retry_count-1)
            else:
                return {"statement": ""}
    
    async def generate_question(self, question_type: QuestionType, context, retrieved_contexts, retry_count=3):
        try:
            user_prompt = prompts.BASE_USER_PROMPT.format(context.content, utils.build_retrieved_context_string(retrieved_contexts))
            if question_type == QuestionType.MCQ:
                res = await self.openai_client.get_result(prompts.MCQ_SYSTEM_PROMPT, user_prompt)
                # print(f"Got following json from openai:\n{res}")
                res = json.loads(res)
                res['question_complexity'] = QuestionComplexity.BASE
                question = MultipleChoiceQuestion(**res).shuffle_options()
            elif question_type == QuestionType.FREE_FORM:
                res = await self.openai_client.get_result(prompts.FFQ_SYSTEM_PROMPT, user_prompt)
                # print(f"Got following json from openai:\n{res}")
                res = json.loads(res)
                res['question_complexity'] = QuestionComplexity.BASE
                question = FreeFormQuestion(**res)
            is_valid = await self.is_question_valid(question, context, retrieved_contexts)
            if is_valid:
                question.full_context = utils.build_full_context(context, retrieved_contexts)
                return question
            else:
                return None
        except Exception as e:
            logger.error(f"Got error while generating question {e}")
            logger.info(f"Result from openai:\n{res}")
            if retry_count > 0:
                logger.info("Retrying...")
                return await self.generate_question(question_type, context, retrieved_contexts, retry_count-1)
            else:
                return None

    async def add_complexity(self, question: BaseQuestion, question_complexity: QuestionComplexity, context, retrieved_contexts, retry_count=3):
        try:
            if question.question_type == QuestionType.MCQ:
                if question_complexity == QuestionComplexity.REASONING:
                    system_prompt = prompts.REASONING_MCQ_PROMPT
                elif question_complexity == QuestionComplexity.HYPOTHETICAL:
                    system_prompt = prompts.HYPOTHETICAL_MCQ_PROMPT
            elif question.question_type == QuestionType.FREE_FORM:
                if question_complexity == QuestionComplexity.REASONING:
                    system_prompt = prompts.REASONING_FFQ_PROMPT
                if question_complexity == QuestionComplexity.HYPOTHETICAL:
                    system_prompt = prompts.HYPOTHETICAL_FFQ_PROMPT
            user_prompt = prompts.COMPLEXITY_USER_PROMPT.format(question.get_text(), context.content,
                                                                utils.build_retrieved_context_string(retrieved_contexts))
            
            res = await self.openai_client.get_result(system_prompt, user_prompt)
            # print(f"Got following json from openai:\n{res}")
            res = json.loads(res)
            res['question_complexity'] = question_complexity

            if question.question_type == QuestionType.MCQ:
                complex_question = MultipleChoiceQuestion(**res).shuffle_options()
            elif question.question_type == QuestionType.FREE_FORM:
                complex_question = FreeFormQuestion(**res)
            
            is_valid = await self.is_question_valid(complex_question, context, retrieved_contexts)
            if is_valid:
                complex_question.full_context = utils.build_full_context(context, retrieved_contexts)
                return complex_question
            else:
                return None
        except Exception as e:
            logger.error(f"Got error while generating question {e}")
            logger.info(f"Result from openai:\n{res}")
            if retry_count > 0:
                logger.info("Retrying...")
                return await self.add_complexity(question, question_complexity, context, retrieved_contexts, retry_count-1)
            else:
                return None

    async def generate_question_list(self, question_type):
        context = random.choice(self.context_list)
        retrieved_contexts = await self.vectorstore_handler.retrieve_contexts(context.content)
        question = await self.generate_question(question_type, context, retrieved_contexts)
        if question is not None and (await self.pass_annotation_filter(question)):
            question_list = [question]
            reasoning_question = await self.add_complexity(question, QuestionComplexity.REASONING, context, retrieved_contexts)
            if reasoning_question is not None and (await self.pass_annotation_filter(reasoning_question)):
                question_list.append(reasoning_question)
            hypothetical_question = await self.add_complexity(question, QuestionComplexity.HYPOTHETICAL, context, retrieved_contexts)
            if hypothetical_question is not None and (await self.pass_annotation_filter(hypothetical_question)):
                question_list.append(hypothetical_question)
            for item in question_list:
                item.full_context = utils.build_retrieved_context_string([context] + retrieved_contexts)
            return question_list, context, retrieved_contexts
        else:
            return None, context, retrieved_contexts
    
    async def is_question_valid(self, question: BaseQuestion, context, retrieved_contexts):
        if 'context' in question.question:
            logger.info(f'Context was refered in question with complexity {question.question_complexity}')
            if not self.offline_mode:
                await self.submit_invalid_question(question, 'Context Reference', context, retrieved_contexts)
            return False
        if question.question_type == QuestionType.MCQ:
            agent_answer = await self.mcq_agent.get_answer(question, context, retrieved_contexts)
            if agent_answer != question.correct_option:
                logger.info(f'The LLM was not self consistent for the question with complexity {question.question_complexity}')
                if not self.offline_mode:
                    await self.submit_invalid_question(question, 'Self Inconsistency', context, retrieved_contexts)
                return False
        return True
    
    async def pass_annotation_filter(self, question):
        annotation, confidence = await self.annotator.get_annotation(question)
        # logger.info(f"Got annotation for {question.question_type}: {annotation}, {confidence}")
        if annotation is None:
            return True
        if self.offline_mode:
            return annotation == "VALID"
        else:
            if confidence > 0.85:
                return random.random() > 0.5
            else:
                return True

    def get_queue_size(self, question_type: QuestionType):
        if question_type == QuestionType.MCQ:
            return self.mcq_queue.qsize()
        elif question_type == QuestionType.FREE_FORM:
            return self.ffq_queue.qsize()
    
    async def submit_invalid_question(self, question: BaseQuestion, reason, context, retrieved_contexts):
        context_id = self.firebase_client.persist_context(context)
        retrieved_context_ids = [self.firebase_client.persist_context(doc) for doc in retrieved_contexts]
        question.context_id = context_id
        question.retrieved_context_ids = retrieved_context_ids
        question.is_valid = False
        question.reason = reason
        question.user_id = 'agent'
        question.user_email = 'agent'
        question.submission_timestamp = datetime.now().isoformat()
        self.firebase_client.persist_question(question)
    