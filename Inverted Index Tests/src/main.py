from extract import load_corpus
from preprocess import preprocess_all, preprocess_document
from linkedlist import LinkedList, Node
from inverted_index import InvertedIndex
import argparse
import json
import random
import flask
from flask import Flask
from flask import request
from tqdm import tqdm

app = Flask(__name__)

class ProjectRunner:
    def __init__(self, corpus):
        self.corpus_file = corpus
        
        docs_dict = load_corpus(self.corpus_file)
        preprocessed_dict = preprocess_all(docs_dict)
        total_num_docs = len(preprocessed_dict)
        self.inverted_index = InvertedIndex(preprocessed_dict, total_num_docs)
        
        
    def preprocess_query(self, query):
        prepocessed_query = preprocess_document(query)
        return prepocessed_query

    def process_regular_query(self, result_dict, terms, skip = False):
        for term in terms:
            postings = self.inverted_index.inverted_index[term]
            if not skip:
                result_dict["postingsList"][term.strip()] = postings.traverse_list()
            else:
                result_dict["postingsListSkip"][term.strip()] = postings.traverse_skips()
                
        return

    def merge_postings(self, posting_1, posting_2, key, skip = False):
        comparisons = 0
        result = {key: LinkedList()}
        
        ptr_1 = posting_1.head
        ptr_2 = posting_2.head
        
        while ptr_1 and ptr_2:
            if ptr_1.value == ptr_2.value:
                result[key].sorted_insert(ptr_1.value, max(ptr_1.tf_idf, ptr_2.tf_idf))
                ptr_1 = ptr_1.next
                ptr_2 = ptr_2.next
            elif ptr_1.value < ptr_2.value:
                if not skip:
                    ptr_1 = ptr_1.next
                else:
                    if isinstance(ptr_1.skip, Node) and ptr_1.skip.value <= ptr_2.value:
                        while isinstance(ptr_1.skip, Node) and ptr_1.skip.value <= ptr_2.value:
                            ptr_1 = ptr_1.skip
                    else:
                        ptr_1 = ptr_1.next                    
            else:
                if not skip:
                    ptr_2 = ptr_2.next
                else:
                    if isinstance(ptr_2.skip, Node) and ptr_2.skip.value <= ptr_1.value:
                        while isinstance(ptr_2.skip, Node) and ptr_2.skip.value <= ptr_1.value:
                            ptr_2 = ptr_2.skip
                    else:
                        ptr_2 = ptr_2.next        
                    
            comparisons += 1
                
        return result, comparisons            
        
        

    def process_DAAT_AND_query(self, term_postings, query, skip = False, sort_tf_idf = False): #["hello world", "swimming going", "random swimming"]
        
        temp_merged = None
        accumulated_num_comparisons = 0
        
        sorted_term_postings = sorted(term_postings, key = lambda term_postings: term_postings.length)
        # print(f"term postings: {term_postings}")
        # for s in term_postings:
        #     print(s.length)
            
        # print(f"sorted_termpostings: {sorted_term_postings}")
        # for t in sorted_term_postings:
        #     print(t.length)
                    
        
        for i in range(1, len(sorted_term_postings), 2):
            temp_merged, num_comparisons = self.merge_postings(sorted_term_postings[i-1], sorted_term_postings[i], query, skip = skip)
            accumulated_num_comparisons += num_comparisons
        # print(temp_merged)
        if len(sorted_term_postings) % 2 != 0:
            temp_merged, num_comparisons = self.merge_postings(temp_merged[query], term_postings[len(sorted_term_postings) - 1], query, skip = skip)
            accumulated_num_comparisons += num_comparisons
        
        if not skip:
            if not sort_tf_idf:
                return {"num_comparisons": accumulated_num_comparisons, "num_docs": temp_merged[query].length, "results": temp_merged[query].traverse_list()}
            else:
                return {"num_comparisons": accumulated_num_comparisons, "num_docs": temp_merged[query].length, "results": temp_merged[query].sort_by_tf_idf()}
        else:
            if not sort_tf_idf:
                return {"num_comparisons": accumulated_num_comparisons, "num_docs": temp_merged[query].length, "results": temp_merged[query].traverse_list()}
            else:
                return {"num_comparisons": accumulated_num_comparisons, "num_docs": temp_merged[query].length, "results": temp_merged[query].sort_by_tf_idf()}
            
        
            
            
                


    def _output_formatter(self, op):
        """ This formats the result in the required format.
            Do NOT change."""
        if op is None or len(op) == 0:
            return [], 0
        op_no_score = [int(i) for i in op]
        results_cnt = len(op_no_score)
        return op_no_score, results_cnt

    def sanity_checker(self, command):
        """ DO NOT MODIFY THIS. THIS IS USED BY THE GRADER. """

        index = self.inverted_index.inverted_index
        kw = random.choice(list(index.keys()))
        return {"index_type": str(type(index)),
                "indexer_type": str(type(self.inverted_index.inverted_index)),
                "post_mem": str(index[kw]),
                "post_type": str(type(index[kw])),
                "node_mem": str(index[kw].head),
                "node_type": str(type(index[kw].head)),
                "node_value": str(index[kw].head.value),
                "command_result": eval(command) if "." in command else ""}

    def run_queries(self, query_list):
        """ DO NOT CHANGE THE output_dict definition"""
        output_dict = {'postingsList': {},
                       'postingsListSkip': {},
                       'daatAnd': {},
                       'daatAndSkip': {},
                       'daatAndTfIdf': {},
                       'daatAndSkipTfIdf': {},
                       }

        for query in tqdm(query_list):
            """ Run each query against the index. You should do the following for each query:
                1. Pre-process & tokenize the query.
                2. For each query token, get the postings list & postings list with skip pointers.
                3. Get the DAAT AND query results & number of comparisons with & without skip pointers.
                4. Get the DAAT AND query results & number of comparisons with & without skip pointers, 
                    along with sorting by tf-idf scores."""
            input_term_arr = self.preprocess_query(query)
                
            postings_for_daat = []
            
            for term in input_term_arr:
                postings = self.inverted_index.inverted_index[term].traverse_list()
                skip_postings = self.inverted_index.inverted_index[term].traverse_skips()
                
                output_dict['postingsList'][term] = postings
                output_dict['postingsListSkip'][term] = skip_postings
                postings_for_daat.append(self.inverted_index.inverted_index[term])

            

            if len(input_term_arr) > 1:
                
                no_skip_results = self.process_DAAT_AND_query(postings_for_daat, query)
                skip_results = self.process_DAAT_AND_query(postings_for_daat, query, skip = True)
                no_skip_results_tf_idf = self.process_DAAT_AND_query(postings_for_daat, query, sort_tf_idf = True)
                skip_results_tf_idf = self.process_DAAT_AND_query(postings_for_daat, query, skip = True, sort_tf_idf = True)
                


                and_op_no_skip, and_op_skip, and_op_no_skip_sorted, and_op_skip_sorted = no_skip_results["results"], skip_results["results"], no_skip_results_tf_idf["results"], skip_results_tf_idf["results"]
                
                and_comparisons_no_skip, and_comparisons_skip, \
                    and_comparisons_no_skip_sorted, and_comparisons_skip_sorted = no_skip_results["num_comparisons"], skip_results["num_comparisons"], no_skip_results_tf_idf["num_comparisons"], skip_results_tf_idf["num_comparisons"]
                """ Implement logic to populate initialize the above variables.
                    The below code formats your result to the required format.
                    To be implemented."""
                and_op_no_score_no_skip, and_results_cnt_no_skip = self._output_formatter(and_op_no_skip)
                and_op_no_score_skip, and_results_cnt_skip = self._output_formatter(and_op_skip)
                and_op_no_score_no_skip_sorted, and_results_cnt_no_skip_sorted = self._output_formatter(and_op_no_skip_sorted)
                and_op_no_score_skip_sorted, and_results_cnt_skip_sorted = self._output_formatter(and_op_skip_sorted)
                
                output_dict['daatAnd'][query.strip()] = {}
                output_dict['daatAnd'][query.strip()]['results'] = and_op_no_score_no_skip
                output_dict['daatAnd'][query.strip()]['num_docs'] = and_results_cnt_no_skip
                output_dict['daatAnd'][query.strip()]['num_comparisons'] = and_comparisons_no_skip

                output_dict['daatAndSkip'][query.strip()] = {}
                output_dict['daatAndSkip'][query.strip()]['results'] = and_op_no_score_skip
                output_dict['daatAndSkip'][query.strip()]['num_docs'] = and_results_cnt_skip
                output_dict['daatAndSkip'][query.strip()]['num_comparisons'] = and_comparisons_skip

                output_dict['daatAndTfIdf'][query.strip()] = {}
                output_dict['daatAndTfIdf'][query.strip()]['results'] = and_op_no_score_no_skip_sorted
                output_dict['daatAndTfIdf'][query.strip()]['num_docs'] = and_results_cnt_no_skip_sorted
                output_dict['daatAndTfIdf'][query.strip()]['num_comparisons'] = and_comparisons_no_skip_sorted

                output_dict['daatAndSkipTfIdf'][query.strip()] = {}
                output_dict['daatAndSkipTfIdf'][query.strip()]['results'] = and_op_no_score_skip_sorted
                output_dict['daatAndSkipTfIdf'][query.strip()]['num_docs'] = and_results_cnt_skip_sorted
                output_dict['daatAndSkipTfIdf'][query.strip()]['num_comparisons'] = and_comparisons_skip_sorted
            else:
                    output_dict['daatAnd'][query.strip()] = {}
                    output_dict['daatAnd'][query.strip()]['results'] = {}
                    output_dict['daatAnd'][query.strip()]['num_docs'] = {}
                    output_dict['daatAnd'][query.strip()]['num_comparisons'] = {}

                    output_dict['daatAndSkip'][query.strip()] = {}
                    output_dict['daatAndSkip'][query.strip()]['results'] = {}
                    output_dict['daatAndSkip'][query.strip()]['num_docs'] = {}
                    output_dict['daatAndSkip'][query.strip()]['num_comparisons'] = {}

                    output_dict['daatAndTfIdf'][query.strip()] = {}
                    output_dict['daatAndTfIdf'][query.strip()]['results'] = {}
                    output_dict['daatAndTfIdf'][query.strip()]['num_docs'] = {}
                    output_dict['daatAndTfIdf'][query.strip()]['num_comparisons'] = {}

                    output_dict['daatAndSkipTfIdf'][query.strip()] = {}
                    output_dict['daatAndSkipTfIdf'][query.strip()]['results'] = {}
                    output_dict['daatAndSkipTfIdf'][query.strip()]['num_docs'] = {}
                    output_dict['daatAndSkipTfIdf'][query.strip()]['num_comparisons'] = {}
                

        return output_dict    
    
# curl -X POST http://127.0.0.1:9999/execute_query -H "Content-Type: application/json" -d '{"queries" : ["hello world", "hello swimming", "swimming going", "random swimming”], "random_command": "print"}’

@app.route("/execute_query", methods=['POST'])
def execute_query():
    """ This function handles the POST request to your endpoint.
        Do NOT change it."""

    queries = request.json["queries"]

    """ Running the queries against the pre-loaded index. """
    output_dict = runner.run_queries(queries)

    """ Dumping the results to a JSON file. """
    with open(output_location, 'w') as fp:
        json.dump(output_dict, fp)

    response = {
        "Response": output_dict,
    }
    return flask.jsonify(response)


if __name__ == "__main__":
    """ Driver code for the project, which defines the global variables.
        Do NOT change it."""

    output_location = "project2_output.json"
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--corpus", type=str, help="Corpus File name, with path.")
    parser.add_argument("--output_location", type=str, help="Output file name.", default=output_location)

    argv = parser.parse_args()

    corpus = argv.corpus
    output_location = argv.output_location

    """ Initialize the project runner"""
    runner = ProjectRunner(corpus)

    app.run(host="0.0.0.0", port=9999, debug = True)               
                
                
            
        
        
        
        





