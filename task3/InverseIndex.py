import os
from collections import defaultdict
from task3.QueryParser import QueryParser


class InverseIndex:
    def __init__(self):
        self.parser = QueryParser()
        self.index = defaultdict(set)
        self.all_docs = set()

    def extend(self, input_dir):
        for filename in os.listdir(input_dir):
            if filename == 'index.txt':
                continue

            filepath = os.path.join(input_dir, filename)
            if os.path.isfile(filepath):
                print(f'Добавляется файл: {filename}')
                file_id = int(filename.split('.')[0].split('_')[1])
                self.all_docs.add(file_id)

                with open(filepath, 'r', encoding='utf-8') as f:
                    for token in f:
                        token = token[:-1]
                        self.index[token].add(file_id)

    def save(self, out_path):
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, 'w', encoding='utf-8') as f:
            for key, value in self.index.items():
                f.write(f"{key}: {value}\n")

    def load(self, index_path):
        path = index_path
        self.index = defaultdict(set)
        self.all_docs = set()

        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                if ':' in line:
                    key, value = line.strip().split(':', 1)
                    ids = [v.strip() for v in value.replace('[', '').replace(']', '').split(',')]
                    ids = map(int, ids)
                    key_ids = set(ids)
                    self.index[key.strip()] = key_ids
                    self.all_docs = self.all_docs.union(key_ids)

    def query(self, input_query):
        rpn_tokens = self.parser.convert_to_rpn(input_query)

        stack = []

        for token in rpn_tokens:
            if token == "!":
                stack.append(self._not_operation(stack.pop()))
            elif token in "&|":
                a = stack.pop()
                b = stack.pop()

                if token == '&':
                    stack.append(self._and_operation(a, b))
                elif token == '|':
                    stack.append(self._or_operation(a, b))
            else:
                stack.append(set(self.index.get(token)))
        return sorted(stack.pop())

    def get_all_tokens(self):
        return self.index.keys()

    def get_item_by_key(self, key):
        return self.index.get(key)

    @staticmethod
    def _and_operation(set1, set2):
        """Логическое И (пересечение множеств)"""
        return set1.intersection(set2)

    @staticmethod
    def _or_operation(set1, set2):
        """Логическое ИЛИ (объединение множеств)"""
        return set1.union(set2)

    def _not_operation(self, doc_set):
        """Логическое НЕ (разность множеств)"""
        return self.all_docs - doc_set
