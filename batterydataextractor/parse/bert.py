# -*- coding: utf-8 -*-
"""
batterydataextractor.parse.bert

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Bert parsers.
author:
"""
import logging
import re
from abc import ABC

from .base import BaseSentenceParser
from transformers import AutoTokenizer
from transformers.pipelines import pipeline

log = logging.getLogger(__name__)


class BertParser(BaseSentenceParser, ABC):
    """Bert Parser"""

    @staticmethod
    def qa_model(model_name="batterydata/batterybert-cased-squad-v1") -> pipeline:
        return pipeline('question-answering', model=model_name,
                        tokenizer=AutoTokenizer.from_pretrained(model_name, model_max_length=512, use_auth_token=True))


class BertMaterialParser(BertParser):
    """Bert Material Parser."""

    def interpret(self, tokens):
        bert_model = self.qa_model()
        context = " ".join([token[0] for token in tokens])
        for specifier in self.model.defined_names:
            if specifier in context:
                question = "What is the value of {}?".format(specifier)
                qa_input = {'question': question, 'context': context}
                res = bert_model(qa_input, top_k=1)
                cs1 = res['score']
                if cs1 > self.model.confidence_threshold:
                    question2 = "What material has a {} of {}?".format(specifier, res['answer'])
                    qa_input2 = {'question': question2, 'context': context}
                    res2 = bert_model(qa_input2, top_k=1)
                    cs2 = res2['score']
                    value = re.findall(r'(?:\d*\.\d+|\d+)', res['answer'])
                    c = self.model(value=[float(v) for v in value],
                                   units=res['answer'].split(value[-1])[-1].strip(),
                                   raw_value=res['answer'],
                                   specifier=specifier,
                                   material=res2['answer'],
                                   confidence_score="%.4f" % (cs1 * cs2),
                                   original_text=context if self.model.original_text else None,
                                   )
                    yield c


class BertGeneralParser(BertParser):
    """Bert General Parser."""

    def interpret(self, tokens):
        bert_model = self.qa_model()
        context = " ".join([token[0] for token in tokens])
        for specifier in self.model.defined_names:
            question = specifier if self.model.self_defined else "What is the {}?".format(specifier)
            qa_input = {'question': question, 'context': context}
            res = bert_model(qa_input, top_k=1)
            if res['score'] > self.model.confidence_threshold:
                c = self.model(answer=res['answer'],
                               specifier=specifier,
                               confidence_score="%.4f" % res['score'],
                               original_text=context if self.model.original_text else None,
                               )
                yield c
