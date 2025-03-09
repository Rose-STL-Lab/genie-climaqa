from dotenv import load_dotenv
load_dotenv()

import os
import argparse
import logging
import sys
import asyncio
from src.core.qa_generator import QAGenerator

from src.entities.base_question import QuestionType
from src.entities.cloze_question import ClozeQuestion
from tqdm import tqdm
from src.utils import utils
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


parser = argparse.ArgumentParser()
parser.add_argument("--type", type=str, required=True, help="question type (required)")
parser.add_argument("-n", type=int, default=10, help="Minimum number of questions to be generated")
args = parser.parse_args()

question_type = QuestionType(args.type)

OUT_DIR = './results'
os.makedirs(OUT_DIR, exist_ok=True)

generator = QAGenerator()
generator.annotator.ft_model_name[QuestionType.MCQ] = os.getenv('MCQ_ANNOTATOR_MODEL')
generator.annotator.ft_model_name[QuestionType.FREE_FORM] = os.getenv('FFQ_ANNOTATOR_MODEL')
generator.annotator.ft_model_name[QuestionType.CLOZE] = os.getenv('CLOZE_ANNOTATOR_MODEL')
logger.info(f'Using {generator.annotator.ft_model_name[question_type]} for annotation to generate {args.n} {question_type.value} questions')

logging.getLogger().setLevel(logging.WARNING)

async def generate_cloze_qn():
    context = random.choice(generator.context_list)
    retrieved_contexts = await generator.vectorstore_handler.retrieve_contexts(context.content)

    obj = await generator.generate_cloze(context, retrieved_contexts)
    cloze_qn = ClozeQuestion(obj['statement'], None)
    term = await generator.annotator.get_annotation(cloze_qn)
    cloze_qn.term = term

    word_list = []
    for word in cloze_qn.statement.split(' '):
        if word.replace(',','') == term:
            word_list.append('<MASK>')
        else:
            word_list.append(word)
    question = ' '.join(word_list)
    if cloze_qn.statement == question:
        logger.warning(f'Got issue while processing question: {question}. Returned Term: {term}')
        return None
    cloze_qn.statement = question
    cloze_qn.full_context = utils.build_full_context(context, retrieved_contexts)
    return cloze_qn

async def create_questions(generated_questions, total):
    progress_bar = tqdm(total=total, file=sys.stdout)
    if question_type == QuestionType.CLOZE:
        while len(generated_questions) < total:
            res = await generate_cloze_qn()
            if res is not None:
                generated_questions.append(res)
                progress_bar.update(1)
    else:
        while len(generated_questions) < total:
            res, _, _ = await generator.generate_question_list(question_type)
            if res is not None:
                for item in res:
                    generated_questions.append(item)
                progress_bar.update(len(res))
    progress_bar.close()

generated_questions = []
asyncio.run(create_questions(generated_questions, args.n))

if question_type == QuestionType.MCQ:
    df = utils.mcq_to_pandas(generated_questions)
    df = df.drop('Validation', axis=1)
    df.to_csv(os.path.join(OUT_DIR, 'mcq_dataset.csv'))
elif question_type == QuestionType.FREE_FORM:
    df = utils.ffq_to_pandas(generated_questions)
    df = df.drop('Validation', axis=1)
    df.to_csv(os.path.join(OUT_DIR, 'freeform_dataset.csv'))
elif question_type == QuestionType.CLOZE:
    df = utils.cloze_to_pandas(generated_questions)
    df.to_csv(os.path.join(OUT_DIR, 'cloze_dataset.csv'))
