from task4.TfIdf import TfIdf
from task2.TextProcessor import TextProcessor

text_processor = TextProcessor()


def get_query_tokens(query):
    query_tokens = [text_processor.lemmatize_morph(token) for token in text_processor.word_tokenize(query)]
    query_tokens = [token for token in query_tokens if not text_processor.is_stop_word(token)]
    return query_tokens


def get_links(path):
    links = []

    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split(': ', 1)  # разделить по первой ": "
            if len(parts) == 2:
                url = parts[1]
                links.append(url)
    return links


input_dir = "../task4/out"
links_dir = "../task1/out/ru.wikipedia.org/index.txt"

links = get_links(links_dir)

tf_idf = TfIdf()
tf_idf.load_cache_from_files(f"{input_dir}/tf.csv", f"{input_dir}/idf.csv")

queries = [
    "россия",
    "китай",
    "кндр",
    "россия китай",
    "россия китай кндр",
]
for q in queries:
    with_links = [(doc_id, weigth) for doc_id, weigth in
                  tf_idf.get_search_result(get_query_tokens(q))]
    print(q, with_links)
