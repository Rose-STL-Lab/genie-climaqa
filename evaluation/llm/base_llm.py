class BaseLLM:
    
    def __init__(self, name='None'):
        self.name = name

    def get_result(self, system_prompt, user_prompt):
        pass

    def get_logit_result(self, system_prompt, user_prompt, tokens):
        pass

    def get_top_token(self, system_prompt, user_prompt):
        pass

