from .linkedlist import LinkedList
from collections import OrderedDict

class InvertedIndex:
    def __init__(self, preprocessed_dict, total_num_docs):
        self.total_num_docs = total_num_docs
        self.inverted_index = {}
        self.preprocessed_dict = preprocessed_dict # doc id -> terms in doc id (term, tf)
        self.create_index()
        self.sort_terms()
        self.add_skips()
        
        
    def create_index(self):
        for doc_id, terms in self.preprocessed_dict.items():
            for term, tf in terms:
                if term not in self.inverted_index:
                    self.inverted_index[term] = LinkedList(self.total_num_docs)
                    self.inverted_index[term].sorted_insert(doc_id, tf)
                else:
                    self.inverted_index[term].sorted_insert(doc_id, tf)
        for terms, postings_list in self.inverted_index.items():
            postings_list.calculate_tf_idf()
    
    def sort_terms(self):
        sorted_index = OrderedDict({})
        for term in sorted(self.inverted_index.keys()):
            sorted_index[term] = self.inverted_index[term]
        self.inverted_index = sorted_index
        
    def add_skips(self):
        for term in self.inverted_index:
            self.inverted_index[term].add_skip_connections()
        