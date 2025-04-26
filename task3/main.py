from task3.InverseIndex import InverseIndex

root_dir = "../task2/out"
out_path = "out/inverse_index.txt"
query_out = "out/query_results.txt"
input_expression = "Около"

index = InverseIndex()
index.load(out_path)
# index.extend(root_dir)
# index.save(out_path)

word1 = "Кндр"
word2 = "Россия"
word3 = "Казахстан"

q1 = f"{word1} & {word2} | {word3}"
q2 = f"{word1} & !{word2} | !{word3}"
q3 = f"{word1} | {word2} | {word3}"
q4 = f"{word1} | !{word2} | !{word3}"
q5 = f"{word1} & {word2} & {word3}"

with open(query_out, "w", encoding="utf-8") as f:
    for query in [q1, q2, q3, q4, q5]:
        result = index.query(query)
        f.write(f"{query}:\n")
        f.write(f"Результат: {sorted(result)}\n\n")
