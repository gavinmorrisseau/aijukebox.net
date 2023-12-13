from flask import Flask, render_template, request, url_for
from openai import OpenAI
import time
import json
import sys
import traceback

placeholder_response = {'1': {'artist': '', 'track': ''}, '2': {'artist': '', 'track': ''}, '3': {'artist': '', 'track': ''}, '4': {'artist': '', 'track': ''}, '5': {'artist': '', 'track': ''}} 

app = Flask(__name__)

''' RETURNS CHAT GPT'S TO A QUESTION IN FORMATTED JSON OBJECT'''
def run_GPT(question):
    global placeholder_response
    print("RUNNING GPT")
    print("QUESTION: " + question)

    client = OpenAI(organization='org-1VoooiSLTr711Aax6i6A5nUT',)
    thread = client.beta.threads.create()
    assistant_id = "asst_Z8EJORrugfSAMUgxKXWNAaXw"

    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=question,
    )   
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )
    run = wait_on_run(run, client, thread)
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    message_string = messages.data[0].content[0].text.value
    print(message_string)
    message_parsed = "FAILED"
    try:
        message_parsed = json.loads(message_string)
        print("ANSWER: " + str(message_parsed))
        print("COMPLETED GPT")
        return(message_parsed)
    except json.decoder.JSONDecodeError:
        print("FAILED! placeholder_response used")
        return(placeholder_response)

def wait_on_run(run, client, thread):
    while run.status in ["queued","in_progress"]:
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.1)
    return run

@app.route('/', methods = ['POST','GET'])
def index():
    global placeholder_response
    # if request.method == 'GET':
    #     pass
    question = ''
    message_parsed = ''
    if request.method in ['POST','GET'] and request.form.get('question') != '':
        question = request.form.to_dict().get('question','')
        #print("BEHIND QUESTION: " + str(question))
        if(question not in ["",None]):
            message_parsed = run_GPT(question)
        else:
            message_parsed = placeholder_response
        #print("BEHIND MSG PARSED: " + str(message_parsed))
    return render_template("index.html", question=question, message_parsed=message_parsed)

@app.errorhandler(404)
def page_not_found(error):
    return 'This page does not exist', 404

if __name__ == "__main__":
    app.run(debug=True, port=5001)