import math
import os
from concurrent.futures import ThreadPoolExecutor

import pandas as pd

from task3.InverseIndex import InverseIndex


class TfIdf:
    def __init__(self):
        self.inverse_index = InverseIndex()
        self.inverse_index.load("../task3/out/inverse_index.txt")
        self._tf_cache = {}
        self._idf_cache = {}

        self._doc_vectors = {}
        self._doc_norms = {}

    def calculate_idf(self, term):
        if term not in self._idf_cache:
            idf_value = len(self.inverse_index.all_docs) / len(self.inverse_index.get_item_by_key(term))
            self._idf_cache[term] = math.log2(idf_value)
        return self._idf_cache[term]

    def get_doc_tf_ifd_vector(self, document_id):
        if document_id not in self._doc_vectors:
            document_tf = self.get_doc_tf(document_id)
            result = {}
            for term, tf_value in document_tf.items():
                value = tf_value * self.calculate_idf(term)
                if value != 0:
                    result[term] = value
            self._doc_vectors[document_id] = result
        return self._doc_vectors[document_id]

    def calculate_tf_idf(self, term, document_id):
        return self.get_tf(term, document_id) * self.calculate_idf(term)

    def get_tf(self, term, document_id):
        return self._tf_cache[document_id][term]

    def get_doc_tf(self, document_id):
        if document_id not in self._tf_cache:
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
            self._tf_cache[document_id] = term_frequencies
        return self._tf_cache[document_id]

    def _initialize_caches(self):
        print("инициализация кеша: начато")
        doc_ids = list(self._tf_cache.keys())

        with ThreadPoolExecutor() as executor:
            for doc_id in doc_ids:
                self._doc_vectors[doc_id] = self.get_doc_tf_ifd_vector(doc_id)

            # Вычисляем нормы всех документов
            for doc_id in doc_ids:
                self._doc_norms[doc_id] = math.sqrt(sum(v * v for v in self._doc_vectors[doc_id].values()))
        print("инициализация кеша: завершено")

    @staticmethod
    def calculate_query_tf(tokenized_query):
        token_counts = {}

        for token in tokenized_query:
            token = token.strip()
            if token in token_counts:
                token_counts[token] += 1
            else:
                token_counts[token] = 1

        total_tokens_count = sum(token_counts.values())
        term_frequencies = {token: count / total_tokens_count for token, count in token_counts.items()}
        return term_frequencies

    def cos_similarity(self, doc_id, query_vec):
        doc_vec = self.get_doc_tf_ifd_vector(doc_id)
        common_terms = set(query_vec.keys()) & set(doc_vec.keys())
        vector_multiply = sum(doc_vec[term] * query_vec[term] for term in common_terms)

        doc_norm = self.get_doc_norm(doc_id)
        query_norm = math.sqrt(sum([i * i for i in query_vec.values()]))
        if doc_norm * query_norm == 0:
            return 0
        cos_similarity = vector_multiply / (doc_norm * query_norm)
        return cos_similarity

    def get_doc_norm(self, document_id):
        if not document_id in self._doc_norms:
            doc_vec = self.get_doc_tf_ifd_vector(document_id)
            norm = math.sqrt(sum([i * i for i in doc_vec.values()]))
            self._doc_norms[document_id] = norm

        return self._doc_norms[document_id]

    def get_search_result(self, query_tokens):
        query_vec = {token: token_tf * self.calculate_idf(token) for (token, token_tf) in
                     self.calculate_query_tf(query_tokens).items()}
        print(query_vec)

        result = [(doc_id, self.cos_similarity(doc_id, query_vec)) for doc_id in range(200)]

        return list(sorted(result, key=lambda x: x[1], reverse=True))

    def load_cache_from_files(self, tf_path, idf_path):
        if os.path.exists(tf_path):
            tf_df = pd.read_csv(tf_path, index_col=0)
            self._tf_cache = {}
            for doc_id in tf_df.columns:
                self._tf_cache[doc_id] = tf_df[doc_id].dropna().to_dict()
        else:
            print(f"[!] TF cache file not found: {tf_path}")

        if os.path.exists(idf_path):
            idf_df = pd.read_csv(idf_path, index_col=0)
            self._idf_cache = idf_df['idf'].dropna().to_dict()
        else:
            print(f"[!] IDF cache file not found: {idf_path}")

        self._initialize_caches()

    def save_tf_idf_csv(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        all_tf_idf = {}

        sorted_doc_ids = sorted(self.inverse_index.all_docs)
        doc_indexes = {doc_id: i for i, doc_id in enumerate(sorted_doc_ids)}

        for doc_id in sorted_doc_ids:
            term_frequencies = self.get_doc_tf(doc_id)
            for token, tf in term_frequencies.items():
                tf_idf = tf * self.calculate_idf(token)
                if token not in all_tf_idf:
                    all_tf_idf[token] = [0] * len(sorted_doc_ids)
                doc_index = doc_indexes[doc_id]
                all_tf_idf[token][doc_index] = tf_idf

        df = pd.DataFrame.from_dict(all_tf_idf, orient='index', columns=sorted_doc_ids)
        df = df.round(6)
        df.to_csv(path)

    def save_tf_csv(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)

        all_term_frequencies = {}

        sorted_doc_ids = sorted(self.inverse_index.all_docs)
        doc_indexes = {doc_id: i for i, doc_id in enumerate(sorted_doc_ids)}

        for doc_id in sorted_doc_ids:
            term_frequencies = self.get_doc_tf(doc_id)
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
