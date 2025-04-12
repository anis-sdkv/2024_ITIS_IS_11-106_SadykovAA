from InverseIndex import InverseIndex

root_dir = "../task2/out"
out_path = "out/inverse_index.txt"
input_expression = "Около"

index = InverseIndex()
index.load(out_path)
# index.extend(root_dir)
# index.save(out_path)

print(index.query(input_expression))
