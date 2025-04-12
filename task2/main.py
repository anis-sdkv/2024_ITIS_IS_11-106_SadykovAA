import os
from TextProcessor import TextProcessor

root_dir = "../task1/out/ru.wikipedia.org"
out_dir = "out"
processor = TextProcessor()

os.makedirs(out_dir, exist_ok=True)

for filename in os.listdir(root_dir):
    if filename == 'index.txt':
        continue

    filepath = os.path.join(root_dir, filename)
    if os.path.isfile(filepath):
        print(f'Обрабатывается файл: {filename}')
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()

        tokens = set(processor.word_tokenize(text))
        lemmatized_tokens = [processor.lemmatize_morph(token) for token in tokens]
        valid_tokens = [token for token in lemmatized_tokens if not processor.is_stop_word(token)]
        with open(os.path.join(out_dir, filename), 'w', encoding='utf-8') as file:
            file.writelines(token + "\n" for token in valid_tokens)
