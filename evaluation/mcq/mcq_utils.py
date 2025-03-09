from mcq.mcq import MCQ
from mcq.mcq_agent import MCQAgent
from mcq import mcq_utils
import pandas as pd
from tqdm import tqdm
import os
from tabulate import tabulate
from mcq.mcq_agent import MCQAgent
import random
import time
import copy
import numpy as np

from llm.together_ai_llm import TogetherAILLM

OPTIONS_DELIMITER = '\n--------------------\n'
OPTIONS_KEY_DELIMITER = ') '

def get_results_for_question(mcq_agents: list[MCQAgent], mcq: MCQ):
    print(mcq.get_text())
    print('Correct Answer: ' + mcq.correct_option + '\n')
   
    for mcq_agent in mcq_agents:
        print(mcq_agent.name + ': ' + mcq_agent.get_answer(mcq))

def compare_results_for_question(mcq_agents: list[MCQAgent], mcq: MCQ):
    print(mcq.get_text())
    print('Correct Answer: ' + mcq.correct_option + '\n')
    
    print('Answers without context:')
    for mcq_agent in mcq_agents:
        print(mcq_agent.llm.name + ': ' + mcq_agent.get_answer(mcq, use_context=False))
    print('\nAnswers with context:')
    for mcq_agent in mcq_agents:
        print(mcq_agent.llm.name + ': ' + mcq_agent.get_answer(mcq, use_context=True))

def get_options_string(mcq: MCQ):
    string = ''
    num_options = len(mcq.options)
    i = 0
    for key in mcq.options:
        string += key + OPTIONS_KEY_DELIMITER + mcq.options[key]
        i += 1
        if i < num_options:
            string += OPTIONS_DELIMITER
    return string

def mcq_to_pandas(mcq_list):
    df = {
        'Question': [],
        'Options': [],
        'Answer': [],
        'Context': []
    }
    for mcq in mcq_list:
        df['Question'].append(mcq.question)
        df['Options'].append(get_options_string(mcq))
        df['Answer'].append(mcq.correct_option)
        df['Context'].append(mcq.context)
    return pd.DataFrame(df)

def shuffle_options(mcq: MCQ):
    option_keys = ['a', 'b', 'c', 'd']
    keys = list(mcq.options.keys())
    random.shuffle(keys)

    new_options = {}
    for i in range(len(keys)):
        new_options[option_keys[i]] = mcq.options[keys[i]]
    
    new_mcq = MCQ(mcq.question, new_options, option_keys[keys.index(mcq.correct_option)])
    return new_mcq


def pandas_to_mcq(df):
    mcq_list = []
    for ind in range(len(df)):
        options_string = list(df['Options'])[ind]
        options_list = options_string.split(OPTIONS_DELIMITER)
        options = {}
        for option in sorted(options_list):
            key, value = option.split(OPTIONS_KEY_DELIMITER, 1)
            options[key] = value

        mcq = MCQ(list(df['Question'])[ind], options, correct_option=list(df['Answer'])[ind],
                  context=list(df['Context'])[ind] if 'Context' in df.columns else None)
        mcq_list.append(mcq)
    return mcq_list

def generate_and_save_answer(mcq_agent, mcq_df, result_dir):
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    mcq_df = copy.deepcopy(mcq_df)
    mcq_list = pandas_to_mcq(mcq_df)
    llm_answers = []
    for mcq in tqdm(mcq_list):
        llm_answer = mcq_agent.get_answer(mcq)
        # if llm_answer == 'Bad Answer':
        #     print("Got bad answer")
        llm_answers.append(llm_answer)
    mcq_df['LLM Answer'] = llm_answers
    num_correct = len(mcq_df[mcq_df['Answer'] == mcq_df['LLM Answer']])
    print(f'Score: {num_correct} / {len(mcq_df)}')
    mcq_df.to_csv(os.path.join(result_dir, mcq_agent.name + '.csv'))

def evaluate_experiment(result_dir):
    models = []
    base_scores = []
    reason_scores = []
    hypo_scores = []
    overall_scores = []
    for file in sorted(os.listdir(result_dir)):
        model_name = file[:-4]
        models.append(model_name)
        result_df = pd.read_csv(os.path.join(result_dir, file))
        
        base_df = result_df[result_df['Complexity'] == 'BASE']
        num_correct = len(base_df[base_df['Answer'] == base_df['LLM Answer']])
        base_score = 100*num_correct/len(base_df)
        base_scores.append(base_score)

        reason_df = result_df[result_df['Complexity'] == 'REASONING']
        num_correct = len(reason_df[reason_df['Answer'] == reason_df['LLM Answer']])
        reason_score = 100*num_correct/len(reason_df)
        reason_scores.append(reason_score)

        hypo_df = result_df[result_df['Complexity'] == 'HYPOTHETICAL']
        num_correct = len(hypo_df[hypo_df['Answer'] == hypo_df['LLM Answer']])
        hypo_score = 100*num_correct/len(hypo_df)
        hypo_scores.append(hypo_score)

        overall_score = (base_score*len(base_df) + reason_score*len(reason_df) + hypo_score*len(hypo_df))/len(result_df)
        overall_scores.append(overall_score)

        num_none = len(result_df[result_df['LLM Answer'] == 'Bad Answer'])
        if num_none > 0:
            print(f'{model_name} could not answer for {num_none} questions')

    result_dict = {
        '': models,
        'Base': base_scores,
        'Reasoning': reason_scores,
        'Hypothetical': hypo_scores,
        'Overall': overall_scores
        }
    return result_dict

def report_result(l):
    result = []
    mean_list = np.mean(l, axis=0)
    std_list = np.std(l, axis=0)
    for i in range(len(mean_list)):
        result.append(f'{mean_list[i]:.2f} +- {std_list[i]:.2f}')
    return result

def evaluate_result(result_dir):
    models = []
    composite_dict = {}
    for exp_folder in sorted(os.listdir(result_dir)):
        exp_result = evaluate_experiment(os.path.join(result_dir, exp_folder))
        if len(models) == 0:
            models = exp_result['']
        elif models != exp_result['']:
            raise Exception('Same models were not found in all trials!')
        
        for key in exp_result:
            if key != '':
                if key not in composite_dict:
                    composite_dict[key] = [exp_result[key]]
                else:
                    composite_dict[key].append(exp_result[key])
            
    benchmark_dict = {
        '': models,
        'Base': report_result(composite_dict['Base']),
        'Reasoning': report_result(composite_dict['Reasoning']),
        'Hypothetical': report_result(composite_dict['Hypothetical']),
        'Overall': report_result(composite_dict['Overall'])
        }
    benchmark_result_df = pd.DataFrame(benchmark_dict)
    print(tabulate(benchmark_result_df, headers='keys', tablefmt='fancy_grid', showindex=False))