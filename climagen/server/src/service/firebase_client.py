import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from src.entities.context import Context
from src.entities.base_question import QuestionType, BaseQuestion

cred = credentials.Certificate(os.getenv('FIREBASE_CERTIFICATE'))
firebase_admin.initialize_app(cred)

class FirebaseClient:
    def __init__(self):
        self.db = firestore.client()
        self.collection_dict = {
            QuestionType.MCQ: 'mcq',
            QuestionType.FREE_FORM: 'ffq',
            QuestionType.CLOZE: 'cloze'
        }
    
    def persist_context(self, context: Context):
        collection_ref = self.db.collection('context')
        query = collection_ref.where(filter=FieldFilter('hash', '==', context.hash))
        query_results = query.get()

        for doc in query_results:
            if doc.to_dict()['content'] == context.content:
                return doc.id

        context_dict = context.__dict__
        doc_ref = collection_ref.add(context_dict)
        return doc_ref[1].id

    def persist_question(self, question: BaseQuestion):
        collection_name = self.collection_dict[question.question_type]
        question_dict = question.__dict__
        question_dict['question_type'] = question_dict['question_type'].value
        question_dict['question_complexity'] = question_dict['question_complexity'].value
        doc_ref = self.db.collection(collection_name).add(question_dict)
        return doc_ref[1].id
    
    def update_question(self, question_id, is_valid, question_type: QuestionType, reason):
        collection_name = self.collection_dict[question_type]
        doc_ref =  self.db.collection(collection_name).document(question_id)
        
        doc = doc_ref.get()
        if doc.exists:
            question = doc.to_dict()
        else:
            raise Exception(f'Question with id {question_id} and type {question_type.value} does not exist!')

        question['is_valid'] = is_valid
        question['reason'] = reason
        doc_ref.update(question)
        
    def update_cloze(self, question_id, statement, term):
        collection_name = self.collection_dict[QuestionType.CLOZE]
        doc_ref =  self.db.collection(collection_name).document(question_id)
        
        doc = doc_ref.get()
        if doc.exists:
            question = doc.to_dict()
        else:
            raise Exception(f'Question with id {question_id} and type CLOZE does not exist!')

        question['statement'] = statement
        question['term'] = term
        doc_ref.update(question)

    def get_questions_by_user(self, user_id, question_type):
        collection_name = self.collection_dict[question_type]
        collection_ref = self.db.collection(collection_name)
        
        if(user_id == os.getenv('ADMIN_UID')):
            query = collection_ref.where('user_id', 'not-in', ['agent'])
        else:
            query = collection_ref.where('user_id', '==', user_id)
        
        query_results = query.get()
        
        questions = {}
        for doc in query_results:
            questions[doc.id] = doc.to_dict()
        return questions
    
    def get_contexts(self, context_ids):
        collection_ref = self.db.collection('context')
        contexts = {}
        for id in context_ids:
            doc_ref = collection_ref.document(id)
            doc = doc_ref.get()
            if doc.exists:
                contexts[id] = doc.to_dict()
            else:
                raise Exception(f'Context with id {id} does not exist!')
        return contexts
    
    def get_user_ranks(self):
        collection_ref = self.db.collection('mcq')
        query = collection_ref.where('user_id', 'not-in', ['agent'])
        mcq_query_results = query.get()

        collection_ref = self.db.collection('ffq')
        query = collection_ref.where('user_id', 'not-in', ['agent'])
        ffq_query_results = query.get()

        result_dict = {}

        for doc in mcq_query_results:
            obj = doc.to_dict()
            key = obj['user_id']
            if key not in result_dict:
                result_dict[key] = {'email': obj['user_email'], 'mcq': 1, 'free_form': 0}
            else:
                result_dict[key]['mcq'] += 1

        for doc in ffq_query_results:
            obj = doc.to_dict()
            key = obj['user_id']
            if key not in result_dict:
                result_dict[key] = {'email': obj['user_email'], 'free_form': 1, 'mcq': 0}
            else:
                result_dict[key]['free_form'] += 1

        for key in result_dict:
            result_dict[key]['total'] = result_dict[key]['mcq'] + result_dict[key]['free_form']

        result = sorted(result_dict.values(), key=lambda obj: obj['total'], reverse=True)
        return result
    
    def get_invalid_question_count(self):
        collection_ref = self.db.collection('mcq')
        query = collection_ref.where('user_id', 'not-in', ['agent']).where('is_valid', '==', False)
        mcq_query_results = query.get()

        collection_ref = self.db.collection('ffq')
        query = collection_ref.where('user_id', 'not-in', ['agent']).where('is_valid', '==', False)
        ffq_query_results = query.get()

        return len(mcq_query_results), len(ffq_query_results)