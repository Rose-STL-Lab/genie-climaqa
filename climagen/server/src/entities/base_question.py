from enum import Enum
from dataclasses import dataclass

class QuestionType(Enum):
    FREE_FORM = "FREE_FORM"
    MCQ = "MCQ"
    CLOZE = "CLOZE"

class QuestionComplexity(Enum):
    BASE = "BASE"
    REASONING = "REASONING"
    HYPOTHETICAL = "HYPOTHETICAL"

@dataclass
class BaseQuestion:
    def __init__(self, question_type, question_complexity, retrieved_context_ids=None,
                 context_id=None, full_context=None, user_id=None, user_email=None, is_valid=False, 
                 reason=None, open_timestamp=None, submission_timestamp=None) -> None:
        self.question_type = QuestionType(question_type)
        self.context_id = context_id
        self.retrieved_context_ids = retrieved_context_ids
        self.full_context = full_context
        self.user_id = user_id
        self.user_email = user_email
        self.is_valid = is_valid
        self.reason = reason
        self.question_complexity = QuestionComplexity(question_complexity)
        self.open_timestamp = open_timestamp
        self.submission_timestamp = submission_timestamp