import json
import textwrap

class MCQ:
    def __init__(self, question, options, correct_option=None, context=None):
        self.question = question
        self.options = options
        self.correct_option = correct_option
        self.context = context
    
    @classmethod
    def from_json(cls, json_string):
        dct = json.loads(json_string)
        return cls(dct['question'], dct['options'], dct['correct_option'])

    def get_text(self, wrap_text=False):
        text = ''
        if wrap_text:
            question_text = '\n'.join(textwrap.wrap(self.question, width=120))
        else:
            question_text = self.question
        text += question_text + '\n\n'
        for key in self.options:
            text += f'{key}) {self.options[key]}\n'
        return text
    
    def is_answer_correct(self, answer):
        return answer == self.correct_option