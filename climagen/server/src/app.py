import os
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import logging

load_dotenv()

from src.utils import utils
from src.core.qa_generator import QAGenerator
from src.service.firebase_client import FirebaseClient
from src.entities.base_question import QuestionType

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000",
                   "https://genie-validation.nrp-nautilus.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.getLogger("httpx").setLevel(logging.WARNING)

qa_generator = QAGenerator(queue_max_size=int(os.getenv('QUEUE_SIZE')), offline_mode=False)
firebase_client = FirebaseClient()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(qa_generator.populate_queues())
    asyncio.create_task(qa_generator.annotator.trigger())

@app.get("/qadata")
async def get_question(question_type: QuestionType):
    data = await qa_generator.pop_queue(question_type)
    return data

@app.get("/queue_size")
async def get_queue_size(question_type: QuestionType):
    return {"queue_size": qa_generator.get_queue_size(question_type)}

@app.post("/qadata")
async def submit_question(request: Request):
    request = await request.json()
    question_list, context, retrieved_contexts = utils.parse_submission_request(request)
    context_id = firebase_client.persist_context(context)
    retrieved_context_ids = [firebase_client.persist_context(doc) for doc in retrieved_contexts]
    for question in question_list:
        question.context_id = context_id
        question.retrieved_context_ids = retrieved_context_ids
        _ = firebase_client.persist_question(question)
    asyncio.create_task(qa_generator.annotator.trigger())
    return {"presist": "success"}

@app.put("/question/{question_id}")
async def update_question(request: Request, question_id: str, question_type: QuestionType):
    request = await request.json()
    if (question_type == QuestionType.CLOZE):
        firebase_client.update_cloze(question_id, request["statement"], request["term"])
    else:
        firebase_client.update_question(question_id, request['is_valid'], question_type, request['reason'])
    return {}

@app.get("/user/{user_id}/questions")
async def get_questions_for_user(user_id: str, question_type: QuestionType):
    return {"questions": firebase_client.get_questions_by_user(user_id, question_type)}

@app.post("/context")
async def get_contexts(request: Request):
    request = await request.json()
    return firebase_client.get_contexts(request['context_ids'])

@app.get("/user/ranks")
async def get_user_ranks():
    return firebase_client.get_user_ranks()