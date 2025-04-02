import json

def load_docs(json_file):
    with open(json_file) as file:
        docs = json.load(file)
    return docs 