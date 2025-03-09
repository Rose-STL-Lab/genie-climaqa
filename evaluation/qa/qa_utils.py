import os
import numpy as np
import pandas as pd
from tqdm import tqdm
from tabulate import tabulate
from qa.qa_agent import QAAgent
from qa.metrics.bert_score import BERTScore
from qa.metrics.bleu_score import BLEUScore
from qa.metrics.fa_score import FAScore
import copy

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

bleu_evaluator = BLEUScore()
bert_evaluator = BERTScore()
# fa_evaluator = FAScore(openai_model='ft:gpt-4o-mini-2024-07-18:ucsd::AAGkhacf')
fa_evaluator = FAScore()


def smooth_probability(p, T=5):
    if p==0 or p==1:
        return p
    logit = np.log(p / (1 - p))
    smooth_logit = logit / T
    return 1 / (1 + np.exp(-smooth_logit))

def get_metrics_for_question(qa_agents, question, reference_answer):
    print('Quesition: ' + question)
    print('Reference Answer: ' + reference_answer)
    print('')

    for qa_agent in qa_agents:
        generated_answer = qa_agent.get_answer(question)
        print("LLM: " + qa_agent.name)
        print("\tGenerated Answer: " + generated_answer + "\n")

        bleu_score = bleu_evaluator.get_sentence_score(reference_answer, generated_answer)
        print(f"\tBleu: {bleu_score:.3f}")

        _, _, bert_f1 = bert_evaluator.get_sentence_score(reference_answer, generated_answer)
        print(f"\tBert: {bert_f1:.3f}")

        fa_score = fa_evaluator.get_sentence_score(reference_answer, generated_answer)
        print(f"\tFA Score: {fa_score:.3f}")

def get_metrics_for_corpus(df):
    reference_answer_corpus = list(df['Answer'])
    generated_answer_corpus = list(df['LLM Answer'])

    fa_score, _ = fa_evaluator.get_corpus_score(reference_answer_corpus, generated_answer_corpus)
    metrics = {
        'Bleu': bleu_evaluator.get_corpus_score(reference_answer_corpus, generated_answer_corpus),
        'Bert': bert_evaluator.get_corpus_score(reference_answer_corpus, generated_answer_corpus),
        'FA Score': fa_score
    }

    return metrics

def generate_and_save_answer(qa_agent: QAAgent, benchmark_df, result_dir):
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
    answer_list = []
    for question in tqdm(benchmark_df['Question']):
        answer_list.append(qa_agent.get_answer(question))
    df = copy.deepcopy(benchmark_df)
    df['LLM Answer'] = answer_list
    df.to_csv(os.path.join(result_dir, qa_agent.name + '.csv'))

def evaluate_experiment(result_dir):
    models = []
    bleu_scores = {
        'Base': [],
        'Reasoning': [],
        'Hypothetical': [],
        'Overall': []
    }
    bert_scores = {
        'Base': [],
        'Reasoning': [],
        'Hypothetical': [],
        'Overall': []
    }
    fa_scores = {
        'Base': [],
        'Reasoning': [],
        'Hypothetical': [],
        'Overall': []
    }

    for file in sorted(os.listdir(result_dir)):
        model_name = file[:-4]
        models.append(model_name)
        print(f'Evaluating answers by model: {model_name}...')

        answer_df = pd.read_csv(os.path.join(result_dir, file))
        
        base_df = answer_df[answer_df['Complexity'] == "BASE"]
        base_metrics = get_metrics_for_corpus(base_df)
        bleu_scores['Base'].append(base_metrics['Bleu'])
        bert_scores['Base'].append(base_metrics['Bert'])
        fa_scores['Base'].append(base_metrics['FA Score'])

        reason_df = answer_df[answer_df['Complexity'] == "REASONING"]
        reason_metrics = get_metrics_for_corpus(reason_df)
        bleu_scores['Reasoning'].append(reason_metrics['Bleu'])
        bert_scores['Reasoning'].append(reason_metrics['Bert'])
        fa_scores['Reasoning'].append(reason_metrics['FA Score'])

        hypo_df = answer_df[answer_df['Complexity'] == "HYPOTHETICAL"]
        hypo_metrics = get_metrics_for_corpus(hypo_df)
        bleu_scores['Hypothetical'].append(hypo_metrics['Bleu'])
        bert_scores['Hypothetical'].append(hypo_metrics['Bert'])
        fa_scores['Hypothetical'].append(hypo_metrics['FA Score'])

        bleu_overall = (base_metrics['Bleu']*len(base_df) + reason_metrics['Bleu']*len(reason_df) + hypo_metrics['Bleu']*len(hypo_df))/len(answer_df)
        bert_overall = (base_metrics['Bert']*len(base_df) + reason_metrics['Bert']*len(reason_df) + hypo_metrics['Bert']*len(hypo_df))/len(answer_df)
        fa_overall = (base_metrics['FA Score']*len(base_df) + reason_metrics['FA Score']*len(reason_df) + hypo_metrics['FA Score']*len(hypo_df))/len(answer_df)
        bleu_scores['Overall'].append(bleu_overall)
        bert_scores['Overall'].append(bert_overall)
        fa_scores['Overall'].append(fa_overall)

    bleu_dict = {'': models}
    for key in bleu_scores.keys():
        bleu_dict[f'{key}: Bleu'] = bleu_scores[key]

    bert_dict = {'': models}
    for key in bert_scores.keys():
        bert_dict[f'{key}: Bert'] = bert_scores[key]

    fa_dict = {'': models}
    for key in fa_scores.keys():
        fa_dict[f'{key}: FA'] = fa_scores[key]

    return bleu_dict, bert_dict, fa_dict

def report_result(l):
    result = []
    mean_list = np.mean(l, axis=0)
    std_list = np.std(l, axis=0)
    for i in range(len(mean_list)):
        result.append(f'{mean_list[i]:.4f} +- {std_list[i]:.4f}')
    return result

def evaluate_result(result_dir):
    models = []
    bleu_composite_dict = {}
    bert_composite_dict = {}
    fa_composite_dict = {}
    for exp_folder in sorted(os.listdir(result_dir)):
        print(f'\nEvaluating {exp_folder}')
        bleu_result, bert_result, fa_result = evaluate_experiment(os.path.join(result_dir, exp_folder))
        if len(models) == 0:
            models = bleu_result['']
        elif models != bleu_result['']:
            raise Exception('Same models were not found in all trials!')
        
        for key in bleu_result:
            if key != '':
                if key not in bleu_composite_dict:
                    bleu_composite_dict[key] = [bleu_result[key]]
                else:
                    bleu_composite_dict[key].append(bleu_result[key])

        for key in bert_result:
            if key != '':
                if key not in bert_composite_dict:
                    bert_composite_dict[key] = [bert_result[key]]
                else:
                    bert_composite_dict[key].append(bert_result[key])
        
        for key in fa_result:
            if key != '':
                if key not in fa_composite_dict:
                    fa_composite_dict[key] = [fa_result[key]]
                else:
                    fa_composite_dict[key].append(fa_result[key])

    bleu_dict = {'': models}
    for key in bleu_composite_dict:
        bleu_dict[key] = report_result(bleu_composite_dict[key])
    bleu_result_df = pd.DataFrame(bleu_dict)
    print(tabulate(bleu_result_df, headers='keys', tablefmt='fancy_grid', showindex=False))

    bert_dict = {'': models}
    for key in bert_composite_dict:
        bert_dict[key] = report_result(bert_composite_dict[key])
    bert_result_df = pd.DataFrame(bert_dict)
    print(tabulate(bert_result_df, headers='keys', tablefmt='fancy_grid', showindex=False))

    fa_dict = {'': models}
    for key in fa_composite_dict:
        fa_dict[key] = report_result(fa_composite_dict[key])
    fa_result_df = pd.DataFrame(fa_dict)
    print(tabulate(fa_result_df, headers='keys', tablefmt='fancy_grid', showindex=False))