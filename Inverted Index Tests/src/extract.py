from tqdm import tqdm

def load_corpus(corpus):
    docs = {}
    with open(corpus, 'r', encoding = "utf-8") as fp:
        for line in tqdm(fp.readlines()):
            doc_id, document = get_doc_id(line)
            docs[doc_id] = document
    return docs    

def get_doc_id(doc):
    arr = doc.split("\t")
    return int(arr[0]), arr[1]