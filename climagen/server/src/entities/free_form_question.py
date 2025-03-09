from dataclasses import dataclass
from src.entities.base_question import BaseQuestion, QuestionType

@dataclass
class FreeFormQuestion(BaseQuestion):
    def __init__(self, question_complexity, question, answer, **kwargs) -> None:
        super().__init__(QuestionType.FREE_FORM, question_complexity, **kwargs)
        self.question = question
        self.answer = answer
    
    def get_text(self):
        text = ''
        text += self.question + '\n\n'
        text += 'Answer: ' + self.answer
        return text