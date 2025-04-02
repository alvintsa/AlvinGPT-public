import nltk

from nltk.stem.porter import *
from nltk.corpus import stopwords

def preprocess_all(documents):
    result = {}
    for doc_id, doc in documents.items():
        doc_summary = doc[1]
        terms = preprocess_document(doc_summary)
        terms_with_tf = calculate_tf(terms)
        # print(terms_with_tf)
        result[doc_id] = terms_with_tf
    return result 
        
    
def preprocess_document(document):
    new_document = remove_special(document)
    tokenized_doc = tokenize(new_document)
    stop_removed_tokens = remove_stop(tokenized_doc)
    terms = porter_stem(stop_removed_tokens)
    
    return terms  

def calculate_tf(terms):
    result = []
    seen_terms = set()
    n = len(terms)
    tf = 0
    
    for i in range(n):
        if terms[i] in seen_terms:
            continue
        token_freq = 1
        for j in range(n):
            if i != j:
                if terms[i] == terms[j]:
                    token_freq += 1
        if n != 0:
            tf = token_freq/n
        result.append( (terms[i], tf) )
        seen_terms.add(terms[i])
    
    return result
        
        

def remove_special(document):
    valid_chars = {"a", "b", "c", "d", "e", "f", "g", "h", 
                      "i", "j", "k", "l", "m", "n", "o", "p", 
                      "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
                      "A", "B", "C", "D", "E", "F", "G", "H", 
                      "I", "J", "K", "L", "M", "N", "O", "P",
                      "Q", "R", "S", "T", "U", "V", "W", 
                      "X", "Y", "Z", "0", "1", "2", "3", "4", "5",
                      "6", "7", "8", "9", " "}
    result = ""
    for char in document:
        if char in valid_chars:
            result += char.lower()
        else:
            result += " "
            
    return result

def tokenize(document): # removes white spaces and tokenizes
    return document.split()

def remove_stop(tokenized_document):
    result = []
    
    # nltk.download("stopwords")
    stop_words = set(stopwords.words("english"))
    
    for token in tokenized_document:
        if token not in stop_words:
            result.append(token)
    
    return result
      
 
def porter_stem(tokenized_document):
    porter_stemmer = PorterStemmer()
    stemmed_tokens = [porter_stemmer.stem(token) for token in tokenized_document]
    
    return stemmed_tokens
    




