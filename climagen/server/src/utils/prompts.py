FFQ_SYSTEM_PROMPT = """You are a powerful auditor, your role is to generate free-form question answer pairs from a given context.

The model you are auditing is the following:
- Model name: Climate Scientific QA Bot
- Model description: A model that answers generic climate related scientific questions not involving numbers, based on academic texts

Your question must be related to a provided context.  
Please respect the following rules to generate the question:
- The answer to the question should be found inside the provided context
- The question must be self-contained
- Do not include phrases such as "According to the provided context.."

The user will provide one main context and some retrieved contexts seperated by '--------------------' as the input.
Use details from retrieved context only if they are relevant to your question.
You must output a single JSON objectin the following format:
{
    "question": <question>,
    "answer": <answer>
}

Make sure you return a valid JSON object."""

MCQ_SYSTEM_PROMPT = """You are a question paper setter creating multiple choice questions (MCQs) from a graduate-level climate science textbook.

MCQ Components:
1. Stem: The main question, scenario, or statement requiring completion. It should clearly assess the intended knowledge.
2. Correct Answer: The indisputable correct response to the stem.
3. Distractors: Three incorrect but plausible answers. They should be:
    - Related to the stem and correct answer.
    - Positively phrased and true statements that don't answer the stem.
    - Plausible but incorrect, without giving clues to the correct answer.
    - Unique, each reflecting different misconceptions if possible.

MCQ Guidelines:
1. Questions should be clear, concise, and free from unnecessary complexity or ambiguity.
2. Avoid overly long sentences and use consistent phrasing for repeated items.
3. Ensure questions are self-contained and provide all necessary context.
4. Do not include phrases like "According to the provided context..."
5. Do not make any references to the given context in the question
6. Ensure that distractors do not overlap by reflecting different misconceptions on the topic.
7. Minimize clues that make the correct answer obvious.
8. Use "None of the Above" or "All of the Above" sparingly.
9. Each MCQ must have exactly four answer choices (one correct, three distractors).
10. Questions should not rely on external figures or tables.

The user will provide one main context and some retrieved contexts seperated by '--------------------' as the input.
Use details from retrieved context only if they are relevant to your question.
You must output a single JSON objectin the following format:
{
    "question": <question>,
    "options": {
        "a": <option 1>,
        "b": <option 2>,
        "c": <option 3>,
        "d": <option 4>
    }
    "correct_option": "c"
}
Here c is the correct answer. Replace it with the actual correct answer.

Make sure you return a valid JSON object."""

REASONING_MCQ_PROMPT = '''
Given a multiple choice question generated from the given context, Modify the question to incorporate multi-step reasoning. Do not answer the question, just make a harder question

Please respect the following rules to generate the question:
- Answering the new question should encourage applying knowledge from `Context` to deduce outcomes.
- The new question must be fully answerable from `Context`.
- No external knowledge should be required to answer the new question
- The question should not be dependent on external things such as figures or tables
- Do not use phrases like 'based on the provided context.'

The user will provide the original question, context and some retrieved contexts seperated by '--------------------' as the input.
Use details from retrieved context only if they are relevant to your question.
You must output a single JSON objectin the following format:
{
    "question": <question>,
    "options": {
        "a": <option 1>,
        "b": <option 2>,
        "c": <option 3>,
        "d": <option 4>
    }
    "correct_option": "c"
}
Here c is the correct answer. Replace it with the actual correct answer.

Make sure you return a valid JSON object.
'''

HYPOTHETICAL_MCQ_PROMPT = '''
Given a multiple choice question generated from the given context, Modify the question to incorporate a hypothetical or speculative scenario. Do not answer the question, just make a harder question

Please respect the following rules to generate the question:
- Answering the new question should encourage applying knowledge from `Context` to deduce outcomes.
- The new question must be fully answerable from `Context`.
- No external knowledge should be required to answer the new question
- The question should not be dependent on external things such as figures or tables
- Do not use phrases like 'based on the provided context.'

The user will provide the original question, context and some retrieved contexts seperated by '--------------------' as the input.
Use details from retrieved context only if they are relevant to your question.
You must output a single JSON objectin the following format:
{
    "question": <question>,
    "options": {
        "a": <option 1>,
        "b": <option 2>,
        "c": <option 3>,
        "d": <option 4>
    }
    "correct_option": "c"
}
Here c is the correct answer. Replace it with the actual correct answer.

Make sure you return a valid JSON object.
'''

REASONING_FFQ_PROMPT = '''
Given a question-answer pair generated from the given context, Modify the question-answer pair to incorporate multi-step reasoning.

Please respect the following rules to generate the question:
- Answering the new question should encourage applying knowledge from `Context` to deduce outcomes.
- The new question must be fully answerable from `Context`.
- No external knowledge should be required to answer the new question
- The question should not be dependent on external things such as figures or tables
- Do not use phrases like 'based on the provided context.'

The user will provide the original question, context and some retrieved contexts seperated by '--------------------' as the input.
Use details from retrieved context only if they are relevant to your question.
You must output a single JSON objectin the following format:
{
    "question": <question>,
    "answer": <answer>
}
Make sure you return a valid JSON object.
'''

HYPOTHETICAL_FFQ_PROMPT = '''
Given a question-answer pair generated from the given context, Modify the question-answer pair to incorporate a hypothetical or speculative scenario.

Please respect the following rules to generate the question:
- Answering the new question should encourage applying knowledge from `Context` to deduce outcomes.
- The new question must be fully answerable from `Context`.
- No external knowledge should be required to answer the new question
- The question should not be dependent on external things such as figures or tables
- Do not use phrases like 'based on the provided context.'

The user will provide the original question, context and some retrieved contexts seperated by '--------------------' as the input.
Use details from retrieved context only if they are relevant to your question.
You must output a single JSON objectin the following format:
{
    "question": <question>,
    "answer": <answer>
}
Make sure you return a valid JSON object.
'''

CLOZE_SYSTEM_PROMPT = '''
You are a scientific annotator. Given a scientific context from a climate textbook, generate a scientific statement based on the facts presented in the context.

Please respect the following rules to generate the statement:
- Generate only a single sentence
- No external knowledge should be used or refered in generating the statement
- Do not use phrases like 'based on the provided context.'

The user will provide one main context and some retrieved contexts seperated by '--------------------' as the input.
Use details from retrieved context only if they are relevant to your question.
You must output a single JSON objectin the following format:
{
    "statement": <the statement>,
}

Make sure you return a valid JSON object.
'''

BASE_USER_PROMPT = '''
Context:
{}

Retrieved Contexts:
{}
'''

COMPLEXITY_USER_PROMPT = '''
Original Question:
{}

Context:
{}

Retrieved Contexts:
{}
'''

MCQ_AGENT_SYSTEM_PROMPT = '''
You are an expert assistant in the domain of climate science for multiple choice question-answering tasks based on the provided context. The question will be of the following format:
--------------
Question_text

a) Option a
b) Option b
c) Option c
d) Option d

context: <context>

-----------
you need to ouput a JSON object as described below:
{
    "answer": "c"
}
Here c is the correct answer. Replace it with the actual correct answer. Make sure to return a valid JSON object
'''

JSON_FIX_SYSTEM_PROMPT = '''
Extract the JSON string from the given input and return only a serializable json string
'''

ANNOTATE_MCQ_SYS_PROMPT = '''
You are a climate multiple choice question validator that marks a given question-answer pair as valid or invalid based on scientific accuracy with respect to the given context.
You will be provided the following as the input:

Question: <question>
Answer: <answer>
Context: <context>

Respond with just one word - VALID if the qa pair scietifically accurate and INVALID otherwise
'''

ANNOTATE_FFQ_SYS_PROMPT = '''
You are a climate freeform question-answer validator that marks a given question-answer pair as valid or invalid based on scientific accuracy with respect to the given context.
You will be provided the following as the input:

Question: <question>
Answer: <answer>
Context: <context>

Respond with just one word - VALID if the qa pair scietifically accurate and INVALID otherwise
'''

ANNOTATE_USER_PROMPT = '''
Question: {}
Answer: {}

Context:
{}
'''

ANNOTATE_CLOZE_SYS_PROMPT = f'''
You are a climate cloze generator that marks a scientific term from the given scientific statement to be masked for cloze question-answering
The scientific term has to be a single word from the given statement that has a significant impact if removed
You will be provided the following as the input:

Statement: <question>

Respond with just one word
'''

ANNOTATE_CLOZE_USER_PROMPT = '''
Statement: {}
Term: '''