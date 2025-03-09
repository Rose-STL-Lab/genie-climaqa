import json
import random
from dataclasses import dataclass
from src.entities.base_question import BaseQuestion, QuestionType

@dataclass
class MultipleChoiceQuestion(BaseQuestion):
    def __init__(self, question_complexity, question, options, correct_option, **kwargs) -> None:
        super().__init__(QuestionType.MCQ, question_complexity, **kwargs)
        self.question = question
        self.options = options
        self.correct_option = correct_option
    
    def shuffle_options(self):
        option_keys = ['a', 'b', 'c', 'd']
        keys = list(self.options.keys())
        random.shuffle(keys)

        new_options = {}
        for i in range(len(keys)):
            new_options[option_keys[i]] = self.options[keys[i]]
        
        new_mcq = MultipleChoiceQuestion(self.question_complexity, self.question, new_options, option_keys[keys.index(self.correct_option)])
        return new_mcq
    
    def get_text(self):
        text = ''
        text += self.question + '\n\n'
        for key in sorted(self.options.keys()):
            text += f'{key}) {self.options[key]}\n'
        # text += '\nCorrect Option: ' + self.correct_option
        return text