from dataclasses import dataclass
from src.entities.base_question import BaseQuestion, QuestionType, QuestionComplexity

@dataclass
class ClozeQuestion(BaseQuestion):
    def __init__(self, statement, term, **kwargs) -> None:
        super().__init__(QuestionType.CLOZE, QuestionComplexity.BASE, **kwargs)
        self.statement = statement
        self.term = term
    
    def get_text(self):
        text = ''
        text += self.statement + '\n\n'
        text += 'Answer: ' + self.term
        return text