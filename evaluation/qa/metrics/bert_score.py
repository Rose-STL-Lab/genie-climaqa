from qa.metrics.base_metric import BaseMetric
from bert_score import score
import logging

logging.getLogger("transformers.modeling_utils").setLevel(logging.ERROR)

class BERTScore(BaseMetric):
    
    def get_sentence_score(self, reference_answer, generated_answer):
        references = [reference_answer]
        candidates = [generated_answer]

        P, R, F1 = score(candidates, references, lang='en')
        return P[0].item(), R[0].item(), F1[0].item()
    
    def get_corpus_score(self, reference_answer_corpus, generated_answer_corpus):
        if len(reference_answer_corpus)== 0:
            return 0
        P, R, F1 = score(generated_answer_corpus, reference_answer_corpus, lang='en')
        return F1.mean().item()
