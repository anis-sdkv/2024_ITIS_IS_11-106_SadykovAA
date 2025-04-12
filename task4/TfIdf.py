import math
import os
import pandas as pd

from task3.InverseIndex import InverseIndex


class TfIdf:
    def __init__(self):
        self.inverse_index = InverseIndex()
        self.inverse_index.load("../task3/out/inverse_index.txt")
        self._tf_cache = {}
        self._idf_cache = {}

    def calculate_tf(self, term, document_id):
        if document_id not in self._tf_cache:
            self._tf_cache[document_id] = self._calculate_document_tf(document_id)
        return self._tf_cache[document_id][term]

    def calculate_idf(self, term):
        if term not in self._idf_cache:
            idf_value = len(self.inverse_index.all_docs) / len(self.inverse_index.get_item_by_key(term))
            self._idf_cache[term] = math.log2(idf_value)
        return self._idf_cache[term]

    def calculate_tf_idf(self, term, document_id):
        return self.calculate_tf(term, document_id) * self.calculate_idf(term)

    def save_tf_csv(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)

        all_term_frequencies = {}

        sorted_doc_ids = sorted(self.inverse_index.all_docs)
        doc_indexes = {doc_id: i for i, doc_id in enumerate(sorted_doc_ids)}

        for doc_id in sorted_doc_ids:
            term_frequencies = self._calculate_document_tf(doc_id)
            for token, tf in term_frequencies.items():
                if token not in all_term_frequencies:
                    all_term_frequencies[token] = [0] * len(sorted_doc_ids)
                doc_index = doc_indexes[doc_id]
                all_term_frequencies[token][doc_index] = tf

        df = pd.DataFrame.from_dict(all_term_frequencies, orient='index', columns=sorted_doc_ids)
        df = df.round(6)
        df.to_csv(path)

    def save_idf_csv(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        all_idf = {}

        for token in self.inverse_index.get_all_tokens():
            all_idf[token] = self.calculate_idf(token)

        df = pd.DataFrame.from_dict(all_idf, orient='index', columns=['idf'])
        df = df.round(6)
        df.to_csv(path)

    def save_tf_idf_csv(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        all_tf_idf = {}

        sorted_doc_ids = sorted(self.inverse_index.all_docs)
        doc_indexes = {doc_id: i for i, doc_id in enumerate(sorted_doc_ids)}

        for doc_id in sorted_doc_ids:
            term_frequencies = self._calculate_document_tf(doc_id)
            for token, tf in term_frequencies.items():
                tf_idf = tf * self.calculate_idf(token)
                if token not in all_tf_idf:
                    all_tf_idf[token] = [0] * len(sorted_doc_ids)
                doc_index = doc_indexes[doc_id]
                all_tf_idf[token][doc_index] = tf_idf

        df = pd.DataFrame.from_dict(all_tf_idf, orient='index', columns=sorted_doc_ids)
        df = df.round(6)
        df.to_csv(path)

    @staticmethod
    def _calculate_document_tf(document_id):
        token_counts = {}
        document_path = f"../task2/out/page_{document_id}.txt"
        with open(document_path, 'r', encoding='utf-8') as file:
            for token in file:
                token = token.strip()
                if token in token_counts:
                    token_counts[token] += 1
                else:
                    token_counts[token] = 1

        total_tokens_count = sum(token_counts.values())

        term_frequencies = {token: count / total_tokens_count for token, count in token_counts.items()}
        return term_frequencies
