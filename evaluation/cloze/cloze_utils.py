import os
import copy
import pandas as pd
from tqdm import tqdm
from tabulate import tabulate
from cloze.cloze_agent import ClozeAgent
from cloze.metrics.phrase_similarity import PhraseSimilarity
import numpy as np

similarity_metric = PhraseSimilarity()

def get_results_for_question(cloze_agents: list[ClozeAgent], question, reference_answer):
    print(question)
    print('Reference Answer: ' + reference_answer + '\n')
   
    for cloze_agent in cloze_agents:
        llm_answer = cloze_agent.get_answer(question)
        print(cloze_agent.name + ': ' + llm_answer )
        print(f'Phrase Similarity: {similarity_metric.phrase_similarity(question, llm_answer, reference_answer)}\n')

def generate_and_save_answer(cloze_agent: ClozeAgent, benchmark_df, result_dir):
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
    answer_list = []
    for question in tqdm(benchmark_df['Question']):
        answer_list.append(cloze_agent.get_answer(question))
    df = copy.deepcopy(benchmark_df)
    df['LLM Answer'] = answer_list
    df.to_csv(os.path.join(result_dir, cloze_agent.name + '.csv'))

def evaluate_experiment(result_dir):
    models = []
    em_scores = []
    phrase_similarity_scores = []
    for file in sorted(os.listdir(result_dir)):
        model_name = file[:-4]
        models.append(model_name)
        result_df = pd.read_csv(os.path.join(result_dir, file))
        
        num_match = len(result_df[result_df['Answer'] == result_df['LLM Answer']])
        em_score = 100*num_match/len(result_df)
        em_scores.append(em_score)

        # mean_similarity = result_df.apply(lambda row: similarity_metric.phrase_similarity(row['Question'], row['LLM Answer'], row['Answer']), axis=1).to_numpy().mean()
        # phrase_similarity_scores.append(mean_similarity)
        similarities = []
        for i, row in result_df.iterrows():
            question = row['Question']
            llm_answer = row['LLM Answer']
            answer = row['Answer']

            similarity = similarity_metric.phrase_similarity(blank_statement=question, generated_term=llm_answer, correct_term=answer)
            similarities.append(similarity)
        mean_similarity = np.array(similarities).mean()
        phrase_similarity_scores.append(mean_similarity)

    benchmark_dict = {
        '': models,
        'EM': em_scores,
        'Phrase Similarity': phrase_similarity_scores
    }
    return benchmark_dict

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

    benchmark_dict = {'': models}
    for key in composite_dict:
        benchmark_dict[key] = report_result(composite_dict[key])
    benchmark_result_df = pd.DataFrame(benchmark_dict)
    print(tabulate(benchmark_result_df, headers='keys', tablefmt='fancy_grid', showindex=False))