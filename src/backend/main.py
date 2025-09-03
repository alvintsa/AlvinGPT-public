from .extract import load_docs
from .preprocess import preprocess_all, preprocess_document
from .linkedlist import LinkedList, Node
from .inverted_index import InvertedIndex

from pathlib import Path

import argparse
import json
import random
import flask
from flask import request
from tqdm import tqdm
import plotly.express as px
import plotly.graph_objects as go
from plotly import utils
import pickle
import sys
import os
import pickle


# Make print statements flush immediately
sys.stdout.reconfigure(line_buffering=True)
# app = Flask(__name__)


this_path = Path(__file__).resolve()
top_path = this_path.parents[2]
data_path = top_path/"data"

def get_keys_data(counts):
    keys = []
    data = []
    for topic in list(counts.keys()):
        if counts[topic] > 0:
            data.append(counts[topic])
            keys.append(topic)
    return keys, data


def get_precision_scatter(query_num_terms, precision_tracker):
    fig = px.scatter(x=query_num_terms, y=precision_tracker)
    fig.update_layout(title_text='precision-num-terms', title_x=0.5,  font=dict(size=12),width=300, height=300, 
    xaxis=dict(
            title=dict(
                text="num_terms"
            )
        ),
        yaxis=dict(
            title=dict(
                text="precision"
            )
    ))

    return json.loads(fig, cls=utils.PlotlyJSONEncoder)

def get_plotly_pie(topic_counts): # num docs from each topic
    topics, vals = get_keys_data(topic_counts)
    print(f"Keys: {topics}\n\n Data: {vals}")
    fig = go.Figure(data=[go.Pie(labels=topics, values=vals, textinfo='label+percent',
                             insidetextorientation='radial'
                            )])
    fig.update_layout(title_text='Distribution of documents found', title_x=0.5,  font=dict(size=12),width=300, height=300)
    return json.loads(fig, cls=utils.PlotlyJSONEncoder)

def get_plotly_timeseries(query_num_terms, query_time_taken): # time taken per query vs num tokens
    fig = px.scatter(x=query_num_terms, y=query_time_taken)
    fig.update_layout(title_text='time taken per query', title_x=0.5,  font=dict(size=12),width=300, height=300, 
    xaxis=dict(
            title=dict(
                text="num_terms"
            )
        ),
        yaxis=dict(
            title=dict(
                text="time (s)"
        )
    ))

    return json.loads(fig, cls=utils.PlotlyJSONEncoder)

class ProjectRunner:
    def __init__(self):
        # print("starting loading of docs and preprocessing of docs")
        # health_dict = preprocess_all(load_docs(data_path/"Health.json"))
        # print("loaded and preprocessed health")
        # # print(health_dict)
        # environment_dict = preprocess_all(load_docs(data_path/"Environment.json"))
        # print("loaded and preprocessed environment")

        # technology_dict = preprocess_all(load_docs(data_path/"Technology.json"))

        # print("loaded and preprocessed technology")
        # economy_dict = preprocess_all(load_docs(data_path/"Economy.json"))

        # print("loaded and preprocessed ecoomy")
        # entertainment_dict = preprocess_all(load_docs(data_path/"Entertainment.json"))

        # print("loaded and preprocessed entertainment")
        # sports_dict = preprocess_all(load_docs(data_path/"Sports.json"))

        # print("loaded and preprocessed sports")
        # politics_dict = preprocess_all(load_docs(data_path/"Politics.json"))

        # print("loaded and preprocessed politics")
        # education_dict = preprocess_all(load_docs(data_path/"Education.json"))

        # print("loaded and preprocessed education")
        # travel_dict = preprocess_all(load_docs(data_path/"Travel.json"))

        # print("loaded and preprocessed travel")
        # food_dict = preprocess_all(load_docs(data_path/"Food.json"))

        # print("loaded and preprocessed food")

        print("starting to load files")

        with open('dicts/health_dict.pkl', 'rb') as f:
            health_dict = pickle.load(f)
            
        with open('dicts/environment_dict.pkl', 'rb') as f:
            environment_dict = pickle.load(f)
        with open('dicts/technology_dict.pkl', 'rb') as f:
            technology_dict = pickle.load(f)
        with open('dicts/economy_dict.pkl', 'rb') as f:
            economy_dict = pickle.load(f)
        with open('dicts/entertainment_dict.pkl', 'rb') as f:
            entertainment_dict = pickle.load(f)
        with open('dicts/sports_dict.pkl', 'rb') as f:
            sports_dict = pickle.load(f)
        with open('dicts/politics_dict.pkl', 'rb') as f:
            politics_dict = pickle.load(f)
        with open('dicts/education_dict.pkl', 'rb') as f:
            education_dict = pickle.load(f)
        with open('dicts/travel_dict.pkl', 'rb') as f:
            travel_dict = pickle.load(f)
        with open('dicts/food_dict.pkl', 'rb') as f:
            food_dict = pickle.load(f)
    
        print("finished loading!")

        
        
        
  
        print("starting to create indexes")
        self.health_index = InvertedIndex(health_dict, len(health_dict))
        print("finished constructing health index")
        self.environment_index = InvertedIndex(environment_dict, len(environment_dict))
        print("finished constructing environment index")

        self.technology_index = InvertedIndex(technology_dict, len(technology_dict))
        print("finished constructing technology index")

        self.economy_index = InvertedIndex(economy_dict, len(economy_dict))
        print("finished constructing economy index")

        self.entertainment_index = InvertedIndex(entertainment_dict, len(entertainment_dict))
        print("finished constructing entertainment index")

        self.sports_index = InvertedIndex(sports_dict, len(sports_dict))
        print("finished constructing sports index")

        self.politics_index = InvertedIndex(politics_dict, len(politics_dict))
        print("finished constructing politics index")

        self.education_index = InvertedIndex(education_dict, len(politics_dict))
        print("finished constructing education index")

        self.travel_index = InvertedIndex(travel_dict, len(travel_dict))
        print("finished constructing travel index")

        self.food_index = InvertedIndex(food_dict, len(food_dict))
        print("finished constructing food index")
        


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

    def run_queries(self, topic_index, query_list):
        """ DO NOT CHANGE THE output_dict definition"""
        # output_dict = {'postingsList': {},
        #                'postingsListSkip': {},
        #                'daatAnd': {},
        #                'daatAndSkip': {},
        #                'daatAndTfIdf': {},
        #                'daatAndSkipTfIdf': {},
        #                }
        
        output_dict = {'postingsList': {},
                       'postingsListSkip': {},
                       'daatAndSkip': {},
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
                try:
                    print(f"{term} TERM LOOK HERE1")
                    postings = topic_index.inverted_index[term].traverse_list()
                    skip_postings = topic_index.inverted_index[term].traverse_skips()
                    
                    output_dict['postingsList'][term] = postings
                    output_dict['postingsListSkip'][term] = skip_postings
                    postings_for_daat.append(topic_index.inverted_index[term])
                    print(f"{term} TERM LOOK HERE2")

                except:
                    output_dict['postingsList'][term] = []
                    output_dict['postingsListSkip'][term] = []
                    postings_for_daat.append(LinkedList())
                    

            

            if len(input_term_arr) > 1:
                
                # no_skip_results = self.process_DAAT_AND_query(postings_for_daat, query)
                skip_results = self.process_DAAT_AND_query(postings_for_daat, query, skip = True)
                # no_skip_results_tf_idf = self.process_DAAT_AND_query(postings_for_daat, query, sort_tf_idf = True)
                skip_results_tf_idf = self.process_DAAT_AND_query(postings_for_daat, query, skip = True, sort_tf_idf = True)
                

                # and_op_no_skip, and_op_skip, and_op_no_skip_sorted, and_op_skip_sorted = no_skip_results["results"], skip_results["results"], no_skip_results_tf_idf["results"], skip_results_tf_idf["results"]

                and_op_skip, and_op_skip_sorted =  skip_results["results"], skip_results_tf_idf["results"]
                
                # and_comparisons_no_skip, and_comparisons_skip, \
                #     and_comparisons_no_skip_sorted, and_comparisons_skip_sorted = no_skip_results["num_comparisons"], skip_results["num_comparisons"], no_skip_results_tf_idf["num_comparisons"], skip_results_tf_idf["num_comparisons"]
                
                and_comparisons_skip, and_comparisons_skip_sorted =  skip_results["num_comparisons"], skip_results_tf_idf["num_comparisons"]
                """ Implement logic to populate initialize the above variables.
                    The below code formats your result to the required format.
                    To be implemented."""
                    
                # and_op_no_score_no_skip, and_results_cnt_no_skip = self._output_formatter(and_op_no_skip)
                # and_op_no_score_skip, and_results_cnt_skip = self._output_formatter(and_op_skip)
                # and_op_no_score_no_skip_sorted, and_results_cnt_no_skip_sorted = self._output_formatter(and_op_no_skip_sorted)
                # and_op_no_score_skip_sorted, and_results_cnt_skip_sorted = self._output_formatter(and_op_skip_sorted)



                # output_dict['daatAnd'][query.strip()] = {}
                # output_dict['daatAnd'][query.strip()]['results'] = and_op_no_score_no_skip
                # output_dict['daatAnd'][query.strip()]['num_docs'] = and_results_cnt_no_skip
                # output_dict['daatAnd'][query.strip()]['num_comparisons'] = and_comparisons_no_skip

                # output_dict['daatAndSkip'][query.strip()] = {}
                # output_dict['daatAndSkip'][query.strip()]['results'] = and_op_no_score_skip
                # output_dict['daatAndSkip'][query.strip()]['num_docs'] = and_results_cnt_skip
                # output_dict['daatAndSkip'][query.strip()]['num_comparisons'] = and_comparisons_skip

                # output_dict['daatAndTfIdf'][query.strip()] = {}
                # output_dict['daatAndTfIdf'][query.strip()]['results'] = and_op_no_score_no_skip_sorted
                # output_dict['daatAndTfIdf'][query.strip()]['num_docs'] = and_results_cnt_no_skip_sorted
                # output_dict['daatAndTfIdf'][query.strip()]['num_comparisons'] = and_comparisons_no_skip_sorted

                # output_dict['daatAndSkipTfIdf'][query.strip()] = {}
                # output_dict['daatAndSkipTfIdf'][query.strip()]['results'] = and_op_no_score_skip_sorted
                # output_dict['daatAndSkipTfIdf'][query.strip()]['num_docs'] = and_results_cnt_skip_sorted
                # output_dict['daatAndSkipTfIdf'][query.strip()]['num_comparisons'] = and_comparisons_skip_sorted
                
                
                and_op_no_score_skip, and_results_cnt_skip = self._output_formatter(and_op_skip)
                and_op_no_score_skip_sorted, and_results_cnt_skip_sorted = self._output_formatter(and_op_skip_sorted)

                output_dict['daatAndSkip'][query.strip()] = {}
                output_dict['daatAndSkip'][query.strip()]['results'] = and_op_no_score_skip
                output_dict['daatAndSkip'][query.strip()]['num_docs'] = and_results_cnt_skip
                output_dict['daatAndSkip'][query.strip()]['num_comparisons'] = and_comparisons_skip

                output_dict['daatAndSkipTfIdf'][query.strip()] = {}
                output_dict['daatAndSkipTfIdf'][query.strip()]['results'] = and_op_no_score_skip_sorted
                output_dict['daatAndSkipTfIdf'][query.strip()]['num_docs'] = and_results_cnt_skip_sorted
                output_dict['daatAndSkipTfIdf'][query.strip()]['num_comparisons'] = and_comparisons_skip_sorted
            else:
                    print(f"{term} TERM LOOK HERE3")
                   
                    skip_results_tf_idf = postings_for_daat[0].sort_by_tf_idf()
                    print(skip_results_tf_idf)

                    and_op_no_score_skip_sorted, and_results_cnt_skip_sorted = self._output_formatter(skip_results_tf_idf)
                    print(and_op_no_score_skip_sorted)
                    print(and_results_cnt_skip_sorted)



                    output_dict['daatAndSkip'][query.strip()] = {}
                    output_dict['daatAndSkip'][query.strip()]['results'] = {}
                    output_dict['daatAndSkip'][query.strip()]['num_docs'] = {}
                    output_dict['daatAndSkip'][query.strip()]['num_comparisons'] = {}

                    output_dict['daatAndSkipTfIdf'][query.strip()] = {}
                    output_dict['daatAndSkipTfIdf'][query.strip()]['results'] = and_op_no_score_skip_sorted
                    output_dict['daatAndSkipTfIdf'][query.strip()]['num_docs'] = and_results_cnt_skip_sorted
                    output_dict['daatAndSkipTfIdf'][query.strip()]['num_comparisons'] = {}
                

        return output_dict
    
def get_topic_index(topic, runner):
    if topic == "Health":
        return runner.health_index
    elif topic == "Environment":
        return runner.environment_index
    elif topic == "Technology":
        return runner.technology_index
    elif topic == "Economy":
        return runner.economy_index
    elif topic == "Entertainment":
        return runner.entertainment_index
    elif topic == "Sports":
        return runner.sports_index
    elif topic == "Politics":
        return runner.politics_index
    elif topic == "Education":
        return runner.education_index
    elif topic == "Travel":
        return runner.travel_index
    else: # guranteed to be all or at least one of them, so else is fine here
        return runner.food_index
    
def get_topic_dict(topic):
    if topic == "Health":
        with open(data_path/"Health.json", "rb") as file:
            loaded = json.load(file)
        return loaded
    elif topic == "Environment":
        with open(data_path/"Environment.json", "rb") as file:
            loaded = json.load(file)
        return loaded
    elif topic == "Technology":
        with open(data_path/"Technology.json", "rb") as file:
            loaded = json.load(file)
        return loaded
    elif topic == "Economy":
        with open(data_path/"Economy.json", "rb") as file:
            loaded = json.load(file)
        return loaded
    elif topic == "Entertainment":
        with open(data_path/"Entertainment.json", "rb") as file:
            loaded = json.load(file)
        return loaded
    elif topic == "Sports":
        with open(data_path/"Sports.json", "rb") as file:
            loaded = json.load(file)
        return loaded
    elif topic == "Politics":
        with open(data_path/"Politics.json", "rb") as file:
            loaded = json.load(file)
        return loaded
    elif topic == "Education":
        with open(data_path/"Education.json", "rb") as file:
            loaded = json.load(file)
        return loaded
    elif topic == "Travel":
        with open(data_path/"Travel.json", "rb") as file:
            loaded = json.load(file)
        return loaded
    else: # guranteed to be all or at least one of them, so else is fine here
        with open(data_path/"Food.json", "rb") as file:
            loaded = json.load(file)
        return loaded
        
# curl -X POST http://127.0.0.1:9999/execute_query -H "Content-Type: application/json" -d '{"queries" : ["hello world", "hello swimming", "swimming going", "random swimming”], "random_command": "print"}’

# @app.route("/execute_query", methods=['POST'])

def chitchat(openai_model, model_message_history, json_data, runner):
    user_message = json_data["query"]
    model_message_history.append({
                "role": "user",
                "content": user_message
            })
    
    completion = openai_model.chat.completions.create(
    model="gpt-4o-mini",
    messages= model_message_history
    )
    
    response = completion.choices[0].message.content
    
    return response
    
def docschat(openai_model, relevance_model, model_message_history, json_data, topic_counts, runner):
    
    query = json_data["query"]
    doc_summaries = []
    
    try:
        response_dict, ret_topic_counts, num_docs = execute_query(json_data, topic_counts, runner)
    except:
        print("excepted")
        return "Sorry, but there were no relevant documents found for your query. Please refine your query or select different topics and try again.", "", 0, {}, 0
    
    if num_docs == 0:
        print("no rel docs")
        return "Sorry, but there were no relevant documents found for your query. Please refine your query and try again.", "", 0, {}, 0
    
    content = ""
    doc_info_response = f"Here are documents that I found for \"{query}\": <br><br>"

    topic_counter = 1
    
    for topic in response_dict:
        doc_info_response += f"<b>{topic} Documents: <br></b>"
        # topic_counts[topic] += len(response_dict[topic])
        if len(response_dict[topic]) > 0:
            for doc_id in response_dict[topic]:
                content += response_dict[topic][doc_id][1]
                doc_summaries.append(response_dict[topic][doc_id][1])
                doc_title = response_dict[topic][doc_id][0]
                doc_link = response_dict[topic][doc_id][2]
                embedded_link_title = f"<a href =\"{doc_link}\">{doc_title}</a>"
                doc_info_response += f"Document {topic_counter} - {embedded_link_title}<br>"
                # doc_info_response += f"<br><br>Document {topic_counter} - {response_dict[topic][doc_id][0]}: {response_dict[topic][doc_id][2]}<br><br>"
                topic_counter += 1
            doc_info_response += "<br>"
        else:
            doc_info_response += "None <br><br>"
            
    doc_info_response += "Here is a summary I generated based on the documents retrieved: <br><br>"     
    
    model_message_history.append({
                "role": "user",
                "content": f"Here are summaries of docs retrieved for the query {query} Summarize all of them in one short cohesive paragraph. {content}"
            })
    
    completion = openai_model.chat.completions.create(
        model = "gpt-4o-mini",
        messages = model_message_history
    )
    
    response = completion.choices[0].message.content 
    print(ret_topic_counts)
    
    relevant = 0
    precision = len(doc_summaries)
    
    for summary in doc_summaries:
        relevance_response = relevance_model.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
                {"role": "system", "content": "You are a helpful assistant. Your job is to answer 'Relevant' or 'Non-relevant' in relation\
                to a query for a Wikipedia document summary, which will both be provided to you. Make sure you only answer 'Relevant' or 'Non-relevant'."
                },
                {
                "role": "user",
                "content": f"The query is {query}, and the document summary is {summary}."
                }
            ]
        )
        
        if relevance_response.choices[0].message.content.strip() == "Relevant":
            relevant += 1
    
    if len(doc_summaries) != 0:
        precision = relevant / precision

    num_terms = len(runner.preprocess_query(query))

    # query_num_terms.append(num_terms)
    # query_time_taken.append(1)
    
    # pie_chart = get_plotly_pie()
    # time_graph = get_plotly_timeseries()
    
    return doc_info_response, response, precision, num_terms, ret_topic_counts
    
    
    
def execute_query(json_data, topic_counts, runner):
    """ This function handles the POST request to your endpoint.
        Do NOT change it."""
    
    docs_retrieved = 0
    
    output_dict = {}
    result_dict = {}
    
    topics = json_data["topic_type"].strip().split(",")
    topics = [topic.strip() for topic in topics]
    print(f"TOPICS AFTER STRIP AND SPLIT {topics}")
    queries = json_data["query"]

    """ Running the queries against the pre-loaded index. """
    
    for topic in topics:
        output_dict[topic] = runner.run_queries(get_topic_index(topic, runner), [queries])

        """ loading the results to a JSON file. """
    with open("output_result.json", 'w') as fp:
        json.load(output_dict, fp)
        
    for topic in output_dict:
        topic_dict = get_topic_dict(topic)
        # print(f"topic dict {topic_dict}")
        retrieved_docs = output_dict[topic]["daatAndSkipTfIdf"]
        
        print(f"retrieved docs {retrieved_docs}")
        result_dict[topic] = {}
        
        if len(retrieved_docs[queries]["results"]) > 0:
            docs_retrieved += 1
            topic_counts[topic] += len(retrieved_docs[queries]["results"])
        n = 0
        for doc_id in retrieved_docs[queries]["results"]:
            if n == 3:
                break
            print(f"{topic} with {result_dict}")
            result_dict[topic][str(doc_id)] = topic_dict[str(doc_id)]
            print(f"{topic} with {result_dict}\n")
            n += 1

    
    
    """ loading the results to a JSON file. """
    with open("sample_result.json", 'w') as fp:
        json.load(result_dict, fp)

    response = result_dict
    
    return response, topic_counts, docs_retrieved


# if __name__ == "__main__":
#     """ Driver code for the project, which defines the global variables.
#         Do NOT change it."""

#     output_location = "project2_output.json"
#     parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
#     parser.add_argument("--corpus", type=str, help="Corpus File name, with path.")
#     parser.add_argument("--output_location", type=str, help="Output file name.", default=output_location)

#     argv = parser.parse_args()

#     corpus = argv.corpus
#     output_location = argv.output_location

#     """ Initialize the project runner"""
#     runner = ProjectRunner(corpus)

#     app.run(host="0.0.0.0", port=9999, debug = True)               
                
                
            
        
        
        
        





