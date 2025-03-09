from qa.metrics.base_metric import BaseMetric
from nltk.translate.bleu_score import corpus_bleu, SmoothingFunction

# while running first time
# import nltk
# nltk.download('punkt')

class BLEUScore(BaseMetric):
    
    def get_sentence_score(self, reference_answer, generated_answer):
        blue_references = [[reference_answer]]
        candidates = [generated_answer]

        bleu_score = corpus_bleu(blue_references, candidates, smoothing_function=SmoothingFunction().method1)
        return bleu_score
    
    def get_corpus_score(self, reference_answer_corpus, generated_answer_corpus):
        if len(reference_answer_corpus) == 0:
            return 0
        blue_references = []
        for reference in reference_answer_corpus:
            blue_references.append([reference])

        bleu_score = corpus_bleu(blue_references, generated_answer_corpus, smoothing_function=SmoothingFunction().method1)
        return bleu_score
