import pandas as pd
import copy
import numpy as np

from src.entities.base_question import QuestionType, BaseQuestion
from src.entities.free_form_question import FreeFormQuestion
from src.entities.multiple_choice_question import MultipleChoiceQuestion
from src.entities.cloze_question import ClozeQuestion
from src.entities.context import Context

DELIMITER = '\n--------------------\n'
OPTIONS_KEY_DELIMITER = ') '

def question_from_dict(question_dict, question_type) -> BaseQuestion:
    if 'question_type' in question_dict:
        del question_dict['question_type']
    if question_type == QuestionType.MCQ:
        question = MultipleChoiceQuestion(**question_dict)
    elif question_type == QuestionType.FREE_FORM:
        question = FreeFormQuestion(**question_dict)
    elif question_type == QuestionType.CLOZE:
        if 'question_complexity' in question_dict:
            del question_dict['question_complexity']
        question = ClozeQuestion(**question_dict)
    return question

def build_queue_object(question_list: list[BaseQuestion], scientific_annotation, context, retrieved_contexts):
    obj = {}
    obj['context'] = copy.deepcopy(context.__dict__)
    obj['retrieved_contexts'] = [copy.deepcopy(doc.__dict__) for doc in retrieved_contexts]
    for dict in obj['retrieved_contexts'] + [obj['context']]:
        del dict['hash']
    obj['question_type'] = question_list[0].question_type
    obj['questions'] = []
    for question in question_list:
        question_dict = question.__dict__
        for key in ['context_id', 'user_id', 'user_email', 'open_timestamp', 'submission_timestamp',
                    'is_valid', 'reason', 'question_type', 'retrieved_context_ids', 'full_context']:
            del question_dict[key]
        obj['questions'].append(question_dict)
    obj['scientific_annotation'] = scientific_annotation
    return obj

def parse_submission_request(request):
    question_type = QuestionType(request['question_type'])
    question_list = []
    for question_dict in request['questions']:
        question = question_from_dict(question_dict, question_type)
        question.user_id = request['user_id']
        question.user_email = request['user_email']
        question.open_timestamp = request['open_timestamp']
        question.submission_timestamp = request['submission_timestamp']
        question_list.append(question)
    
    term = request['scientific_annotation']['term']
    if term != "":
        statement = request['scientific_annotation']['statement']
        assert '<MASK>' in statement
        cloze_question = ClozeQuestion(statement, term)
        cloze_question.user_id = request['user_id']
        cloze_question.user_email = request['user_email']
        cloze_question.open_timestamp = request['open_timestamp']
        cloze_question.submission_timestamp = request['submission_timestamp']
        question_list.append(cloze_question)
    
    context = Context(**request['context'])
    retrieved_contexts = [Context(**context_dict) for context_dict in request['retrieved_contexts']]
    
    return question_list, context, retrieved_contexts

def get_options_string(mcq: MultipleChoiceQuestion):
    string = ''
    num_options = len(mcq.options)
    i = 0
    for key in sorted(mcq.options.keys()):
        string += key + OPTIONS_KEY_DELIMITER + mcq.options[key]
        i += 1
        if i < num_options:
            string += DELIMITER
    return string

def mcq_to_pandas(mcq_list: list[MultipleChoiceQuestion]):
    df = {
        'Question': [],
        'Options': [],
        'Answer': [],
        'Context': [],
        'Complexity': [],
        'Validation': []
    }
    for mcq in mcq_list:
        df['Question'].append(mcq.question)
        df['Options'].append(get_options_string(mcq))
        df['Answer'].append(mcq.correct_option)
        df['Context'].append(mcq.full_context)
        df['Complexity'].append(mcq.question_complexity.value)
        df['Validation'].append(mcq.is_valid)
    return pd.DataFrame(df)

def ffq_to_pandas(ffq_list: list[FreeFormQuestion]):
    df = {
        'Question': [],
        'Answer': [],
        'Context': [],
        'Complexity': [],
        'Validation': []
    }
    for ffq in ffq_list:
        df['Question'].append(ffq.question)
        df['Answer'].append(ffq.answer)
        df['Context'].append(ffq.full_context)
        df['Complexity'].append(ffq.question_complexity.value)
        df['Validation'].append(ffq.is_valid)
    return pd.DataFrame(df)

def cloze_to_pandas(cloze_list: list[ClozeQuestion]):
    df = {
        'Question': [],
        'Answer': [],
        'Context': []
    }
    for cloze in cloze_list:
        df['Question'].append(cloze.statement)
        df['Answer'].append(cloze.term)
        df['Context'].append(cloze.full_context)
    return pd.DataFrame(df)

def build_retrieved_context_string(retrieved_contexts: list[Context]):
    if len(retrieved_contexts) > 0:
        res = retrieved_contexts[0].content
        for doc in retrieved_contexts[1:]:
            res += '\n' + DELIMITER + '\n'
            res += doc.content
        return res
    else:
        return ""

def build_full_context(context: Context, retrieved_contexts: list[Context]):
    all_contexts = [context] + retrieved_contexts
    if len(all_contexts) > 0:
        res = all_contexts[0].content
        for doc in all_contexts[1:]:
            res += '\n' + DELIMITER + '\n'
            res += doc.content
        return res
    else:
        return ""

def smooth_probability(p, T=5):
        logit = np.log(p / (1 - p))
        smooth_logit = logit / T
        return 1 / (1 + np.exp(-smooth_logit))