import threading
from flask import Flask, render_template, send_file, send_from_directory, jsonify
from flask_socketio import SocketIO, emit
import json
from backend.extract import load_docs
from backend.preprocess import preprocess_all, preprocess_document
from backend.linkedlist import LinkedList, Node
from backend.inverted_index import InvertedIndex
from backend.main import ProjectRunner, execute_query, chitchat, docschat, get_plotly_pie, get_plotly_timeseries, get_precision_scatter
import json
from tqdm import tqdm
from dotenv import load_dotenv
from openai import OpenAI
import time
import os

load_dotenv()
app = Flask(__name__)
socketio = SocketIO(app)
openai_model = OpenAI()
relevance_model = OpenAI()

chit_chat_continue = False
doc_chat_continue = False

internal_chat_history = []

topic_counts = {"Health": 0, "Environment": 0, "Technology": 0, "Economy": 0, "Entertainment": 0, "Sports": 0, "Politics": 0, "Education": 0, "Travel": 0, "Food": 0}
query_num_terms = []
query_time_taken = []
precision_vals = []

runner = None
def init_runner():
    global runner
    print("Starting ProjectRunner preprocessing...")
    runner = ProjectRunner()
    print("ProjectRunner ready!")
    
    return

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/style.css")
def home_css():
    return send_file("templates/style.css", mimetype="text/css")

@app.route("/messages.js")
def functions_js():
    return send_file("frontend/messages.js", mimetype="text/js")

@app.route("/execute_query", methods=['POST']) # for testing without full stack working
def query_index():
    global runner
    
    if not runner:
        return jsonify({"error": "Server still loading, try again in a few seconds."}), 503
    
    return execute_query(runner)


@app.route("/profile_pic/prof_headshot_funny.jpg")
def send_alvin():
    return send_file("frontend/prof_headshot_funny.png")

@app.route("/profile_pic/max.png")
def send_max():
    return send_file("frontend/max.png")

# Handle messages from client
@socketio.on("message")
def process_message(data):
    start = time.time()
    
    global chit_chat_continue
    global doc_chat_continue
    global internal_chat_history
    global query_num_terms
    global query_time_taken
    global precision_vals
    global topic_counts
    
    
    data = json.loads(data)
    chit_chat_mode = data["chitchat"]
    
    if chit_chat_mode:
        if not chit_chat_continue:
            internal_chat_history.append({"role": "system", "content": "Disregard your previous role. You are a helpful assistant that will just chit chat with the user. If a user asks a \
                complicated question that would require something like a Google Search, classify their query based on these potential topics: \
          'Health', 'Environment', 'Technology', 'Economy', 'Entertainment', 'Sports', 'Politics', 'Education', 'Travel', and 'Food''.\
          Queries are able to have more than one topic, so if you feel more than one are relevant (up to two) are relevant, then list both of them, \
              and tell the user to click the appropriate checkboxes for the topics in order to query our database. Tell the user that \
                  their query seems to fall under the topic/topics; do not give a definitive conclusion. Do not provide them\
                  any information for that specific query after you classify it for them. If the user starts to chit chat again after the classification\
                      , continue chit chatting. Keep the answers relatively short. \
                    If the user types a string of characters that makes no sense, then you can tell them you don't understand."})
            
            chit_chat_continue = True
            
        response = chitchat(openai_model, internal_chat_history, data, runner)
        # print(internal_chat_history)
        emit("message", response, broadcast = True)
    
    else:
        if not doc_chat_continue: # first time for this state in the model to doc chat - saves token moneys
            internal_chat_history.append({"role": "system", "content": "Disregard your previous role. You are a helpful assistant. I will provide you one or more wikipedia summaries based on my database, \
                    and you will create a single cohesive, but brief summary of them to the best of your ability in relation to the query, but also referencing and relating\
                        to the summaries retrieved. You must generate the summary. If the summaries retrieved are completely irrelevant to the query,\
                            still summarize what the documents talk about, and then mention that the retrieved documents may not be entirely relevant to the query."})
            doc_chat_continue = True
            
        print(f"Received message: {data}")
        
        # num_terms is the number of terms in the query
        # topic_counts is the dict of topic -> total num docs retrieved in this topic so far
        # precision is precision

        #gurleen: once the topic_counts is determined, call the plot function
        # plot = get_plotly_pie()
        # emit("plot_data",{"type": "pie", "data": plot}, broadcast=True)
        
        # plot2 = get_plotly_timeseries(query_datetimes, query_time_taken)
        # emit("plot_data",{"type": "timeseries", "data": plot}, broadcast=True)
        
        

        doc_response, response, precision, num_terms, ret_topic_counts = docschat(openai_model, relevance_model, internal_chat_history, data, topic_counts, runner)
        
        emit("message", doc_response + response + f"<br><br> Precision of system for this query: {precision}", broadcast=True)
        
        if len(response) > 0:
            end = time.time()
            time_taken = end - start
            
            precision_vals.append(precision)
            query_num_terms.append(num_terms)
            query_time_taken.append(time_taken)
            
            pie_chart = get_plotly_pie(ret_topic_counts)
            time_graph = get_plotly_timeseries(query_num_terms, query_time_taken)     
            precision_graph = get_precision_scatter(query_num_terms, precision_vals)
            
            emit("plot_data", {"type": "pie_chart", "data": pie_chart}, broadcast=True)
            emit("plot_data", {"type": "timeseries", "data": time_graph}, broadcast=True)
            emit("plot_data", {"type": "precision_terms_graph", "data": precision_graph}, broadcast=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 9999))
    print("Starting Flask app on port", port)

    # Start ProjectRunner in background
    threading.Thread(target=init_runner, daemon=True).start()

    app.run(host="0.0.0.0", port=port, debug=False)
